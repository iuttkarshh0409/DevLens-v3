# Visual Studio Marketplace Publishing Checklist

Follow these steps to pack, bundle, compile, and publish the DevLens VS Code Extension to the public marketplace.

---

## 1. Prerequisites
- [x] Install node package manager dependencies in `vscode-extension/`.
- [x] Compile TS compiler targets (`npm run compile`).
- [x] Verify extension manifest parameters in `package.json`.

---

## 2. Compile & Bundle
To prepare the package for marketplace publication:
1. Navigate to the extension folder:
   ```bash
   cd vscode-extension
   ```
2. Install packaging tools globally (if not already installed):
   ```bash
   npm install -g @vscode/vsce
   ```
3. Build the production VSIX bundle locally:
   ```bash
   vsce package
   ```
   This generates a `devlens-1.0.0.vsix` package in the root directory.

---

## 3. Metadata Verification
Before publishing, ensure the following fields are defined in `package.json`:
- `publisher`: Unique publisher identifier.
- `icon`: High-res extension logo path (PNG format, recommended size 128x128).
- `repository`: Source control link repository.
- `license`: Standard licensing schema (`MIT`).

---

## 4. Visual Studio Marketplace Publishing
1. Create a publisher account on the [Visual Studio Marketplace Publisher Portal](https://marketplace.visualstudio.com/manage).
2. Set up a Personal Access Token (PAT) with "Marketplace (Publish)" scopes on Azure DevOps.
3. Publish using the CLI command:
   ```bash
   vsce publish -p <YOUR_PERSONAL_ACCESS_TOKEN>
   ```
4. Verify the active listing in the Visual Studio Code Extensions search bar.
