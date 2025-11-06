# Deployment Guide 🚀

This guide covers deploying your webhook processor to **completely FREE** cloud platforms.

## Render.com Deployment (Recommended - 100% Free)

Render offers 750 hours/month free tier with managed databases - perfect for demos and portfolios.

### Steps:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (free)
   - Click "New" → "Blueprint"
   - Connect your GitHub repo
   - Render will automatically use `render.yaml` and deploy both app + database

3. **Get Your URL**
   - Your app will be available at: `https://webhook-processor.onrender.com`
   - Test with: `curl https://webhook-processor.onrender.com/`

### Render Features:
- ✅ 750 hours/month FREE
- ✅ Free MongoDB database
- ✅ Auto-deploys on git push
- ✅ SSL certificates included
- ✅ Zero configuration needed

## Fly.io Deployment (Free Tier)

Fly.io offers 3 free VMs with excellent performance.

### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Or download from: https://fly.io/docs/getting-started/installing-flyctl/
   ```

2. **Deploy**
   ```bash
   fly auth login
   fly launch --name webhook-processor-yourname
   # Choose "Yes" to deploy now
   ```

3. **Add Free MongoDB**
   - Use MongoDB Atlas free tier (512MB)
   - Get connection string from Atlas
   - Set environment variable:
   ```bash
   fly secrets set MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net/webhook_processor"
   ```

### Fly.io Features:
- ✅ 3 shared VMs FREE
- ✅ 160GB transfer/month
- ✅ Global edge deployment
- ✅ Excellent Docker support

## Vercel Deployment (Serverless - Free)

Vercel offers unlimited deployments but has 10-second timeout (good for demos).

### Steps:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel login
   vercel --prod
   ```

3. **Add MongoDB Atlas (Free)**
   - Sign up at [MongoDB Atlas](https://cloud.mongodb.com)
   - Create free cluster (512MB)
   - Get connection string
   - Add to Vercel environment variables

### Vercel Features:
- ✅ Unlimited deployments FREE
- ✅ Global CDN
- ✅ Instant deployments
- ⚠️ 10-second timeout limit

## Heroku Deployment (Still Free Options)

Heroku still offers free options through GitHub Student Pack or eco dynos.

### Steps:

1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy**
   ```bash
   heroku login
   heroku create webhook-processor-yourname
   git push heroku main
   ```

3. **Add MongoDB Atlas**
   ```bash
   heroku config:set MONGODB_URL="mongodb+srv://..."
   ```

## Environment Variables

All platforms need this environment variable:

```
MONGODB_URL=mongodb://username:password@host:port/webhook_processor
```

Railway and Render handle this automatically when you add their MongoDB services.

## Testing Your Deployment

Once deployed, test your live API:

```bash
# Replace YOUR_URL with your actual deployment URL
export API_URL="https://your-app-name.railway.app"

# Health check
curl $API_URL/

# Send webhook
curl -X POST $API_URL/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "live_test_123",
    "source_account": "acc_test_1",
    "destination_account": "acc_test_2",
    "amount": 100,
    "currency": "USD"
  }'

# Check status immediately
curl $API_URL/v1/transactions/live_test_123

# Wait 35 seconds and check again
sleep 35
curl $API_URL/v1/transactions/live_test_123
```

## Troubleshooting

### Common Issues:

1. **App won't start**
   - Check logs in your platform's dashboard
   - Verify `MONGODB_URL` is set correctly
   - Ensure port is set to platform's `$PORT` variable

2. **Database connection failed**
   - Verify MongoDB service is running
   - Check connection string format
   - Ensure database allows connections from your app

3. **Slow responses**
   - Check if you're on free tier (may have cold starts)
   - Verify background processing isn't blocking main thread

### Platform-Specific Logs:

- **Railway**: Project dashboard → "Deployments" → Click deployment → "View Logs"
- **Render**: Service dashboard → "Logs" tab
- **Fly.io**: `fly logs` command

## Cost Estimates

### Free Tiers:
- **Railway**: 500 hours/month (enough for demos)
- **Render**: 750 hours/month
- **Fly.io**: 3 VMs with 160GB/month transfer

### Paid Plans (if needed):
- **Railway**: $5/month for hobby plan
- **Render**: $7/month for starter plan  
- **Fly.io**: Pay-as-you-go pricing

## Production Considerations

For production use, consider:

1. **Environment Variables**: Use platform secrets management
2. **Database**: Upgrade to dedicated MongoDB instance
3. **Monitoring**: Add health checks and alerting
4. **Scaling**: Configure auto-scaling based on load
5. **Logging**: Centralized logging with structured logs
6. **Security**: API rate limiting and authentication

Choose Railway for the easiest deployment experience! 🚀