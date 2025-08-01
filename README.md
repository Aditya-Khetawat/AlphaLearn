# AlphaLearn

A stock trading learning platform for college students in India. It provides a simulated trading environment where students can learn about stock trading without risking real money.

## Features

- Users start with ₹100,000 of virtual money
- Real-time stock data from Indian markets
- Buy and sell stocks
- View portfolio performance
- Leaderboard to compare with other users

## Tech Stack

### Frontend

- Next.js
- React
- Shadcn UI
- TypeScript
- Supabase Auth

### Backend

- FastAPI
- PostgreSQL (via Supabase)
- SQLAlchemy ORM
- Pydantic
- JWT Authentication

## Setup Instructions

### Prerequisites

- Node.js (v18+)
- Python (v3.11+)
- Supabase account

### Quick Setup

1. **Clone the repository:**

```bash
git clone https://github.com/Aditya-Khetawat/AlphaLearn.git
cd AlphaLearn
```

2. **Backend Setup:**

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup:**

```bash
cd Frontend
npm install
```

### Supabase Setup

1. Create a new project on [Supabase](https://app.supabase.com/)
2. Note down your project URL and anon key from the project settings
3. Set up the following tables in the Supabase SQL editor:

```sql
-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  full_name TEXT,
  balance NUMERIC NOT NULL DEFAULT 100000,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Enable RLS on users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create policy for users to access only their own data
CREATE POLICY "Users can view and update their own data" ON public.users
  FOR ALL USING (auth.uid() = id);

-- Stocks table
CREATE TABLE public.stocks (
  id SERIAL PRIMARY KEY,
  symbol TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  current_price NUMERIC NOT NULL,
  previous_close NUMERIC,
  change NUMERIC,
  change_percent NUMERIC,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Portfolio positions table
CREATE TABLE public.positions (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) NOT NULL,
  stock_id INTEGER REFERENCES public.stocks(id) NOT NULL,
  shares NUMERIC NOT NULL,
  average_cost NUMERIC NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
  UNIQUE(user_id, stock_id)
);

-- Enable RLS on positions table
ALTER TABLE public.positions ENABLE ROW LEVEL SECURITY;

-- Create policy for users to access only their own positions
CREATE POLICY "Users can view and update their own positions" ON public.positions
  FOR ALL USING (auth.uid() = user_id);

-- Transactions table
CREATE TABLE public.transactions (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) NOT NULL,
  stock_id INTEGER REFERENCES public.stocks(id) NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('BUY', 'SELL')),
  shares NUMERIC NOT NULL,
  price NUMERIC NOT NULL,
  total NUMERIC NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Enable RLS on transactions table
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- Create policy for users to access only their own transactions
CREATE POLICY "Users can view their own transactions" ON public.transactions
  FOR ALL USING (auth.uid() = user_id);
```

### Backend Setup

1. Navigate to the backend directory (if not already there)
2. Create a `.env` file in the backend directory with the following content:

```
# API Settings
PROJECT_NAME=AlphaLearn
SECRET_KEY=your_secret_key
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Supabase Settings
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret

# Database
DATABASE_URL=postgresql://postgres:your_password@your_project_ref.supabase.co:5432/postgres
```

3. Run the backend server:

```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory (if not already there)
2. Create a `.env.local` file in the frontend directory with the following content:

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## 🚀 Deployment

### Quick Deploy (Recommended)

**Frontend (Vercel):**
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Aditya-Khetawat/AlphaLearn&project-name=alphalearn&framework=nextjs&root-directory=Frontend)

**Backend (Railway):**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Aditya-Khetawat/AlphaLearn&rootDirectory=Backend)

### Manual Deployment

1. **Backend (Railway/Heroku):**

   - Connect your GitHub repository
   - Set root directory to `Backend`
   - Add environment variables
   - Deploy

2. **Frontend (Vercel/Netlify):**
   - Connect your GitHub repository
   - Set root directory to `Frontend`
   - Add environment variables
   - Deploy

### Environment Variables for Production

**Frontend (.env.production):**

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.railway.app
```

**Backend (.env.production):**

```env
PROJECT_NAME=AlphaLearn
SECRET_KEY=your_super_secure_production_key
BACKEND_CORS_ORIGINS=["https://your-frontend-url.vercel.app"]
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
DATABASE_URL=your_supabase_database_url
```

## 📊 Features Showcase

- **📈 Real-time Stock Charts**: 30-minute intervals for 1D, 4 points per day for 1W
- **💰 Portfolio Management**: Live portfolio updates with real market data
- **🏆 Leaderboard**: Compete with other traders
- **🌙 Dark/Light Mode**: Full theme support
- **📱 Responsive Design**: Works on all devices
- **🔐 Secure Authentication**: Supabase Auth integration

## 🛠️ Tech Highlights

- **Next.js 15** with App Router
- **FastAPI** with async/await
- **Real-time data** with yfinance
- **Supabase** for database and auth
- **Tailwind CSS** for styling
- **TypeScript** for type safety

## 📸 Screenshots

![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)
![Trading](https://via.placeholder.com/800x400?text=Trading+Page+Screenshot)
![Portfolio](https://via.placeholder.com/800x400?text=Portfolio+Screenshot)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Live Demo

**🌐 Frontend**: [Coming Soon - Deploy to see your live app!]  
**🔗 API**: [Coming Soon - Your backend URL here!]

---

**Built with ❤️ by [Aditya Khetawat](https://github.com/Aditya-Khetawat)**

## Usage

1. Register for an account or login if you already have one
2. Browse available stocks on the learn page
3. Buy stocks from the trade page
4. Track your portfolio performance
5. Check the leaderboard to see how you compare to others
