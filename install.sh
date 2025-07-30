#!/bin/bash

echo "🔧 Setting up Connection Manager..."

# --- Step 1: Install system dependencies ---
echo "📦 Installing system packages (sshpass, freerdp)..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update
    sudo apt install -y sshpass freerdp2-x11 python3-venv
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install freerdp sshpass
fi

# --- Step 2: Set up Python virtual environment ---
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# --- Step 3: Install Python dependencies ---
echo "📦 Installing Python packages (PyQt6, cryptography)..."
pip install --upgrade pip
pip install PyQt6 cryptography

# --- Step 4: Create encryption key ---
KEY_FILE="key.key"
if [ ! -f "$KEY_FILE" ]; then
    echo "🔐 Generating encryption key..."
    python3 -c "
from cryptography.fernet import Fernet
with open('$KEY_FILE', 'wb') as f:
    f.write(Fernet.generate_key())
"
else
    echo "✅ Encryption key already exists: $KEY_FILE"
fi

# --- Step 5: Create example connections.json ---
CONN_FILE="connections.json"
if [ ! -f "$CONN_FILE" ]; then
    echo "📝 Creating example connections.json..."
    cat > "$CONN_FILE" <<EOF
[
    {
        "name": "SSH with Key",
        "type": "ssh",
        "address": "user@192.168.1.100",
        "private_key": "~/.ssh/id_rsa"
    },
    {
        "name": "Custom Script",
        "type": "custom",
        "command": "echo 'Running custom script...'"
    }
]
EOF
else
    echo "✅ connections.json already exists"
fi

# --- Step 7: Create .desktop entry ---
DESKTOP_FILE="$HOME/.local/share/applications/connection-manager.desktop"
APP_DIR="$(pwd)"
echo "🖥️ Creating desktop entry..."

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Connection Manager
Comment=Manage and launch SSH, RDP, and custom connections
Exec=bash -c 'cd "$APP_DIR" && source venv/bin/activate && python3 main.py'
Icon=utilities-terminal
Terminal=false
Categories=Network;Utility;
EOF

chmod +x "$DESKTOP_FILE"

# Optional: Add launcher to desktop
cp "$DESKTOP_FILE" "$HOME/Desktop/"
chmod +x "$HOME/Desktop/connection-manager.desktop"

echo "✅ Desktop entry created at:"
echo "   $DESKTOP_FILE"
echo "   and on your Desktop"

# --- Step 6: Run the app ---
echo "🚀 Launching the application..."
python3 main.py
