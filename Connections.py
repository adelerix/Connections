import sys
import json
import subprocess
import platform
from pathlib import Path
from cryptography.fernet import Fernet

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton,
    QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt

DATA_FILE = Path("connections.json")
KEY_FILE = Path("key.key")


def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)


def load_key():
    if not KEY_FILE.exists():
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()


fernet = Fernet(load_key())


def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()


def decrypt_password(encrypted: str) -> str:
    try:
        return fernet.decrypt(encrypted.encode()).decode()
    except Exception:
        return ""


class ConnectionManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connection Manager")
        self.resize(600, 400)

        self.connections = []
        self.load_connections()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.list_widget = QListWidget()
        self.refresh_list()
        self.layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.remove_button = QPushButton("Remove")

        self.connect_button.clicked.connect(self.connect_to_selected)
        self.add_button.clicked.connect(self.add_connection)
        self.edit_button.clicked.connect(self.edit_selected)
        self.remove_button.clicked.connect(self.remove_selected)

        for btn in (self.connect_button, self.add_button, self.edit_button, self.remove_button):
            button_layout.addWidget(btn)

        self.layout.addLayout(button_layout)

    def load_connections(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, "r") as f:
                self.connections = json.load(f)

    def save_connections(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.connections, f, indent=4)

    def refresh_list(self):
        self.list_widget.clear()
        self.connections.sort(key=lambda c: c["name"].lower())
        for conn in self.connections:
            self.list_widget.addItem(f"{conn['name']} ({conn['type']})")

    def connect_to_selected(self):
        idx = self.list_widget.currentRow()
        if idx == -1:
            QMessageBox.warning(self, "No Selection", "Please select a connection.")
            return

        conn = self.connections[idx]
        system = platform.system().lower()

        try:
            if conn["type"] == "ssh":
                if "private_key" in conn and conn["private_key"].strip():
                    subprocess.Popen(["ssh", "-i", conn["private_key"], conn["address"]])
                elif "password" in conn:
                    # Using sshpass for password automation (Linux only)
                    password = decrypt_password(conn["password"])
                    subprocess.Popen(["sshpass", "-p", password, "ssh", conn["address"]])
                else:
                    subprocess.Popen(["ssh", conn["address"]])

            elif conn["type"] == "rdp":
                if "windows" in system:
                    subprocess.Popen(["mstsc", "/v:" + conn["address"]])
                else:
                    cmd = ["xfreerdp", f"/v:{conn['address']}"]
                    if "username" in conn:
                        cmd.append(f"/u:{conn['username']}")
                    if "password" in conn:
                        cmd.append(f"/p:{decrypt_password(conn['password'])}")
                    subprocess.Popen(cmd)

            elif conn["type"] == "custom":
                subprocess.Popen(conn["command"], shell=True)

        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def add_connection(self):
        name, ok = QInputDialog.getText(self, "Name", "Connection Name:")
        if not ok or not name.strip():
            return

        type_, ok = QInputDialog.getItem(self, "Type", "Connection Type:", ["ssh", "rdp", "custom"], editable=False)
        if not ok:
            return

        new_conn = {"name": name.strip(), "type": type_}

        if type_ == "custom":
            cmd, ok = QInputDialog.getText(self, "Command", "Custom Command:")
            if ok and cmd.strip():
                new_conn["command"] = cmd.strip()

        elif type_ == "ssh":
            addr, ok = QInputDialog.getText(self, "SSH", "SSH Address (user@host):")
            if not ok or not addr.strip():
                return
            new_conn["address"] = addr.strip()

            use_key, ok = QInputDialog.getItem(self, "SSH Auth", "Use private key or password?", ["private_key", "password"], editable=False)
            if not ok:
                return

            if use_key == "private_key":
                key, ok = QInputDialog.getText(self, "SSH Key", "Path to private key:")
                if ok and key.strip():
                    new_conn["private_key"] = key.strip()
            else:
                pw, ok = QInputDialog.getText(self, "SSH Password", "Password (optional):")
                if ok and pw.strip():
                    new_conn["password"] = encrypt_password(pw.strip())

        elif type_ == "rdp":
            addr, ok = QInputDialog.getText(self, "RDP", "RDP Address (IP or host):")
            if not ok or not addr.strip():
                return
            new_conn["address"] = addr.strip()

            user, ok = QInputDialog.getText(self, "RDP", "Username (optional):")
            if ok and user.strip():
                new_conn["username"] = user.strip()

            pw, ok = QInputDialog.getText(self, "RDP", "Password (optional):")
            if ok and pw.strip():
                new_conn["password"] = encrypt_password(pw.strip())

        self.connections.append(new_conn)
        self.save_connections()
        self.refresh_list()

    def edit_selected(self):
        idx = self.list_widget.currentRow()
        if idx == -1:
            QMessageBox.warning(self, "No Selection", "Please select a connection to edit.")
            return

        conn = self.connections[idx]
        updated = {"type": conn["type"]}

        name, ok = QInputDialog.getText(self, "Edit Name", "Connection Name:", text=conn["name"])
        if not ok or not name.strip():
            return
        updated["name"] = name.strip()

        if conn["type"] == "custom":
            cmd, ok = QInputDialog.getText(self, "Edit Command", "Custom Command:", text=conn.get("command", ""))
            if ok and cmd.strip():
                updated["command"] = cmd.strip()

        elif conn["type"] == "ssh":
            addr, ok = QInputDialog.getText(self, "Edit SSH", "SSH Address:", text=conn.get("address", ""))
            if not ok or not addr.strip():
                return
            updated["address"] = addr.strip()

            auth_method = "private_key" if "private_key" in conn else "password"
            method, ok = QInputDialog.getItem(self, "SSH Auth", "Use private key or password?",
                                              ["private_key", "password"],
                                              current=0 if auth_method == "private_key" else 1,
                                              editable=False)
            if method == "private_key":
                key, ok = QInputDialog.getText(self, "Edit Key", "Private key path:", text=conn.get("private_key", ""))
                if ok and key.strip():
                    updated["private_key"] = key.strip()
            else:
                pw, ok = QInputDialog.getText(self, "Edit SSH Password", "Password:",
                                              text=decrypt_password(conn.get("password", "")))
                if ok and pw.strip():
                    updated["password"] = encrypt_password(pw.strip())

        elif conn["type"] == "rdp":
            addr, ok = QInputDialog.getText(self, "Edit RDP", "RDP Address:", text=conn.get("address", ""))
            if not ok or not addr.strip():
                return
            updated["address"] = addr.strip()

            user, ok = QInputDialog.getText(self, "Edit RDP", "Username:", text=conn.get("username", ""))
            if ok and user.strip():
                updated["username"] = user.strip()

            pw, ok = QInputDialog.getText(self, "Edit RDP", "Password:", text=decrypt_password(conn.get("password", "")))
            if ok and pw.strip():
                updated["password"] = encrypt_password(pw.strip())

        self.connections[idx] = updated
        self.save_connections()
        self.refresh_list()

    def remove_selected(self):
        idx = self.list_widget.currentRow()
        if idx == -1:
            QMessageBox.warning(self, "No Selection", "Please select a connection to remove.")
            return
        self.connections.pop(idx)
        self.save_connections()
        self.refresh_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConnectionManager()
    window.show()
    sys.exit(app.exec())
