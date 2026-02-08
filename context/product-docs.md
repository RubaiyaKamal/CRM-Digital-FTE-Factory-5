# CloudFlow Product Documentation

**Product:** CloudFlow by TechCorp SaaS
**Version:** 3.2.1
**Last Updated:** 2026-02-06

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication & Account Management](#authentication--account-management)
3. [Projects & Workspaces](#projects--workspaces)
4. [Tasks & Assignments](#tasks--assignments)
5. [Collaboration Features](#collaboration-features)
6. [Integrations](#integrations)
7. [Time Tracking & Reporting](#time-tracking--reporting)
8. [Mobile Apps](#mobile-apps)
9. [Billing & Subscription Management](#billing--subscription-management)
10. [Security & Compliance](#security--compliance)
11. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Creating an Account

1. Visit https://www.techcorp-cloudflow.com
2. Click "Start Free Trial"
3. Enter email and create password (minimum 8 characters, 1 uppercase, 1 number)
4. Verify email address (check spam folder if not received within 5 minutes)
5. Complete onboarding wizard

**Trial Period:** 14 days, full access to Professional features

### First Project Setup

1. Click "Create Project" from dashboard
2. Enter project name and description
3. Choose template (Blank, Software Development, Marketing Campaign, Product Launch)
4. Invite team members via email
5. Start adding tasks

---

## Authentication & Account Management

### Logging In

**Standard Login:**
- Email + password
- "Remember me" keeps you logged in for 30 days
- Session timeout: 12 hours of inactivity

**Single Sign-On (SSO):**
- Available for Enterprise tier only
- Supports SAML 2.0, Google Workspace, Microsoft Azure AD
- Contact support@techcorp.com to enable

### Password Reset

**Self-Service Reset:**
1. Click "Forgot Password" on login page
2. Enter email address
3. Check email for reset link (expires in 1 hour)
4. Create new password
5. Re-login with new credentials

**If reset link doesn't arrive:**
- Check spam/junk folder
- Verify you're using the correct email address
- Request a new link (previous link will be invalidated)
- Contact support if still not received after 15 minutes

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 number
- At least 1 special character (optional but recommended)
- Cannot reuse last 5 passwords

### Two-Factor Authentication (2FA)

**Available for:** Professional and Enterprise tiers

**Setup:**
1. Go to Settings → Security
2. Click "Enable Two-Factor Authentication"
3. Scan QR code with authenticator app (Google Authenticator, Authy, 1Password)
4. Enter 6-digit code to confirm
5. Save recovery codes in a safe place

**Recovery:** Use backup codes if you lose access to authenticator app

### Account Settings

**Profile Management:**
- Update name, email, profile photo
- Set notification preferences
- Configure timezone
- Set work hours for scheduling

**Email Notifications:**
- Task assignments
- Task comments and mentions
- Project updates
- Due date reminders
- Weekly summary emails

---

## Projects & Workspaces

### Workspaces

**Definition:** A workspace is a collection of related projects, typically used per team or department.

**Creating a Workspace:**
1. Click workspace dropdown in top-left
2. Select "Create New Workspace"
3. Name the workspace
4. Set privacy (Public = all team members can see, Private = invite only)

**Workspace Roles:**
- **Admin:** Full control, can delete workspace
- **Member:** Can create projects, manage own tasks
- **Guest:** View-only access to specific projects

### Projects

**Creating a Project:**
- From workspace, click "New Project"
- Use templates or start blank
- Set project visibility (Public or Private)
- Set project color and icon (for visual organization)

**Project Templates:**
1. **Software Development** - Sprint planning, bug tracking, release management
2. **Marketing Campaign** - Campaign planning, content calendar, launch tasks
3. **Product Launch** - Pre-launch, launch, post-launch phases
4. **Event Planning** - Venue, speakers, marketing, day-of execution
5. **Onboarding** - New hire checklist and training tasks

**Project Settings:**
- Description and goals
- Default assignee
- Default due date behavior
- Custom fields (Professional+)
- Automation rules (Professional+)

### Project Views

**List View:** Traditional task list with filters and sorting
**Board View:** Kanban-style columns (To Do, In Progress, Done)
**Timeline View:** Gantt chart for dependency visualization (Professional+)
**Calendar View:** See tasks by due date
**Table View:** Spreadsheet-like interface with custom columns (Professional+)

---

## Tasks & Assignments

### Creating Tasks

**Quick Add:**
- Press `Ctrl+N` (Windows) or `Cmd+N` (Mac)
- Type task name and press Enter

**Detailed Task Creation:**
1. Click "+ Add Task" button
2. Enter task name (required)
3. Set assignee (optional)
4. Set due date (optional)
5. Add description with rich text editor
6. Add subtasks for multi-step work
7. Attach files (max 25MB per file on Starter, 100MB on Professional+)
8. Add tags for categorization
9. Set priority (Low, Medium, High, Urgent)

### Task Dependencies

**Available for:** Professional and Enterprise tiers

**Setting Dependencies:**
1. Open task details
2. Click "Add Dependency"
3. Search for the blocking task
4. Select relationship:
   - **Blocks:** This task must be completed first
   - **Blocked by:** Cannot start until another task completes
   - **Related to:** Informational link only

**Dependency Rules:**
- Circular dependencies are automatically prevented
- Dependent tasks show a warning when the blocking task is incomplete

### Task Statuses

**Default Statuses:**
- **To Do** - Not started
- **In Progress** - Actively being worked on
- **Review** - Awaiting feedback or approval
- **Done** - Completed

**Custom Statuses:** Available for Professional+ tiers (up to 20 custom statuses)

### Recurring Tasks

**Available for:** All tiers

**Setup:**
1. Open task details
2. Enable "Repeat"
3. Choose frequency:
   - Daily (every N days)
   - Weekly (specific days of week)
   - Monthly (specific day of month)
   - Yearly (specific date)
4. Set end date or "Repeat indefinitely"

**Behavior:** New task instance is created automatically when previous instance is completed or due date passes

---

## Collaboration Features

### Comments & Mentions

**Adding Comments:**
- Open task and scroll to comments section
- Type message (supports markdown formatting)
- Mention teammates with `@username`
- Mention specific teams with `@team-name`

**Notifications:** Mentioned users receive email and in-app notification

### File Attachments

**Supported File Types:**
- Documents: PDF, DOC, DOCX, TXT, MD
- Spreadsheets: XLS, XLSX, CSV
- Presentations: PPT, PPTX
- Images: JPG, PNG, GIF, SVG
- Videos: MP4, MOV (preview not available)
- Archives: ZIP, TAR, GZ

**File Size Limits:**
- **Starter:** 25MB per file
- **Professional:** 100MB per file
- **Enterprise:** 500MB per file

**Storage Limits:**
- **Starter:** 5GB total
- **Professional:** 100GB total
- **Enterprise:** 1TB total (can be increased)

### Real-Time Collaboration

**Features:**
- See who's viewing a task (avatars in top-right)
- See typing indicators in comments
- Live updates when others make changes
- Conflict resolution for simultaneous edits

### Activity Feed

**Location:** Right sidebar in project view

**Displays:**
- Task creations and completions
- Status changes
- Comments
- File uploads
- Team member additions
- Due date changes

**Filtering:** Filter by team member or activity type

---

## Integrations

### Available Integrations

#### Slack Integration

**Setup:**
1. Go to Settings → Integrations
2. Click "Connect Slack"
3. Authorize CloudFlow to access your Slack workspace
4. Choose notification settings

**Features:**
- Receive task notifications in Slack channels
- Create tasks from Slack with `/cloudflow create-task`
- Link tasks to Slack threads
- Get daily digest of due tasks

**Channels:** Can configure notifications per project to specific Slack channels

#### GitHub Integration

**Available for:** Professional and Enterprise tiers

**Setup:**
1. Go to Settings → Integrations
2. Click "Connect GitHub"
3. Authorize OAuth access
4. Select repositories to sync

**Features:**
- Link pull requests to tasks
- Auto-complete tasks when PR is merged
- Show commit history in task details
- Create tasks from GitHub issues

**Branch Naming:** Link automatically by including task ID in branch name: `feature/TASK-123-new-feature`

#### Jira Integration

**Available for:** Enterprise tier only

**Setup:**
1. Contact support@techcorp.com to enable
2. Provide Jira instance URL and credentials
3. Configure field mapping
4. Choose sync direction (one-way or two-way)

**Features:**
- Sync issues between Jira and CloudFlow
- Maintain status synchronization
- Link comments across systems
- Import historical issues

#### Google Workspace Integration

**Available for:** All tiers

**Setup:**
1. Go to Settings → Integrations
2. Click "Connect Google Workspace"
3. Sign in with Google account

**Features:**
- Attach files from Google Drive
- Create tasks from Gmail emails
- Sync with Google Calendar (Professional+)
- SSO with Google accounts (Enterprise)

**Calendar Sync:** Task due dates appear as calendar events

#### Zapier Integration

**Available for:** Professional and Enterprise tiers

**Setup:**
1. Sign up for Zapier (separate account)
2. Search for "CloudFlow" in Zapier
3. Create Zaps to connect 5,000+ apps

**Common Zaps:**
- Create task from Typeform submission
- Add task to Google Sheets
- Send SMS when task is completed (via Twilio)
- Create invoice in QuickBooks when project completes

#### API Access

**Available for:** Professional and Enterprise tiers

**API Documentation:** https://api.techcorp-cloudflow.com/docs

**Authentication:** Bearer token (generate in Settings → API)

**Rate Limits:**
- **Professional:** 1,000 requests/hour
- **Enterprise:** 10,000 requests/hour

**Common Endpoints:**
- `GET /projects` - List all projects
- `POST /tasks` - Create a task
- `GET /tasks/:id` - Get task details
- `PATCH /tasks/:id` - Update task
- `DELETE /tasks/:id` - Delete task
- `POST /comments` - Add comment

**Webhooks:** Configure webhooks to receive real-time notifications of events (Enterprise only)

---

## Time Tracking & Reporting

### Time Tracking

**Available for:** Professional and Enterprise tiers

**Tracking Methods:**

**1. Manual Entry:**
- Open task
- Click "Log Time"
- Enter hours and minutes
- Add optional note
- Save entry

**2. Timer:**
- Click timer icon on task
- Clock starts running
- Click stop when done
- Review and save time entry

**Time Entry Rules:**
- Can log time in 15-minute increments
- Can edit or delete own time entries
- Can backdate time entries up to 30 days
- Admins can see all time entries

### Reports

**Available Reports:**

**1. Team Performance Report**
- Tasks completed per team member
- Average completion time
- Task velocity trend
- Workload distribution

**2. Project Status Report**
- Tasks by status (To Do, In Progress, Done)
- Overdue tasks
- Upcoming due dates
- Completion percentage

**3. Time Report** (Professional+)
- Time logged per project
- Time logged per team member
- Billable vs. non-billable hours
- Time breakdown by task type

**4. Custom Reports** (Enterprise)
- Build reports with custom fields
- Schedule automated email delivery
- Export to PDF, Excel, or CSV

**Export Options:**
- PDF (formatted report)
- Excel/CSV (raw data)
- Google Sheets (live sync for Professional+)

---

## Mobile Apps

### iOS App

**Requirements:** iOS 14.0 or later
**Download:** App Store (search "CloudFlow")

**Features:**
- View and create tasks
- Add comments and attachments
- Receive push notifications
- Offline mode (syncs when reconnected)
- Face ID / Touch ID support

### Android App

**Requirements:** Android 8.0 or later
**Download:** Google Play Store (search "CloudFlow")

**Features:**
- View and create tasks
- Add comments and attachments
- Receive push notifications
- Offline mode (syncs when reconnected)
- Fingerprint authentication support

### Mobile Limitations

**Not Available on Mobile:**
- Timeline/Gantt view
- Bulk editing tasks
- Custom field creation
- Integration setup
- Billing management

**Workaround:** Use web browser on mobile device for full functionality

---

## Billing & Subscription Management

### Viewing Current Plan

1. Go to Settings → Billing
2. See current plan, billing cycle, and next payment date
3. View usage metrics (users, storage, API calls)

### Upgrading Plan

**From Starter to Professional:**
1. Go to Settings → Billing
2. Click "Upgrade to Professional"
3. Enter payment information (credit card or PayPal)
4. Confirm upgrade
5. Changes take effect immediately

**To Enterprise:**
- Contact sales@techcorp.com for custom pricing
- Minimum 50 users
- Annual contract required

### Downgrading Plan

**From Professional to Starter:**
1. Go to Settings → Billing
2. Click "Downgrade to Starter"
3. Review features you'll lose (list shown)
4. Confirm downgrade
5. Change takes effect at end of current billing cycle

**Data Retention:**
- All data is preserved during downgrade
- Features locked behind Professional tier become unavailable
- Can re-upgrade anytime to regain access

### Adding/Removing Users

**Adding Users:**
- Go to Settings → Team
- Click "Invite Member"
- Enter email address
- Choose role (Admin, Member, Guest)
- Send invitation

**Billing Impact:**
- Charged pro-rated amount for remainder of billing cycle
- Full price charged starting next cycle

**Removing Users:**
- Go to Settings → Team
- Click "..." next to user
- Select "Remove from Team"
- Confirm removal

**Billing Impact:**
- Credit applied to next invoice (pro-rated refund)
- Must keep at least 1 admin user

### Payment Methods

**Accepted:**
- Credit cards (Visa, Mastercard, Amex, Discover)
- Debit cards
- PayPal

**Not Accepted:**
- Purchase orders (Enterprise only)
- Wire transfer (Enterprise only)
- Cryptocurrency

### Billing Cycle

**Monthly:** Charged on the same day each month
**Annual:** Charged once per year (15% discount compared to monthly)

**Changing Billing Cycle:**
- Can switch from monthly to annual anytime (immediate charge)
- Cannot switch from annual to monthly mid-contract

### Invoices

**Accessing Invoices:**
1. Go to Settings → Billing → Invoice History
2. Click invoice to view or download PDF
3. Email invoices to accounting@yourcompany.com

**Invoice Details:**
- Invoice number
- Billing period
- Itemized charges (users, add-ons, storage overages)
- Payment method
- Transaction ID

### Refund Policy

**Trial Period:** No charges during trial, can cancel anytime

**Monthly Subscriptions:**
- No refunds for partial months
- Can cancel anytime, no further charges
- Access continues until end of paid period

**Annual Subscriptions:**
- Refund available within 30 days of initial purchase
- No refunds after 30 days
- Pro-rated refund for cancellations (at discretion)

**Refund Process:**
1. Email support@techcorp.com with "Refund Request" subject
2. Provide account email and reason
3. Processed within 5-7 business days
4. Refunded to original payment method

---

## Security & Compliance

### Data Security

**Encryption:**
- Data in transit: TLS 1.3
- Data at rest: AES-256 encryption
- Database backups: Encrypted and stored in geographically distributed locations

**Backups:**
- Automated daily backups
- Retained for 30 days (Professional), 90 days (Enterprise)
- Can request point-in-time recovery (Enterprise only)

### Access Control

**Permissions Levels:**
- **Workspace Admin:** Full control over workspace, projects, and team
- **Project Admin:** Manage specific projects and tasks
- **Member:** Create and complete tasks, comment
- **Guest:** View-only access to specific projects

**IP Allowlisting:** Enterprise tier can restrict access to specific IP ranges

### Compliance Certifications

**Current Certifications:**
- SOC 2 Type II
- GDPR compliant
- CCPA compliant
- ISO 27001 (in progress, expected Q3 2026)

**Data Location:** US-based servers (AWS us-east-1 and us-west-2)
**EU Data Residency:** Available for Enterprise customers (contact sales)

### GDPR & Data Rights

**Right to Access:**
- Request data export from Settings → Privacy
- Receives zip file with all personal data in JSON format
- Delivered within 30 days

**Right to Deletion:**
- Request account deletion from Settings → Privacy → Delete Account
- All personal data deleted within 30 days
- Some data retained for legal compliance (billing records, 7 years)

**Data Processing Agreement (DPA):**
- Available for Enterprise customers
- Contact support@techcorp.com to request signed DPA

---

## Troubleshooting

### Login Issues

**"Email or password incorrect":**
- Verify email address (case-sensitive)
- Use "Forgot Password" to reset
- Check if account was created with SSO instead

**"Account locked":**
- Too many failed login attempts (5 in 10 minutes)
- Wait 30 minutes and try again
- Or use "Forgot Password" to reset

**SSO not working:**
- Verify SSO is enabled for your organization
- Contact your IT admin to check user provisioning
- Try logging out of Google/Microsoft and back in

### Tasks Not Saving

**Possible Causes:**
- Network connectivity issue - check internet connection
- Session expired - refresh page and log back in
- Browser cache issue - clear cache or try incognito mode
- File attachment too large - check file size limits

**Solution:**
1. Copy your task description (Ctrl+C)
2. Refresh the page
3. Try creating task again
4. If persists, contact support with error message

### Notifications Not Received

**Check notification settings:**
1. Settings → Notifications
2. Verify email address is correct
3. Check that notification type is enabled
4. Check spam/junk folder

**Check email deliverability:**
- Add notifications@techcorp-cloudflow.com to contacts
- Check if emails are being blocked by IT admin
- Try adding a secondary email address

### Slow Performance

**Browser-related:**
- Close unused tabs (CloudFlow works best with <20 tabs open)
- Update browser to latest version
- Clear browser cache
- Disable unnecessary browser extensions
- Try different browser (Chrome recommended)

**Project-related:**
- Large projects (500+ tasks) may load slowly
- Archive completed tasks to improve performance
- Split large projects into smaller projects
- Use filters to view subset of tasks

**Internet-related:**
- Check internet speed (minimum 5 Mbps recommended)
- CloudFlow servers may be under maintenance (check status.techcorp-cloudflow.com)

### Integration Issues

**Slack notifications not working:**
- Re-authorize Slack integration
- Check that CloudFlow bot is invited to the channel
- Verify notification settings in CloudFlow

**GitHub not syncing:**
- Check that repositories are still accessible
- Re-authorize OAuth token
- Verify branch naming includes task ID

**Google Calendar not syncing:**
- Re-connect Google account
- Check calendar permissions
- Ensure Professional plan is active (required for calendar sync)

### Mobile App Issues

**App crashing:**
- Update app to latest version
- Restart phone
- Clear app cache (Settings → Apps → CloudFlow → Clear Cache)
- Uninstall and reinstall app (data is safe in cloud)

**Push notifications not working:**
- Check phone notification settings
- Ensure CloudFlow has notification permission
- Check "Do Not Disturb" mode
- Log out and back in to reset connection

### Data Export

**How to export all data:**
1. Go to Settings → Privacy → Export Data
2. Click "Request Export"
3. Receive email when export is ready (usually within 24 hours)
4. Download zip file (link expires in 7 days)

**Export format:** JSON files for all projects, tasks, comments, time entries

---

## Getting Help

### Self-Service Resources

- **Knowledge Base:** https://docs.techcorp-cloudflow.com
- **Video Tutorials:** https://www.youtube.com/techcorp-cloudflow
- **Community Forum:** https://community.techcorp-cloudflow.com
- **Status Page:** https://status.techcorp-cloudflow.com

### Contact Support

**Email Support:**
- **Address:** support@techcorp.com
- **Response Time:**
  - Starter: Within 24 hours
  - Professional: Within 12 hours
  - Enterprise: Within 4 hours (SLA)

**What to Include:**
- Your account email
- Description of issue
- Steps to reproduce
- Screenshots (if applicable)
- Browser and OS version

**Live Chat:** Professional and Enterprise customers only (9 AM - 6 PM CST, Mon-Fri)

**Phone Support:** Enterprise customers only - call number provided in welcome email

---

*For the latest updates, visit https://docs.techcorp-cloudflow.com*
