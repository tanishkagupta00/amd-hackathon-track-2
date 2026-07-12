param(
    [string]$FireworksKey = $env:FIREWORKS_API_KEY,
    [string]$GhcrUser = "",
    [string]$ImageName = "captionforge-ai",
    [string]$Tag = "latest"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

function Step($msg) { Write-Host "" ; Write-Host "=== $msg ===" -ForegroundColor Cyan }
function OK($msg)   { Write-Host "[OK] $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red ; exit 1 }

# ── 0. Pre-flight ─────────────────────────────────────────────────────────────
Step "Pre-flight checks"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Fail "Docker not found. Install Docker Desktop first."
}
$dv = docker --version
OK "Docker found: $dv"

if ([string]::IsNullOrEmpty($FireworksKey)) {
    Fail "FIREWORKS_API_KEY not set. Pass -FireworksKey <key>"
}
OK "FIREWORKS_API_KEY is present."

# ── 1. Build ──────────────────────────────────────────────────────────────────
Step "Building Docker image"

docker build -t "${ImageName}:${Tag}" $ProjectRoot
if ($LASTEXITCODE -ne 0) { Fail "docker build failed." }
OK "Image built."

$sizeBytes = docker image inspect "${ImageName}:${Tag}" --format "{{.Size}}"
$sizeMB = [math]::Round([int64]$sizeBytes / 1MB)
OK "Image size: $sizeMB MB"

# ── 2. Prepare test directories ───────────────────────────────────────────────
Step "Preparing test I/O directories"

$TestInput  = Join-Path $ProjectRoot "test_input"
$TestOutput = Join-Path $ProjectRoot "test_output"
New-Item -ItemType Directory -Force -Path $TestInput  | Out-Null
New-Item -ItemType Directory -Force -Path $TestOutput | Out-Null

$outputFile = Join-Path $TestOutput "results.json"
if (Test-Path $outputFile) { Remove-Item $outputFile -Force }

OK "test_input  -> $TestInput"
OK "test_output -> $TestOutput"

# ── 3. Run CLI (headless hackathon mode) ──────────────────────────────────────
Step "Running CLI test"

docker run --rm `
    -v "${TestInput}:/input:ro" `
    -v "${TestOutput}:/output" `
    -e FIREWORKS_API_KEY=$FireworksKey `
    "${ImageName}:${Tag}"

if ($LASTEXITCODE -ne 0) { Fail "Container exited with code $LASTEXITCODE." }
OK "Container finished cleanly."

# ── 4. Validate results.json ──────────────────────────────────────────────────
Step "Validating output"

if (-not (Test-Path $outputFile)) {
    Fail "results.json not found at $outputFile"
}

$raw = Get-Content $outputFile -Raw
try {
    $json = $raw | ConvertFrom-Json
} catch {
    Fail "results.json is not valid JSON: $_"
}
OK "results.json is valid JSON."

if (-not $json.tasks) { Fail "Missing top-level tasks key." }
$taskCount = $json.tasks.Count
OK "tasks count: $taskCount"

$styles = @("formal","sarcastic","humorous-tech","humorous-non-tech")
foreach ($task in $json.tasks) {
    $tid = $task.task_id
    foreach ($style in $styles) {
        $val = $task.captions.$style
        if ([string]::IsNullOrWhiteSpace($val)) {
            Fail "Task $tid is missing caption for style $style"
        }
    }
    OK "Task $tid has all 4 captions."
}

# ── 5. Print sample output ────────────────────────────────────────────────────
Step "Sample output"
$first = $json.tasks[0]
Write-Host "task_id : $($first.task_id)" -ForegroundColor Yellow
foreach ($style in $styles) {
    $cap = $first.captions.$style
    $preview = $cap.Substring(0, [Math]::Min(90, $cap.Length))
    Write-Host "$style : $preview ..." -ForegroundColor White
}

# ── 6. Web mode smoke test ────────────────────────────────────────────────────
Step "Web mode smoke test"

$cid = docker run -d -p 8000:8000 `
    -e FIREWORKS_API_KEY=$FireworksKey `
    "${ImageName}:${Tag}" web

Write-Host "Container started: $cid"
Write-Host "Polling health endpoint (up to 45s)..."

$healthUri = "http://localhost:8000/api/v1/health"
$maxAttempts = 15
$resp = $null
for ($i = 1; $i -le $maxAttempts; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri $healthUri -TimeoutSec 3
        OK "Health check passed on attempt $i`: status=$($resp.status) version=$($resp.version)"
        break
    } catch {
        Write-Host "  attempt $i/$maxAttempts not ready yet: $($_.Exception.Message)" -ForegroundColor Yellow
        if ($i -lt $maxAttempts) { Start-Sleep -Seconds 3 }
    }
}

if ($null -eq $resp) {
    Write-Host "[WARN] Health check failed (non-fatal): server did not become ready in time." -ForegroundColor Yellow
} else {
    OK "Web server is healthy."
}

docker stop $cid | Out-Null
docker rm $cid   | Out-Null
OK "Web container stopped."

# ── 7. Push to GHCR ───────────────────────────────────────────────────────────
if (-not [string]::IsNullOrEmpty($GhcrUser)) {
    Step "Pushing to GHCR"

    $GhcrTag = "ghcr.io/$GhcrUser/${ImageName}:${Tag}"

    gh auth token | docker login ghcr.io -u $GhcrUser --password-stdin
    if ($LASTEXITCODE -ne 0) { Fail "GHCR login failed." }
    OK "Logged into ghcr.io"

    docker tag "${ImageName}:${Tag}" $GhcrTag
    docker push $GhcrTag
    if ($LASTEXITCODE -ne 0) { Fail "docker push failed." }
    OK "Pushed: $GhcrTag"

    Write-Host ""
    Write-Host ">>> Paste this into the hackathon Docker Image field:" -ForegroundColor Cyan
    Write-Host "    $GhcrTag" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Skipping push. Re-run with -GhcrUser YOUR_GITHUB_USERNAME to push." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  All checks passed. Ready for submission!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
