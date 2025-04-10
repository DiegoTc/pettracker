# Local Testing Instructions

This document provides instructions for testing the Pet Tracker application locally.

## Prerequisites

- Python 3.11+
- Node.js 16+
- PostgreSQL database
- Google OAuth credentials (for Google login)

## Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/DiegoTc/pettracker.git
   cd pettracker
   ```

2. Create a virtual environment and install Python dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r local-requirements.txt
   ```

3. Set up environment variables by creating a `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/pettracker
   SESSION_SECRET=your_secret_key
   GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret
   ```

4. Set up Google OAuth credentials:
   - Go to https://console.cloud.google.com/apis/credentials
   - Create a new OAuth 2.0 Client ID
   - Set the authorized redirect URI to `http://localhost:5000/api/auth/callback`

## Database Setup

1. Create a PostgreSQL database:
   ```bash
   createdb pettracker
   ```

2. Initialize the database:
   ```bash
   flask db upgrade
   ```

## Running the Application

### Backend

1. Start the Flask backend:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

### Frontend

1. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the Vue.js development server:
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

## Testing the Application

### Testing Google OAuth Login

1. Open your browser and navigate to http://localhost:3000
2. Click on "Log in with Google"
3. Complete the Google authentication process
4. You should be redirected back to the application and be logged in

### Testing Development Token (for API testing)

If you're developing or testing APIs without wanting to go through the Google OAuth flow:

1. Navigate to http://localhost:3000/dev-token
2. This will generate a JWT token for development purposes
3. Use this token in your API requests with the header: `Authorization: Bearer <token>`

### Testing the JT808 Protocol Server

1. Start the protocol server:
   ```bash
   python run_protocol_server.py
   ```

2. Use the simulator to test the connection:
   ```bash
   python tools/jt808_simulator.py
   ```

## Troubleshooting

### Database Connection Issues

- Verify your PostgreSQL connection string in the `.env` file
- Make sure PostgreSQL is running
- Check the database exists: `psql -l | grep pettracker`

### OAuth Authentication Issues

- Verify your Google OAuth credentials in the `.env` file
- Make sure the redirect URI exactly matches what's configured in the Google Cloud Console
- Check the browser console for any JavaScript errors

### Model/Migration Issues

If you encounter database schema errors:

```bash
# Reset the database migration
flask db stamp head
flask db migrate
flask db upgrade
```

## Security Notes

- The application has been configured to NOT expose detailed database errors to the client
- Security vulnerability fixes are in place to protect sensitive information
- OAuth flow has been configured for secure authentication