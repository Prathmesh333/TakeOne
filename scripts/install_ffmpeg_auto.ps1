# FFmpeg Auto-Installer for Windows
# Downloads and installs FFmpeg automatically

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "FFmpeg Auto-Installer" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if FFmpeg is already installed
$ffmpegExists = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegExists) {
    Write-Host "✅ FFmpeg is already installed!" -ForegroundColor Green
    ffmpeg -version | Select-Object -First 1
    exit 0
}

Write-Host "Downloading FFmpeg..." -ForegroundColor Yellow

# Create temp directory
$tempDir = "$env:TEMP\ffmpeg_install"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Download FFmpeg (essentials build)
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipPath = "$tempDir\ffmpeg.zip"

try {
    Write-Host "Downloading from: $ffmpegUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $zipPath -UseBasicParsing
    Write-Host "✅ Download complete" -ForegroundColor Green
} catch {
    Write-Host "❌ Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install manually using install_ffmpeg.bat" -ForegroundColor Yellow
    pause
    exit 1
}

# Extract
Write-Host "Extracting FFmpeg..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
    
    # Find the extracted folder (name varies by version)
    $extractedFolder = Get-ChildItem -Path $tempDir -Directory | Where-Object { $_.Name -like "ffmpeg-*" } | Select-Object -First 1
    
    if (-not $extractedFolder) {
        throw "Could not find extracted FFmpeg folder"
    }
    
    # Install to C:\ffmpeg
    $installPath = "C:\ffmpeg"
    if (Test-Path $installPath) {
        Write-Host "Removing old installation..." -ForegroundColor Gray
        Remove-Item -Path $installPath -Recurse -Force
    }
    
    Write-Host "Installing to: $installPath" -ForegroundColor Gray
    Move-Item -Path $extractedFolder.FullName -Destination $installPath -Force
    Write-Host "✅ Installation complete" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Extraction/Installation failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install manually using install_ffmpeg.bat" -ForegroundColor Yellow
    pause
    exit 1
}

# Add to PATH
Write-Host "Adding FFmpeg to PATH..." -ForegroundColor Yellow
$ffmpegBin = "$installPath\bin"

try {
    # Get current PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    
    # Check if already in PATH
    if ($currentPath -notlike "*$ffmpegBin*") {
        # Add to PATH (requires admin)
        $newPath = "$currentPath;$ffmpegBin"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "✅ Added to system PATH" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANT: Restart your terminal for changes to take effect!" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Already in PATH" -ForegroundColor Green
    }
    
    # Also add to current session
    $env:Path += ";$ffmpegBin"
    
} catch {
    Write-Host "⚠️  Could not add to system PATH (requires admin)" -ForegroundColor Yellow
    Write-Host "   Please add manually: $ffmpegBin" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Or run this script as Administrator" -ForegroundColor Gray
}

# Cleanup
Write-Host "Cleaning up..." -ForegroundColor Gray
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow

# Test FFmpeg
try {
    $version = & "$ffmpegBin\ffmpeg.exe" -version 2>&1 | Select-Object -First 1
    Write-Host "✅ $version" -ForegroundColor Green
    Write-Host ""
    Write-Host "FFmpeg is ready to use!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Remember to restart your terminal/IDE for PATH changes!" -ForegroundColor Yellow
} catch {
    Write-Host "⚠️  FFmpeg installed but not in PATH yet" -ForegroundColor Yellow
    Write-Host "   Restart your terminal and try: ffmpeg -version" -ForegroundColor Gray
}

Write-Host ""
pause
