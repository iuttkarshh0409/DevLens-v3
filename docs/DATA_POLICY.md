# DevLens Data Retention & Deletion Policy

This document governs the collection, lifecycle, retention, and purging of data within the DevLens V3 ecosystem.

---

## 1. Code Processing Sandbox
- **In-Memory Lifespan**: Source code files are pulled into memory via GitHub Trees and Single File APIs, audited immediately, and then discarded. No code content is persisted to storage databases or local disk caches.
- **Payload Buffers**: Webhook payload details are parsed and stored in active memory for processing and discarded once the job completes.

---

## 2. Retention Schedules

| Data Entity | Retention Period | Storage Location | Purge Trigger |
|---|---|---|---|
| Repository Source Code | None (Processed in memory) | RAM only | Immediate analysis exit |
| Audit Job History / Metadata | 30 days | Redis / PostgreSQL | Automatic cron job purge |
| Scoring Indexes | Lifetime of Installation | PostgreSQL / Cache | Webhook `installation.deleted` |
| Error Logs | 14 days | File Logger | Automatic rollover rotation |

---

## 3. Automated Deletion Triggers
DevLens listens to standard GitHub installation hook events to purge customer records.

- **Installation Uninstalled (`installation.deleted`)**: Triggers an asynchronous cascade task that purges all logs, job references, and historical scores associated with the Installation ID within 24 hours.
- **Repository Removed (`installation_repositories.removed`)**: Removes scores and historical data references for the detached repositories immediately.

---

## 4. Compliance Audits
System logs undergo automated audits every 30 days to guarantee that code fragments or keys are not written to logging files or persistent caches.
