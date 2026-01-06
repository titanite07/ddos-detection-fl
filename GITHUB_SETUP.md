# GitHub Setup & Deployment Guide

## Step 1: Initialize Git Repository

```bash
cd "c:\Users\HP\Desktop\Major Project\Main File-Code\ddosdfl"

# Initialize git (if not already done)
git init

# Check status
git status
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name**: `ddos-detection-fl` (or your preferred name)
3. **Description**: "Privacy-Preserving Distributed DDoS Detection using Federated Learning"
4. **Visibility**: ✅ Public
5. **DO NOT** initialize with README (we have one)
6. Click "Create repository"

## Step 3: Add Files to Git

```bash
# Add all files
git add .

# Check what will be committed
git status

# Create first commit
git commit -m "Initial commit: DDoS Detection FL System"
```

## Step 4: Connect to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ddos-detection-fl.git

# Verify remote
git remote -v
```

## Step 5: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

## Step 6: Verify on GitHub

1. Go to your repository URL
2. Verify all files are present
3. Check README displays correctly

## Step 7: Configure Repository Settings

### On GitHub website:

1. **About Section** (top right)

   - Add description
   - Add topics: `ddos-detection`, `federated-learning`, `privacy`, `deep-learning`
   - Add website (if any)

2. **Branch Protection** (Settings → Branches)

   - Protect `main` branch
   - Require PR reviews
   - Enable status checks

3. **Issues** (Settings → Features)

   - Enable Issues for bug tracking

4. **Discussions** (Settings → Features)
   - Enable Discussions for team communication

## Step 8: Create Development Branch

```bash
# Create and switch to development branch
git checkout -b develop

# Push development branch
git push -u origin develop
```

## Post-Setup Checklist

- [ ] Repository is public and accessible
- [ ] README displays correctly
- [ ] .gitignore working (no venv, data, models in repo)
- [ ] LICENSE file present
- [ ] CONTRIBUTING.md present
- [ ] No sensitive data committed
- [ ] All team members have access

## Team Collaboration Workflow

### For Contributors:

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/ddos-detection-fl.git

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit
git add .
git commit -m "feat: Your feature description"

# 4. Push to GitHub
git push -u origin feature/your-feature-name

# 5. Create Pull Request on GitHub
```

### For Code Review:

1. Review PR on GitHub
2. Comment on code changes
3. Request changes if needed
4. Approve and merge when ready

## Useful Git Commands

```bash
# Check current branch
git branch

# Pull latest changes
git pull origin main

# View commit history
git log --oneline

# Discard local changes
git checkout -- .

# View remote URL
git remote -v

# Update remote URL (if needed)
git remote set-url origin https://github.com/NEW_URL.git
```

## Common Issues & Solutions

### Issue: "Permission denied"

**Solution**:

```bash
# Use HTTPS with personal access token
# Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

### Issue: "Large files rejected"

**Solution**:

```bash
# Remove from staging
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit the change
git commit -m "Remove large file"
```

### Issue: "Merge conflicts"

**Solution**:

```bash
# Pull latest changes
git pull origin main

# Resolve conflicts in editor
# Then commit
git add .
git commit -m "Resolve merge conflicts"
```

## Next Steps After GitHub Setup

1. ✅ Share repository link with team
2. ✅ Add team members as collaborators
3. ✅ Create initial issues for tasks
4. ✅ Set up project board (optional)
5. ✅ Configure branch protection rules
6. ✅ Start first sprint!

## Repository URL Structure

After setup, your repository will be at:

```
https://github.com/YOUR_USERNAME/ddos-detection-fl
```

Clone URL:

```
https://github.com/YOUR_USERNAME/ddos-detection-fl.git
```

---

**Ready to push?** Follow Steps 1-6 above! 🚀
