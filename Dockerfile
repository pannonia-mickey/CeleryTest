FROM python:3.12-slim AS base

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends bash gcc python3-dev libpq-dev curl
RUN python3 -m pip install poetry==1.8.3

WORKDIR /opt/project

COPY pyproject.toml poetry.lock /opt/project/
RUN poetry install
COPY . /opt/project/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

FROM base AS devcontainer
RUN apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
SHELL ["/bin/bash", "-c"]
ENV PYDEVD_DISABLE_FILE_VALIDATION=1

VOLUME /opt/project

COPY .devcontainer/service.sh /usr/local/bin/service
COPY .devcontainer/docker-entrypoint.sh /usr/local/bin/docker-entrypoint
RUN chmod +x /usr/local/bin/service && \
    chmod +x /usr/local/bin/docker-entrypoint
CMD [ "docker-entrypoint" ]