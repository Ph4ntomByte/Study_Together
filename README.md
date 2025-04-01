# Study Together

A collaborative platform for students to organize and join study sessions.

## Features

- **Canvas Integration**: Log in with your Canvas account
- **Study Plan Creation**: Create study plans with place, time, and subject
- **Privacy Controls**: Make your study plans public or share them via private links
- **Collaboration**: Join existing study sessions and form study groups
- **Group Communication**: Chat and coordinate with your study group
- **Meeting Management**: Suggest and vote on meeting location changes

## Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```
   flask db upgrade
   ```

5. Start the development server:
   ```
   flask run
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

## Project Structure

- `/app` - Flask backend application
- `/frontend` - React frontend application
- `/migrations` - Database migration files
