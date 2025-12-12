from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QGroupBox, QFormLayout, 
                             QMessageBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class UyelikYenileDialog(QDialog):
    """Üyelik yenileme dialog penceresi."""
    uyelik_yenilendi = pyqtSignal()
    
    def __init__(self, db, uye_id, uye_ad, parent=None):
        super().__init__(parent)
        self.db = db
        self.uye_id = uye_id
        self.uye_ad = uye_ad
        self.setWindowTitle("Üyelik Yenile")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık
        baslik = QLabel(f'Üyelik Yenileme - {self.uye_ad}')
        baslik.setFont(QFont('Arial', 16, QFont.Bold))
        baslik.setStyleSheet('color: #2c3e50;')
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)
        
        # Bilgi mesajı
        info_label = QLabel('Yeni paket seçin ve ödeme tipini belirleyin.')
        info_label.setFont(QFont('Arial', 11))
        info_label.setStyleSheet('color: #7f8c8d; padding: 5px;')
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Paket Seçimi
        paket_group = QGroupBox('Paket Seçimi')
        paket_group.setStyleSheet("""
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
        paket_layout = QFormLayout()
        paket_layout.setSpacing(15)
        
        self.paket_combo = QComboBox()
        self.paketleri_yukle()
        self.styleInput(self.paket_combo)
        
        paket_layout.addRow('Yeni Paket *:', self.paket_combo)
        paket_group.setLayout(paket_layout)
        layout.addWidget(paket_group)
        
        # Ödeme Tipi
        odeme_group = QGroupBox('Ödeme Tipi')
        odeme_group.setStyleSheet(paket_group.styleSheet())
        odeme_layout = QVBoxLayout()
        odeme_layout.setSpacing(10)
        
        self.odeme_button_group = QButtonGroup(self)
        
        self.nakit_radio = QRadioButton('💵 Nakit')
        self.nakit_radio.setChecked(True)
        self.nakit_radio.setStyleSheet("font-size: 13px; padding: 5px;")
        
        self.kredi_radio = QRadioButton('💳 Kredi Karti')
        self.kredi_radio.setStyleSheet("font-size: 13px; padding: 5px;")
        
        self.havale_radio = QRadioButton('🏦 Havale/EFT')
        self.havale_radio.setStyleSheet("font-size: 13px; padding: 5px;")
        
        self.odeme_button_group.addButton(self.nakit_radio, 1)
        self.odeme_button_group.addButton(self.kredi_radio, 2)
        self.odeme_button_group.addButton(self.havale_radio, 3)
        
        odeme_layout.addWidget(self.nakit_radio)
        odeme_layout.addWidget(self.kredi_radio)
        odeme_layout.addWidget(self.havale_radio)
        
        odeme_group.setLayout(odeme_layout)
        layout.addWidget(odeme_group)
        
        # Uyarı mesajı
        uyari_label = QLabel('⚠️ Eski üyelik pasif hale gelecek ve yeni üyelik başlatılacaktır.')
        uyari_label.setFont(QFont('Arial', 10))
        uyari_label.setStyleSheet("""
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ffc107;
        """)
        uyari_label.setWordWrap(True)
        layout.addWidget(uyari_label)
        
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
        
        yenile_btn = QPushButton('✓ Üyeliği Yenile')
        yenile_btn.setFixedHeight(45)
        yenile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yenile_btn.clicked.connect(self.uyelik_yenile)
        
        button_layout.addWidget(iptal_btn)
        button_layout.addWidget(yenile_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def styleInput(self, widget):
        widget.setFixedHeight(40)
        widget.setStyleSheet("""
            QComboBox {
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                color: #2c3e50;
            }
            QComboBox:focus {
                border: 2px solid #e94560;
            }
            QComboBox::drop-down {
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
    
    def paketleri_yukle(self):
        """Paketleri combo box'a yükle."""
        paketler = self.db.paketleri_getir()
        for paket in paketler:
            # paket = (id, paket_adi, sure_gun, fiyat, aciklama)
            self.paket_combo.addItem(
                f"{paket[1]} - {paket[3]:.0f} TL ({paket[4]})", 
                paket[0]
            )
    
    def uyelik_yenile(self):
        """Üyeliği yenile."""
        if self.paket_combo.currentIndex() == -1:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir paket seçiniz!')
            return
        
        # Ödeme tipini belirle
        odeme_tipi = "Nakit"
        if self.kredi_radio.isChecked():
            odeme_tipi = "Kredi Kartı"
        elif self.havale_radio.isChecked():
            odeme_tipi = "Havale/EFT"
        
        # Onay al
        paket_adi = self.paket_combo.currentText()
        reply = QMessageBox.question(
            self,
            'Onay',
            f'Üyelik yenilenecek:\n\n'
            f'Üye: {self.uye_ad}\n'
            f'Paket: {paket_adi}\n'
            f'Ödeme: {odeme_tipi}\n\n'
            f'Onaylıyor musunuz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            paket_id = self.paket_combo.currentData()
            uyelik_id = self.db.uyelik_yenile(self.uye_id, paket_id, odeme_tipi)
            
            if uyelik_id:
                QMessageBox.information(
                    self,
                    'Başarılı',
                    f'Üyelik başarıyla yenilendi!\n\n'
                    f'Yeni Üyelik No: {uyelik_id}\n'
                    f'Ödeme Tipi: {odeme_tipi}'
                )
                self.uyelik_yenilendi.emit()
                self.accept()
            else:
                QMessageBox.warning(self, 'Hata', 'Üyelik yenilenirken bir hata oluştu!')
