param(
    [Parameter(Mandatory=$false)]
    [string[]] $ArgsFromUser
)

# === Function for colored output ===
function Write-Info($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-ErrorMsg($msg) { Write-Host $msg -ForegroundColor Red }
function Write-Success($msg) { Write-Host $msg -ForegroundColor Green }

# === Check if user passed arguments ===
if (-not $ArgsFromUser -or $ArgsFromUser.Count -eq 0) {
    Write-ErrorMsg "Usage: .\run.ps1 --cli, --bot, or both"
    Write-Host "Example: .\run.ps1 --cli --bot"
    exit 1
}

# === Auto-generate hiscore metadata first ===
Write-Info "Auto-generating python files..."
python "util\osrs_api\hiscore_mdata_autogen.py"
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Error running hiscore_mdata_autogen.py. Exiting."
    exit 1
}

# === Run main.py with user arguments ===
Write-Info "Running main.py with arguments: $ArgsFromUser"
python "main.py" @ArgsFromUser
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "main.py exited with errors."
    exit 1
}

Write-Success "All tasks completed successfully."
