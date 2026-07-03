# DevLens V3 Backup & Disaster Recovery Guide

This document details policies and operations for backing up system states and recovering services from severe outages.

---

## 1. Backup Strategy

### State Data Backups
- **Target**: Redis RDB (snapshot) data and PostgreSQL score records.
- **Frequency**: Daily database exports.
- **Retention**: Keep daily backups for 7 days, weekly backups for 30 days.

### Snapshot commands
To capture a manual snapshot of Redis data:
```bash
redis-cli save
cp /var/lib/redis/dump.rdb /mnt/backups/redis/dump-$(date +%F).rdb
```

---

## 2. Disaster Recovery Scenarios

### Scenario A: Complete Datacenter Outage
1. **Provision Infrastructure**: Spawn new API and worker containers in a secondary cloud region.
2. **Restore State**: Pull the latest Redis RDB backup file and place it in the Redis directory.
3. **Update Domain DNS**: Update the DNS record for `api.devlens.io` to point to the new load balancer IP.
4. **Verify Callback Integrity**: Verify that webhook payloads from GitHub resolve correctly.

### Scenario B: Database/Cache Corruption
1. **Stop Services**: Stop API and worker containers.
2. **Clear Cache**: Flush Redis DB using `FLUSHALL`.
3. **Restore Backup**: Load the last healthy snapshot database file.
4. **Restart Services**: Start API and worker containers.
