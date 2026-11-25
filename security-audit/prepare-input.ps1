[CmdletBinding(DefaultParameterSetName = 'Snapshot')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Snapshot')][string]$OutputFile,
    [Parameter(Mandatory, ParameterSetName = 'Sboms')][string]$SbomOutputDirectory,
    [ValidateSet('docker-desktop', 'kind-otel-course')][string]$Context = 'docker-desktop',
    [string[]]$ImageFilter = @()
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$namespace = 'observability'
$kubeArgs = @('--context', $Context, '-n', $namespace)
if ($Context -eq 'kind-otel-course') {
    $kubeArgs += @('--kubeconfig', (Join-Path $PSScriptRoot '../.kubeconfig'))
}
$arch = & kubectl @kubeArgs get nodes -o 'jsonpath={.items[0].status.nodeInfo.architecture}'
if ($LASTEXITCODE -ne 0 -or $arch -notin @('amd64', 'arm64')) { throw 'Failed to determine a supported node architecture.' }
$platform = "linux/$arch"
$result = & kubectl @kubeArgs get pods,deployments,services,networkpolicies,roles,rolebindings -o json
if ($LASTEXITCODE -ne 0) { throw 'Could not read the namespace inventory.' }
$resources = ($result | ConvertFrom-Json -Depth 60).items
$pods = @($resources | Where-Object {
    $_.kind -eq 'Pod' -and ($SbomOutputDirectory -or $_.status.phase -eq 'Running') -and
    !$_.metadata.deletionTimestamp -and
    $_.metadata.labels.app -ne 'target-security-audit'
})
$capturedAt = [DateTimeOffset]::UtcNow.ToString('o')

$catalog = 'https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json'
$kev = @{}
$feedStatus = @{ status = 'unavailable'; source = $catalog }
if (!$SbomOutputDirectory) {
    try {
        $feed = Invoke-RestMethod $catalog -TimeoutSec 20
        if (!$feed.vulnerabilities) { throw 'Empty KEV catalogue.' }
        foreach ($entry in $feed.vulnerabilities) { $kev[$entry.cveID] = $true }
        $feedStatus = @{
            status = 'ok'
            source = $catalog
            retrievedAt = [DateTimeOffset]::UtcNow.ToString('o')
            catalogVersion = $feed.catalogVersion
            entries = $kev.Count
        }
    } catch {
        Write-Warning 'The CISA KEV catalogue is unavailable. The report will mark this coverage gap.'
    }
}

$inventory = @()
$images = @{}
foreach ($pod in $pods) {
    $spec = $pod.spec
    $containers = @($spec.containers) + @($spec.initContainers | Where-Object { $_ })
    $inventory += @{
        name = $pod.metadata.name
        app = $pod.metadata.labels.app
        labels = $pod.metadata.labels
        hostNetwork = [bool]$spec.hostNetwork
        hostPID = [bool]$spec.hostPID
        hostIPC = [bool]$spec.hostIPC
        hostVolumes = @($spec.volumes | Where-Object { $_.hostPath } | ForEach-Object name)
        tokenMounted = [bool]@($spec.volumes | Where-Object { $_.projected.sources.serviceAccountToken }).Count
        serviceAccount = $spec.serviceAccountName
        securityContext = $spec.securityContext
        containers = @(foreach ($container in $containers) {
            $cmdTokens = @($container.command | Where-Object { $_ }) + @($container.args | Where-Object { $_ })
            $secretArgs = @()
            for ($i = 0; $i -lt $cmdTokens.Count; $i++) {
                $token = [string]$cmdTokens[$i]
                if ($token -match '(?i)^(-{1,2}[a-z0-9_.-]*(?:password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key|token))=(.+)$') {
                    $val = $Matches[2].Trim('"', "'")
                    if ($val -and $val -notmatch '^\$') { $secretArgs += $Matches[1] }
                } elseif ($token -match '(?i)^(-{1,2}[a-z0-9_.-]*(?:password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key|token))$' -and ($i + 1) -lt $cmdTokens.Count) {
                    $nextVal = ([string]$cmdTokens[$i + 1]).Trim('"', "'")
                    if ($nextVal -and $nextVal -notmatch '^\$' -and !$nextVal.StartsWith('-')) { $secretArgs += $Matches[1] }
                }
            }
            @{
                name = $container.name
                securityContext = $container.securityContext
                secretLikeLiteralVariables = @($container.env | Where-Object {
                    $_.name -match '(?i)PASSWORD|SECRET|API_KEY|ACCESS_TOKEN|PRIVATE_KEY' -and $_.value
                } | ForEach-Object name)
                secretLikeArgs = @($secretArgs | Select-Object -Unique)
                configMapEnvFrom = @($container.envFrom | Where-Object { $_.configMapRef.name } | ForEach-Object { $_.configMapRef.name })
            }
        })
    }
    $statuses = @($pod.status.containerStatuses) + @($pod.status.initContainerStatuses | Where-Object { $_ })
    foreach ($container in $statuses) {
        if (!$container.imageID) { continue }
        if (!$images.ContainsKey($container.imageID)) {
            $images[$container.imageID] = @{ image = $container.image; usedBy = @() }
        }
        $images[$container.imageID].usedBy += "$($pod.metadata.name)/$($container.name)"
    }
}

$tempBase = [IO.Path]::GetTempPath()
if ($tempBase -match ',') {
    $tempBase = Join-Path $PSScriptRoot '../.transfer-runtime'
    [void](New-Item -ItemType Directory -Path $tempBase -Force)
}
$scratch = Join-Path $tempBase ([IO.Path]::GetRandomFileName())
[void](New-Item -ItemType Directory -Path $scratch)
$archive = Join-Path $scratch 'image.tar'
$scanArgs = @(
    'run', '--rm', '--platform', $platform, '--network', 'none', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
    '--mount', "type=bind,source=$archive,target=/scan/image.tar,readonly",
    '--mount', 'type=volume,source=target-audit-trivy-db,target=/cache',
    'aquasec/trivy:0.76.2', 'image', '--cache-dir', '/cache', '--skip-db-update',
    '--skip-java-db-update', '--offline-scan', '--input', '/scan/image.tar',
    '--cache-backend', 'memory', '--timeout', '4m', '--skip-version-check'
)
$scans = @()
try {
    foreach ($digest in ($images.Keys | Sort-Object)) {
        $image = $images[$digest]
        if ($ImageFilter.Count -and $image.image -notin $ImageFilter) { continue }
        $report = @{ image = $image.image; digest = $digest; usedBy = $image.usedBy; status = 'unavailable'; findings = @() }
        $scans += $report
        $localDigests = docker image inspect --format '{{json .RepoDigests}}' $image.image 2>$null
        $expected = ($digest -split '@')[-1]
        if ($expected -notmatch '^sha256:[0-9a-f]{64}$') {
            $report.reason = 'Pod did not report a SHA-256 digest.'
            continue
        }
        if ($SbomOutputDirectory) {
            $path = Join-Path $SbomOutputDirectory "$($expected.Substring(7)).cdx.gz"
            if (Test-Path -LiteralPath $path -PathType Leaf) {
                $report.status = 'ok'
                continue
            }
        }
        $exportRef = $image.image
        if ($LASTEXITCODE -ne 0 -or $expected -notin @(($localDigests | ConvertFrom-Json) | ForEach-Object { ($_ -split '@')[-1] })) {
            $publicRepository = '^docker\.io/(clickhouse/clickhouse-server|grafana/grafana|library/postgres|otel/opentelemetry-collector-contrib)@sha256:[0-9a-f]{64}$'
            if ($digest -notmatch $publicRepository) {
                $report.reason = 'Local image matching the Pod digest is unavailable.'
                continue
            }
            docker pull --platform $platform $digest | Out-Host
            if ($LASTEXITCODE -ne 0) {
                $report.reason = 'Public image matching the Pod digest is unavailable.'
                continue
            }
            $exportRef = $digest
        }
        Write-Host "Scanning packages for $($image.image)"
        docker image save --platform $platform --output $archive $exportRef
        if ($LASTEXITCODE -ne 0) {
            $report.reason = 'Failed to export image archive for Trivy.'
            continue
        }
        if ($SbomOutputDirectory) {
            $sbom = docker @scanArgs --format cyclonedx
            if ($LASTEXITCODE -ne 0 -or !$sbom) {
                Write-Warning "Trivy failed to generate an SBOM for image $($image.image)."
                continue
            }
            $file = [IO.File]::Create($path)
            try {
                $gzip = [IO.Compression.GZipStream]::new($file, [IO.Compression.CompressionLevel]::Optimal)
                try {
                    $bytes = [Text.Encoding]::UTF8.GetBytes(($sbom -join "`n"))
                    $gzip.Write($bytes, 0, $bytes.Length)
                } finally {
                    $gzip.Dispose()
                }
            } finally {
                $file.Dispose()
            }
            $report.status = 'ok'
            continue
        }
        $scanOutput = docker @scanArgs --scanners vuln --severity HIGH,CRITICAL --format json
        if ($LASTEXITCODE -ne 0) {
            $report.reason = 'Trivy exited with an error.'
            continue
        }
        $scan = $scanOutput | ConvertFrom-Json -Depth 85
        $report.status = 'ok'
        $report.findings = @(foreach ($group in $scan.Results) {
            foreach ($item in $group.Vulnerabilities) {
                @{
                    id = $item.VulnerabilityID
                    package = $item.PkgName
                    installed = $item.InstalledVersion
                    fixed = $item.FixedVersion
                    severity = $item.Severity
                    kev = $kev.ContainsKey([string]$item.VulnerabilityID)
                    reference = $item.PrimaryURL
                }
            }
        })
    }
} finally {
    if (Test-Path -LiteralPath $archive) { Remove-Item -LiteralPath $archive }
    [IO.Directory]::Delete($scratch)
}
if ($SbomOutputDirectory) {
    return $scans
}

$snapshot = @{
    namespace = $namespace
    capturedAt = $capturedAt
    deployments = @($resources | Where-Object kind -eq 'Deployment' | ForEach-Object { $_.metadata.name })
    pods = $inventory
    services = @($resources | Where-Object kind -eq 'Service' | ForEach-Object {
        @{ name = $_.metadata.name; type = $_.spec.type; ports = $_.spec.ports; selector = $_.spec.selector }
    })
    networkPolicies = @($resources | Where-Object kind -eq 'NetworkPolicy' | ForEach-Object {
        @{ name = $_.metadata.name; spec = $_.spec }
    })
    roles = @($resources | Where-Object kind -eq 'Role' | ForEach-Object {
        @{ name = $_.metadata.name; rules = $_.rules }
    })
    roleBindings = @($resources | Where-Object kind -eq 'RoleBinding' | ForEach-Object {
        @{ name = $_.metadata.name; roleRef = $_.roleRef }
    })
    kev = $feedStatus
    images = $scans
}
$snapshot | ConvertTo-Json -Depth 50 -Compress | Set-Content -LiteralPath $OutputFile -Encoding utf8NoBOM
