FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# 가상환경을 /app 밖에 둔다. /app에 소스를 마운트해도 가상환경이 가려지지 않는다.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

# opencv-python(LibreYOLO 의존성)이 쓰는 시스템 라이브러리
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --group prep --group train --group dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --group prep --group train --group dev

CMD ["bash"]
