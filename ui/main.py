
import sys
import os

# Proje root dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from giris_ekrani import GirisEkrani


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



