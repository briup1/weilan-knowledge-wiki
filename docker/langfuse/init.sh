#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -e .env ]]; then
  printf 'Keeping existing .env; no credentials changed.\n'
  exit 0
fi

command -v openssl >/dev/null
command -v uuidgen >/dev/null
umask 077

{
  printf 'POSTGRES_PASSWORD=%s\n' "$(openssl rand -hex 24)"
  printf 'CLICKHOUSE_PASSWORD=%s\n' "$(openssl rand -hex 24)"
  printf 'REDIS_AUTH=%s\n' "$(openssl rand -hex 24)"
  printf 'MINIO_ROOT_PASSWORD=%s\n' "$(openssl rand -hex 24)"
  printf 'SALT=%s\n' "$(openssl rand -hex 32)"
  printf 'ENCRYPTION_KEY=%s\n' "$(openssl rand -hex 32)"
  printf 'NEXTAUTH_SECRET=%s\n' "$(openssl rand -hex 32)"
  printf 'LANGFUSE_INIT_ORG_ID=%s\n' "$(uuidgen | tr '[:upper:]' '[:lower:]')"
  printf 'LANGFUSE_INIT_PROJECT_ID=%s\n' "$(uuidgen | tr '[:upper:]' '[:lower:]')"
  printf 'LANGFUSE_INIT_PROJECT_PUBLIC_KEY=pk-lf-%s\n' "$(uuidgen | tr '[:upper:]' '[:lower:]')"
  printf 'LANGFUSE_INIT_PROJECT_SECRET_KEY=sk-lf-%s\n' "$(uuidgen | tr '[:upper:]' '[:lower:]')"
  printf 'LANGFUSE_INIT_USER_PASSWORD=%s\n' "$(openssl rand -hex 16)"
} > .env

printf 'Created .env with mode 0600. Login: weilan@local.test. Password and API keys stay in .env.\n'
