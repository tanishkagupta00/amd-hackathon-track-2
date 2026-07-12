# Vercel Deployment Fix: CLI vs Git

## Problem
✅ **Vercel CLI deployment** worked  
❌ **Git-connected deployment** failed

## Root Causes

### 1. Missing `api/requirements.txt`
**Issue**: The `@vercel/python` builder expects `requirements.txt` at the same level as the Python file (`api/index.py`), not at the root.

**Why CLI worked**: CLI deployments may have used cached dependencies or root-level requirements.

**Why Git failed**: Fresh Git deployments couldn't find Python dependencies for the serverless function.

**Fix**: Created `api/requirements.txt` with all necessary dependencies.

### 2. Missing Python Version Configuration
**Issue**: No explicit Python version in `vercel.json`.

**Fix**: Added `PYTHON_VERSION` environment variable in `vercel.json`.

### 3. Missing `.vercelignore`
**Issue**: Unnecessary files were being uploaded, potentially causing conflicts or size limits.

**Fix**: Created `.vercelignore` to exclude test files, cache, and unnecessary documentation.

### 4. No Timeout Configuration
**Issue**: Default serverless function timeout (10s) might be too short for AI operations.

**Fix**: Added `maxDuration: 60` to Python build config.

## Changes Made

### ✅ Created `api/requirements.txt`
```txt
openai>=1.12.0
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
pydantic-settings>=2.2.1
requests>=2.31.0
sqlalchemy>=2.0.0
python-multipart>=0.0.9
Pillow>=10.0.0
python-dotenv>=1.0.0
httpx>=0.27.0
imageio>=2.30.0
imageio-ffmpeg>=0.4.9
numpy>=1.20.0
aiofiles>=23.2.1
```

### ✅ Updated `vercel.json`
Added:
- `config.maxDuration: 60` for Python build
- `env.PYTHON_VERSION: "3.12"` globally

### ✅ Created `.vercelignore`
Excludes:
- Python cache files (`__pycache__`, `*.pyc`)
- Environment files (`.env`)
- Test directories
- Documentation
- Large files
- Node modules

## Testing the Fix

### Option 1: Push to Git (Recommended)
```bash
git add api/requirements.txt vercel.json .vercelignore VERCEL_DEPLOYMENT_FIX.md
git commit -m "fix: Add api/requirements.txt for Git deployment compatibility"
git push
```

Vercel will automatically trigger a new deployment from Git.

### Option 2: CLI Deployment (To Verify)
```bash
vercel --prod
```

## Expected Results

### Before Fix
```
❌ Git Deployment: BUILD FAILED
   - Missing requirements.txt
   - Python dependencies not found
   - Function may timeout

✅ CLI Deployment: SUCCESS
   - Used cached dependencies
   - Local .vercel config helped
```

### After Fix
```
✅ Git Deployment: SUCCESS
   - api/requirements.txt found
   - All dependencies installed
   - Python 3.12 used
   - 60s timeout configured

✅ CLI Deployment: SUCCESS
   - Still works as before
```

## How Vercel Python Builder Works

### File Structure Expected
```
/api
  ├── index.py          # Your serverless function
  └── requirements.txt  # Dependencies (MUST be here!)
```

### Build Process
1. Vercel detects `api/index.py` with `@vercel/python` builder
2. Looks for `api/requirements.txt` (NOT root-level!)
3. Creates isolated Python environment
4. Installs dependencies: `pip install -r requirements.txt`
5. Packages function as serverless endpoint

### Why Location Matters
- Each serverless function is built **independently**
- Dependencies must be **co-located** with the function
- Root-level `requirements.txt` is **ignored** for serverless functions
- Only used if you have a monolithic build

## Additional Recommendations

### 1. Environment Variables
Make sure these are set in Vercel dashboard:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` (if using)
- Any other API keys from `backend/.env`

Go to: Project Settings → Environment Variables

### 2. Monitor First Deployment
- Check build logs for any missing dependencies
- Verify function doesn't timeout (now set to 60s)
- Test API endpoints after deployment

### 3. Logs Access
```bash
# View deployment logs
vercel logs

# View function logs
vercel logs --follow
```

### 4. Python Version Verification
If you encounter Python version issues:
1. Check `runtime.txt` (currently `python-3.12`)
2. Verify Vercel supports that version: https://vercel.com/docs/functions/runtimes/python
3. Update if needed

## Common Pitfalls to Avoid

❌ **Don't** put `requirements.txt` only at root  
✅ **Do** put it in `api/` directory

❌ **Don't** rely on CLI deployment success  
✅ **Do** test Git deployment as the source of truth

❌ **Don't** ignore environment variables  
✅ **Do** set them in Vercel dashboard

❌ **Don't** use default 10s timeout for AI  
✅ **Do** set at least 60s for OpenAI calls

## Troubleshooting

### If deployment still fails:

#### 1. Check Build Logs
```bash
vercel logs <deployment-url>
```
Look for:
- "requirements.txt not found" → File not committed
- "Module not found" → Missing dependency
- "Timeout" → Increase maxDuration

#### 2. Verify Files Are Committed
```bash
git ls-files api/
```
Should show:
- `api/index.py`
- `api/requirements.txt`

#### 3. Check Vercel Dashboard
Project → Deployments → [Failed Deployment] → Build Logs

#### 4. Test Locally with Vercel CLI
```bash
vercel dev
```
This simulates Vercel environment locally.

## References
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Configuration](https://vercel.com/docs/projects/project-configuration)
- [Git vs CLI Deployments](https://vercel.com/docs/deployments/git)

## Status
- ✅ Fix implemented
- ⏳ Waiting for Git deployment test
- 📝 Document created for future reference
