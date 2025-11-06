# Deployment Guide 🚀

This guide covers deploying your webhook processor to various cloud platforms.

## Railway Deployment (Recommended)

Railway is the easiest option - connects directly to GitHub and handles everything.

### Steps:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your webhook processor repo
   - Railway will auto-detect the Dockerfile and deploy

3. **Add MongoDB**
   - In your Railway project, click "New Service"
   - Select "Database" → "MongoDB"
   - Railway will automatically set the `MONGODB_URL` environment variable

4. **Get Your URL**
   - Your app will be available at: `https://your-app-name.railway.app`
   - Test with: `curl https://your-app-name.railway.app/`

### Railway Features:
- ✅ Auto-deploys on git push
- ✅ Built-in MongoDB
- ✅ Free tier: 500 hours/month
- ✅ Custom domains
- ✅ Environment variables management

## Render Deployment

### Steps:

1. **Push to GitHub** (same as above)

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New" → "Web Service"
   - Connect your GitHub repo
   - Render will use the included `render.yaml` config

3. **MongoDB Setup**
   - Render will automatically create MongoDB from `render.yaml`
   - Database connection will be auto-configured

### Render Features:
- ✅ Free tier available
- ✅ Managed databases
- ✅ Auto-deploys from GitHub
- ✅ Built-in SSL certificates

## Fly.io Deployment

### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Or download from: https://fly.io/docs/getting-started/installing-flyctl/
   ```

2. **Login and Deploy**
   ```bash
   fly auth login
   fly launch --name your-webhook-processor
   fly deploy
   ```

3. **Add MongoDB**
   ```bash
   # Create MongoDB app
   fly postgres create --name webhook-db
   
   # Set connection string
   fly secrets set MONGODB_URL="your-mongodb-connection-string"
   ```

### Fly.io Features:
- ✅ Global edge deployment
- ✅ Excellent Docker support
- ✅ Free tier: 3 shared-cpu-1x VMs
- ✅ Fast deployments

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