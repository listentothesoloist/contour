FROM aquasec/trivy:0.76.2 AS trivy
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONUTF8=1
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
COPY audit.py passive.py package_audit.py prompt.txt /app/
USER 10001:10001
ENTRYPOINT ["python", "/app/audit.py"]
