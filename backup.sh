#!/bin/bash
set -e
BACKUP_DIR="/backups"
mkdir -p "$BACKUP_DIR"
DATE=$(date +%F)
FILE="$BACKUP_DIR/backup-$DATE.sql"
pg_dump postgresql://appuser:StrongPass123@dilivery-db.flycast:5432/postgres > "$FILE"
# keep last 7 backups
ls -1t "$BACKUP_DIR"/backup-*.sql 2>/dev/null | tail -n +8 | xargs -r rm --
