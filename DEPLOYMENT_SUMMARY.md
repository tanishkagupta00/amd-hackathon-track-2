# Vercel Deployment Issue - Quick Summary

## The Problem
✅ `vercel deploy --prod` (CLI) → **WORKED**  
❌ Git push → Vercel automatic deployment → **FAILED**

## The Root Cause
Vercel's `@vercel/python` builder requires `requirements.txt` **next to the Python file**:

```
❌ Wrong Structure:
/requirements.txt          ← Vercel ignores this for serverless functions
/api/index.py

✅ Correct Structure:
/api/requirements.txt      ← Must be here!
/api/index.py
```

## Why CLI Worked But Git Didn't

| Aspect | CLI Deployment | Git Deployment |
|--------|---------------|----------------|
| **Dependency Resolution** | Uses local `.vercel/` cache | Fresh build, requires explicit files |
| **File Lookup** | Can fallback to root requirements | Strict: only looks in `/api/` |
| **State** | Stateful (remembers previous builds) | Stateless (clean slate) |
| **Configuration** | Can use local overrides | Only uses committed files |

## The Fix (3 Files)

### 1. **Created `api/requirements.txt`**
```txt
openai>=1.12.0
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
# ... (full list of dependencies)
```

### 2. **Updated `vercel.json`**
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxDuration": 60  // ← Added: AI calls need more time
      }
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.12"  // ← Added: Explicit Python version
  }
}
```

### 3. **Created `.vercelignore`**
```
__pycache__/
*.pyc
.env
tests/
docs/
*.md
# ... (excludes unnecessary files from deployment)
```

## Deploy the Fix

```bash
# Commit the changes
git add api/requirements.txt vercel.json .vercelignore
git commit -m "fix: Add api/requirements.txt for Vercel Git deployment"
git push

# Vercel will automatically deploy
# Check: https://vercel.com/dashboard
```

## Verification

After deployment, test:
```bash
# Check API health
curl https://your-domain.vercel.app/api/health

# Check function logs
vercel logs --follow
```

## Key Learnings

1. **Each serverless function needs its own `requirements.txt`**
   - Located in the same directory as the `.py` file
   - Root-level requirements are ignored

2. **CLI deployment ≠ Git deployment**
   - CLI can use cached state
   - Git is the source of truth for production

3. **Always test Git deployment**
   - CLI success doesn't guarantee Git success
   - Git deployment is what runs in production

4. **Timeout matters for AI**
   - Default: 10 seconds (too short)
   - AI calls: 60+ seconds recommended

## Files Modified/Created

- ✅ `api/requirements.txt` (NEW)
- ✅ `vercel.json` (UPDATED)
- ✅ `.vercelignore` (NEW)
- 📝 `VERCEL_DEPLOYMENT_FIX.md` (DOCUMENTATION)
- 📝 `DEPLOYMENT_SUMMARY.md` (THIS FILE)
- 🔧 `verify_deployment_setup.sh` (HELPER SCRIPT)

## Status
🟡 **Ready to Deploy** - Push to Git to test the fix

---
**Next Action**: Commit and push these changes to trigger a Git deployment.
