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

- Upload multiple file types (PDF, DOC, DOCX, TEX)
- Download files with organized naming convention
- Default resume functionality
- File replacement and deletion
- Secure file storage with unique naming

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

3. **Configure application settings**
   Edit `app/app_settings.json`:

   ```json
   {
     "app_folder": "/absolute/path/to/your/data/folder"
   }
   ```

   > **Important**: Use an absolute path for the app_folder

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

## Configuration

### Database

- Uses SQLite by default
- Database location: `{app_folder}/app.db`
- Automatic table creation and migrations

### File Storage

Files are organized in the following structure:

```
{app_folder}/
├── app.db
└── JobTrackerFiles/
    ├── Resumes/
    ├── Cover_Letters/
    └── Job_Descriptions/
```

### Settings

- **Local Timezone**: Configured in `app/__init__.py` (default: America/Chicago)
- **File Size Limit**: 16MB maximum
- **Supported File Types**: PDF, DOC, DOCX, TEX, TXT, PNG, JPG, JPEG, GIF, CSV, XLSX

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
├── app/
│   ├── __init__.py              # Application factory
│   ├── models.py                # SQLAlchemy models
│   ├── startup_tasks.py         # Database initialization
│   ├── app_settings.json        # Configuration file
│   ├── blueprints/              # Route modules
│   │   ├── main.py              # Main pages
│   │   ├── jobs.py              # Job CRUD operations
│   │   ├── job_activities.py    # Activity management
│   │   ├── job_notes.py         # Notes functionality
│   │   ├── files.py             # File operations
│   │   └── settings.py          # Application settings
│   ├── services/
│   │   └── api_service.py       # Internal API service
│   ├── static/                  # CSS, JavaScript, assets
│   └── templates/               # Jinja2 templates
├── migrations/                  # Database migrations
├── requirements.txt             # Python dependencies
├── run.py                      # Application entry point
└── README.md                   # This file
```

## Security Considerations

- File uploads use secure filename generation
- Unique UUID-based file naming prevents conflicts
- File type validation on upload
- SQL injection protection through SQLAlchemy ORM
- CSRF protection via Flask-WTF

## Troubleshooting

### Common Issues

1. **Database not found**

   - Ensure app_folder path exists and is writable
   - Run database migrations

2. **File upload failures**

   - Check file size (16MB limit)
   - Verify file type is supported
   - Ensure storage directory permissions

3. **Application won't start**
   - Verify app_settings.json has valid absolute path
   - Check all dependencies are installed
   - Ensure Python version compatibility

### Database Migration

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# View migration history
flask db history
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under [Custom Non-Commercial License / CC BY-NC 4.0] - see the [LICENSE](LICENSE) file for details.

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
