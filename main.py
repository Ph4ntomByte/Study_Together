from app import create_app

def main():
    """
    This is the entry point to run the Study Together application.
    For a better development experience, use 'flask run' instead.
    """
    app = create_app()
    app.run(debug=True)


if __name__ == "__main__":
    main()
