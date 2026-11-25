param([Parameter(Mandatory)][string]$EvidenceFile)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$kubeArgs = @('--context', 'docker-desktop', '-n', 'observability')
$evidence = (Resolve-Path -LiteralPath $EvidenceFile).Path
$snapshot = Get-Content -LiteralPath $evidence -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 60
if ($snapshot.namespace -ne 'observability') { throw 'Only observability snapshots are accepted.' }
if ((Get-Item -LiteralPath $evidence).Length -gt 900000) { throw 'Evidence exceeds the ConfigMap size budget.' }

function Invoke-Kube {
    & kubectl @kubeArgs @args
    if ($LASTEXITCODE -ne 0) { throw 'kubectl command failed.' }
}

Invoke-Kube apply -f (Join-Path $PSScriptRoot 'isolation.yaml') | Write-Host
$inputName = "target-security-input-$([Guid]::NewGuid().ToString('N').Substring(0,12))"
Invoke-Kube create configmap $inputName "--from-file=evidence.json=$evidence" | Write-Host
try {
    $manifest = (Get-Content (Join-Path $PSScriptRoot 'job.yaml') -Raw -Encoding UTF8).
        Replace('name: target-security-audit-input', "name: $inputName")
    $resource = $manifest | kubectl @kubeArgs create -f - -o name
    if ($LASTEXITCODE -ne 0 -or !$resource) { throw 'Could not create the audit Job.' }
    Write-Host "Created $resource"

    $deadline = [DateTimeOffset]::UtcNow.AddMinutes(9)
    while ([DateTimeOffset]::UtcNow -lt $deadline) {
        $job = Invoke-Kube get $resource -o json | ConvertFrom-Json -Depth 30
        if ($job.status.conditions | Where-Object { $_.type -eq 'Failed' -and $_.status -eq 'True' }) {
            throw "$resource failed. Inspect its Pod events and audit container logs."
        }
        if ($job.status.conditions | Where-Object { $_.type -eq 'Complete' -and $_.status -eq 'True' }) {
            $json = Invoke-Kube logs $resource -c audit
            $report = $json | ConvertFrom-Json -Depth 60
            if ($report.run -ne $job.metadata.name) { throw 'Audit report does not match the requested Job.' }
            $reports = Join-Path $PSScriptRoot 'reports'
            [void](New-Item -ItemType Directory -Path $reports -Force)
            $path = Join-Path $reports "$($report.run).json"
            $report | ConvertTo-Json -Depth 60 | Set-Content -LiteralPath $path -Encoding utf8NoBOM
            [pscustomobject]@{
                Job = $report.run
                Status = $report.status
                Pods = $report.coverage.pods
                Images = "$($report.coverage.images_scanned)/$($report.coverage.images_total)"
                Findings = @($report.findings).Count
                LocalModel = $report.model_review.status
                Report = $path
            }
            return
        }
        Start-Sleep -Seconds 4
    }
    throw "Timed out while waiting for $resource."
} finally {
    & kubectl @kubeArgs delete configmap $inputName --ignore-not-found | Out-Null
}
