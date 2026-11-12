param (
    [string]$ModelName = "vosk-model-small-en-us-0.15",
    [string]$DestinationDir = ".\models"
)

$ErrorActionPreference = "Stop"

# Construct URLs and file paths
$ModelUrl = "https://alphacephei.com"
$ZipPath = Join-Path $env:TEMP "$ModelName.zip"
$ExtractedModelPath = Join-Path $DestinationDir $ModelName

# Create destination directory if it does not exist
if (-not (Test-Path -Path $DestinationDir)) {
    New-Item -ItemType Directory -Path $DestinationDir | Out-Null
}

# Skip if the model is already installed
if (Test-Path -Path $ExtractedModelPath) {
    Write-Host "Model '$ModelName' is already installed at $ExtractedModelPath" -ForegroundColor Yellow
    exit 0
}

try {
    Write-Host "Downloading $ModelName from Alpha Cephei..." -ForegroundColor Cyan
    # Use Invoke-WebRequest with progress bar disabled for much faster downloads
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $ModelUrl -OutFile $ZipPath

    Write-Host "Extracting archive to $DestinationDir..." -ForegroundColor Cyan
    Expand-Archive -Path $ZipPath -DestinationPath $DestinationDir -Force

    Write-Host "Successfully installed $ModelName to $ExtractedModelPath" -ForegroundColor Green
}
catch {
    Write-Error "Failed to install Vosk model. Check that '$ModelName' is a valid model name. Error: $_"
}
finally {
    # Clean up the downloaded zip file
    if (Test-Path -Path $ZipPath) {
        Remove-Item -Path $ZipPath -Force
    }
}
