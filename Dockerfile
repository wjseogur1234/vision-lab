FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# opencv-python(LibreYOLO 의존성)이 쓰는 시스템 라이브러리
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 가상환경을 /app 밖에 둔다. /app에 소스를 마운트해도 가상환경이 가려지지 않는다.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

# 의존성을 먼저 설치한다. 코드만 바뀌면 이 층은 캐시에서 다시 쓴다.
# uv.lock이 생기면 `uv sync`에 `--locked`를 붙인다.
COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["bash"]
