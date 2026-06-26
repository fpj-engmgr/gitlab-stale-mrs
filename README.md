# GitLab Stale MRs Tracker

A focused, lightweight dashboard for tracking and managing **stale merge requests** across GitLab groups and projects. Helps engineering teams identify MRs that need attention before they're forgotten.

## Key Features

- **🚨 Stale MR Detection**: Instantly see which MRs have been open too long
- **⚙️ Configurable Threshold**: Set stale threshold from 3-30 days (default: 7 days)
- **🎨 Severity Color Coding**: Visual indicators based on age
  - 🟡 **Moderate** (7-14 days) - Needs attention soon
  - 🟠 **High** (15-30 days) - Overdue for review
  - 🔴 **Critical** (>30 days) - Urgent action required
- **📊 Key Metrics**: Total open MRs, stale count, stale percentage
- **🔍 Multi-Group Support**: Track multiple GitLab groups/projects
- **📑 Sortable Table**: Sort by title, project, author, days open, or created date
- **🌙 Dark Mode**: Toggle between light and dark themes
- **💾 Smart Caching**: Fast loads with configurable cache duration
- **🔄 Manual Refresh**: Update data on demand

## Why This Tool?

Stale merge requests are a common problem in software teams:
- Important work gets forgotten
- Context is lost over time
- Review backlog grows unmanageable
- Bottlenecks aren't visible

This tool provides a **single focused view** of the problem, making it easy to:
1. See ALL stale MRs across your teams
2. Prioritize by severity (age-based color coding)
3. Take action with direct links to each MR
4. Track progress as stale count decreases

## Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd gitlab-stale-mrs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your GitLab token
# Required:
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_personal_access_token
GITLAB_GROUP=yourorg/yourgroup

# Optional (with defaults):
STALE_MR_DAYS=7
CACHE_DURATION_HOURS=1
```

**Get a GitLab Personal Access Token:**
1. Go to GitLab → Settings → Access Tokens
2. Create token with `read_api` scope
3. Copy token to `.env` file

### 3. Multi-Group Setup (Optional)

To track multiple groups/projects:

```bash
cp groups.json.example groups.json
```

Edit `groups.json`:
```json
{
  "groups": [
    {
      "id": "backend",
      "name": "Backend Team",
      "path": "yourorg/backend",
      "type": "group",
      "enabled": true
    },
    {
      "id": "frontend",
      "name": "Frontend Team",
      "path": "yourorg/frontend",
      "type": "group",
      "enabled": true
    }
  ]
}
```

**Source Types:**
- `"type": "group"` - Track all projects within a GitLab group
- `"type": "project"` - Track a single specific project

If `groups.json` doesn't exist, uses single-group mode with `GITLAB_GROUP` from `.env`.

### 4. Run

```bash
uvicorn app.main:app --reload
```

Open browser: [http://localhost:8001](http://localhost:8001)

**Note:** Runs on port 8001 by default (configurable via `PORT` in `.env`) so you can run it alongside the full GitLab Dashboard (port 8000).

## Usage

### Dashboard Overview

The dashboard shows:

1. **Metrics Cards**
   - **Total Open MRs**: All currently open merge requests
   - **Stale MRs**: Count of MRs older than threshold (warning styling if > 0)
   - **Stale Percentage**: What % of open MRs are stale
   - **Last Updated**: How long ago data was refreshed

2. **Controls**
   - **Group Filter**: View all groups or filter to specific group
   - **Stale Threshold**: Choose from 3, 5, 7, 10, 14, 21, or 30 days
   - **Refresh Data**: Manually update from GitLab
   - **Dark Mode Toggle**: Switch between light/dark themes

3. **Stale MRs Table**
   - All MRs older than selected threshold
   - Sortable by any column (click headers)
   - Color-coded by severity
   - Direct links to each MR
   - Shows title, project, author, days open, created date

### Typical Workflow

1. **Morning Check**: Open dashboard to see overnight stale MRs
2. **Triage**: Click through critical (red) and high (orange) MRs
3. **Take Action**: Review, merge, or close each stale MR
4. **Track Progress**: Watch stale count decrease as you clear backlog
5. **Adjust Threshold**: If too noisy, increase to 10-14 days

### Customizing Stale Threshold

The threshold determines when an MR is considered "stale":

- **3-5 days**: Fast-moving teams with quick review cycles
- **7 days** (default): Balanced for most teams
- **10-14 days**: Larger teams or longer review processes
- **21-30 days**: Only catch truly abandoned MRs

**Tip**: Start with 7 days. If you have too many false positives (MRs that are legitimately waiting), increase threshold.

## Configuration Reference

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `GITLAB_URL` | `https://gitlab.com` | GitLab instance URL |
| `GITLAB_TOKEN` | *(required)* | Personal access token with `read_api` scope |
| `GITLAB_GROUP` | *(required)* | Default group path (used if no `groups.json`) |
| `DATABASE_URL` | `sqlite:///./stale_mrs.db` | Database connection string |
| `CACHE_DURATION_HOURS` | `1` | How long to cache data (1 hour recommended for stale tracking) |
| `STALE_MR_DAYS` | `7` | Default threshold for stale MRs (overridable in UI) |
| `PORT` | `8001` | Port to run server on (8001 avoids conflict with main dashboard) |

### Multi-Group Configuration (groups.json)

```json
{
  "groups": [
    {
      "id": "unique-id",           // Short identifier
      "name": "Display Name",      // Shown in UI
      "path": "org/group/path",    // GitLab group or project path
      "type": "group",             // "group" or "project"
      "description": "Optional",   // Context note
      "enabled": true              // Enable/disable without deleting
    }
  ]
}
```

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/groups` - List configured groups
- `GET /api/stale-mrs?stale_days=7&group_id=backend` - Get stale MRs
- `POST /api/refresh` - Force refresh from GitLab
- `GET /health` - Health check

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Vanilla JavaScript + CSS
- **GitLab Integration**: python-gitlab library

## Project Structure

```
gitlab-stale-mrs/
├── app/
│   ├── api/
│   │   └── routes.py              # API endpoints
│   ├── models/
│   │   ├── database.py            # Database setup
│   │   └── schemas.py             # SQLAlchemy models
│   ├── services/
│   │   ├── gitlab_client.py       # GitLab API client
│   │   └── stale_service.py       # Stale MR logic
│   ├── static/
│   │   ├── css/style.css          # Dashboard styles
│   │   └── js/dashboard.js        # Frontend logic
│   ├── templates/
│   │   └── dashboard.html         # Main dashboard
│   ├── config.py                  # Configuration
│   └── main.py                    # FastAPI app
├── .env.example
├── .gitignore
├── groups.json.example
├── requirements.txt
└── README.md
```

## Performance

- **First Load**: 5-10 seconds (fetches from GitLab)
- **Cached Loads**: <1 second (served from database)
- **Cache Duration**: 1 hour (configurable)
- **Refresh**: Manual via "Refresh Data" button

**Why 1-hour cache?**  
Stale MR status doesn't change minute-to-minute. A 1-hour cache keeps the dashboard fast while staying reasonably current. Increase to 6-12 hours if you prefer less frequent updates.

## Comparison to Full Dashboard

This project is derived from [gitlab-dashboard](https://github.com/fpj-engmgr/gitlab-dashboard) but **focused solely on stale MR tracking**.

| Feature | Stale MRs Tracker | Full Dashboard |
|---------|-------------------|----------------|
| Stale MR detection | ✅ **Primary focus** | ✅ One of many metrics |
| MR metrics (total, merged, time-to-merge) | ❌ | ✅ |
| Contributor stats | ❌ | ✅ |
| Comment/review metrics | ❌ | ✅ |
| Charts & visualizations | ❌ | ✅ |
| Database size | Small (MRs only) | Larger (MRs + commits + comments) |
| Refresh time | Fast (10s) | Slower (30s - 10min) |
| Use case | Daily stale MR triage | Comprehensive team analytics |

**When to use this:**
- You primarily care about stale MRs
- You want a lightweight, fast tool
- You need quick daily triage workflows

**When to use full dashboard:**
- You want comprehensive team metrics
- You need contributor analytics and trends
- You want historical data and charts

## Troubleshooting

**"Failed to load stale MRs"**  
→ Check GitLab token is valid and has `read_api` scope

**"No data showing"**  
→ Verify `GITLAB_GROUP` path is correct or `groups.json` is configured  
→ Click "Refresh Data" to force fetch from GitLab

**"All MRs showing as stale"**  
→ Increase stale threshold (try 14 or 21 days)

**"Empty dashboard"**  
→ Check you have open MRs in configured groups  
→ Verify group paths in `groups.json` are accessible with your token

## Contributing

This is a focused tool extracted from a larger dashboard project. Contributions welcome for:
- Bug fixes
- Performance improvements
- UI/UX enhancements
- Additional sorting/filtering options

Please keep the scope focused on **stale MR tracking**. For broader metrics, see [gitlab-dashboard](https://github.com/fpj-engmgr/gitlab-dashboard).

## License

MIT

---

**Built with focus.** One problem, solved well.
