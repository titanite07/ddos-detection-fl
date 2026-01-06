# GitHub CLI Deployment Guide

## ✨ Automated Deployment with GitHub CLI

### Prerequisites

1. **Install GitHub CLI** (if not installed):

   - Windows: `winget install --id GitHub.cli`
   - Or download from: https://cli.github.com/

2. **Login to GitHub**:
   ```bash
   gh auth login
   # Select: GitHub.com
   # Select: HTTPS
   # Authenticate via browser
   ```

### 🚀 One-Command Deployment

```bash
# Navigate to project
cd "c:\Users\HP\Desktop\Major Project\Main File-Code\ddosdfl"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Privacy-Preserving DDoS Detection FL System"

# Create GitHub repo and push (all in one!)
gh repo create ddos-detection-fl --public --source=. --push

# Add description
gh repo edit --description "Privacy-Preserving Distributed DDoS Detection using Federated Learning with CNN-BiLSTM"

# Add topics
gh repo edit --add-topic ddos-detection,federated-learning,privacy-preserving-ml,deep-learning,cnn-bilstm,feature-selection
```

### Alternative: Step-by-Step with gh

```bash
# 1. Create repository on GitHub
gh repo create ddos-detection-fl --public --description "Privacy-Preserving DDoS Detection with FL"

# 2. Add remote
git remote add origin https://github.com/YOUR_USERNAME/ddos-detection-fl.git

# 3. Push code
git branch -M main
git push -u origin main
```

### Verify Deployment

```bash
# Open repository in browser
gh repo view --web

# Check repository info
gh repo view
```

### Manage Repository

```bash
# Add collaborators
gh repo add-collaborator USERNAME

# Create first issue
gh issue create --title "Setup CI/CD pipeline" --body "Add automated testing"

# Enable discussions
gh repo edit --enable-discussions

# Clone for team members
gh repo clone YOUR_USERNAME/ddos-detection-fl
```

### Common GitHub CLI Commands

```bash
# View your repositories
gh repo list

# View pull requests
gh pr list

# Create pull request
gh pr create

# View issues
gh issue list

# Create issue
gh issue create

# Check authentication
gh auth status

# Logout
gh auth logout
```

---

## 🎯 Quick Deploy

**If gh is installed and authenticated:**

```bash
cd "c:\Users\HP\Desktop\Major Project\Main File-Code\ddosdfl"
git add .
git commit -m "Initial commit: DDoS Detection FL System"
gh repo create ddos-detection-fl --public --source=. --push
```

**Done!** Repository created and code pushed automatically! 🚀

Visit: `https://github.com/YOUR_USERNAME/ddos-detection-fl`
