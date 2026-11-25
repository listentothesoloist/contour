#requires -Version 7.4
[CmdletBinding()]
param(
    [switch]$ValidateOnly,
    [switch]$Preflight,
    [switch]$SkipChecksum
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$context = 'docker-desktop'

function Invoke-Checked([string]$program, [string[]]$arguments) {
    & $program @arguments
    if ($LASTEXITCODE -ne 0) { throw "$program exited with code $LASTEXITCODE." }
}

Push-Location -LiteralPath $PSScriptRoot
try {
    if ($ValidateOnly -or !$SkipChecksum) {
        if (!(Test-Path -LiteralPath 'FILES.sha256.json' -PathType Leaf)) {
            throw 'Manifest file FILES.sha256.json not found.'
        }
        $payload = Get-Content -LiteralPath 'FILES.sha256.json' -Raw | ConvertFrom-Json -AsHashtable
        foreach ($entry in $payload.GetEnumerator()) {
            $relative = $entry.Key
            if ($relative -notmatch '^[\p{L}\p{Nd}._ /()—-]+$' -or $relative -match '(?:^|/)\.\.(?:/|$)' -or $relative.StartsWith('/')) {
                throw "Invalid path in manifest: $relative"
            }
            $actual = (Get-FileHash -LiteralPath $relative -Algorithm SHA256).Hash
            if ($actual -ne $entry.Value) {
                throw "Checksum mismatch: $relative (use -SkipChecksum for local edits)."
            }
        }
        Write-Host "Verified checksums for $($payload.Count) files."
        if ($ValidateOnly) { return }
    } else {
        Write-Host 'Skipped FILES.sha256.json verification (-SkipChecksum).'
    }

    foreach ($tool in 'docker', 'kubectl') {
        if (!(Get-Command $tool -ErrorAction SilentlyContinue)) { throw "Utility $tool not found in PATH." }
    }

    $engine = Invoke-Checked 'docker' @('info', '--format', '{{.OSType}}|{{.Architecture}}|{{.OperatingSystem}}')
    $system, $architecture, $distribution = $engine -split '\|', 3
    if ($system -ne 'linux' -or $distribution -notmatch 'Docker Desktop') {
        if ($IsWindows) {
            throw 'Docker Desktop running in Linux containers mode (WSL 2) is required.'
        }
        throw 'Connection to local Docker Desktop is required.'
    }
    $nodes = (Invoke-Checked 'kubectl' @('--context', $context, '--request-timeout=15s', 'get', 'nodes', '-o', 'json') | Out-String) |
        ConvertFrom-Json
    $ready = @($nodes.items | Where-Object { $_.status.conditions | Where-Object { $_.type -eq 'Ready' -and $_.status -eq 'True' } })
    if ($ready.Count -ne 1 -or $ready[0].status.nodeInfo.operatingSystem -ne 'linux') {
        throw 'Docker Desktop Kubernetes requires one Ready Linux node (kind). Check Kubernetes settings.'
    }
    $arch = $ready[0].status.nodeInfo.architecture
    $engineArch = switch ($architecture) {
        'x86_64' { 'amd64' }
        'aarch64' { 'arm64' }
        default { $architecture }
    }
    if ($arch -notin @('arm64','amd64') -or $arch -ne $engineArch) {
        throw "Expected a Docker Desktop Linux node with native amd64 or arm64 architecture. Node: $arch, Docker: $engineArch."
    }
    $platform = "linux/$arch"
    if ($Preflight) {
        Write-Host "Ready: Docker and Kubernetes $context ($platform)."
        return
    }

    $build = @('build', '--platform', $platform, '--provenance=false', '--sbom=false')
    Invoke-Checked 'docker' ($build + @('-t', 'otel-course-invoices:local', './invoice-service'))
    Invoke-Checked 'docker' ($build + @('-t', 'otel-course-generator:local', './generator'))
    Invoke-Checked 'docker' @('pull', '--platform', $platform, 'aquasec/trivy:0.76.2')
    Invoke-Checked 'docker' ($build + @('-t', 'target-security-audit:passive-v2', '-t', 'target-security-audit:local', './security-audit'))
    Invoke-Checked 'docker' ($build + @('-f', './security-audit/Dockerfile.model', '-t', 'target-audit-model:local', './security-audit'))

    & './deploy.ps1' -Context $context
    Invoke-Checked 'kubectl' @('--context', $context, '-n', 'observability', 'get', 'deployments,pods,pvc')
} finally {
    Pop-Location
}
