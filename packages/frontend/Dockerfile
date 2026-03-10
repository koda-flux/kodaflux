FROM node:lts-alpine AS base
WORKDIR /app

ARG TURBO_MAJOR_VERSION=^2

ENV PATH="/usr/local/bin:${PATH}"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apk update \
	&& apk add --no-cache libc6-compat \
	&& npm install --global turbo@${TURBO_MAJOR_VERSION} \
	&& corepack enable pnpm


FROM base AS prepare

COPY . .
RUN turbo prune frontend --docker


FROM base AS builder

COPY --from=prepare /app/out/json/ .
RUN pnpm install --frozen-lockfile

COPY --from=prepare /app/out/full/ .
RUN turbo run build


FROM base AS runner

RUN addgroup --system --gid 1001 nodejs \
	&& adduser --system --uid 1001 nextjs

USER nextjs

COPY --from=builder --chown=nextjs:nodejs /app/packages/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/packages/frontend/.next/static ./packages/frontend/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/packages/frontend/public ./packages/frontend/public

ENTRYPOINT [ "node" ]
CMD [ "packages/frontend/server.js" ]
