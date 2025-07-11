import subprocess
import os
import tempfile
import json
import shutil
from datetime import datetime
from flask import current_app
from typing import Dict, List, Tuple, Optional
import configparser
from pathlib import Path


class CloudBackupService:
    """Service for managing cloud backups using rclone"""
    
    def __init__(self):
        self.rclone_config_path = current_app.config.get('RCLONE_CONFIG_PATH')
        self.default_remote = current_app.config.get('RCLONE_DEFAULT_REMOTE')
        self.backup_path = current_app.config.get('RCLONE_BACKUP_PATH', 'job-tracker-backups')
        self.rclone_executable = self._find_rclone_executable()
        
    def _find_rclone_executable(self) -> str:
        """Find rclone executable with Windows compatibility"""
        # Try different possible names/locations
        possible_names = ['rclone', 'rclone.exe']
        
        # First, try to find it using shutil.which (most reliable)
        for name in possible_names:
            executable = shutil.which(name)
            if executable:
                return executable
        
        # If not found with shutil.which, try common Windows locations
        common_paths = [
            r"C:\Program Files\rclone\rclone.exe",
            r"C:\Program Files (x86)\rclone\rclone.exe", 
            r"C:\rclone\rclone.exe",
            r"C:\tools\rclone\rclone.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # Check if RCLONE_PATH is set in environment variables
        rclone_path = os.environ.get('RCLONE_PATH')
        if rclone_path and os.path.exists(rclone_path):
            return rclone_path
        
        # Fallback to just 'rclone' and let it fail with a better error message
        print("rclone not found in common locations, falling back to 'rclone'")
        return 'rclone'
    
    def get_rclone_config_path(self) -> str:
        """Get the path to the rclone config file"""
        if self.rclone_config_path and os.path.exists(self.rclone_config_path):
            return self.rclone_config_path
        
        # Try to detect the default rclone config path
        import platform
        
        if platform.system() == 'Windows':
            # Windows default path
            config_path = os.path.expandvars(r'%APPDATA%\rclone\rclone.conf')
        else:
            # Unix-like systems (Linux, macOS)
            # Check if we're running as a specific user in Docker
            home_dir = os.path.expanduser('~')
            if home_dir == '/home/appuser':
                # Docker container with appuser
                config_path = '/home/appuser/.config/rclone/rclone.conf'
            else:
                # Standard Unix path
                config_path = os.path.join(home_dir, '.config', 'rclone', 'rclone.conf')
        
        return config_path
    
    def get_rclone_config_info(self) -> Dict:
        """Get information about the rclone config file"""
        config_path = self.get_rclone_config_path()
        
        info = {
            'path': config_path,
            'exists': os.path.exists(config_path),
            'readable': False,
            'writable': False,
            'size': 0,
            'remotes_count': 0,
            'can_create': False
        }
        
        if info['exists']:
            try:
                info['readable'] = os.access(config_path, os.R_OK)
                info['writable'] = os.access(config_path, os.W_OK)
                info['size'] = os.path.getsize(config_path)
                
                # Count remotes in config
                if info['readable']:
                    config = configparser.ConfigParser()
                    config.read(config_path)
                    info['remotes_count'] = len(config.sections())
                    
            except Exception as e:
                print(f"Error checking config file: {e}")
        else:
            # Check if we can create the file
            config_dir = os.path.dirname(config_path)
            try:
                # Check if directory exists or can be created
                if os.path.exists(config_dir):
                    info['can_create'] = os.access(config_dir, os.W_OK)
                else:
                    # Check if parent directory exists and is writable
                    parent_dir = os.path.dirname(config_dir)
                    info['can_create'] = os.path.exists(parent_dir) and os.access(parent_dir, os.W_OK)
            except Exception as e:
                print(f"Error checking if config can be created: {e}")
                info['can_create'] = False
        
        return info
    
    def validate_config_section(self, config_text: str) -> Tuple[bool, str, Dict]:
        """Validate a pasted rclone config section"""
        if not config_text.strip():
            return False, "Config text is empty", {}
        
        try:
            # Parse the config section
            config = configparser.ConfigParser()
            config.read_string(config_text)
            
            sections = config.sections()
            if not sections:
                return False, "No valid config sections found", {}
            
            if len(sections) > 1:
                return False, "Multiple sections found. Please paste one remote configuration at a time.", {}
            
            section_name = sections[0]
            section_data = dict(config.items(section_name))
            
            # Basic validation
            if 'type' not in section_data:
                return False, f"Missing 'type' field in [{section_name}] section", {}
            
            provider_type = section_data['type']
            
            return True, f"Valid {provider_type} configuration for remote '{section_name}'", {
                'name': section_name,
                'type': provider_type,
                'data': section_data
            }
            
        except Exception as e:
            return False, f"Invalid config format: {str(e)}", {}
    
    def create_config_file(self) -> Tuple[bool, str]:
        """Create an empty rclone config file"""
        config_path = self.get_rclone_config_path()
        
        try:
            # Ensure the config directory exists
            config_dir = os.path.dirname(config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            # Create empty config file with proper permissions
            with open(config_path, 'w') as config_file:
                config_file.write("# rclone configuration file\n")
                config_file.write("# Created by Job Tracker application\n")
                config_file.write("# Add your cloud storage configurations below\n\n")
            
            # Set appropriate permissions (readable/writable by owner only)
            os.chmod(config_path, 0o600)
            
            return True, f"Config file created successfully at {config_path}"
            
        except Exception as e:
            return False, f"Failed to create config file: {str(e)}"
    
    def append_config_section(self, config_text: str) -> Tuple[bool, str]:
        """Append a config section to the rclone config file"""
        # Validate the config first
        is_valid, message, config_info = self.validate_config_section(config_text)
        if not is_valid:
            return False, message
        
        config_path = self.get_rclone_config_path()
        remote_name = config_info['name']
        
        try:
            # Ensure the config directory exists
            config_dir = os.path.dirname(config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            # Create config file if it doesn't exist
            if not os.path.exists(config_path):
                success, create_message = self.create_config_file()
                if not success:
                    return False, f"Could not create config file: {create_message}"
            
            # Read existing config if it exists
            existing_config = configparser.ConfigParser()
            if os.path.exists(config_path):
                existing_config.read(config_path)
            
            # Check if remote already exists
            if remote_name in existing_config.sections():
                return False, f"Remote '{remote_name}' already exists in config. Please remove it first or use a different name."
            
            # Parse the new config section
            new_config = configparser.ConfigParser()
            new_config.read_string(config_text)
            
            # Add the new section to existing config
            for section_name in new_config.sections():
                existing_config.add_section(section_name)
                for key, value in new_config.items(section_name):
                    existing_config.set(section_name, key, value)
            
            # Write the updated config back to file
            with open(config_path, 'w') as config_file:
                existing_config.write(config_file)
            
            # Set appropriate permissions
            os.chmod(config_path, 0o600)
            
            return True, f"Successfully added remote '{remote_name}' to rclone config"
            
        except Exception as e:
            return False, f"Error writing config: {str(e)}"
    
    def remove_remote_from_config(self, remote_name: str) -> Tuple[bool, str]:
        """Remove a remote from the rclone config file"""
        config_path = self.get_rclone_config_path()
        
        if not os.path.exists(config_path):
            return False, "Config file does not exist"
        
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if remote_name not in config.sections():
                return False, f"Remote '{remote_name}' not found in config"
            
            # Remove the section
            config.remove_section(remote_name)
            
            # Write the updated config back
            with open(config_path, 'w') as config_file:
                config.write(config_file)
            
            return True, f"Successfully removed remote '{remote_name}' from config"
            
        except Exception as e:
            return False, f"Error removing remote: {str(e)}"
    
    def get_config_content(self) -> Tuple[bool, str]:
        """Get the current rclone config file content"""
        config_path = self.get_rclone_config_path()
        
        if not os.path.exists(config_path):
            return False, "Config file does not exist"
        
        try:
            with open(config_path, 'r') as config_file:
                content = config_file.read()
            return True, content
        except Exception as e:
            return False, f"Error reading config: {str(e)}"
    
    def check_rclone_available(self) -> bool:
        """Check if rclone is available in the system"""
        try:
            # Use shell=True on Windows to help with PATH resolution
            import platform
            use_shell = platform.system() == 'Windows'
            
            result = subprocess.run(
                [self.rclone_executable, 'version'], 
                capture_output=True, 
                text=True, 
                timeout=10,
                shell=use_shell
            )
            if result.stderr:
                print(f"stderr: {result.stderr}")
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            print(f"rclone is not available or not found: {e}")
            print(f"Exception type: {type(e)}")
            
            # Additional debugging for Windows
            if platform.system() == 'Windows':
                # Try with .exe extension explicitly
                try:
                    result = subprocess.run(
                        ['rclone.exe', 'version'], 
                        capture_output=True, 
                        text=True, 
                        timeout=10,
                        shell=True
                    )
                    if result.returncode == 0:
                        print("rclone.exe works with shell=True")
                        self.rclone_executable = 'rclone.exe'
                        return True
                except Exception as e2:
                    print(f"rclone.exe also failed: {e2}")
            
            return False
    
    def _run_rclone_command(self, cmd_args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """Run rclone command with Windows compatibility"""
        import platform
        
        # Prepare command
        cmd = [self.rclone_executable] + cmd_args
        
        # Add config path if specified
        if self.rclone_config_path:
            cmd.extend(['--config', self.rclone_config_path])
        
        # Use shell=True on Windows for better compatibility
        use_shell = platform.system() == 'Windows'
        
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            shell=use_shell
        )
    
    def list_configured_remotes(self) -> List[Dict[str, str]]:
        """List all configured rclone remotes"""
        if not self.check_rclone_available():
            return []
        
        try:
            result = self._run_rclone_command(['listremotes'])
            if result.returncode == 0:
                remotes = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip() and line.endswith(':'):
                        remote_name = line.rstrip(':')
                        remote_info = self._get_remote_info(remote_name)
                        remotes.append({
                            'name': remote_name,
                            'type': remote_info.get('type', 'unknown'),
                            'description': f"{remote_name} ({remote_info.get('type', 'unknown')})"
                        })
                return remotes
            else:
                print(f"listremotes failed: {result.stderr}")
                return []
        except Exception as e:
            current_app.logger.error(f"Error listing rclone remotes: {str(e)}")
            return []
    
    def _get_remote_info(self, remote_name: str) -> Dict[str, str]:
        """Get information about a specific remote"""
        try:
            result = self._run_rclone_command(['config', 'show', remote_name], timeout=10)
            
            if result.returncode == 0:
                # Parse the config output to extract type
                for line in result.stdout.split('\n'):
                    if line.strip().startswith('type ='):
                        return {'type': line.split('=')[1].strip()}
            return {}
        except Exception:
            return {}
    
    def test_remote_connection(self, remote_name: str) -> Tuple[bool, str]:
        """Test connection to a specific remote"""
        if not self.check_rclone_available():
            return False, "rclone is not available"
        
        try:
            result = self._run_rclone_command([
                'lsd', f'{remote_name}:', '--max-depth', '1'
            ], timeout=30)
            
            if result.returncode == 0:
                return True, "Connection successful"
            else:
                return False, f"Connection failed: {result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Error testing connection: {str(e)}"
    
    # ... (rest of the existing methods remain the same)
    def upload_backup(self, backup_file_path: str, remote_name: str, 
                     custom_path: Optional[str] = None) -> Tuple[bool, str, Dict]:
        """Upload backup file to cloud storage"""
        if not self.check_rclone_available():
            return False, "rclone is not available", {}
        
        if not os.path.exists(backup_file_path):
            return False, "Backup file not found", {}
        
        # Generate remote path
        timestamp = datetime.now().strftime('%Y/%m/%d')
        filename = os.path.basename(backup_file_path)
        
        if custom_path:
            remote_path = f"{remote_name}:{custom_path}/{filename}"
        else:
            remote_path = f"{remote_name}:{self.backup_path}/{timestamp}/{filename}"
        
        try:
            # Upload with progress
            result = self._run_rclone_command([
                'copy', backup_file_path, 
                os.path.dirname(remote_path),
                '--progress',
                '--stats-one-line',
                '--stats', '1s'
            ], timeout=300)
            
            if result.returncode == 0:
                # Get file info after upload
                file_info = self._get_remote_file_info(remote_path)
                return True, f"Backup uploaded successfully to {remote_path}", file_info
            else:
                error_msg = result.stderr.strip() or "Upload failed"
                return False, error_msg, {}
                
        except subprocess.TimeoutExpired:
            return False, "Upload timeout (5 minutes)", {}
        except Exception as e:
            return False, f"Upload error: {str(e)}", {}
    
    def _get_remote_file_info(self, remote_path: str) -> Dict:
        """Get information about uploaded file"""
        try:
            # Use rclone lsjson to get file details
            remote_dir = os.path.dirname(remote_path)
            filename = os.path.basename(remote_path)
            
            result = self._run_rclone_command(['lsjson', remote_dir], timeout=30)
            
            if result.returncode == 0:
                files = json.loads(result.stdout)
                for file_info in files:
                    if file_info.get('Name') == filename:
                        return {
                            'size': file_info.get('Size', 0),
                            'modified': file_info.get('ModTime', ''),
                            'path': remote_path
                        }
            return {}
        except Exception:
            return {}
    
    def list_cloud_backups(self, remote_name: str, 
                      custom_path: Optional[str] = None) -> List[Dict]:
        """List backups stored in cloud with improved path handling"""
        if not self.check_rclone_available():
            return []
        
        try:
            search_path = f"{remote_name}:{custom_path or self.backup_path}"
            backup_base_path = custom_path or self.backup_path
            
            result = self._run_rclone_command(['lsjson', search_path, '--recursive'], timeout=60)
            
            if result.returncode == 0:
                try:
                    files = json.loads(result.stdout)
                    backups = []
                    
                    for file_info in files:
                        filename = file_info.get('Name', '')
                        relative_path = file_info.get('Path', '')
                        
                        # Skip directories
                        if file_info.get('IsDir', False):
                            continue
                        
                        # More flexible matching for backup files
                        is_zip = filename.endswith('.zip')
                        
                        # Check multiple patterns to identify backup files
                        is_backup = any([
                            'job_tracker_backup_' in filename,  # Standard pattern
                            filename.startswith('job_tracker_'),  # Alternative pattern
                            self._is_likely_backup_file(file_info, filename),  # Heuristic check
                        ])
                        
                        if is_zip and is_backup:
                            # Create full path for deletion
                            full_path = f"{backup_base_path}/{relative_path}" if relative_path else f"{backup_base_path}/{filename}"
                            
                            backups.append({
                                'name': filename,
                                'path': full_path,  # Store full path including backup base
                                'relative_path': relative_path,  # Store relative path for reference
                                'size': file_info.get('Size', 0),
                                'size_mb': round(file_info.get('Size', 0) / (1024 * 1024), 2),
                                'modified': file_info.get('ModTime', ''),
                                'remote': remote_name,
                                'detection_method': self._get_detection_method(filename)
                            })
                    
                    # Sort by modification time (newest first)
                    backups.sort(key=lambda x: x['modified'], reverse=True)
                    return backups
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    return []
            else:
                print(f"rclone command failed with return code {result.returncode}")
                print(f"Error output: {result.stderr}")
                return []
        except Exception as e:
            print(f"Exception in list_cloud_backups: {e}")
            current_app.logger.error(f"Error listing cloud backups: {str(e)}")
            return []
    
    def _is_likely_backup_file(self, file_info: Dict, filename: str) -> bool:
        """Use heuristics to identify backup files"""
        # Check if it contains manifest.json (for existing backups)
        # This would require downloading and checking, so let's use other heuristics
        
        # Size-based heuristic: backup files are usually larger than 1KB
        size = file_info.get('Size', 0)
        if size < 1024:  # Less than 1KB, probably not a backup
            return False
        
        # Path-based heuristic: in a date-structured folder
        path = file_info.get('Path', '')
        date_pattern_in_path = any([
            '/2024/' in path or '/2025/' in path,  # Year in path
            path.count('/') >= 2,  # Deep path structure (year/month/day)
        ])
        
        # Filename-based heuristic: looks like a backup
        filename_hints = any([
            'backup' in filename.lower(),
            'job' in filename.lower(),
            'tracker' in filename.lower(),
            len(filename) > 10,  # Reasonably long filename
        ])
        
        # Consider it a backup if it meets size + (date pattern OR filename hints)
        is_likely = size >= 1024 and (date_pattern_in_path or filename_hints)
        
        return is_likely

    def _get_detection_method(self, filename: str) -> str:
        """Return how the backup was detected"""
        if 'job_tracker_backup_' in filename:
            return 'standard_pattern'
        elif filename.startswith('job_tracker_'):
            return 'alternative_pattern'
        else:
            return 'heuristic_detection'

    def download_backup(self, remote_name: str, remote_file_path: str, 
                   local_download_path: str) -> Tuple[bool, str]:
        """Download backup from cloud storage"""
        if not self.check_rclone_available():
            return False, "rclone is not available"
        
        try:
            # Use the full path as provided (now includes backup base path)
            remote_path = f"{remote_name}:{remote_file_path}"
            
            # Ensure local directory exists
            local_dir = os.path.dirname(local_download_path)
            os.makedirs(local_dir, exist_ok=True)
            
            # First, verify the file exists on remote
            verify_result = self._run_rclone_command(['lsjson', remote_path], timeout=30)
            
            if verify_result.returncode == 0:
                try:
                    remote_files = json.loads(verify_result.stdout)
                    if not remote_files:
                        return False, f"File not found at {remote_path}"
                except json.JSONDecodeError:
                    pass
            else:
                print(f"Failed to verify remote file: {verify_result.stderr}")
                return False, f"Could not verify remote file: {verify_result.stderr}"
            
            # Download the file
            result = self._run_rclone_command([
                'copy', remote_path, 
                local_dir,
                '--progress',
                '--stats', '1s',
                '--stats-one-line'
            ], timeout=300)
            
            if result.returncode == 0:
                # Verify the downloaded file
                if os.path.exists(local_download_path):
                    local_size = os.path.getsize(local_download_path)
                    
                    if local_size > 0:
                        return True, f"Backup downloaded successfully to {local_download_path}"
                    else:
                        print("Downloaded file is 0 bytes!")
                        return False, "Downloaded file is empty (0 bytes)"
                else:
                    # List what files were actually downloaded
                    if os.path.exists(local_dir):
                        downloaded_files = os.listdir(local_dir)
                        
                        # Maybe the filename is different, find any .zip files
                        zip_files = [f for f in downloaded_files if f.endswith('.zip')]
                        if zip_files:
                            actual_file = os.path.join(local_dir, zip_files[0])
                            actual_size = os.path.getsize(actual_file)
                            
                            # Rename to expected filename
                            os.rename(actual_file, local_download_path)
                            
                            if actual_size > 0:
                                return True, f"Backup downloaded successfully to {local_download_path}"
                            else:
                                return False, "Downloaded file is empty (0 bytes)"
                    
                    return False, "Downloaded file not found at expected location"
            else:
                error_msg = result.stderr.strip() or "Download failed"
                print(f"rclone copy failed: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            print("Download timeout (5 minutes)")
            return False, "Download timeout (5 minutes)"
        except Exception as e:
            print(f"Exception in download_backup: {e}")
            return False, f"Download error: {str(e)}"

    def delete_cloud_backup(self, remote_name: str, remote_file_path: str) -> Tuple[bool, str]:
        """Delete backup from cloud storage"""
        if not self.check_rclone_available():
            return False, "rclone is not available"
        
        try:
            # Check if the path already includes the backup folder
            if remote_file_path.startswith(self.backup_path):
                # Path already includes backup folder
                remote_path = f"{remote_name}:{remote_file_path}"
            else:
                # Path is relative, need to add backup folder
                remote_path = f"{remote_name}:{self.backup_path}/{remote_file_path}"
            
            result = self._run_rclone_command(['delete', remote_path], timeout=60)
            
            if result.returncode == 0:
                return True, "Backup deleted successfully"
            else:
                error_msg = result.stderr.strip() or "Delete failed"
                print(f"Delete failed with error: {error_msg}")
                return False, error_msg
            
        except Exception as e:
            print(f"Exception in delete_cloud_backup: {e}")
            return False, f"Delete error: {str(e)}"
    
    def get_storage_usage(self, remote_name: str) -> Dict:
        """Get storage usage information for the remote"""
        if not self.check_rclone_available():
            return {}
        
        try:
            result = self._run_rclone_command(['about', f'{remote_name}:'], timeout=30)
            
            if result.returncode == 0:
                # Parse the about output
                usage_info = {}
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        usage_info[key.strip()] = value.strip()
                return usage_info
            return {}
        except Exception:
            return {}