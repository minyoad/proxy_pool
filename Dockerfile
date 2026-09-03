FROM python:3.10-slim

LABEL maintainer="jhao104 <j_hao104@163.com>"

WORKDIR /app

COPY ./requirements.txt .

# 使用腾讯云镜像源加速 apt (debian.sources 或 sources.list 两种格式兼容)
RUN sed -i 's|deb.debian.org|mirrors.cloud.tencent.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirrors.cloud.tencent.com|g' /etc/apt/sources.list 2>/dev/null || true

# timezone and init process
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata tini && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    rm -rf /var/lib/apt/lists/*

# runtime environment (slim 镜像下依赖均有预编译 wheel, 无需 gcc 编译)
# pip 使用腾讯云 PyPI 镜像源
RUN pip install --no-cache-dir \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -r requirements.txt

COPY . .

EXPOSE 5010

ENTRYPOINT ["tini", "--", "bash", "proxy_pool.sh", "start", "--fg"]
