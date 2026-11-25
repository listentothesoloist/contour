FROM postgres:17-alpine

ENV POSTGRES_DB=orders \
    POSTGRES_USER=orders

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
    CMD pg_isready -q -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
