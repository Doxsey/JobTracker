# Job Tracker Application

A comprehensive Flask-based web application for tracking job applications, managing related files, and monitoring application progress through activities and notes.

## Features

### Core Functionality

- **Job Management**: Create, view, edit, and delete job applications
- **Activity Tracking**: Log various job-related activities (interviews, emails, applications, etc.)
- **Notes System**: Add detailed notes to job applications
- **File Management**: Upload and manage resumes, cover letters, and job descriptions
- **Status Tracking**: Monitor job posting status (Open/Closed)

### File Management

- Upload multiple file types (PDF, DOC, DOCX, TEX, TXT, PNG, JPG, JPEG, GIF, CSV, XLSX)
- Download files with organized naming convention
- Default resume functionality
- File replacement and deletion
- Secure file storage with unique naming

### Backup & Restore System

- **Complete Data Export**: Download full backup including database and all uploaded files
- **Data Import**: Restore from previously exported backup files
- **Database Maintenance**: Optimize SQLite database with VACUUM operations
- **CSV Export**: Export job data to CSV format for external analysis
- **Database-only Backup**: Export just the database file for quick backups

### Activity Types

The application comes pre-loaded with comprehensive activity types including:

- Application-related: Application Submitted, Updated, Withdrawn
- Communication: Received/Sent Emails, Phone Calls, Follow-ups
- Interviews: Various interview types and scheduling
- Company Actions: Application viewed, moved to next round, offers
- Other: Job saved, company research, networking contacts

### User Interface

- Dark theme with responsive Bootstrap design
- Expandable table rows for detailed information
- Modal dialogs for activity details
- Pagination for large datasets
- File upload/download integration
- Advanced search and filtering for activity types

## Installation

### Prerequisites

- Python 3.7+
- pip package manager

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd job-tracker
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   # Copy the example environment file
   cp .env.example .env
   ```

   Edit `.env` file with your actual values:

   ```bash
   # Generate a secure secret key (run this command to generate one):
   # python -c "import secrets; print(secrets.token_hex(32))"
   SECRET_KEY=your-generated-secret-key-here

   # Set your data folder path (use absolute path)
   APP_FOLDER=/absolute/path/to/your/data/folder

   # Optional: Set your timezone (defaults to America/Chicago)
   LOCAL_TIMEZONE=America/Chicago

   # Environment setting
   FLASK_ENV=development
   ```

   > **Important**:
   >
   > - Use an absolute path for APP_FOLDER
   > - Generate a secure SECRET_KEY using the command shown above
   > - Never commit your `.env` file to version control

4. **Initialize the database**

   ```bash
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

## Docker Deployment

### Production Deployment

1. **Create production environment file**

   ```bash
   cp .env.production.example .env.production
   # Edit with your production values
   ```

2. **Deploy using Docker Compose**
   ```bash
   # Using pre-built image from GitHub Container Registry
   ENV_FILE=.env.production docker-compose -f docker-compose.prod.yml up -d
   ```

### Development with Docker

```bash
# Copy local environment file
cp .env.example .env.local
# Edit with your local values

# Build and run
ENV_FILE=.env.local docker-compose up -d
```

## Configuration

### Environment Variables

The application uses environment variables for secure configuration:

- **SECRET_KEY**: Flask secret key for sessions and CSRF protection
- **APP_FOLDER**: Absolute path to data storage directory
- **LOCAL_TIMEZONE**: Your local timezone (default: America/Chicago)
- **FLASK_ENV**: Environment setting (development/production)

### Database

- Uses SQLite by default
- Database location: `{APP_FOLDER}/app.db`
- Automatic table creation and migrations
- Built-in database optimization tools

### File Storage

Files are organized in the following structure:

```
{APP_FOLDER}/
├── app.db
└── JobTrackerFiles/
    ├── Resumes/
    ├── Cover_Letters/
    └── Job_Descriptions/
```

### Application Settings

- **File Size Limit**: 16MB maximum
- **Supported File Types**: PDF, DOC, DOCX, TEX, TXT, PNG, JPG, JPEG, GIF, CSV, XLSX
- **Security**: Environment-based configuration with secure secret key management

## Usage

### Adding a Job Application

1. Navigate to "Add New Job"
2. Fill in required fields (Company, Title, Description, Location)
3. Optionally upload files (resume, cover letter, job description)
4. Use default resume or upload a specific one
5. Add referrer information if applicable

### Tracking Activities

1. From the main page, click "Add Activity" for any job
2. Select from predefined activity types or search
3. Fill in activity-specific information
4. Add date and brief description

### Managing Files

- **Upload**: Use the file upload sections when creating/editing jobs
- **Download**: Access files through the job view page or main table
- **Default Resume**: Set up in Settings for quick application creation
- **Replace/Delete**: Use the edit mode in job view

### Adding Notes

1. Click "Add Note" for any job application
2. Write detailed notes about the position or application process
3. Notes are automatically timestamped

### Backup & Restore

#### Creating Backups

1. Navigate to Settings → "Access Backup & Restore Page"
2. Click "Download Backup" for complete data export
3. For database-only backup, use "Export Jobs to CSV" or database export options

#### Restoring Data

1. Go to Backup & Restore page
2. Select your backup ZIP file
3. Click "Replace All Data with Backup"
4. **Warning**: This completely replaces all existing data

#### Database Maintenance

- Use "Optimize Database" to run SQLite VACUUM operation
- Export data to CSV for external analysis
- Monitor database size and performance through database info

## API Endpoints

The application provides several API endpoints for programmatic access:

### Job Management

- `POST /jobs/create` - Create new job (JSON or multipart)
- `GET /jobs/<id>/view` - View job details
- `POST /jobs/<id>/view` - Update job information

### Activities

- `POST /job_activities/api/create` - Add new activity

### Files

- `POST /files/upload` - Upload files
- `POST /files/delete` - Delete files
- `GET /files/<job_id>/<file_type>` - Download files

### Settings

- `POST /settings/api/update` - Update application settings
- `POST /settings/api/upload_default_resume` - Upload default resume

### Backup & Restore

- `GET /backup/export-stream` - Download complete backup
- `POST /backup/import` - Import backup data
- `GET /backup/export-csv` - Export jobs to CSV
- `POST /backup/vacuum-db` - Optimize database

## Database Schema

### Main Tables

- **jobs**: Core job application data
- **job_notes**: Text notes associated with jobs
- **job_activities**: Activity tracking with JSON data storage
- **job_activity_types**: Predefined activity categories
- **settings**: Application configuration

### Key Relationships

- Jobs have many notes and activities (one-to-many)
- Activities reference predefined activity types
- Cascade deletion ensures data integrity

## File Structure

```
job-tracker/
├── config.py                   # Application configuration
├── .env.example                # Environment variables template
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Development Docker setup
├── docker-compose.prod.yml     # Production Docker setup
├── app/
│   ├── __init__.py             # Application factory
│   ├── models.py               # SQLAlchemy models
│   ├── startup_tasks.py        # Database initialization
│   ├── blueprints/             # Route modules
│   │   ├── main.py             # Main pages
│   │   ├── jobs.py             # Job CRUD operations
│   │   ├── job_activities.py   # Activity management
│   │   ├── job_notes.py        # Notes functionality
│   │   ├── files.py            # File operations
│   │   ├── settings.py         # Application settings
│   │   └── backup.py           # Backup & restore functionality
│   ├── services/
│   │   └── api_service.py      # Internal API service
│   ├── static/                 # CSS, JavaScript, assets
│   └── templates/              # Jinja2 templates
├── migrations/                 # Database migrations
└── README.md                   # This file
```

## Security Considerations

- **Environment-based configuration** with secure secret key management
- **File uploads** use secure filename generation with UUID-based naming
- **File type validation** on upload prevents malicious files
- **SQL injection protection** through SQLAlchemy ORM
- **CSRF protection** via Flask-WTF
- **Secrets management** through environment variables (never committed to git)
- **Docker security** with non-root user and proper permissions

## Troubleshooting

### Common Issues

1. **Application won't start**

   - Verify `.env` file exists and has valid values
   - Ensure APP_FOLDER path exists and is writable
   - Check that SECRET_KEY is set
   - Verify all dependencies are installed

2. **Database not found**

   - Ensure APP_FOLDER path exists and is writable
   - Run database migrations: `flask db upgrade`

3. **File upload failures**

   - Check file size (16MB limit)
   - Verify file type is supported
   - Ensure storage directory permissions

4. **Secret key errors**

   - Generate a new SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Add it to your `.env` file
   - Never use the example/placeholder keys in production

5. **Backup/Restore issues**
   - Ensure sufficient disk space for backups
   - Check file permissions on backup files
   - Verify ZIP file integrity before restore

### Database Migration

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# View migration history
flask db history
```

### Environment Setup for Different Environments

```bash
# Development
FLASK_ENV=development

# Production
FLASK_ENV=production
SECRET_KEY=your-secure-production-key
```

## Roadmap

### Completed ✅

- [x] Basic job CRUD operations
- [x] File upload/download functionality
- [x] Activity tracking system
- [x] Responsive dark theme UI
- [x] Secure environment-based configuration
- [x] Database migrations support
- [x] Comprehensive backup and restore system
- [x] Docker deployment support
- [x] Database optimization tools
- [x] CSV export functionality

### In Progress 🚧

- [ ] Advanced search and filtering
- [ ] Email notifications

### Planned Features 📋

- [ ] Dashboard with analytics
- [ ] Calendar integration for interviews
- [ ] API documentation
- [ ] Automated testing suite
- [ ] Multi-user support
- [ ] Role-based access control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under Custom Non-Commercial License - see the [LICENSE](LICENSE) file for details.

### Commercial Use

This software is free for personal and educational use. Commercial use requires explicit permission.
For commercial licensing inquiries, please contact [doxsey.gh@tuss.mozmail.com].

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the application logs
3. Submit an issue with detailed information about the problem

---

**Note**: This application is designed for personal job tracking and should be deployed securely if used in a multi-user environment.
