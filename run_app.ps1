# InfoPulse App Command Line Runner (Runs Backend + Android Frontend)

$SDK_DIR = "D:\ProgramFiles\AppData"
$JAVA_HOME_DIR = "I:\ProgramFiles\Android\jbr"

# Set up environment variables
$env:JAVA_HOME = $JAVA_HOME_DIR
$env:PATH = "$JAVA_HOME_DIR\bin;$SDK_DIR\platform-tools;$SDK_DIR\emulator;$env:PATH"
$env:PYTHONUTF8 = 1

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  InfoPulse App - All-in-One Runner" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Start FastAPI backend (uvicorn) in the background so the App can fetch real data.
#    Emulator reaches the host via 10.0.2.2:8000 (see ApiClient.kt).
Write-Host "[1/5] Starting FastAPI backend (uvicorn) on :8000 ..." -ForegroundColor Yellow
Push-Location backend
Start-Process -FilePath "python" `
    -ArgumentList "-m","uvicorn","infopulse.api.main:app","--host","0.0.0.0","--port","8000" `
    -WindowStyle Minimized
Pop-Location

Write-Host "Waiting for backend to come up..." -ForegroundColor Magenta
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/categories" -UseBasicParsing -TimeoutSec 3
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}
if ($ready) {
    Write-Host "Backend is up. Seeding latest briefing for cat_ai..." -ForegroundColor Green
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/api/v1/categories/cat_ai/refresh" `
            -Method Post -ContentType "application/json" -Body "{}" | Out-Null
    } catch {
        Write-Host "Seed refresh failed (App still launches; pull-to-refresh in app)." -ForegroundColor Magenta
    }
} else {
    Write-Host "Backend not ready in time; App will fall back to mock data." -ForegroundColor Magenta
}

# 2. Check if ADB works & Start emulator if needed
Write-Host "[2/5] Checking connected devices..." -ForegroundColor Yellow
$devices = adb devices | Select-String -Pattern "device$"
if ($devices.Count -eq 0) {
    Write-Host "No running emulators/devices detected. Attempting to start default emulator..." -ForegroundColor Magenta
    # List available emulators
    $emulators = emulator -list-avds
    if ($emulators) {
        $avdName = $emulators[0]
        Write-Host "Starting emulator: $avdName in background..." -ForegroundColor Magenta
        Start-Process -FilePath "emulator" -ArgumentList "-avd $avdName" -WindowStyle Minimized
        
        Write-Host "Waiting for emulator to boot (this might take a moment)..." -ForegroundColor Magenta
        adb wait-for-device
        # Additional wait for system to boot
        Start-Sleep -Seconds 10
    } else {
        Write-Host "Error: No Android emulators found. Please create one in Android Studio first." -ForegroundColor Red
        Exit 1
    }
} else {
    Write-Host "Detected connected device(s):" -ForegroundColor Green
    foreach ($dev in $devices) {
        Write-Host "  - $dev" -ForegroundColor Green
    }
}

# 3. Build and Install the App
Write-Host "[3/5] Compiling and installing the Android App..." -ForegroundColor Yellow
Push-Location android
.\gradlew.bat installDebug
$buildResult = $LASTEXITCODE
Pop-Location

if ($buildResult -ne 0) {
    Write-Host "Build failed with exit code $buildResult" -ForegroundColor Red
    Exit $buildResult
}

# 4. Start the App
Write-Host "[4/5] Launching the App on the device..." -ForegroundColor Yellow
adb shell am start -n com.infopulse.app/com.infopulse.app.MainActivity

# 5. Done
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  Success! InfoPulse App is running!  " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
