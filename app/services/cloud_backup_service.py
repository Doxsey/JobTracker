import subprocess
import os
import tempfile
import json
import shutil
from datetime import datetime
from flask import current_app
from typing import Dict, List, Tuple, Optional


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
                print(f"Found rclone at: {executable}")
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
                print(f"Found rclone at: {path}")
                return path
        
        # Check if RCLONE_PATH is set in environment variables
        rclone_path = os.environ.get('RCLONE_PATH')
        if rclone_path and os.path.exists(rclone_path):
            print(f"Found rclone via RCLONE_PATH: {rclone_path}")
            return rclone_path
        
        # Fallback to just 'rclone' and let it fail with a better error message
        print("rclone not found in common locations, falling back to 'rclone'")
        return 'rclone'
    
    def check_rclone_available(self) -> bool:
        """Check if rclone is available in the system"""
        print("Checking if rclone is available...")
        print(f"Using rclone executable: {self.rclone_executable}")
        print(f"Current PATH: {os.environ.get('PATH', 'Not found')}")
        
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
            print(f"rclone version check result: returncode={result.returncode}")
            print(f"stdout: {result.stdout[:200]}...")  # First 200 chars
            if result.stderr:
                print(f"stderr: {result.stderr}")
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            print(f"rclone is not available or not found: {e}")
            print(f"Exception type: {type(e)}")
            
            # Additional debugging for Windows
            if platform.system() == 'Windows':
                print("Windows-specific debugging:")
                print(f"Trying to find rclone.exe specifically...")
                
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
        
        print(f"Running command: {' '.join(cmd)}")
        
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
            print(f"listremotes result: returncode={result.returncode}")
            print(f"stdout: {result.stdout[:200]}...")  # First 200
            
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
        """List backups stored in cloud"""
        if not self.check_rclone_available():
            return []
        
        try:
            search_path = f"{remote_name}:{custom_path or self.backup_path}"
            result = self._run_rclone_command(['lsjson', search_path, '--recursive'], timeout=60)
            
            if result.returncode == 0:
                files = json.loads(result.stdout)
                backups = []
                
                for file_info in files:
                    if (file_info.get('Name', '').endswith('.zip') and 
                        'job_tracker_backup_' in file_info.get('Name', '')):
                        backups.append({
                            'name': file_info.get('Name'),
                            'path': file_info.get('Path'),
                            'size': file_info.get('Size', 0),
                            'size_mb': round(file_info.get('Size', 0) / (1024 * 1024), 2),
                            'modified': file_info.get('ModTime', ''),
                            'remote': remote_name
                        })
                
                # Sort by modification time (newest first)
                backups.sort(key=lambda x: x['modified'], reverse=True)
                return backups
            return []
        except Exception as e:
            current_app.logger.error(f"Error listing cloud backups: {str(e)}")
            return []
    
    def download_backup(self, remote_name: str, remote_file_path: str, 
                       local_download_path: str) -> Tuple[bool, str]:
        """Download backup from cloud storage"""
        if not self.check_rclone_available():
            return False, "rclone is not available"
        
        try:
            remote_path = f"{remote_name}:{remote_file_path}"
            
            result = self._run_rclone_command([
                'copy', remote_path, 
                os.path.dirname(local_download_path),
                '--progress'
            ], timeout=300)
            
            if result.returncode == 0:
                return True, f"Backup downloaded successfully to {local_download_path}"
            else:
                error_msg = result.stderr.strip() or "Download failed"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Download timeout (5 minutes)"
        except Exception as e:
            return False, f"Download error: {str(e)}"
    
    def delete_cloud_backup(self, remote_name: str, 
                           remote_file_path: str) -> Tuple[bool, str]:
        """Delete backup from cloud storage"""
        if not self.check_rclone_available():
            return False, "rclone is not available"
        
        try:
            remote_path = f"{remote_name}:{remote_file_path}"
            
            result = self._run_rclone_command(['delete', remote_path], timeout=60)
            
            if result.returncode == 0:
                return True, "Backup deleted successfully"
            else:
                error_msg = result.stderr.strip() or "Delete failed"
                return False, error_msg
                
        except Exception as e:
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