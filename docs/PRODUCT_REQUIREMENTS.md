# 📝 DevLens: Product Requirements Document (PRD)

This document defines the product requirements, target audience, competitive analysis, and long-term release roadmap guiding the development of DevLens.

---

## 1. Problem Statement

### 1.1 Problems Faced by Developers & Portfolio Builders
* **Recruiter Invisibility**: Job hunters build complex projects, but their technical skills are hidden behind dense code repositories that non-technical recruiters do not have the time or expertise to read.
* **Lack of Setup Direction**: Developers often write poor READMEs, missing critical environment variables or setups, causing recruiters or reviewers to abandon the project immediately.

### 1.2 Problems Faced by Recruiters
* **Technical Communication Gap**: Non-technical talent evaluators struggle to distinguish between high-quality, production-ready portfolios and simple tutorial clones.
* **Slow Manual Screening**: Evaluating candidates' GitHub profiles takes hours of coordination with technical team members, slowing down the sourcing pipeline.

### 1.3 Problems Faced by Open-Source Maintainers & Managers
* **Audit Fatigue**: Continuous manual auditing of repository documentation, licensing, test coverage, and design architecture on new PRs is repetitive.
* **Onboarding Friction**: New contributors struggle to run projects because setup instructions become outdated.

### 1.4 Why Existing Tools Fall Short
Traditional code quality tools (e.g., SonarQube, CodeQL) focus strictly on static analysis, security vulnerabilities, or language rules. They completely ignore contextual indicators like **licensing, professional setup quality, developer intent, and recruiter readability**.

---

## 2. Target Users & Personas

### 2.1 Student Developers & Portfolio Builders
* **Goal**: Land entry-level software engineering roles by showcasing clean code.
* **Workflow**: Builds personal projects, hosts them on public GitHub profiles, and links them in job applications.
* **Pain Point**: Cannot get recruiter feedback on why their application was rejected or if their project structure is correct.

### 2.2 Technical Recruiters & Sourcing Specialists
* **Goal**: Identify qualified candidates quickly without bothering engineering managers.
* **Workflow**: Scrapes GitHub portfolios or reviews inbound applicant profile links.
* **Pain Point**: Cannot tell if a repository is a simple code-along clone or a complex multi-layered architecture.

### 2.3 Open-Source Maintainers
* **Goal**: Ensure high-quality pull requests and simplify contributor onboarding.
* **Workflow**: Configures setup instructions, checks licenses, reviews PR checks, and issues contributions.
* **Pain Point**: Contributor setups break frequently because setup documents are not validated as part of CI/CD.

### 2.4 Engineering Managers
* **Goal**: Validate repository health and developer onboarding standards across organizational projects.
* **Workflow**: Audits repository test coverage, CI/CD statuses, and structure compliance.
* **Pain Point**: No centralized dashboard showing which repositories lack clean setups, licenses, or setup automation.

---

## 3. Competitive Analysis

| Competitor | What They Do Well | Where They Fall Short | DevLens Differentiation |
| :--- | :--- | :--- | :--- |
| **SonarQube** | Deep static analysis, security scans, test coverage tracking. | No evaluation of setup documents, licenses, or candidate hireability signals. | **Contextual Audit**: DevLens scores documentation readability, setup guidelines, and project intent. |
| **CodeRabbit** | AI-driven line-by-line pull request reviews. | Focused on local PR code diffs, not overall project readiness or portfolio metrics. | **High-Level Scorecard**: DevLens provides a structured recruiter scorecard and bento insight board. |
| **GitHub CodeQL** | Excellent security scanning and semantic analysis. | Hard to configure, purely security-focused. | **Onboarding & Design**: Setup takes 1 click (GitHub App); returns instant developer feedback. |
| **GitHub Insights** | Tracks team velocity, commits, and pull requests. | Measures developer activity quantity, not project setup or architectural quality. | **Qualitative Scoring**: Evaluates the *quality* of setups and architecture, not just commit volume. |

---

## 4. Product Pillars

```text
       ┌────────────────────────────────────────────────────────┐
       │                 DEVLENS CORE PILLARS                   │
       └───────┬───────────────────┬────────────────────┬───────┘
               │                   │                    │
 ┌─────────────▼─────────┐ ┌───────▼─────────────┐ ┌────▼────────────────┐
 │Repository Intelligence│ │ Recruiter Readiness │ │ Continuous Analysis │
 ├───────────────────────┤ ├─────────────────────┤ ├─────────────────────┤
 │ Architecture mapping, │ │ Scoring engine,     │ │ Webhooks, PR checks │
 │ setup checks & README │ │ recruiter verdicts, │ │ and automated       │
 │ verification.         │ │ portable JSON specs.│ │ status badges.      │
 └───────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

1. **Repository Intelligence**: Structural mapping of file trees, configuration detection (Vite, Docker, etc.), and README audits.
2. **Recruiter Readiness**: Translates complex repository trees into standardized scorecards, feedback text, and priority checklists.
3. **Continuous Analysis**: Connects directly to the GitHub event pipeline via Webhooks to evaluate repositories automatically on commit push.

---

## 5. Feature Roadmap

### 5.1 Phase 1: MVP (Q1)
* **Objective**: Establish the core analysis pipeline with high accuracy and reliability.
* **Features**:
  * Public repository auditing via URL paste.
  * Scorecard generation (Base 5.0 with Merit/Deductions, capped at 7.0 if tests/CI/CD are missing).
  * Collapsible Priority Checklist explaining hiring impact.
  * Save analysis as a portable JSON download.
  * *Rationale*: Validates user value and algorithm rules with minimal operational cost.

### 5.2 Phase 2: Version 3.1 (Q2)
* **Objective**: Implement secure authentication and GitHub App support.
* **Features**:
  * GitHub App registration with installation-level tokens.
  * Secure OAuth (Sign-In with GitHub) to manage personal profiles.
  * Basic user dashboard showing active installations and historic audit trends.
  * *Rationale*: Transitions DevLens into a secure, multi-tenant cloud service.

### 5.3 Phase 3: Version 3.5 (Q3)
* **Objective**: Automate evaluations via continuous event listening.
* **Features**:
  * Webhook listener tracking repository commits (`push`, `pull_request`).
  * Asynchronous processing using Redis tasks to eliminate browser timeout.
  * SVG Badge generator endpoints (`/badge/{repo_id}`).
  * *Rationale*: Embeds DevLens directly in open-source development workflows.

### 5.4 Phase 4: Version 4.0 (Q4)
* **Objective**: Scale as an Enterprise organization platform.
* **Features**:
  * Organization-wide dashboards displaying repository setup audits.
  * Advanced PR feedback bot leaving automated inline code comments.
  * Public Developer API for programmatically retrieving scorecard metrics.
  * *Rationale*: Opens monetizable features for enterprise and commercial developer teams.

---

## 6. Success Metrics (KPIs)

* **WAU (Weekly Active Users)**: Target >5,000 active developers checking portfolios.
* **GitHub App Installations**: Target >1,000 public and private installations.
* **Audit Duration**: Ensure background evaluations finish in `<15 seconds`.
* **API Latency**: Gateway endpoints (e.g. badge fetching) must return in `<100ms`.
* **User Retention**: Percentage of users who rerun audits weekly to track scorecard updates.

---

## 7. Product Constraints & Exclusions

* **No Code Editing**: DevLens will analyze and propose changes, but will **never write or edit** files in the repository. Security constraints prohibit write access.
* **No Git Hosting**: Will not compete with GitHub, GitLab, or Bitbucket. DevLens is strictly an intelligence layer.
* **No General AI Chat**: There is no free-form AI text prompt. Feedback is focused purely on repository scores and setup fixes.

---

## 8. Guiding Principles

Every feature built for DevLens must adhere to these 15 principles:
1. **Developer First**: Every feature must help developers build better portfolios.
2. **Deterministic Evaluation**: AI scoring must remain consistent for identical commits.
3. **No Hidden Costs**: Explain the mathematical deductions in a `logic_scratchpad`.
4. **Actionable Priority**: Order checklists by hiring impact (High, Medium, Low).
5. **Least Privilege Scope**: Request only read access to metadata and repository contents.
6. **No Code Retaining**: Code data must be analyzed in memory and immediately discarded.
7. **One-Click Setup**: Registration of the GitHub App must take under 10 seconds.
8. **GitHub Native**: Support markdown and badges that render directly in GitHub readmes.
9. **No Tutorial Clones**: Penalty scoring rules must flag unoriginal boilerplates.
10. **Explainable AI**: Avoid generic feedback; detail *why* the audit item passed or failed.
11. **Performance Over Complexity**: Keep endpoints fast; delegate heavy analysis to workers.
12. **Accurate Error Handling**: Inform users immediately if Git or LLM APIs are unreachable.
13. **Mobile First Viewports**: Make bento grids and dashboards fully responsive.
14. **Design Transparency**: Avoid dark patterns; pricing, support, and data terms must be plain.
15. **Developer Standards Compliance**: Scoring checks must update to match modern dev practices (e.g., modern packaging, containerization, lint configurations).
