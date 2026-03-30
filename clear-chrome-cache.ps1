# Requires -RunAsAdministrator (Optional but recommended if there are permission issues)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      Clearing Google Chrome Cache        " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Closing Google Chrome..." -ForegroundColor Yellow
Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue

# Give it a tiny bit of time to release file locks
Start-Sleep -Seconds 2

$userDataPath = "$env:LOCALAPPDATA\Google\Chrome\User Data"

if (-not (Test-Path $userDataPath)) {
    Write-Host "Error: Chrome User Data directory not found." -ForegroundColor Red
    Write-Host "Paths checked: $userDataPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

$cachePaths = @(
    "Default\Cache",
    "Default\Code Cache",
    "Default\GPUCache",
    "System Profile\Cache",
    "ShaderCache",
    "GrShaderCache"
)

# Find all 'Profile *' directories and add their cache paths
$profiles = Get-ChildItem -Path $userDataPath -Filter "Profile *" -Directory -ErrorAction SilentlyContinue
foreach ($profile in $profiles) {
    $cachePaths += "$($profile.Name)\Cache"
    $cachePaths += "$($profile.Name)\Code Cache"
    $cachePaths += "$($profile.Name)\GPUCache"
}

Write-Host "Deleting cache files..." -ForegroundColor Yellow
$clearedCount = 0

foreach ($relPath in $cachePaths) {
    $fullPath = Join-Path -Path $userDataPath -ChildPath $relPath -Resolve -ErrorAction SilentlyContinue
    if ($fullPath -and (Test-Path $fullPath)) {
        Remove-Item -Path "$fullPath\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Cleared: $relPath" -ForegroundColor DarkGray
        $clearedCount++
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
if ($clearedCount -gt 0) {
    Write-Host "  Chrome Cache successfully cleared!" -ForegroundColor Green
} else {
    Write-Host "  No cache files found to clear.    " -ForegroundColor Green
}
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
