
import sys
import os
import PyQt5
# Proje root dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from giris_ekrani import GirisEkrani
try:
    import PyQt5
    plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
except ImportError:
    pass # Henüz yüklü değilse hata vermesin
from PyQt5.QtWidgets import QApplication, QMainWindow
def main():
    app = QApplication(sys.argv)
    
    # Uygulama stili
    app.setStyle('Fusion')
    
    # Uygulama bilgileris
    app.setApplicationName("Spor Salonu Yönetim Sistemi")
    app.setOrganizationName("Spor Salonu")
    
    # Giriş ekranını başla
    giris = GirisEkrani()
    giris.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



