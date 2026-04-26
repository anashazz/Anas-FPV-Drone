import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage

# --- STEP 1: CHROMIUM FLAGS ---
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--allow-file-access-from-files --disable-web-security"

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class AnasFPVDrone(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.setWindowTitle("Anas FPV Drone")
        self.setWindowIcon(QIcon(get_resource_path("icon.png")))
        
        # Initialize the Browser
        self.browser = QWebEngineView()
        
        # --- STEP 2: PERMISSION HANDLING ---
        self.browser.page().featurePermissionRequested.connect(self.handle_feature_permission)
        
        # --- STEP 3: BROWSER SETTINGS ---
        settings = self.browser.settings()
        
        # We use the direct Attribute access here to avoid the AttributeError
        Attr = QWebEngineSettings.WebAttribute
        
        settings.setAttribute(Attr.WebGLEnabled, True)
        settings.setAttribute(Attr.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(Attr.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(Attr.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(Attr.PlaybackRequiresUserGesture, False)
        settings.setAttribute(Attr.JavascriptEnabled, True)
        
        # This was the line causing your error - updated for compatibility
        if hasattr(Attr, 'DeveloperExtrasEnabled'):
            settings.setAttribute(Attr.DeveloperExtrasEnabled, True)

        # Load your game
        game_path = get_resource_path("index.html")
        self.browser.setUrl(QUrl.fromLocalFile(game_path))
        
        self.setCentralWidget(self.browser)
        self.showMaximized()

    def handle_feature_permission(self, securityOrigin, feature):
        """ Automatically grant permission for Mouse Lock """
        if feature == QWebEnginePage.Feature.MouseLock:
            self.browser.page().setFeaturePermission(
                securityOrigin, 
                feature, 
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )

    def keyPressEvent(self, event):
        """ Press Escape to exit the game """
        if event.key() == Qt.Key.Key_Escape:
            self.close()

# --- STEP 4: START APPLICATION ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_resource_path("icon.png")))
    
    window = AnasFPVDrone()
    window.show()
    
    sys.exit(app.exec())