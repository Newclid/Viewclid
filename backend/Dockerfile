FROM ghcr.io/astral-sh/uv:0.11.11-python3.12-trixie-slim AS builder

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV CC=/usr/bin/gcc-14
ENV CXX=/usr/bin/g++-14
ENV CMAKE_GENERATOR=Ninja
ENV CMAKE_ARGS="-DUSE_STATIC_LINK=OFF -DBUILD_DOC=OFF -DCMAKE_BUILD_TYPE=Release"

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    build-essential \
    gcc-14 \
    g++-14 \
    cmake \
    ninja-build \
    pkg-config \
    libboost-dev \
    libboost-log-dev \
    libboost-json-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-test-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev


FROM ghcr.io/astral-sh/uv:0.11.11-python3.12-trixie-slim AS runtime

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libboost-log1.83.0 \
    libboost-json1.83.0 \
    libboost-program-options1.83.0 \
    libboost-system1.83.0 \
    libboost-test1.83.0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
