# AlphaLearn Deployment Guide

This guide covers multiple deployment options for the AlphaLearn stock trading platform.

## Quick Deploy Options

### 1. Vercel (Frontend) + Railway (Backend) - Recommended

#### Frontend on Vercel:
1. Go to [Vercel](https://vercel.com)
2. Import your GitHub repository
3. Set project root to `Frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL` = your Railway backend URL
5. Deploy automatically

#### Backend on Railway:
1. Go to [Railway](https://railway.app)
2. Create new project from GitHub
3. Select your repository
4. Set root directory to `Backend`
5. Add environment variables from `.env.example`
6. Deploy automatically

### 2. Docker Deployment

#### Prerequisites:
- Docker and Docker Compose installed
- Environment files configured

#### Steps:
```bash
# Clone the repository
git clone https://github.com/Aditya-Khetawat/AlphaLearn.git
cd AlphaLearn

# Configure environment
cp Backend/.env.example Backend/.env
cp Frontend/.env.example Frontend/.env.local
# Edit the .env files with your actual values

# Build and run
docker-compose up --build
```

Access the application at `http://localhost`

### 3. Heroku Deployment

#### Backend:
```bash
cd Backend
heroku create alphalearn-backend
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
heroku config:set SUPABASE_URL=your-supabase-url
heroku config:set SUPABASE_KEY=your-supabase-key
git push heroku main
```

#### Frontend:
```bash
cd Frontend
heroku create alphalearn-frontend
heroku config:set NEXT_PUBLIC_API_URL=https://alphalearn-backend.herokuapp.com
git push heroku main
```

### 4. AWS/GCP/Azure Deployment

Use the provided Dockerfiles to deploy on any cloud platform:
- **AWS**: ECS, Elastic Beanstalk, or App Runner
- **GCP**: Cloud Run, App Engine, or GKE
- **Azure**: Container Instances, App Service, or AKS

## Environment Variables Reference

### Backend (.env)
```env
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
SECRET_KEY=...
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Production Checklist

- [ ] Database configured and accessible
- [ ] Environment variables set
- [ ] CORS origins configured
- [ ] SSL certificates configured (for custom domains)
- [ ] Database migrations run
- [ ] Health checks working
- [ ] Monitoring and logging set up

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Ensure backend CORS_ORIGINS includes your frontend URL
2. **Database Connection**: Verify DATABASE_URL is correct and accessible
3. **Build Failures**: Check Node.js/Python versions match requirements
4. **Environment Variables**: Ensure all required variables are set

### Health Checks:
- Backend: `GET /health`
- Frontend: Should load homepage successfully

## Performance Optimization

### Backend:
- Use Redis for caching
- Configure database connection pooling
- Enable gzip compression

### Frontend:
- Enable Next.js image optimization
- Configure CDN for static assets
- Use proper caching headers

## Security Considerations

- Use HTTPS in production
- Set strong SECRET_KEY
- Configure rate limiting
- Use environment variables for all secrets
- Regular security updates

## Monitoring

### Recommended Tools:
- **Vercel**: Built-in analytics
- **Railway**: Built-in monitoring
- **Sentry**: Error tracking
- **LogRocket**: Session replay
- **Uptime Robot**: Uptime monitoring

## Support

For deployment issues:
1. Check logs for specific error messages
2. Verify environment variables
3. Test locally first
4. Create GitHub issue with details
