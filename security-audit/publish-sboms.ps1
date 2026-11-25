param(
    [ValidateSet('docker-desktop', 'kind-otel-course')]
    [string]$Context = 'docker-desktop'
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$kubeArgs = @('--context', $Context, '-n', 'observability')
if ($Context -eq 'kind-otel-course') {
    $kubeArgs += @('--kubeconfig', (Join-Path $PSScriptRoot '../.kubeconfig'))
}

$scratch = [IO.Directory]::CreateTempSubdirectory('target-sboms-').FullName
$configMap = 'target-audit-sboms'
try {
    $current = kubectl @kubeArgs get configmap $configMap --ignore-not-found -o json
    if ($LASTEXITCODE -ne 0) { throw 'Failed to inspect existing SBOMs.' }
    if ($current) {
        $existing = ($current | ConvertFrom-Json -AsHashtable).binaryData
        foreach ($key in $existing.Keys) {
            if ($key -cmatch '^[a-f0-9]{64}\.cdx\.gz$') {
                [IO.File]::WriteAllBytes((Join-Path $scratch $key), [Convert]::FromBase64String($existing[$key]))
            }
        }
    }
    $scans = @(& (Join-Path $PSScriptRoot 'prepare-input.ps1') -Context $Context -SbomOutputDirectory $scratch)
    $keys = @(foreach ($scan in $scans) {
        if ($scan.status -eq 'ok') {
            "$(($scan.digest -split 'sha256:')[-1]).cdx.gz"
        } else {
            Write-Warning "$($scan.image): $($scan.reason)"
        }
    })
    if (!$keys.Count) { throw 'SBOM preparation produced no verified digest bindings.' }
    $inputs = @($keys | Sort-Object -Unique | ForEach-Object { "--from-file=$(Join-Path $scratch $_)" })
    $manifest = kubectl @kubeArgs create configmap $configMap @inputs --dry-run=client -o json
    if ($LASTEXITCODE -ne 0) { throw 'Failed to build the SBOM ConfigMap manifest.' }
    $manifest | kubectl @kubeArgs apply --server-side --field-manager=target-sbom-publisher -f -
    if ($LASTEXITCODE -ne 0) { throw 'Failed to publish SBOMs.' }
    Write-Host "SBOMs available for $($keys.Count) of $($scans.Count) images."
} finally {
    foreach ($file in (Get-ChildItem -LiteralPath $scratch -File)) {
        Remove-Item -LiteralPath $file.FullName
    }
    [IO.Directory]::Delete($scratch)
}
