# PostgreSQL backup and recovery exercise

## Goal

Prove that a PostgreSQL backup is readable and restorable without overwriting the primary
`private_ai` database. The exercise restores only into the disposable
`private_ai_restore_check` database and removes it afterward.

## Boundary

- Backup and evidence files stay below ignored `.local/` paths.
- The script never passes the primary database to `pg_restore`.
- The restore path is guarded by `CONFIRM_POSTGRES_RECOVERY_EXERCISE=YES`.
- The disposable database is removed on success and through the failure trap.
- This lab does not claim encrypted or off-site backup retention.

## Preconditions

Start the local platform and ingest at least one synthetic or non-sensitive document:

```bash
cp -n .env.example .env
docker compose up -d postgres app
curl --fail http://localhost:8000/readyz
```

## Create and verify a backup

```bash
make recovery-backup
make recovery-verify
```

The custom-format archive is validated with `pg_restore --list`; a readable archive must contain
table definitions.

## Exercise a disposable restore

```bash
CONFIRM_POSTGRES_RECOVERY_EXERCISE=YES make recovery-exercise
```

The exercise creates a separate database, restores the archive with `--exit-on-error`, counts the
restored public tables, writes `.local/postgres-recovery-evidence.md` and drops the disposable
database. Inspect the evidence and retain it only as long as required.

## Real-use extensions

- encrypt archives with an operator-managed key
- store backups outside the host failure domain
- define retention and deletion rules
- record recovery point and recovery time objectives
- rehearse application-level integrity checks after restore
