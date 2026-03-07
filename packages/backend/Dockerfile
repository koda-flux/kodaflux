FROM node:lts-alpine AS prepare
WORKDIR /code


ARG TURBO_MAJOR_VERSION=^2

COPY . .
RUN apk update \
	&& apk add --no-cache libc6-compat \
	&& npm install --global turbo@${TURBO_MAJOR_VERSION} \
	&& turbo prune backend --docker


FROM python:3.12-slim
WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/* \
	&& addgroup --system --gid 1001 python \
	&& adduser --system --uid 1001 fastapi


# NOTE: Update uv image tag when changed in project
COPY --from=ghcr.io/astral-sh/uv:0.10.6 /uv /uvx /bin/
COPY --from=prepare /code/out/full/packages/backend/ .
RUN uv sync --no-dev \
	&& chown -R fastapi:python .venv/

USER fastapi

ENTRYPOINT [ ".venv/bin/fastapi" ]
CMD [ "run", "app/main.py", "--port", "80" ]
