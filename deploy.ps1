param(
    [ValidateSet('kind-otel-course', 'docker-desktop')]
    [string]$Context = 'kind-otel-course'
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$manifests = Join-Path $PSScriptRoot 'k8s'
$kubeArgs = @('--context', $Context)
if ($Context -eq 'kind-otel-course') {
    $kubeconfig = Join-Path $PSScriptRoot '.kubeconfig'
    if (!(Test-Path -LiteralPath $kubeconfig)) { throw 'Create the otel-course cluster first.' }
    $kubeArgs += @('--kubeconfig', $kubeconfig)
}

function Invoke-Kube {
    & kubectl @kubeArgs @args
    if ($LASTEXITCODE -ne 0) { throw 'kubectl command failed.' }
}

Invoke-Kube apply -f (Join-Path $manifests 'namespace.yaml')
$secret = Invoke-Kube -n observability get secret demo-credentials --ignore-not-found -o name
if (!$secret) {
    $data = @{}
    $random = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        foreach ($key in 'POSTGRES_PASSWORD', 'CLICKHOUSE_PASSWORD', 'GF_SECURITY_ADMIN_PASSWORD') {
            $bytes = New-Object byte[] 24
            $random.GetBytes($bytes)
            $data[$key] = [Convert]::ToBase64String($bytes)
        }
    } finally {
        $random.Dispose()
    }
    @{
        apiVersion = 'v1'
        kind = 'Secret'
        metadata = @{name = 'demo-credentials'; namespace = 'observability'}
        stringData = $data
    } | ConvertTo-Json -Depth 4 -Compress | kubectl @kubeArgs create -f -
    if ($LASTEXITCODE -ne 0) { throw 'Could not create demo credentials.' }
}

$dashboards = @('otel-invoices.json', 'otel-system.json') |
    ForEach-Object { "--from-file=$(Join-Path $PSScriptRoot "grafana/$_")" }
$manifest = Invoke-Kube -n observability create configmap grafana-dashboard @dashboards --dry-run=client -o yaml
$manifest | kubectl @kubeArgs apply -f -
if ($LASTEXITCODE -ne 0) { throw 'Could not provision dashboard.' }

$target = if ($Context -eq 'docker-desktop') { 'docker-desktop' } else { 'components' }
$collectorBefore = Invoke-Kube -n observability get configmap otel-collector --ignore-not-found -o 'jsonpath={.metadata.resourceVersion}'
Invoke-Kube apply -k (Join-Path $manifests $target)
$collectorAfter = Invoke-Kube -n observability get configmap otel-collector -o 'jsonpath={.metadata.resourceVersion}'
if ($collectorBefore -and $collectorBefore -ne $collectorAfter) {
    Invoke-Kube -n observability rollout restart deployment/otel-collector
}

$deployments = @('postgres', 'clickhouse', 'otel-collector', 'grafana', 'invoice-service', 'log-generator') |
    ForEach-Object { "deployment/$_" }
$auditorReplicas = Invoke-Kube -n observability get deployment/target-passive-auditor -o 'jsonpath={.spec.replicas}'
if ($auditorReplicas -ne '0') {
    $deployments += 'deployment/target-passive-auditor'
}
Invoke-Kube -n observability rollout status @deployments --timeout=180s
& (Join-Path $PSScriptRoot 'security-audit/publish-sboms.ps1') -Context $Context
