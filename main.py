import os
from app import create_app

def main():
    db_path = os.environ.get('SQLITE_PATH', '/data/app.db')
    db_url = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')

    app = create_app({'SQLALCHEMY_DATABASE_URI': db_url})
    
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()