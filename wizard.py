import sys
import os
import urllib.request
import winshell  # For shortcut creation
from win32com.client import Dispatch
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, create_shortcut):
        super().__init__()
        self.create_shortcut = create_shortcut

    def run(self):
        install_dir = r"C:\Program Files\Anashazz\Anas-FPV-Drone"
        game_exe_path = os.path.join(install_dir, "internal_game_engine_V1.exe")
        
        files_to_download = [
            {
                "url": "https://github.com/anashazz/Anas-FPV-Drone/releases/download/game-engine/internal_game_engine_V1.exe",
                "name": "internal_game_engine_V1.exe"
            },
            {
                "url": "https://github.com/anashazz/Anas-FPV-Drone/raw/main/three.min.js",
                "name": "three.min.js"
            }
        ]

        try:
            # Create directory
            if not os.path.exists(install_dir):
                os.makedirs(install_dir)

            for i, item in enumerate(files_to_download):
                file_path = os.path.join(install_dir, item["name"])
                req = urllib.request.Request(item["url"], headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req) as response, open(file_path, 'wb') as f:
                    total_size = int(response.info().get('Content-Length', 0))
                    downloaded = 0
                    while True:
                        chunk = response.read(8192)
                        if not chunk: break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            p = int((i / len(files_to_download) * 100) + (downloaded / total_size * 50))
                            self.progress.emit(p)

            # Create Desktop Shortcut if checked
            if self.create_shortcut:
                desktop = winshell.desktop()
                path = os.path.join(desktop, "Anas FPV Drone.lnk")
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = game_exe_path
                shortcut.WorkingDirectory = install_dir
                shortcut.IconLocation = game_exe_path
                shortcut.save()

            self.finished.emit(True, "Installation Successful!")
        except Exception as e:
            self.finished.emit(False, str(e))

class AnasInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Anas FPV Drone - Setup")
        self.setFixedSize(400, 280)
        self.setStyleSheet("background-color: black; color: cyan; font-family: 'Segoe UI', Arial;")

        layout = QVBoxLayout()
        
        self.label = QLabel("Ready to install Anas FPV Drone v1.0")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Shortcut Checkbox
        self.shortcut_cb = QCheckBox("Create Desktop Shortcut")
        self.shortcut_cb.setChecked(True)
        self.shortcut_cb.setStyleSheet("QCheckBox { spacing: 10px; } QCheckBox::indicator { border: 1px solid cyan; width: 15px; height: 15px; } QCheckBox::indicator:checked { background-color: cyan; }")
        layout.addWidget(self.shortcut_cb)

        self.pbar = QProgressBar()
        self.pbar.setStyleSheet("QProgressBar { border: 2px solid cyan; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #008b8b; }")
        layout.addWidget(self.pbar)

        self.btn = QPushButton("INSTALL NOW")
        self.btn.setStyleSheet("QPushButton { background-color: cyan; color: black; font-weight: bold; padding: 12px; border-radius: 5px; } QPushButton:hover { background-color: #00ffff; }")
        self.btn.clicked.connect(self.start_install)
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def start_install(self):
        self.btn.setEnabled(False)
        self.shortcut_cb.setEnabled(False)
        self.label.setText("Installing to Program Files...")
        self.thread = DownloadThread(self.shortcut_cb.isChecked())
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def update_progress(self, val):
        self.pbar.setValue(val)

    def on_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Fly Time!", "Installation Complete!\n\nNote: if the game won't open, use Vista Compatibility mode.")
            self.close()
        else:
            QMessageBox.critical(self, "Install Failed", f"Error: {message}\n\nPlease run as Administrator.")
            self.btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnasInstaller()
    window.show()
    sys.exit(app.exec())