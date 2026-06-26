# Quick Start Guide

Get the GitLab Stale MRs Tracker running in 5 minutes.

## Prerequisites

- Python 3.8+
- GitLab personal access token with `read_api` scope
- Access to GitLab group(s) you want to track

## Installation Steps

### 1. Setup Environment

```bash
# Navigate to project
cd gitlab-stale-mrs

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure GitLab Access

```bash
# Copy example config
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Minimum required config:**
```env
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_GROUP=yourorg/yourgroup
```

### 3. Run the Dashboard

```bash
# Option 1: Use helper script
./start.sh

# Option 2: Direct command
uvicorn app.main:app --reload
```

### 4. Open Dashboard

Open your browser to: **http://localhost:8001**

**Note:** Uses port 8001 by default (different from main GitLab Dashboard's 8000) so you can run both simultaneously.

## First Use

When you first open the dashboard:

1. **Click "Refresh Data"** - Fetches current MRs from GitLab (takes ~10 seconds)
2. **Adjust Threshold** - Try different stale thresholds (3, 5, 7, 10, 14 days)
3. **Sort Table** - Click column headers to sort by different criteria
4. **Take Action** - Click "View MR →" links to review each stale MR

## What You'll See

### Metrics Cards
- **Total Open MRs**: All currently open merge requests
- **Stale MRs**: Count older than threshold (yellow/orange if any exist)
- **Stale Percentage**: What % of open MRs are stale
- **Last Updated**: Cache age

### Stale MRs Table
- All MRs older than selected threshold
- Color-coded by severity:
  - 🟡 Yellow = 7-14 days (moderate)
  - 🟠 Orange = 15-30 days (high priority)
  - 🔴 Red = >30 days (critical)
- Sorted by oldest first (most urgent at top)
- Direct links to each MR

## Common Configurations

### Multiple Groups

If you want to track multiple groups:

```bash
# Copy example
cp groups.json.example groups.json

# Edit to add your groups
nano groups.json
```

Example `groups.json`:
```json
{
  "groups": [
    {
      "id": "backend",
      "name": "Backend Services",
      "path": "myorg/backend",
      "type": "group",
      "enabled": true
    },
    {
      "id": "frontend",
      "name": "Frontend Apps",
      "path": "myorg/frontend",
      "type": "group",
      "enabled": true
    }
  ]
}
```

### Adjust Cache Duration

By default, data is cached for 1 hour. To change:

```env
# In .env file
CACHE_DURATION_HOURS=6  # Cache for 6 hours
```

**When to increase:**
- You don't need real-time data
- You want faster dashboard loads
- You have GitLab API rate limits

**When to decrease:**
- You need fresher data
- You're actively triaging stale MRs
- Your team merges MRs frequently

### Change Default Stale Threshold

```env
# In .env file
STALE_MR_DAYS=10  # Default to 10 days instead of 7
```

Note: This is just the default - users can still change it via the UI dropdown.

### Change Port

```env
# In .env file
PORT=8002  # Use a different port
```

Default is 8001 (to avoid conflict with main GitLab Dashboard on 8000).

## Troubleshooting

### "Failed to load stale MRs"

**Check token:**
```bash
# Verify your token has correct permissions
# Should have: read_api scope
```

**Check group path:**
```bash
# Make sure group path is correct
# Format: org/group or org/group/subgroup
# NOT: https://gitlab.com/org/group
```

### No data showing

1. Click "Refresh Data" button to force fetch
2. Check browser console for errors (F12)
3. Verify you have open MRs in the configured group

### All MRs showing as stale

Your stale threshold might be too aggressive. Try:
- Increase threshold to 14 or 21 days
- Check if MRs are actually old (verify in GitLab)

## Next Steps

- **Set up daily routine**: Check dashboard each morning
- **Customize threshold**: Find the right balance for your team
- **Dark mode**: Click moon icon (🌙) in top-right for dark theme
- **Multi-group**: Add more groups to track your full organization

## Support

For issues or questions:
1. Check the main [README.md](README.md) for detailed documentation
2. Review the [GitLab Dashboard](https://github.com/fpj-engmgr/gitlab-dashboard) for the full-featured version
3. Open an issue on GitHub

---

**That's it!** You should now have a working stale MR tracker. Happy triaging! 🎉
