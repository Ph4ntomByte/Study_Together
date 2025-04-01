from http.server import BaseHTTPRequestHandler
import os
from app import create_app
from urllib.parse import parse_qs

app = create_app()

def handle_flask_app(path, headers, method, body=None):
    # Convert Netlify request to WSGI environment
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': '',
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': headers.get('content-length', '0'),
        'HTTP_HOST': headers.get('host', ''),
        'wsgi.input': body,
        'wsgi.errors': None,
        'wsgi.version': (1, 0),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.url_scheme': 'https',
    }

    # Process the request through Flask
    response_headers = []
    status_code = [200]
    body_parts = []

    def start_response(status, headers):
        status_code[0] = int(status.split(' ')[0])
        response_headers.extend(headers)

    response_iter = app(environ, start_response)
    
    for part in response_iter:
        if isinstance(part, bytes):
            body_parts.append(part.decode('utf-8'))
        else:
            body_parts.append(part)
    
    response_body = ''.join(body_parts)
    
    # Clean up if needed
    if hasattr(response_iter, 'close'):
        response_iter.close()
    
    return {
        'statusCode': status_code[0],
        'headers': dict(response_headers),
        'body': response_body
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = handle_flask_app(self.path, dict(self.headers), 'GET')
        self.send_response(response['statusCode'])
        
        for key, value in response['headers'].items():
            self.send_header(key, value)
        self.end_headers()
        
        self.wfile.write(response['body'].encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length) if content_length > 0 else None
        
        response = handle_flask_app(self.path, dict(self.headers), 'POST', post_body)
        self.send_response(response['statusCode'])
        
        for key, value in response['headers'].items():
            self.send_header(key, value)
        self.end_headers()
        
        self.wfile.write(response['body'].encode('utf-8'))


def handler(event, context):
    path = event.get('path', '')
    headers = event.get('headers', {})
    method = event.get('httpMethod', 'GET')
    body = event.get('body', None)
    
    return handle_flask_app(path, headers, method, body) 