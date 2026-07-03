# DevLens Privacy Policy

**Effective Date:** July 3, 2026

At DevLens, we are committed to protecting the privacy and security of your source code, configuration files, and repository metadata. This Privacy Policy details what information we collect, how we process it, and your rights concerning your data when you install the DevLens GitHub App.

---

## 1. Information We Collect and Process
DevLens is a stateless code audit platform. To perform analysis, we access and process:

- **Repository Content**: Source files and package manifests (e.g. `package.json`, `requirements.txt`, `Dockerfile`) are read transiently to run linters, security audits, and configuration policy checks.
- **Repository Metadata**: Default branch name, commit SHAs, and check run targets.
- **Installation Context**: GitHub installation ID, organization name, and repository permissions context.

We do **NOT** store, archive, or cache your source code files permanently. All file reads are performed in-memory and discarded immediately after the analysis finishes.

---

## 2. Third-Party Integrations & LLM Processing
- **AI Engine (Groq / Large Language Model)**: The narrative generation and semantic diagnostic audits are run through the Groq inference service using API endpoints. 
- **Data Protection**: No source code is sent to the LLM. Only raw audit outputs, technology stacks list, and validation summaries are sent to generate structural narratives. None of this data is used by Groq or DevLens to train underlying models.

---

## 3. Data Protection (GDPR & CCPA Compliance)
- **Data Deletion**: When you uninstall DevLens or delete a repository from the installation scope, our webhook handler receives `installation.deleted` and deletes all historical score logs and analytics indexes.
- **Right to Erasure**: You can request full purge of metrics data by reaching out to support.

---

## 4. Contact Us
For any privacy-related inquiries, please contact our privacy compliance officer at `privacy@devlens.io`.
