# Medicaid Work Requirements Monitor

A comprehensive public-facing platform that tracks Medicaid work requirements across all 50 US states plus the District of Columbia. The system provides automated weekly updates, an elegant user interface, and administrative tools for data management.

## Features

### Public Dashboard
- **State-by-State Overview**: View current Medicaid work requirements status for all 51 jurisdictions
- **Search & Filter**: Quickly find states by name or filter by implementation status
- **Real-time Statistics**: See counts of active programs, pending implementations, and more
- **Responsive Design**: Optimized for patients and healthcare workers on any device

### State Detail Pages
- **Comprehensive Information**: Work hour requirements, qualifying activities, exemptions
- **Contact Information**: State agency details, phone numbers, websites
- **Source Citations**: Links to official government sources
- **Update History**: Timeline of recent changes and updates

### Automated Update System
- **Weekly Updates**: Automated scanning of government sources and news
- **LLM-Powered Extraction**: Uses AI to extract and structure policy information
- **Change Tracking**: Full audit trail of all data changes with sources
- **Rate Limiting**: 2-second delays between states to respect API limits

### Admin Dashboard
- **Manual Update Triggers**: Update individual states or run full updates
- **Update Logs**: View detailed logs of all changes with status indicators
- **Data Quality Monitoring**: Track update success rates and identify issues
- **Role-Based Access**: Admin-only access to management features

## Technology Stack

- **Frontend**: React 19, Tailwind CSS 4, shadcn/ui components
- **Backend**: Express.js, tRPC for type-safe APIs
- **Database**: MySQL/TiDB with Drizzle ORM
- **Authentication**: Manus OAuth integration
- **AI Integration**: LLM for policy information extraction

## Implementation Status Categories

| Status | Description |
|--------|-------------|
| **Active** | Work requirements are currently being enforced |
| **Pending Approval** | Waiver application pending CMS approval |
| **Approved (Not Active)** | CMS approved but not yet implemented |
| **Suspended** | Program temporarily suspended |
| **Terminated** | Program has been terminated or struck down |
| **Not Implemented** | State has no work requirements program |

## Getting Started

### Prerequisites
- Node.js 18+
- pnpm package manager
- MySQL database

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/medicaid-work-monitor.git
cd medicaid-work-monitor

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Push database schema
pnpm db:push

# Start development server
pnpm dev
```

### Database Seeding

After starting the application:
1. Sign in with an admin account
2. Navigate to `/admin`
3. Click "Seed All States" to initialize the database with all 51 states

### Running Weekly Updates

Updates can be triggered in two ways:

1. **Manual**: From the admin dashboard, click "Start Full Update"
2. **Scheduled**: Configure a cron job to call the update endpoint weekly

## Project Structure

```
medicaid-work-monitor/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   └── lib/           # Utilities and tRPC client
├── server/                 # Express backend
│   ├── routers.ts         # tRPC API routes
│   ├── db.ts              # Database helpers
│   ├── updateService.ts   # Automated update logic
│   └── seedStates.ts      # Initial data seeding
├── drizzle/               # Database schema and migrations
└── shared/                # Shared types and constants
```

## API Endpoints

### Public Endpoints
- `states.list` - Get all states
- `states.byCode` - Get state by code (e.g., "GA")
- `states.search` - Search states by name
- `states.byStatus` - Filter states by implementation status
- `states.stats` - Get dashboard statistics

### Admin Endpoints (requires admin role)
- `admin.seedStates` - Initialize database with all states
- `admin.updateState` - Update a single state
- `admin.updateAllStates` - Run full weekly update
- `admin.recentLogs` - View update logs
- `admin.dashboardStats` - Get admin dashboard data

## Data Sources

The system aggregates information from:
- Official state Medicaid agency websites
- Medicaid.gov state profiles
- Kaiser Family Foundation (KFF) policy tracker
- Government policy announcements

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

MIT License - see LICENSE file for details.

## Disclaimer

This tool is for informational purposes only. For official Medicaid work requirements information, please contact your state's Medicaid agency directly. Data is updated weekly and may not reflect the most recent policy changes.
