# 🔌 Connection Manager

A cross-platform Python Qt6 application to manage and launch SSH, RDP, and custom command connections — all in one place.

Built with simplicity, security, and convenience in mind, this tool allows users to manage remote access workflows securely and efficiently.

---

## ✨ Features

- ✅ **Add, edit, and delete** SSH, RDP, and custom command connections
- 🔐 **Encrypted password storage** using Fernet (`cryptography`)
- 💻 **SSH options**:
  - Password-based (with optional `sshpass` on Linux)
  - Private key-based
- 🖥️ **RDP support**:
  - Windows: Launches with `mstsc`
  - Linux/macOS: Uses `xfreerdp`
- 📋 **Sorted list view** for easy organization
- ⚙️ Creates application menu or desktop shortcuts on all platforms

---

## 💻 Installation

### 🌨️ Linux / macOS

#### 1. Clone the repository

```bash
git clone https://github.com/youruser/connection-manager.git
cd connection-manager
```

#### 2. Run the setup script

```bash
chmod +x install.sh
./install.sh
```

🔹 This will:

- Install dependencies (`sshpass`, `freerdp2-x11`, `PyQt6`, etc.)
- Create a Python virtual environment
- Install Python packages
- Generate `key.key` for encryption
- Create an example `connections.json`
- Add a desktop launcher

---

### 🦠 Windows

#### 1. Clone the repository

```powershell
git clone https://github.com/youruser/connection-manager.git
cd connection-manager
```

#### 2. Run the installer

```powershell
Set-ExecutionPolicy RemoteSigned -Scope Process
.\install.ps1
```

🔹 This will:

- Set up a virtual environment
- Install dependencies
- Generate `key.key` for encryption
- Create an example `connections.json`
- Create a desktop shortcut

---

## 🔐 Encrypted Credential Storage

- Passwords for **SSH** and **RDP** are encrypted using a local `key.key` file (auto-generated).
- Only the local system can decrypt the passwords.
- To manually encrypt a password:

```python
from cryptography.fernet import Fernet
key = open("key.key", "rb").read()
fernet = Fernet(key)
print(fernet.encrypt("your-password".encode()).decode())
```

---

## 🧪 Requirements

- Python 3.8+
- PyQt6
- cryptography
- Linux/macOS:
  - `sshpass` (for password-based SSH)
  - `freerdp2-x11` (for RDP)

---


## 📋 Usage

- Launch from the menu or Desktop shortcut
- Add new connections (SSH, RDP, custom)
- Use encrypted credentials securely
- Double-click a connection and hit **Connect**

---

## 📄 License

MIT © 2025 Adele Rix
This project is free to use and modify.



