FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# 가상환경을 /app 밖에 둔다. /app에 소스를 마운트해도 가상환경이 가려지지 않는다.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

# libgl1, libglib2.0-0: opencv-python(LibreYOLO 의존성)용. git: 학습 run에 코드 출처를 남긴다
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --group prep --group train --group dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --group prep --group train --group dev

# 호스트 사용자와 같은 UID로 실행한다. 마운트 폴더에 root 소유 파일이 생기지 않는다.
# /opt/venv는 root 소유로 남는다. 읽기만 하므로 문제없다.
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} lab && useradd -m -u ${UID} -g ${GID} lab
USER lab

CMD ["bash"]
