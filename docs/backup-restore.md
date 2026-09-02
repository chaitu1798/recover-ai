# PostgreSQL Backup and Restore

This document outlines the practical backup and restore procedure for the RecoverAI database in the local Docker environment.

> **IMPORTANT:** This is an operational procedure designed for disaster recovery or database migration. Do NOT perform a restore on the active development database unless you intend to overwrite existing data.

## Environment Context

The database runs in a Docker container named `recover-ai-postgres-1` (or similar depending on your compose project name).

## 1. Creating a Backup (pg_dump)

To create a logical backup of the PostgreSQL database, run the following command from the host machine:

```bash
docker exec -t recover-ai-postgres-1 pg_dump -U recover_admin -F c -d recover_db > recover_db_backup.dump
```

- `-U recover_admin`: Connects as the database user.
- `-F c`: Uses the custom-format archive suitable for input into `pg_restore`.
- `-d recover_db`: Specifies the database name.
- `> recover_db_backup.dump`: Saves the output to a file on your host machine.

## 2. Restoring a Backup (pg_restore)

To restore a backup into the database, run the following command. 
*Note: It is recommended to restore into an empty database or drop the existing schema first if recreating.*

```bash
cat recover_db_backup.dump | docker exec -i recover-ai-postgres-1 pg_restore -U recover_admin -d recover_db --clean --if-exists
```

- `-i`: Interactive standard input.
- `--clean`: Clean (drop) database objects before recreating them.
- `--if-exists`: Use IF EXISTS commands to drop objects.

## 3. Verification

After restoring, verify the integrity of the data by running the backend health checks and Alembic current head check:

```bash
docker compose exec backend alembic current
docker compose exec backend python scripts/evaluate_final.py
```
