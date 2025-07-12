from flask import Blueprint, render_template, jsonify, request, send_file, flash, redirect, url_for, current_app, Response
from app import db
from app.services.cloud_backup_service import CloudBackupService
import os, io, zipfile, tempfile, sqlite3, shutil, subprocess
from datetime import datetime
from werkzeug.utils import secure_filename

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/', methods=['GET'])
def index():
    """Index route for backup blueprint"""
    return render_template('backup/backup.html')

@backup_bp.route('/export-stream', methods=['GET'])
def export_data_stream():
    """Export all data as a ZIP file using streaming"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'job_tracker_backup_{timestamp}.zip'
        
        def generate_zip():
            # Create an in-memory ZIP file
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add database backup
                db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                print(f"Backing up database from {db_path} to in-memory ZIP")

                # Create temporary database backup - FIX: Use delete=False and manual cleanup
                temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
                try:
                    # Close the file descriptor so SQLite can open it
                    os.close(temp_db_fd)
                    
                    print(f"Temporary database backup created at {temp_db_path}")
                    backup_database_sqlite(db_path, temp_db_path)
                    print("After backup_database_sqlite")
                    zipf.write(temp_db_path, 'app.db')
                    
                finally:
                    # Clean up the temporary file
                    try:
                        os.unlink(temp_db_path)
                    except:
                        pass
                
                print("Start of adding files to ZIP")
                # Add files
                file_storage_path = current_app.config['FILE_STORAGE_PATH']
                if os.path.exists(file_storage_path):
                    for root, dirs, files in os.walk(file_storage_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            print(f"Adding file {file_path} to ZIP")
                            # Create the archive path relative to JobTrackerFiles
                            arcname = os.path.join('JobTrackerFiles', os.path.relpath(file_path, file_storage_path))
                            zipf.write(file_path, arcname)
                
                print("After adding files to ZIP")
                # Add manifest
                manifest = create_manifest_data()
                zipf.writestr('manifest.json', manifest)
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
        
        # Generate the ZIP content
        zip_content = generate_zip()
        
        # Return as a streaming response
        return Response(
            io.BytesIO(zip_content),
            mimetype='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename={zip_filename}',
                'Content-Length': str(len(zip_content))
            }
        )
        
    except Exception as e:
        flash(f'Export failed: {str(e)}', 'danger')
        # return redirect(url_for('settings.index'))
        return render_template('backup/backup.html')

@backup_bp.route('/cloud', methods=['GET'])
def cloud_backup_page():
    """Cloud backup management page"""
    print("=== DEBUG: Cloud backup page accessed ===")
    
    cloud_service = CloudBackupService()
    
    # Check if rclone is available
    rclone_available = cloud_service.check_rclone_available()
    print(f"rclone available: {rclone_available}")
    
    # Get configured remotes
    remotes = cloud_service.list_configured_remotes() if rclone_available else []
    print(f"Found {len(remotes)} remotes: {[r['name'] for r in remotes]}")
    
    # Get cloud backups for each remote
    cloud_backups = {}
    if rclone_available:
        for remote in remotes:
            print(f"\n--- Checking backups for remote: {remote['name']} ---")
            try:
                backups = cloud_service.list_cloud_backups(remote['name'])
                cloud_backups[remote['name']] = backups
                print(f"Found {len(backups)} backups for {remote['name']}")
                
                # Debug: show backup details
                for backup in backups:
                    print(f"  - {backup['name']} ({backup['size_mb']} MB)")
                    
            except Exception as e:
                print(f"Error listing backups for {remote['name']}: {str(e)}")
                current_app.logger.error(f"Error listing backups for {remote['name']}: {str(e)}")
                cloud_backups[remote['name']] = []
    
    print(f"\nFinal cloud_backups dict: {list(cloud_backups.keys())}")
    for remote_name, backups in cloud_backups.items():
        print(f"  {remote_name}: {len(backups)} backups")
    
    return render_template('backup/cloud_backup.html',
                         rclone_available=rclone_available,
                         remotes=remotes,
                         cloud_backups=cloud_backups)

@backup_bp.route('/cloud/test-connection', methods=['POST'])
def test_cloud_connection():
    """Test connection to a cloud remote"""
    data = request.get_json()
    remote_name = data.get('remote_name')
    
    if not remote_name:
        return jsonify({'error': 'Remote name is required'}), 400
    
    cloud_service = CloudBackupService()
    success, message = cloud_service.test_remote_connection(remote_name)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400

@backup_bp.route('/cloud/upload', methods=['POST'])
def upload_to_cloud():
    """Upload backup to cloud storage"""
    data = request.get_json()
    remote_name = data.get('remote_name')
    custom_path = data.get('custom_path')
    create_new_backup = data.get('create_new_backup', True)
    
    if not remote_name:
        return jsonify({'error': 'Remote name is required'}), 400
    
    try:
        cloud_service = CloudBackupService()
        
        # Test connection first
        connection_ok, conn_message = cloud_service.test_remote_connection(remote_name)
        if not connection_ok:
            return jsonify({'error': f'Connection failed: {conn_message}'}), 400
        
        # Create backup file
        if create_new_backup:
            # Create a proper backup filename (not temporary)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'job_tracker_backup_{timestamp}.zip'
            
            # Create backup in a temporary location but with proper name
            temp_dir = tempfile.mkdtemp()
            temp_backup_path = os.path.join(temp_dir, backup_filename)
            
            try:
                print(f"Creating backup at: {temp_backup_path}")
                
                # Create backup using existing backup logic
                with zipfile.ZipFile(temp_backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add database backup
                    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                    
                    # Create temporary database backup
                    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
                    try:
                        os.close(temp_db_fd)
                        backup_database_sqlite(db_path, temp_db_path)
                        zipf.write(temp_db_path, 'app.db')
                    finally:
                        try:
                            os.unlink(temp_db_path)
                        except:
                            pass
                    
                    # Add files
                    file_storage_path = current_app.config['FILE_STORAGE_PATH']
                    if os.path.exists(file_storage_path):
                        for root, dirs, files in os.walk(file_storage_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join('JobTrackerFiles', os.path.relpath(file_path, file_storage_path))
                                zipf.write(file_path, arcname)
                    
                    # Add manifest
                    manifest = create_manifest_data()
                    zipf.writestr('manifest.json', manifest)
                
                print(f"Backup created successfully: {backup_filename}")
                print(f"File size: {os.path.getsize(temp_backup_path)} bytes")
                
                # Upload to cloud with the proper filename
                success, message, file_info = cloud_service.upload_backup(
                    temp_backup_path, remote_name, custom_path
                )
                
                if success:
                    print(f"Upload successful: {message}")
                else:
                    print(f"Upload failed: {message}")
                
                return jsonify({
                    'success': success,
                    'message': message,
                    'file_info': file_info,
                    'backup_filename': backup_filename  # Include the filename in response
                }), 200 if success else 500
                
            finally:
                # Clean up temporary directory and all files in it
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    print(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    print(f"Error cleaning up temp directory: {e}")
        else:
            return jsonify({'error': 'Existing backup upload not implemented yet'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Cloud upload error: {str(e)}")
        print(f"Exception in upload_to_cloud: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@backup_bp.route('/cloud/download', methods=['POST'])
def download_from_cloud():
    """Download backup from cloud storage"""
    data = request.get_json()
    remote_name = data.get('remote_name')
    remote_file_path = data.get('remote_file_path')
    
    if not remote_name or not remote_file_path:
        return jsonify({'error': 'Remote name and file path are required'}), 400
    
    try:
        cloud_service = CloudBackupService()
        
        # Create temporary download location
        filename = os.path.basename(remote_file_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            local_path = temp_file.name
        
        try:
            # Download file
            success, message = cloud_service.download_backup(
                remote_name, remote_file_path, local_path
            )
            
            if success:
                # Return file as download
                return send_file(
                    local_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/zip'
                )
            else:
                return jsonify({'error': message}), 500
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(local_path)
            except:
                pass
                
    except Exception as e:
        current_app.logger.error(f"Cloud download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@backup_bp.route('/cloud/delete', methods=['POST'])
def delete_cloud_backup():
    """Delete backup from cloud storage"""
    data = request.get_json()
    remote_name = data.get('remote_name')
    remote_file_path = data.get('remote_file_path')
    
    if not remote_name or not remote_file_path:
        return jsonify({'error': 'Remote name and file path are required'}), 400
    
    try:
        cloud_service = CloudBackupService()
        success, message = cloud_service.delete_cloud_backup(remote_name, remote_file_path)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 500
        
    except Exception as e:
        current_app.logger.error(f"Cloud delete error: {str(e)}")
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

@backup_bp.route('/cloud/list-remotes', methods=['GET'])
def list_cloud_remotes():
    """List configured rclone remotes"""
    try:
        cloud_service = CloudBackupService()
        remotes = cloud_service.list_configured_remotes()
        
        return jsonify({
            'success': True,
            'remotes': remotes,
            'rclone_available': cloud_service.check_rclone_available()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error listing remotes: {str(e)}")
        return jsonify({'error': f'Failed to list remotes: {str(e)}'}), 500

@backup_bp.route('/cloud/storage-usage/<remote_name>', methods=['GET'])
def get_storage_usage(remote_name):
    """Get storage usage for a remote"""
    try:
        cloud_service = CloudBackupService()
        usage_info = cloud_service.get_storage_usage(remote_name)
        
        return jsonify({
            'success': True,
            'usage': usage_info
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting storage usage: {str(e)}")
        return jsonify({'error': f'Failed to get storage usage: {str(e)}'}), 500

def create_manifest_data():
    """Create manifest data as a JSON string"""
    import json
    from app.models import Job, JobNotes, JobActivities
    
    manifest = {
        'backup_version': '1.0',
        'created_at': datetime.now().isoformat(),
        'database_file': 'app.db',
        'files_directory': 'JobTrackerFiles',
        'statistics': {
            'total_jobs': Job.query.count(),
            'total_notes': JobNotes.query.count(),
            'total_activities': JobActivities.query.count(),
        },
        'application_version': '1.0'
    }
    
    return json.dumps(manifest, indent=2)



@backup_bp.route('/import', methods=['POST'])
def import_data():
    """Import data from uploaded ZIP file - REPLACES all existing data"""
    if 'backup_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['backup_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.zip'):
        return jsonify({'error': 'File must be a ZIP archive'}), 400
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            zip_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(zip_path)
            
            # Extract ZIP
            extract_dir = os.path.join(temp_dir, 'extracted')
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Validate backup
            if not validate_backup(extract_dir):
                return jsonify({'error': 'Invalid backup file format'}), 400
            
            # Close all database connections before replacing database
            db.session.close()
            db.engine.dispose()
            
            # Replace database and files completely
            restore_database_sqlite(extract_dir)
            restore_files_from_backup(extract_dir)
            
        return jsonify({
            'success': True, 
            'message': 'Import completed successfully. All previous data has been replaced.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Import failed: {str(e)}'}), 500

@backup_bp.route('/export-db-only', methods=['GET'])
def export_database_only():
    """Export only the database file"""
    try:
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'job_tracker_db_{timestamp}.db'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            backup_database_sqlite(db_path, temp_file.name)
            
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=backup_filename,
                mimetype='application/octet-stream'
            )
            
    except Exception as e:
        return jsonify({'error': f'Database export failed: {str(e)}'}), 500

@backup_bp.route('/export-csv', methods=['GET'])
def export_csv():
    """Export jobs data to CSV"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Company', 'Title', 'Location', 'Remote Option', 
        'Salary Low', 'Salary High', 'Posting ID', 'Created Date',
        'Status', 'Description', 'Referrer', 'Company Website', 'Posting URL'
    ])
    
    # Write job data
    from app.models import Job
    jobs = Job.query.all()
    for job in jobs:
        writer.writerow([
            job.id, job.company, job.title, job.location, job.remote_option,
            job.salary_range_low, job.salary_range_high, job.posting_id,
            job.created_dt.strftime('%Y-%m-%d') if job.created_dt else '',
            job.posting_status, job.description, job.referrer,
            job.company_website, job.posting_url
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=job_tracker_jobs_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    )

def backup_database_sqlite(source_db_path, backup_db_path):
    """Use SQLite's native backup API with Windows compatibility"""
    import time
    
    # Method 1: Using sqlite3 Python module (Preferred)
    try:
        # Close any existing Flask-SQLAlchemy connections
        db.session.close()
        db.engine.dispose()
        
        # Small delay to ensure connections are closed on Windows
        time.sleep(0.1)
        
        # Connect to source database with a timeout
        source_conn = sqlite3.connect(source_db_path, timeout=30.0)
        print(f"Connected to source database at {source_db_path}")
        
        # Connect to backup database
        backup_conn = sqlite3.connect(backup_db_path)
        print(f"Connected to backup database at {backup_db_path}")
        
        # Perform backup using SQLite's backup API
        with source_conn:
            source_conn.backup(backup_conn)
        
        print("Database backup completed successfully using SQLite backup API")
        
        # Explicitly close connections
        backup_conn.close()
        source_conn.close()
        
        return True
        
    except Exception as e:
        # Method 2: Fallback to sqlite3 command line tool
        print(f"SQLite backup API failed: {str(e)}. Trying command line tool...")
        try:
            # Ensure any Python connections are closed
            db.session.close()
            db.engine.dispose()
            time.sleep(0.1)
            
            # Use sqlite3 command line tool with .backup command
            cmd = [
                'sqlite3', 
                source_db_path, 
                f'.backup "{backup_db_path}"'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
            return True
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as cmd_error:
            # Method 3: Simple file copy as last resort (with retry for Windows)
            print(f"Command line backup failed: {str(cmd_error)}. Falling back to file copy...")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Ensure connections are closed
                    db.session.close()
                    db.engine.dispose()
                    time.sleep(0.5)  # Longer delay for Windows
                    
                    shutil.copy2(source_db_path, backup_db_path)
                    return True
                except PermissionError as pe:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
                        continue
                    raise pe

def restore_database_sqlite(extract_dir):
    """Restore database using SQLite backup"""
    backup_db_path = os.path.join(extract_dir, 'app.db')
    current_db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    if not os.path.exists(backup_db_path):
        raise FileNotFoundError("Database backup file not found in archive")
    
    # Create backup of current database
    if os.path.exists(current_db_path):
        backup_current = f"{current_db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(current_db_path, backup_current)
    
    # Restore database
    try:
        # Method 1: Using sqlite3 backup API
        backup_conn = sqlite3.connect(backup_db_path)
        current_conn = sqlite3.connect(current_db_path)
        
        backup_conn.backup(current_conn)
        
        backup_conn.close()
        current_conn.close()
        
    except Exception as e:
        # Fallback: Simple file copy
        shutil.copy2(backup_db_path, current_db_path)

def restore_files_from_backup(extract_dir):
    """Restore files from backup - REPLACES all existing files"""
    source_files_dir = os.path.join(extract_dir, 'JobTrackerFiles')
    if os.path.exists(source_files_dir):
        dest_files_dir = current_app.config['FILE_STORAGE_PATH']
        
        # Create backup of current files before replacing
        if os.path.exists(dest_files_dir):
            backup_files_dir = f"{dest_files_dir}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"Creating backup of existing files at: {backup_files_dir}")
            shutil.move(dest_files_dir, backup_files_dir)
        
        # Replace with backup files
        shutil.copytree(source_files_dir, dest_files_dir)
        print(f"Files restored from backup to: {dest_files_dir}")
    else:
        print("No files directory found in backup - skipping file restoration")

def validate_backup(extract_dir):
    """Validate backup file structure"""
    required_files = ['app.db', 'manifest.json']
    
    for file in required_files:
        if not os.path.exists(os.path.join(extract_dir, file)):
            return False
    
    # Validate database file
    db_path = os.path.join(extract_dir, 'app.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if required tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['jobs', 'job_notes', 'job_activities', 'job_activity_types']
        for table in required_tables:
            if table not in tables:
                conn.close()
                return False
        
        conn.close()
        return True
        
    except sqlite3.Error:
        return False

@backup_bp.route('/vacuum-db', methods=['POST'])
def vacuum_database():
    """Optimize SQLite database using VACUUM"""
    try:
        # Close current connections
        db.session.close()
        
        # Get database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Connect directly to SQLite and run VACUUM
        conn = sqlite3.connect(db_path)
        conn.execute('VACUUM;')
        conn.close()
        
        return jsonify({'success': True, 'message': 'Database optimized successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Database optimization failed: {str(e)}'}), 500

@backup_bp.route('/db-info', methods=['GET'])
def database_info():
    """Get database information and statistics"""
    try:
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Get file size
        db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        # Get database statistics
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get page count and page size
        cursor.execute('PRAGMA page_count;')
        page_count = cursor.fetchone()[0]
        
        cursor.execute('PRAGMA page_size;')
        page_size = cursor.fetchone()[0]
        
        # Get table information
        cursor.execute("""
            SELECT name, 
                   (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=t.name) as table_count
            FROM sqlite_master t WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """)
        tables = cursor.fetchall()
        
        conn.close()
        
        from app.models import Job, JobNotes, JobActivities, JobActivityTypes, Settings
        
        stats = {
            'database_size_bytes': db_size,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'page_count': page_count,
            'page_size': page_size,
            'total_pages_size_mb': round((page_count * page_size) / (1024 * 1024), 2),
            'record_counts': {
                'jobs': Job.query.count(),
                'job_notes': JobNotes.query.count(),
                'job_activities': JobActivities.query.count(),
                'job_activity_types': JobActivityTypes.query.count(),
                'settings': Settings.query.count(),
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get database info: {str(e)}'}), 500