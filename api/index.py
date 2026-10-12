import os
import sys

# Add project root directory to sys.path so app and dependencies can be loaded
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app

class VercelPathFixerMiddleware:
    """
    WSGI middleware for Vercel Serverless Functions.
    When Vercel rewrites incoming requests to /api/index, PATH_INFO in the WSGI
    environment is often set to '/api/index' instead of the requested route.
    This middleware inspects Vercel's incoming routing headers (HTTP_X_MATCHED_PATH,
    HTTP_X_FORWARDED_URI, REQUEST_URI) and restores the correct PATH_INFO so Flask
    routes can match properly.
    """
    def __init__(self, wsgi_app):
        self.app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = (
            environ.get('HTTP_X_MATCHED_PATH') or
            environ.get('HTTP_X_FORWARDED_URI') or
            environ.get('REQUEST_URI') or
            environ.get('RAW_URI')
        )
        if matched_path:
            clean_path = matched_path.split('?')[0]
            if clean_path and clean_path not in ('/api/index', '/api/index.py'):
                environ['PATH_INFO'] = clean_path
        return self.app(environ, start_response)

app.wsgi_app = VercelPathFixerMiddleware(app.wsgi_app)

