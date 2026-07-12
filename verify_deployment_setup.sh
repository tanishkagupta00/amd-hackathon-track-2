#!/bin/bash
# Vercel Deployment Verification Script

echo "🔍 Verifying Vercel deployment setup..."
echo ""

# Check 1: api/requirements.txt exists
if [ -f "api/requirements.txt" ]; then
    echo "✅ api/requirements.txt exists"
else
    echo "❌ api/requirements.txt is missing!"
    exit 1
fi

# Check 2: vercel.json exists and has Python config
if [ -f "vercel.json" ]; then
    echo "✅ vercel.json exists"
    if grep -q "maxDuration" vercel.json; then
        echo "✅ maxDuration configured"
    else
        echo "⚠️  maxDuration not found (may timeout)"
    fi
else
    echo "❌ vercel.json is missing!"
    exit 1
fi

# Check 3: .vercelignore exists
if [ -f ".vercelignore" ]; then
    echo "✅ .vercelignore exists"
else
    echo "⚠️  .vercelignore not found (recommended)"
fi

# Check 4: runtime.txt for Python version
if [ -f "runtime.txt" ]; then
    echo "✅ runtime.txt exists: $(cat runtime.txt)"
else
    echo "⚠️  runtime.txt not found"
fi

# Check 5: Environment files (shouldn't be in Git)
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env exists (make sure it's in .gitignore)"
fi

# Check 6: Git status
echo ""
echo "📋 Files to commit:"
git status --short api/requirements.txt vercel.json .vercelignore VERCEL_DEPLOYMENT_FIX.md verify_deployment_setup.sh 2>/dev/null || echo "Git not initialized or files not tracked"

echo ""
echo "✨ Verification complete!"
echo ""
echo "Next steps:"
echo "1. Commit the new files:"
echo "   git add api/requirements.txt vercel.json .vercelignore"
echo "   git commit -m 'fix: Add api/requirements.txt for Vercel Git deployment'"
echo "   git push"
echo ""
echo "2. Check Vercel dashboard for automatic deployment"
echo ""
echo "3. Test the deployment:"
echo "   curl https://your-domain.vercel.app/api/health"
