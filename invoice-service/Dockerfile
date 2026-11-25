FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir 'psycopg[binary]==3.2.9' \
    && useradd --create-home --uid 10001 invoice
COPY --chown=10001:10001 *.py ./
COPY --chown=10001:10001 static/ ./static/
COPY --chown=10001:10001 data/case04.xlsx ./data/case04.xlsx
USER 10001
EXPOSE 8040
CMD ["python", "-u", "observed_app.py"]
