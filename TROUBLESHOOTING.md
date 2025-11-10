# Troubleshooting Vercel Deployment

## Common Issues and Solutions

### 1. FUNCTION_INVOCATION_FAILED Error

This error typically occurs due to:
- Import errors
- Path issues
- Missing dependencies
- Handler format issues

#### Solution Steps:

1. **Check Vercel Logs**
   - Go to your Vercel dashboard
   - Navigate to your deployment
   - Click on "Functions" tab
   - Check the logs for specific error messages

2. **Test Health Endpoint**
   - Visit: `https://your-app.vercel.app/health`
   - This will show if the Flask app is running and paths are correct

3. **Verify File Structure**
   ```
   .
   ├── api/
   │   ├── __init__.py
   │   └── index.py
   ├── templates/
   │   └── index.html
   ├── static/
   │   ├── css/
   │   └── js/
   ├── DRipper.py
   ├── vercel.json
   └── requirements.txt
   ```

4. **Check Requirements**
   - Ensure `requirements.txt` includes: `flask>=2.3.0`
   - No WebSocket dependencies (flask-socketio, etc.)

5. **Verify Handler Export**
   - In `api/index.py`, ensure: `handler = app`
   - This exports the Flask app for Vercel

### 2. Import Errors

If you see import errors for `DRipper`:

**Solution:**
- Ensure `DRipper.py` is in the root directory
- The `api/index.py` adds the parent directory to `sys.path`
- Check that the import path is correct

### 3. Template Not Found

If templates aren't loading:

**Solution:**
- Verify `templates/` directory exists in root
- Check `template_dir` path in `api/index.py`
- Visit `/health` endpoint to see path verification

### 4. Static Files Not Loading

**Solution:**
- Ensure `static/` directory exists in root
- Check `vercel.json` routes for static files
- Verify paths in HTML templates

### 5. Function Timeout

**Solution:**
- Reduce thread count (100-500 recommended)
- Use shorter attack durations
- Check `maxDuration` in `vercel.json` (60 seconds max)

## Debugging Steps

1. **Deploy and Check Logs**
   ```bash
   vercel logs
   ```

2. **Test Health Endpoint**
   ```
   GET https://your-app.vercel.app/health
   ```

3. **Test Root Endpoint**
   ```
   GET https://your-app.vercel.app/
   ```

4. **Check Function Logs in Dashboard**
   - Vercel Dashboard → Your Project → Functions Tab
   - Look for error messages and stack traces

## Quick Fixes

### If Handler Not Working

Try updating `api/index.py` handler:

```python
# Ensure this is at the end of the file
handler = app
```

### If Paths Are Wrong

Check the paths in `api/index.py`:

```python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
template_dir = os.path.join(parent_dir, 'templates')
static_dir = os.path.join(parent_dir, 'static')
```

### If Import Fails

Add debug output:

```python
print(f"Current dir: {current_dir}")
print(f"Parent dir: {parent_dir}")
print(f"Python path: {sys.path}")
```

## Testing Locally

Before deploying, test locally:

```bash
cd api
python index.py
```

Visit: `http://localhost:5000`

## Contact

If issues persist:
1. Check Vercel function logs
2. Test `/health` endpoint
3. Verify all files are committed to Git
4. Check `vercel.json` configuration

