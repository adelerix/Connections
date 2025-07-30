# install.ps1

Write-Host "`n🔧 Setting up Connection Manager for Windows..."

# --- Step 1: Check for Python ---
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "❌ Python is not installed. Please install Python 3.10+ from https://www.python.org/downloads/windows/"
    exit 1
}

# --- Step 2: Create virtual environment ---
Write-Host "`n🐍 Creating virtual environment..."
python -m venv venv

# --- Step 3: Activate virtual environment ---
$envScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $envScript) {
    & $envScript
} else {
    Write-Error "❌ Cannot find activate script at $envScript"
    exit 1
}

# --- Step 4: Install dependencies ---
Write-Host "`n📦 Installing Python packages (PyQt6, cryptography)..."
pip install --upgrade pip
pip install PyQt6 cryptography

# --- Step 5: Generate key.key if not exists ---
$keyFile = "key.key"
if (-Not (Test-Path $keyFile)) {
    Write-Host "`n🔐 Generating encryption key..."
    python -c "from cryptography.fernet import Fernet; open('$keyFile', 'wb').write(Fernet.generate_key())"
} else {
    Write-Host "✅ key.key already exists."
}

# --- Step 6: Create example connections.json ---
$jsonFile = "connections.json"
if (-Not (Test-Path $jsonFile)) {
    Write-Host "`n📝 Creating example connections.json..."
    @'
[
    {
        "name": "SSH with Private Key",
        "type": "ssh",
        "address": "user@192.168.1.100",
        "private_key": "C:\\Users\\YourName\\.ssh\\id_rsa"
    },
    {
        "name": "Run Script",
        "type": "custom",
        "command": "echo Hello from Windows"
    }
]
'@ | Out-File -Encoding UTF8 $jsonFile
} else {
    Write-Host "✅ connections.json already exists."
}

# --- Step 8: Create desktop shortcut ---
Write-Host "`n📎 Creating desktop shortcut..."

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Connection Manager.lnk"

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)

$appDir = (Get-Location).Path
$activateScript = Join-Path $appDir "venv\Scripts\Activate.ps1"

$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-ExecutionPolicy Bypass -NoExit -Command `"cd '$appDir'; . '$activateScript'; python main.py`""
$shortcut.WorkingDirectory = $appDir
$shortcut.WindowStyle = 1
$shortcut.IconLocation = "$env:SystemRoot\System32\mstsc.exe,0"  # Optional icon
$shortcut.Save()

Write-Host "✅ Shortcut created on Desktop: 'Connection Manager.lnk'"


# --- Step 7: Launch the application ---
Write-Host "`n🚀 Launching the application..."
python main.py
