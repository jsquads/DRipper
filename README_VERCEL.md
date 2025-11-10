# Vercel Deployment Guide

This guide explains how to deploy the DDoS-Ripper web interface to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. Vercel CLI installed (optional, for CLI deployment)
3. Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Methods

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to a Git repository** (GitHub, GitLab, or Bitbucket)

2. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**

3. **Click "New Project"**

4. **Import your Git repository**

5. **Configure the project:**
   - Framework Preset: **Other**
   - Root Directory: `./` (leave as default)
   - Build Command: Leave empty (no build needed)
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

6. **Click "Deploy"**

7. **Wait for deployment to complete**

8. **Your app will be live at `https://your-project.vercel.app`**

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Follow the prompts:**
   - Link to existing project or create new
   - Confirm settings

5. **For production deployment:**
   ```bash
   vercel --prod
   ```

## Project Structure

```
.
├── api/
│   ├── __init__.py
│   └── index.py          # Vercel serverless function entry point
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   └── index.html
├── DRipper.py            # Core DDoS tool
├── headers.txt           # Custom headers file
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md
```

## Configuration Files

### `vercel.json`
- Configures Vercel to use Python runtime
- Routes API requests to serverless functions
- Serves static files

### `api/index.py`
- Main serverless function entry point
- Handles all routes (/, /api/*)
- Uses Flask for routing

## Important Notes

### Serverless Limitations

1. **Execution Time Limit**: Vercel serverless functions have a maximum execution time (10 seconds on free tier, 60 seconds on Pro)
   - Long-running attacks may timeout
   - Consider using fewer threads for shorter attacks

2. **State Management**: Serverless functions are stateless
   - Attack state is stored in-memory per function instance
   - Multiple instances may have separate states
   - This is handled with unique attack IDs

3. **WebSockets**: Not supported in Vercel serverless functions
   - The app uses HTTP polling instead of WebSockets
   - Status updates are polled every second

4. **Cold Starts**: First request may be slower
   - Subsequent requests are faster (warm instances)

### Best Practices

1. **Thread Count**: Keep thread count reasonable (100-500)
   - Higher counts may cause timeouts
   - Test with your target to find optimal settings

2. **Attack Duration**: Shorter attacks work better
   - Long-running attacks may be interrupted
   - Consider multiple shorter attacks

3. **Monitoring**: Monitor Vercel function logs
   - Check for timeouts or errors
   - Adjust thread count if needed

## Environment Variables

No environment variables are required for basic deployment.

## Custom Domain

1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

## Troubleshooting

### Deployment Fails

- Check that `requirements.txt` is correct
- Ensure all files are committed to Git
- Check Vercel build logs for errors

### Functions Timeout

- Reduce thread count
- Use shorter attack durations
- Consider upgrading to Vercel Pro for longer timeouts

### Static Files Not Loading

- Ensure `static/` directory is in the root
- Check `vercel.json` routes configuration
- Verify file paths in HTML

### Attack Not Starting

- Check browser console for errors
- Verify API endpoints are accessible
- Check Vercel function logs

## Local Development

To test locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python api/index.py

# Open http://localhost:5000
```

## Support

For issues specific to Vercel deployment:
- Check [Vercel Documentation](https://vercel.com/docs)
- Review function logs in Vercel dashboard
- Check [Vercel Community](https://github.com/vercel/vercel/discussions)

## License

Same as main project - MPL-2.0

