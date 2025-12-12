from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import dao


class OdemeEkrani(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık
        header_layout = QHBoxLayout()
        
        baslik = QLabel('Ödeme İşlemleri')
        baslik.setFont(QFont('Arial', 18, QFont.Bold))
        baslik.setStyleSheet('color: #2c3e50;')
        
        header_layout.addWidget(baslik)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Istatistikler
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(15)
        layout.addLayout(self.stats_layout)
        
        # Istatistikleri yukle
        self.istatistikleri_guncelle()
        
        # Arama ve filtre
        arama_layout = QHBoxLayout()
        
        arama_label = QLabel('🔍 Üye Ara:')
        arama_label.setFont(QFont('Arial', 11, QFont.Bold))
        
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText('Üye adı ile ara...')
        self.arama_input.setFixedHeight(40)
        self.arama_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #e94560;
            }
        """)
        self.arama_input.textChanged.connect(self.odemeler_ara)
        
        yenile_btn = QPushButton('🔄 Yenile')
        yenile_btn.setFixedSize(100, 40)
        yenile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yenile_btn.clicked.connect(self.odemeler_yukle)
        
        arama_layout.addWidget(arama_label)
        arama_layout.addWidget(self.arama_input)
        arama_layout.addWidget(yenile_btn)
        
        layout.addLayout(arama_layout)
        
        # Ödeme tablosu
        self.odeme_tablosu = QTableWidget()
        self.odeme_tablosu.setColumnCount(6)
        self.odeme_tablosu.setHorizontalHeaderLabels(['Ödeme ID', 'Üye Adı', 'Tutar (TL)', 
                                                       'Tarih', 'Ödeme Tipi', 'Durum'])
        self.odeme_tablosu.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.odeme_tablosu.setAlternatingRowColors(True)
        self.odeme_tablosu.setStyleSheet("""
            QTableWidget {
                gridline-color: #dfe4ea;
                background-color: white;
                border: 2px solid #dfe4ea;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #e94560;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        
        layout.addWidget(self.odeme_tablosu)
        
        # Ödemeleri yükle
        self.odemeler_yukle()
        
        self.setLayout(layout)
    
    def create_stat_box(self, baslik, deger, renk):
        box = QWidget()
        box.setFixedHeight(100)
        box.setStyleSheet(f"""
            QWidget {{
                background-color: {renk};
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        baslik_label = QLabel(baslik)
        baslik_label.setFont(QFont('Arial', 11, QFont.Bold))
        baslik_label.setStyleSheet('color: white; background: transparent;')
        
        deger_label = QLabel(deger)
        deger_label.setFont(QFont('Arial', 24, QFont.Bold))
        deger_label.setStyleSheet('color: white; background: transparent;')
        
        layout.addWidget(baslik_label)
        layout.addWidget(deger_label)
        layout.addStretch()
        
        box.setLayout(layout)
        return box
    

    def istatistikleri_guncelle(self):
        """Istatistikleri guncelle."""
        # Eski widget'lari temizle
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Yeni istatistikleri hesapla
        odemeler = dao.get_all_subscriptions()
        toplam_odeme = len(odemeler)
        toplam_tutar = sum(o.get('price_sold', 0) for o in odemeler) if odemeler else 0
        
        # Widget'lari ekle
        self.stats_layout.addWidget(self.create_stat_box('Toplam Gelir', f'{toplam_tutar:,.0f} TL', '#2c3e50'))
        self.stats_layout.addWidget(self.create_stat_box('Toplam Islem', str(toplam_odeme), '#34495e'))
        self.stats_layout.addWidget(self.create_stat_box('Ortalama', f'{toplam_tutar/toplam_odeme:,.0f} TL' if toplam_odeme > 0 else '0 TL', '#1a1a2e'))
    
    def odemeler_yukle(self):
        self.istatistikleri_guncelle()  # Istatistikleri guncelle
        odemeler = dao.get_all_subscriptions()
        self.odeme_tablosu.setRowCount(len(odemeler))
        
        for i, odeme in enumerate(odemeler):
            # PostgreSQL dict format
            uye_ad = f"{odeme.get('first_name', '')} {odeme.get('last_name', '')}"
            data = [
                str(odeme.get('id', '')),
                uye_ad,
                f"{odeme.get('price_sold', 0):,.2f}",
                str(odeme.get('created_at', '')).split('.')[0],
                odeme.get('payment_type_name', ''),
                'TAMAMLANDI'
            ]
            
            for j, veri in enumerate(data):
                if j == 2:  # Tutar sütunu
                    item = QTableWidgetItem(veri)
                    item.setFont(QFont('Arial', 11, QFont.Bold))
                elif j == 5:  # Durum sütunu
                    item = QTableWidgetItem(veri)
                    item.setForeground(Qt.darkGreen)
                    item.setFont(QFont('Arial', 10, QFont.Bold))
                else:
                    item = QTableWidgetItem(veri)
                
                item.setTextAlignment(Qt.AlignCenter)
                self.odeme_tablosu.setItem(i, j, item)
    
    def odemeler_ara(self):
        arama_text = self.arama_input.text().lower()
        
        for i in range(self.odeme_tablosu.rowCount()):
            uye_adi = self.odeme_tablosu.item(i, 1).text().lower()
            
            if arama_text in uye_adi:
                self.odeme_tablosu.setRowHidden(i, False)
            else:
                self.odeme_tablosu.setRowHidden(i, True)