import os
from app import create_app

def main():
    app = create_app()
    
    # Use environment variables with sensible defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    # In production, debug should be False
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()