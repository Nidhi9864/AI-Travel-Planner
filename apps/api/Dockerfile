# Production API image (IMP-112; specification §4.5, IMD-38).
# Build: docker compose build api (or docker build apps/api). Render builds this file in staging and
# production. The image holds the installed package only: no tests, no dev extras, no migrations.
# Migrations run from the deploy workflow (make db-migrate), never on container start (IMD-38).

FROM python:3.12-slim AS build
WORKDIR /src
COPY pyproject.toml ./
COPY app ./app
# A wheel, not an editable install, so the prompt templates ship as package data (IMP-111).
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels .

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
COPY --from=build /wheels /wheels
RUN pip install /wheels/*.whl && rm -rf /wheels \
    && useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin app
USER app
# The working directory holds no source, so `app` resolves to the installed package.
WORKDIR /tmp
EXPOSE 8000
# Render sets PORT; locally it defaults to 8000. /health reports BUILD_VERSION; when it is not set,
# Render's RENDER_GIT_COMMIT (the deployed commit) is used, so the deploy workflows can wait for the
# new version (IMP-112); locally it stays "dev". exec makes uvicorn PID 1, so it receives SIGTERM.
CMD ["sh", "-c", "BUILD_VERSION=\"${BUILD_VERSION:-${RENDER_GIT_COMMIT:-dev}}\" exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
