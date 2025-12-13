from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QDateEdit,
                             QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from database import dao


class UyeGuncelleDialog(QDialog):
    """Üye bilgilerini güncelleme dialog penceresi."""
    uye_guncellendi = pyqtSignal()  # Güncelleme başarılı olduğunda sinyal gönder
    
    def __init__(self, uye_id, parent=None):
        super().__init__(parent)
        self.uye_id = uye_id
        self.setWindowTitle("Üye Bilgilerini Güncelle")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.initUI()
        self.uye_bilgilerini_yukle()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık
        baslik = QLabel('Üye Bilgilerini Düzenle')
        baslik.setFont(QFont('Arial', 16, QFont.Bold))
        baslik.setStyleSheet('color: #2c3e50;')
        layout.addWidget(baslik)
        
        # Kişisel Bilgiler
        kisisel_group = QGroupBox('Kişisel Bilgiler')
        kisisel_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        kisisel_layout = QFormLayout()
        kisisel_layout.setSpacing(15)
        
        self.ad_input = QLineEdit()
        self.styleInput(self.ad_input)
        
        self.soyad_input = QLineEdit()
        self.styleInput(self.soyad_input)
        
        # TC değiştirilemez
        self.tc_label = QLabel()
        self.tc_label.setStyleSheet("color: #7f8c8d; font-weight: bold; padding: 8px;")
        
        self.dogum_tarihi = QDateEdit()
        self.dogum_tarihi.setCalendarPopup(True)
        self.dogum_tarihi.setDisplayFormat('dd/MM/yyyy')
        self.styleInput(self.dogum_tarihi)
        
        self.cinsiyet_combo = QComboBox()
        self.cinsiyet_combo.addItems(['Erkek', 'Kadın', 'Belirtmek İstemiyorum'])
        self.styleInput(self.cinsiyet_combo)
        
        kisisel_layout.addRow('Ad *:', self.ad_input)
        kisisel_layout.addRow('Soyad *:', self.soyad_input)
        kisisel_layout.addRow('TC Kimlik No:', self.tc_label)
        kisisel_layout.addRow('Doğum Tarihi:', self.dogum_tarihi)
        kisisel_layout.addRow('Cinsiyet:', self.cinsiyet_combo)
        
        kisisel_group.setLayout(kisisel_layout)
        layout.addWidget(kisisel_group)
        
        # İletişim Bilgileri
        iletisim_group = QGroupBox('İletişim Bilgileri')
        iletisim_group.setStyleSheet(kisisel_group.styleSheet())
        iletisim_layout = QFormLayout()
        iletisim_layout.setSpacing(15)
        
        self.telefon_input = QLineEdit()
        self.telefon_input.setPlaceholderText('0XXX XXX XX XX')
        self.styleInput(self.telefon_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('ornek@email.com')
        self.styleInput(self.email_input)
        
        iletisim_layout.addRow('Telefon:', self.telefon_input)
        iletisim_layout.addRow('E-posta:', self.email_input)
        
        iletisim_group.setLayout(iletisim_layout)
        layout.addWidget(iletisim_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        iptal_btn = QPushButton('✖ İptal')
        iptal_btn.setFixedHeight(45)
        iptal_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        iptal_btn.clicked.connect(self.reject)
        
        kaydet_btn = QPushButton('💾 Güncelle')
        kaydet_btn.setFixedHeight(45)
        kaydet_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        kaydet_btn.clicked.connect(self.uye_guncelle)
        
        button_layout.addWidget(iptal_btn)
        button_layout.addWidget(kaydet_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def styleInput(self, widget):
        widget.setFixedHeight(40)
        widget.setStyleSheet("""
            QLineEdit, QComboBox, QDateEdit {
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #e94560;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #dfe4ea;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e8f4f8;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
    
    def uye_bilgilerini_yukle(self):
        """Mevcut üye bilgilerini forma yükle."""
        uye = dao.get_user(self.uye_id)
        if uye:
            # PostgreSQL dict format
            self.ad_input.setText(uye.get('first_name', ''))
            self.soyad_input.setText(uye.get('last_name', ''))
            self.tc_label.setText(uye.get('tc_number', ''))
            self.telefon_input.setText(uye.get('phone', '') or "")
            self.email_input.setText(uye.get('email', '') or "")
            
            if uye.get('birth_date'):
                tarih_str = str(uye['birth_date'])
                try:
                    tarih = QDate.fromString(tarih_str, 'yyyy-MM-dd')
                    self.dogum_tarihi.setDate(tarih)
                except:
                    self.dogum_tarihi.setDate(QDate.currentDate().addYears(-20))
            
            if uye.get('gender'):
                index = self.cinsiyet_combo.findText(uye['gender'])
                if index >= 0:
                    self.cinsiyet_combo.setCurrentIndex(index)
    
    def uye_guncelle(self):
        """Üye bilgilerini güncelle."""
        if not self.ad_input.text() or not self.soyad_input.text():
            QMessageBox.warning(self, 'Uyarı', 'Ad ve Soyad alanları zorunludur!')
            return
        
        basarili = dao.update_user(
            self.uye_id,
            first_name=self.ad_input.text(),
            last_name=self.soyad_input.text(),
            phone=self.telefon_input.text(),
            email=self.email_input.text(),
            birth_date=self.dogum_tarihi.date().toPyDate(),
            gender=self.cinsiyet_combo.currentText()
        )
        
        if basarili:
            QMessageBox.information(self, 'Başarılı', 'Üye bilgileri başarıyla güncellendi!')
            self.uye_guncellendi.emit()
            self.accept()
        else:
            QMessageBox.warning(self, 'Hata', 'Güncelleme sırasında bir hata oluştu!')
