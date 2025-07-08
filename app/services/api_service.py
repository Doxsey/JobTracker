import requests
from flask import current_app, session, url_for
from typing import Dict, Any, Optional

class APIService:
    def __init__(self):
        self.base_url = url_for('main.index', _external=True).rstrip('/')
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        print(f"Making {method} request to {url} with kwargs: {kwargs}")
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API request failed: {e}")
            raise

    def create_job_activity(self, activity_data: Dict[str, Any]) -> requests.Response:
        add_job_activity_url = url_for('job_activities.add', _external=True)
        response = self._make_request('POST', add_job_activity_url, json=activity_data)
        return response
