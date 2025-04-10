# Local Testing Guide

## Setup and Run Locally

1. Clone the repository
   ```
   git clone https://github.com/DiegoTc/pettracker.git
   cd pettracker
   ```

2. Install Python dependencies in a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r local-requirements.txt
   ```

3. Create a .env file with:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/pettracker
   SESSION_SECRET=your_secret_key
   GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
   ```

4. Setup the database:
   ```
   createdb pettracker
   flask db upgrade
   ```

5. Start the backend:
   ```
   flask run --host=0.0.0.0 --port=5000
   ```

6. In another terminal, start the frontend:
   ```
   cd frontend
   npm install
   npm run dev
   ```

7. Open http://localhost:3000 in your browser

## Testing Google OAuth
- Configure OAuth at https://console.cloud.google.com/apis/credentials
- Add redirect URI: http://localhost:5000/api/auth/callback
- Click Login with Google on the site

## Recent Fixes
- Fixed Google OAuth integration
- Enhanced security by removing detailed error exposure
- Fixed database schema issues