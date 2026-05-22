# ============================================================
#  SWING SCANNER AI — One-Click GitHub + Vercel Deploy
#  Run in PowerShell: Right-click → Run with PowerShell
#  OR: powershell -ExecutionPolicy Bypass -File deploy.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$RepoName = "swing-scanner-ai"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  SWING SCANNER AI — GitHub + Vercel Deploy    " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $ProjectDir

# ── STEP 1: Check git ─────────────────────────────────────
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow
try { git --version | Out-Null } catch {
    Write-Host "  ERROR: git not installed." -ForegroundColor Red
    Write-Host "  Install from: https://git-scm.com/download/win" -ForegroundColor Red
    Read-Host "Press Enter to exit"; exit 1
}
try { node --version | Out-Null } catch {
    Write-Host "  ERROR: Node.js not installed." -ForegroundColor Red
    Write-Host "  Install from: https://nodejs.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"; exit 1
}
Write-Host "  git OK  |  node OK" -ForegroundColor Green
Write-Host ""

# ── STEP 2: Git init + commit ─────────────────────────────
Write-Host "[2/6] Initializing git repository..." -ForegroundColor Yellow

if (Test-Path ".git") {
    Write-Host "  .git already exists — skipping init" -ForegroundColor Gray
} else {
    git init -b main
    git config user.email "istclaude@ispatialtec.com"
    git config user.name "iSpatialTec"
}

git add -A
$commitMsg = "feat: Swing Scanner AI - 10-factor NSE momentum scanner"
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m $commitMsg
    Write-Host "  Committed all files." -ForegroundColor Green
} else {
    Write-Host "  Nothing new to commit." -ForegroundColor Gray
}
Write-Host ""

# ── STEP 3: GitHub CLI ────────────────────────────────────
Write-Host "[3/6] Checking GitHub CLI (gh)..." -ForegroundColor Yellow
$ghInstalled = $null
try { $ghInstalled = gh --version } catch {}

if (-not $ghInstalled) {
    Write-Host "  gh CLI not found. Installing via winget..." -ForegroundColor Yellow
    try {
        winget install --id GitHub.cli -e --source winget --accept-source-agreements --accept-package-agreements
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } catch {
        Write-Host ""
        Write-Host "  Could not auto-install gh CLI." -ForegroundColor Red
        Write-Host "  Install manually: https://cli.github.com" -ForegroundColor Yellow
        Write-Host "  Then re-run this script." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"; exit 1
    }
}
Write-Host "  gh CLI OK" -ForegroundColor Green
Write-Host ""

# ── STEP 4: GitHub Auth + Create Repo ────────────────────
Write-Host "[4/6] Connecting to GitHub..." -ForegroundColor Yellow

$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Opening browser for GitHub login..." -ForegroundColor Yellow
    gh auth login --web --git-protocol https
}

Write-Host "  Creating repo: $RepoName" -ForegroundColor Yellow
try {
    gh repo create $RepoName `
        --public `
        --source=. `
        --remote=origin `
        --push `
        --description "NSE Swing Scanner AI - 10-Factor Momentum | Vercel Dashboard"
    Write-Host "  Repo created and code pushed!" -ForegroundColor Green
} catch {
    Write-Host "  Repo may already exist. Pushing to existing..." -ForegroundColor Yellow
    $ghUser = gh api user --jq '.login' 2>$null
    git remote remove origin 2>$null
    git remote add origin "https://github.com/$ghUser/$RepoName.git"
    git push -u origin main --force
    Write-Host "  Code pushed to existing repo." -ForegroundColor Green
}

$ghUser = gh api user --jq '.login' 2>$null
$repoUrl = "https://github.com/$ghUser/$RepoName"
Write-Host ""
Write-Host "  GitHub URL: $repoUrl" -ForegroundColor Cyan
Write-Host ""

# ── STEP 5: Vercel CLI ────────────────────────────────────
Write-Host "[5/6] Installing Vercel CLI..." -ForegroundColor Yellow
npm install -g vercel 2>$null
try { vercel --version | Out-Null } catch {
    Write-Host "  ERROR: Vercel CLI install failed." -ForegroundColor Red
    Write-Host "  Try: npm install -g vercel" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"; exit 1
}
Write-Host "  Vercel CLI OK" -ForegroundColor Green
Write-Host ""

# ── STEP 6: Vercel Deploy ─────────────────────────────────
Write-Host "[6/6] Deploying to Vercel..." -ForegroundColor Yellow
Write-Host "  (Browser will open for Vercel login if needed)" -ForegroundColor Gray
Write-Host ""

vercel --prod `
    --yes `
    --name $RepoName `
    --build-env OPENROUTER_API_KEY=""

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "  GitHub : $repoUrl" -ForegroundColor Cyan
Write-Host "  Vercel  : https://$RepoName.vercel.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "  OPTIONAL — Add free AI analysis:" -ForegroundColor Yellow
Write-Host "  1. Get free key: https://openrouter.ai" -ForegroundColor White
Write-Host "  2. Run: vercel env add OPENROUTER_API_KEY production" -ForegroundColor White
Write-Host "  3. Run: vercel --prod  (redeploy)" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"
