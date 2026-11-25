# Contour

Contour is a local Kubernetes lab for observability and passive security auditing. It runs in the `observability` namespace and produces synthetic logs and metrics so you can explore the dashboards as soon as the stack is running.

The OpenTelemetry Collector receives logs and metrics and writes them to ClickHouse. Grafana shows simulated security events alongside CPU usage, memory usage, p95 latency, queue depth, and error rate.

The passive auditor reviews Kubernetes resources and permissions. It uses Trivy to scan software inventories tied to the exact container images running in the cluster and checks findings against CISA's Known Exploited Vulnerabilities catalog. A local Qwen model summarizes the findings, and the lab stores the reports in a persistent volume.

## Run locally

Install Docker Desktop and PowerShell 7.4 or newer, and make sure `docker` and `kubectl` are on your `PATH`. In [Docker Desktop](https://docs.docker.com/desktop/use-desktop/kubernetes/), enable the containerd image store and create a Kubernetes cluster with the `kind` provisioner and one node. The first run needs internet access to download container images and the audit model.

```powershell
git clone https://github.com/listentothesoloist/contour.git
cd contour
kubectl --context docker-desktop wait --for=condition=Ready nodes --all --timeout=180s
pwsh -NoProfile -File ./RESTORE.ps1
```

`RESTORE.ps1` verifies the files listed in `FILES.sha256.json`, builds the project images, and deploys the stack.

## Open Grafana

Get the Grafana password in PowerShell, then start the port forward. Leave the terminal running while you use the dashboard.

```powershell
$encoded = kubectl --context docker-desktop -n observability get secret demo-credentials -o 'jsonpath={.data.GF_SECURITY_ADMIN_PASSWORD}'
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded))
kubectl --context docker-desktop -n observability port-forward svc/grafana 13000:3000
```

Open the [system dashboard](http://127.0.0.1:13000/d/otel-system) and sign in as `admin` with the password printed above.

Credits: @listentothesoloist @Squasr
