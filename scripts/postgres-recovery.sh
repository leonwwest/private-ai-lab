#!/usr/bin/env bash
set -euo pipefail

action="${1:-verify}"
backup_file="${BACKUP_FILE:-.local/postgres-recovery.dump}"
evidence_file="${EVIDENCE_FILE:-.local/postgres-recovery-evidence.md}"
postgres_service="postgres"
postgres_user="private_ai"
primary_database="private_ai"
restore_database="private_ai_restore_check"

command -v docker >/dev/null 2>&1 || {
  echo "docker is required" >&2
  exit 1
}

compose() {
  docker compose "$@"
}

require_postgres() {
  compose exec -T "${postgres_service}" \
    pg_isready --username "${postgres_user}" --dbname "${primary_database}" >/dev/null
}

verify_backup() {
  [[ -s "${backup_file}" ]] || {
    echo "Backup not found or empty: ${backup_file}" >&2
    exit 1
  }
  compose exec -T "${postgres_service}" pg_restore --list <"${backup_file}" |
    grep -q "TABLE"
  echo "Backup archive is readable and contains table definitions."
}

backup() {
  require_postgres
  mkdir -p "$(dirname "${backup_file}")"
  compose exec -T "${postgres_service}" \
    pg_dump \
    --username "${postgres_user}" \
    --dbname "${primary_database}" \
    --format=custom \
    --no-owner \
    --no-acl >"${backup_file}"
  verify_backup
  shasum -a 256 "${backup_file}"
}

drop_restore_database() {
  compose exec -T "${postgres_service}" \
    psql \
    --username "${postgres_user}" \
    --dbname postgres \
    --set ON_ERROR_STOP=1 \
    --command="DROP DATABASE IF EXISTS ${restore_database} WITH (FORCE);" >/dev/null
}

exercise() {
  if [[ "${CONFIRM_POSTGRES_RECOVERY_EXERCISE:-}" != "YES" ]]; then
    echo "Recovery exercise is opt-in." >&2
    echo "Run: CONFIRM_POSTGRES_RECOVERY_EXERCISE=YES make recovery-exercise" >&2
    exit 2
  fi

  require_postgres
  verify_backup
  trap drop_restore_database EXIT
  drop_restore_database
  compose exec -T "${postgres_service}" \
    createdb --username "${postgres_user}" "${restore_database}"
  compose exec -T "${postgres_service}" \
    pg_restore \
    --username "${postgres_user}" \
    --dbname "${restore_database}" \
    --no-owner \
    --no-acl \
    --exit-on-error <"${backup_file}"

  table_count="$(
    compose exec -T "${postgres_service}" \
      psql \
      --username "${postgres_user}" \
      --dbname "${restore_database}" \
      --tuples-only \
      --no-align \
      --command="SELECT count(*) FROM pg_tables WHERE schemaname = 'public';"
  )"
  [[ "${table_count}" =~ ^[1-9][0-9]*$ ]]

  mkdir -p "$(dirname "${evidence_file}")"
  checksum="$(shasum -a 256 "${backup_file}" | awk '{print $1}')"
  printf '%s\n' \
    "# PostgreSQL recovery evidence" \
    "" \
    "- Backup: ${backup_file}" \
    "- SHA-256: ${checksum}" \
    "- Disposable restore database: ${restore_database}" \
    "- Restored public tables: ${table_count}" \
    "- Primary database modified: no" \
    >"${evidence_file}"

  drop_restore_database
  trap - EXIT
  echo "Recovery exercise passed; evidence written to ${evidence_file}"
}

case "${action}" in
  backup)
    backup
    ;;
  verify)
    require_postgres
    verify_backup
    ;;
  exercise)
    exercise
    ;;
  *)
    echo "Usage: $0 {backup|verify|exercise}" >&2
    exit 2
    ;;
esac
