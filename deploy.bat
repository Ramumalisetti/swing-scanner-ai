@echo off
setlocal enabledelayedexpansion

echo.
echo ================================================
echo   SWING SCANNER AI — GitHub + Vercel Deploy
echo ================================================
echo.

:: ── STEP 0: Check prerequisites ─────────────────
echo [1/6] Checking prerequisites...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: git not found. Install from https://git-scm.com
    pause & exit /b 1
)
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Install from https://nodejs.org
    pause & exit /b 1
)
echo   git OK  ^|  node OK
echo.

:: ── STEP 1: Initialize git ──────────────────────
echo [2/6] Initializing git repository...
cd /d "%~dp0"
git init -b main
git config user.email "istclaude@ispatialtec.com"
git config user.name "iSpatialTec"
git add -A
git commit -m "feat: Swing Scanner AI - 10-factor NSE momentum scanner with Vercel deployment"
echo   Git repo initialized and committed.
echo.

:: ── STEP 2: Install GitHub CLI if needed ────────
echo [3/6] Checking GitHub CLI (gh)...
gh --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   gh CLI not found. Installing via winget...
    winget install --id GitHub.cli -e --source winget
    if %errorlevel% neq 0 (
        echo.
        echo   Could not auto-install gh CLI.
        echo   Please install manually: https://cli.github.com
        echo   Then re-run this script.
        pause & exit /b 1
    )
)
echo   gh CLI OK
echo.

:: ── STEP 3: GitHub login + create repo ─────────
echo [4/6] Connecting to GitHub...
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo   Logging into GitHub...
    gh auth login --web --git-protocol https
)

echo   Creating GitHub repo: swing-scanner-ai
gh repo create swing-scanner-ai --public --source=. --remote=origin --push --description "NSE Swing Scanner AI - 10-Factor Momentum Scanner with Vercel Dashboard"
if %errorlevel% neq 0 (
    echo.
    echo   Repo may already exist. Trying to push to existing...
    git remote add origin https://github.com/%USERNAME%/swing-scanner-ai.git 2>nul
    git push -u origin main
)
echo.
echo   ✓ Code pushed to GitHub!
echo.

:: ── STEP 4: Install Vercel CLI ──────────────────
echo [5/6] Installing Vercel CLI...
npm install -g vercel >nul 2>&1
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Vercel CLI install failed.
    echo Try manually: npm install -g vercel
    pause & exit /b 1
)
echo   Vercel CLI OK
echo.

:: ── STEP 5: Deploy to Vercel ────────────────────
echo [6/6] Deploying to Vercel...
echo   (A browser window will open to log in to Vercel)
echo.
vercel --prod

echo.
echo ================================================
echo   DEPLOYMENT COMPLETE!
echo.
echo   GitHub : https://github.com/%USERNAME%/swing-scanner-ai
echo   Vercel  : shown above (your-app.vercel.app)
echo.
echo   NEXT STEP — Add OpenRouter API key to Vercel:
echo   vercel env add OPENROUTER_API_KEY production
echo ================================================
echo.
pause
