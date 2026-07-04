# DevLens App Onboarding Guide

This document describes how to connect, install, configure, and use the DevLens V3 GitHub App on your repositories.

## 1. Installation Flow
1. Navigate to `/app/install` in the DevLens application dashboard.
2. You will be redirected to the GitHub App setup page:
   `https://github.com/apps/devlens-v3/installations/new`
3. Select your account or organization, choose "All repositories" or "Only select repositories", and click **Install**.
4. GitHub redirects back to the `/app/callback` endpoint returning a successful confirmation payload containing:
   - `installation_id`
   - Active scopes
   - Connected repositories count
   - Next steps instruction list

---

## 2. Setting Up Merge Gating (Commit Statuses)
To block pull requests with code quality issues or scores below the default 7.0 limit:
1. Go to your GitHub Repository Settings.
2. Select **Branches** under the "Code and automation" sidebar.
3. Click **Add branch protection rule** (or edit an existing rule on `main`/`master`).
4. Enable **Require status checks to pass before merging**.
5. Search for the status check: `devlens/audit` and select it.
6. Click **Save Changes**.

Now, pull requests failing to meet a 7.0 score will block merge actions until recommendations are fixed.

---

## 3. Retrieving Badges
Use our SVG badge API in your README files to display code scores dynamically:

```markdown
![DevLens Score](https://<your-devlens-server>/api/badge?label=devlens&value=8.5&metric=score)
```

### URL Parameters:
- `label`: Text shown on left side (e.g. `devlens`).
- `value`: Score or status (e.g. `8.5`, `passed`).
- `metric`: `score` or `status` (activates color schemes).
- `style`: `flat`, `flat-square`, or `plastic`.
- `color`: Custom HEX color override.

