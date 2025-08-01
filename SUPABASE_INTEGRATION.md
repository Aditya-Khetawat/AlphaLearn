# AlphaLearn Supabase Integration Steps

We've updated the project to use Supabase for authentication and database management. Here's what's been accomplished and what you need to do next.

## Changes Made

### Backend

1. Created a Supabase client module (`app/core/supabase_client.py`)
2. Updated the database configuration to support Supabase
3. Created a setup script (`setup_supabase.py`) to initialize database tables

### Frontend

1. Installed Supabase client library (`@supabase/supabase-js`)
2. Created a Supabase client module (`lib/supabase-client.ts`)
3. Updated the authentication flow in the app context to use Supabase
4. Updated API functions to accept tokens for authentication
5. Created environment files for configuration

## Next Steps

### 1. Set up a Supabase Project

- Go to [Supabase](https://app.supabase.com/) and create a new project
- Make note of your project URL and API keys

### 2. Configure Environment Variables

- Backend: Update the `.env` file with your Supabase credentials

```
# API Settings
PROJECT_NAME=AlphaLearn
SECRET_KEY=your_secret_key_for_jwt_generation
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Supabase Settings
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret

# Database
DATABASE_URL=your_supabase_postgres_connection_string
```

You can find these values in your Supabase project:

- `SUPABASE_URL`: Project Settings > API > URL
- `SUPABASE_KEY`: Project Settings > API > Project API keys > `service_role` key
- `SUPABASE_JWT_SECRET`: Project Settings > API > JWT Settings > JWT Secret
- `DATABASE_URL`: Project Settings > Database > Connection string > URI format

- Frontend: Update the `.env.local` file with your Supabase credentials

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

You can find these values in your Supabase project:

- `NEXT_PUBLIC_SUPABASE_URL`: Project Settings > API > URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Project Settings > API > Project API keys > `anon` / `public` key

```

### 3. Create Database Tables

- Run the setup script to create tables in Supabase:

```

cd Backend
python setup_supabase.py

```

### 4. Set up Row Level Security

- The setup script creates RLS policies, but verify in Supabase dashboard:
  - Users can only access their own data
  - Positions and transactions are properly secured

### 5. Test Authentication Flow

- Start both the backend and frontend:

```

# Backend

cd Backend
uvicorn app.main:app --reload

# Frontend

cd Frontend
npm run dev

```

- Try registering a new user and logging in

### 6. Complete API Integration

- Update any remaining API endpoints to work with Supabase
- Test buying and selling stocks
- Verify portfolio updates correctly

### 7. Integrate Real Indian Stock Market Data

Currently, the application uses mock stock data. To fetch real Indian stock market data, you'll need to integrate with a market data API. Here are some options:

#### Option 1: NSE India API (Official)
- National Stock Exchange of India has an official API but requires formal registration
- More information: [NSE India Developer](https://www.nseindia.com/nse-api-market-data)

#### Option 2: Third-Party APIs
- **Alpha Vantage**: Offers global stock data including Indian stocks (BSE/NSE)
  - Sign up at [Alpha Vantage](https://www.alphavantage.co/) for an API key
  - Add to your backend `.env`: `ALPHA_VANTAGE_API_KEY=your_api_key`

- **Polygon.io**: Offers extensive market data with Indian stock support
  - Sign up at [Polygon.io](https://polygon.io/) for an API key
  - Add to your backend `.env`: `POLYGON_API_KEY=your_api_key`

- **Yahoo Finance API**: Unofficial but works well for basic data
  - No API key required, but has usage limitations
  - Can be accessed via libraries like `yfinance` for Python

#### Implementation Steps:
1. Choose a data provider and get API credentials if required
2. Create a stock data service in the backend (`app/services/stock_data.py`)
3. Set up scheduled tasks to update stock prices periodically
4. Update the `stockAPI` methods to fetch real data instead of mock data

## Common Issues

### CORS Errors

If you encounter CORS errors, ensure your Supabase project has the correct allowed origins:

1. Go to your Supabase project settings
2. Navigate to API > CORS
3. Add `http://localhost:3000` to allowed origins

### Authentication Issues

- Make sure your JWT secret in the backend matches Supabase's JWT secret
  - The `SUPABASE_JWT_SECRET` in your backend `.env` should match the JWT Secret from Supabase Project Settings > API > JWT Settings
  - Ensure you're using the same `SUPABASE_KEY` (service role key) in the backend and `SUPABASE_ANON_KEY` (anon/public key) in the frontend
- Check that tokens are being properly passed to API calls
  - Look at network requests to verify the Authorization header contains a valid JWT token
  - Make sure your frontend is using the Supabase client correctly for authentication

### Database Issues

- Verify database tables were created with correct schemas
  - You can check this in Supabase Dashboard > Table Editor
  - Ensure relationships between tables are properly set up (foreign keys)
- Check that RLS policies are active and working as expected
  - Go to Supabase Dashboard > Authentication > Policies
  - Each table should have policies allowing users to access only their own data
- Examine function hooks and triggers
  - The transaction trigger should update user balance automatically
  - Check Supabase Dashboard > Database > Functions for any errors

### Environment Variable Issues

- Double-check all keys and URLs are correctly copied from Supabase
  - No trailing spaces or quotes in your `.env` files
  - Make sure to use the right key types (service role for backend, anon/public for frontend)
- Verify the frontend can access environment variables
  - Next.js requires variables to be prefixed with `NEXT_PUBLIC_` to be accessible client-side
  - Any changes to environment variables require restarting the development server
```
