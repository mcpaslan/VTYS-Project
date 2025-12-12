from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QDateEdit,
                             QGroupBox, QFormLayout, QMessageBox, QRadioButton, QButtonGroup,
                             QScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from database import dao


class UyeIslemleri(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Scroll icindeki widget
        scroll_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık
        baslik = QLabel('Yeni Üye Kaydı')
        baslik.setFont(QFont('Arial', 18, QFont.Bold))
        baslik.setStyleSheet('color: #2c3e50;')
        layout.addWidget(baslik)
        
        # Kişisel Bilgiler Grubu
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
        self.ad_input.setPlaceholderText('Üyenin adını giriniz')
        self.styleInput(self.ad_input)
        
        self.soyad_input = QLineEdit()
        self.soyad_input.setPlaceholderText('Üyenin soyadını giriniz')
        self.styleInput(self.soyad_input)
        
        self.tc_input = QLineEdit()
        self.tc_input.setPlaceholderText('11 haneli TC kimlik no (sadece rakam)')
        self.tc_input.setMaxLength(11)
        self.styleInput(self.tc_input)
        
        self.dogum_tarihi = QDateEdit()
        self.dogum_tarihi.setCalendarPopup(True)
        self.dogum_tarihi.setDate(QDate.currentDate().addYears(-20))
        self.dogum_tarihi.setDisplayFormat('dd/MM/yyyy')
        self.styleInput(self.dogum_tarihi)
        
        self.cinsiyet_combo = QComboBox()
        self.cinsiyet_combo.addItems(['Erkek', 'Kadın', 'Belirtmek İstemiyorum'])
        self.styleInput(self.cinsiyet_combo)
        
        kisisel_layout.addRow('Ad *:', self.ad_input)
        kisisel_layout.addRow('Soyad *:', self.soyad_input)
        kisisel_layout.addRow('TC Kimlik No *:', self.tc_input)
        kisisel_layout.addRow('Doğum Tarihi:', self.dogum_tarihi)
        kisisel_layout.addRow('Cinsiyet:', self.cinsiyet_combo)
        
        kisisel_group.setLayout(kisisel_layout)
        layout.addWidget(kisisel_group)
        
        # İletişim Bilgileri Grubu
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
        
        # Üyelik Paketi Grubu
        paket_group = QGroupBox('Üyelik Paketi')
        paket_group.setStyleSheet(kisisel_group.styleSheet())
        paket_layout = QFormLayout()
        paket_layout.setSpacing(15)
        
        self.paket_combo = QComboBox()
        self.paketleri_yukle()
        self.styleInput(self.paket_combo)
        
        paket_layout.addRow('Paket Seçin *:', self.paket_combo)
        paket_group.setLayout(paket_layout)
        layout.addWidget(paket_group)
        

        # Odeme Tipi Grubu
        odeme_group = QGroupBox('Odeme Tipi')
        odeme_group.setStyleSheet(kisisel_group.styleSheet())
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
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        kaydet_btn = QPushButton('💾 Kaydet')
        kaydet_btn.setFixedHeight(50)
        kaydet_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        kaydet_btn.clicked.connect(self.uye_kaydet)
        
        temizle_btn = QPushButton('🗑️ Temizle')
        temizle_btn.setFixedHeight(50)
        temizle_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        temizle_btn.clicked.connect(self.formu_temizle)
        
        button_layout.addWidget(kaydet_btn)
        button_layout.addWidget(temizle_btn)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        scroll_widget.setLayout(layout)
        scroll.setWidget(scroll_widget)
        
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
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
    
    def paketleri_yukle(self):
        paketler = dao.get_all_packages()
        for paket in paketler:
            # PostgreSQL dict format: {id, name, duration_days, price, description}
            self.paket_combo.addItem(f"{paket['name']} - {paket['price']:.0f} TL", paket['id'])
    
    def uye_kaydet(self):
        # Zorunlu alanları kontrol et
        if not self.ad_input.text() or not self.soyad_input.text():
            QMessageBox.warning(self, 'Uyarı', 'Ad ve Soyad alanları zorunludur!')
            return
        
        if not self.tc_input.text():
            QMessageBox.warning(self, 'Uyarı', 'TC Kimlik No zorunludur!')
            return
        
        if self.paket_combo.currentIndex() == -1:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir paket seçiniz!')
            return
        
        # Üyeyi kaydet (validasyonlar dao.py'de yapılıyor)
        uye_id = dao.create_user(
            self.ad_input.text(),
            self.soyad_input.text(),
            self.email_input.text(),
            '',  # password (boş bırakılıyor, sadece coach'ler için)
            self.telefon_input.text(),
            self.cinsiyet_combo.currentText(),
            self.tc_input.text(),
            self.dogum_tarihi.date().toPyDate(),
        )
        
        if uye_id:
            # Üyelik oluştur
            paket_id = self.paket_combo.currentData()
            # Odeme tipini belirle
            odeme_tipi_id = 1  # Nakit
            if self.kredi_radio.isChecked():
                odeme_tipi_id = 2  # Kredi Kartı
            elif self.havale_radio.isChecked():
                odeme_tipi_id = 3  # Havale/EFT
            
            # Paket bilgilerini al
            paket = dao.get_package(paket_id)
            if paket:
                from datetime import datetime, timedelta
                baslangic = datetime.now()
                bitis = baslangic + timedelta(days=paket['duration_days'])
                
                uyelik_id = dao.create_subscription(
                    uye_id, 
                    paket_id, 
                    baslangic, 
                    bitis, 
                    paket['price'],
                    odeme_tipi_id
                )
                
                if uyelik_id:
                    QMessageBox.information(self, 'Başarılı', 
                        f'{self.ad_input.text()} {self.soyad_input.text()} başarıyla kaydedildi!\n'
                        f'Üyelik No: {uye_id}')
                    self.formu_temizle()
                else:
                    QMessageBox.warning(self, 'Hata', 'Üyelik oluşturulurken bir hata oluştu!')
            else:
                QMessageBox.warning(self, 'Hata', 'Paket bilgisi alınamadı!')
        else:
            # Hata
            QMessageBox.warning(self, 'Hata', 'Üye kaydedilirken bir hata oluştu!')
    
    def formu_temizle(self):
        self.ad_input.clear()
        self.soyad_input.clear()
        self.tc_input.clear()
        self.telefon_input.clear()
        self.email_input.clear()
        self.dogum_tarihi.setDate(QDate.currentDate().addYears(-20))
        self.cinsiyet_combo.setCurrentIndex(0)
        self.paket_combo.setCurrentIndex(0)
        self.nakit_radio.setChecked(True)