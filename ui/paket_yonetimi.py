
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import dao


class PaketYonetimi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık
        baslik = QLabel('Üyelik Paketleri')
        baslik.setFont(QFont('Arial', 18, QFont.Bold))
        baslik.setStyleSheet('color: #2c3e50;')
        layout.addWidget(baslik)
        
        # Açıklama
        aciklama = QLabel('Sistemde tanımlı üyelik paketlerini görüntüleyebilir ve yönetebilirsiniz.')
        aciklama.setFont(QFont('Arial', 11))
        aciklama.setStyleSheet('color: #7f8c8d; margin-bottom: 10px;')
        layout.addWidget(aciklama)
        
        # Paket tablosu
        self.paket_tablosu = QTableWidget()
        self.paket_tablosu.setColumnCount(5)
        self.paket_tablosu.setHorizontalHeaderLabels(['ID', 'Paket Adı', 'Süre (Gün)', 'Fiyat (TL)', 'Açıklama'])
        self.paket_tablosu.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.paket_tablosu.setAlternatingRowColors(True)
        self.paket_tablosu.setStyleSheet("""
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
        
        layout.addWidget(self.paket_tablosu)
        
        # Paketleri yükle
        self.paketleri_yukle()
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        yenile_btn = QPushButton('🔄 Yenile')
        yenile_btn.setFixedHeight(45)
        yenile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yenile_btn.clicked.connect(self.paketleri_yukle)
        
        button_layout.addStretch()
        button_layout.addWidget(yenile_btn)
        
        layout.addLayout(button_layout)
        
        # Paket detayları bilgi kutusu
        bilgi_widget = QWidget()
        bilgi_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        bilgi_layout = QVBoxLayout()
        
        bilgi_baslik = QLabel('💡 Paket Bilgileri')
        bilgi_baslik.setFont(QFont('Arial', 12, QFont.Bold))
        bilgi_baslik.setStyleSheet('color: #2c3e50; background: transparent;')
        
        bilgi_text = QLabel(
            '• 1 Aylık: Deneme paketi, yeni üyeler için uygundur\n'
            '• 3 Aylık: %10 indirimli, düzenli spor yapanlar için\n'
            '• 6 Aylık: %20 indirimli, orta vadeli hedefler için\n'
            '• 12 Aylık: %30 indirimli, en avantajlı paket'
        )
        bilgi_text.setFont(QFont('Arial', 10))
        bilgi_text.setStyleSheet('color: #34495e; background: transparent; padding: 5px;')
        
        bilgi_layout.addWidget(bilgi_baslik)
        bilgi_layout.addWidget(bilgi_text)
        bilgi_widget.setLayout(bilgi_layout)
        
        layout.addWidget(bilgi_widget)
        
        self.setLayout(layout)
    
    def paketleri_yukle(self):
        paketler = dao.get_all_packages()
        self.paket_tablosu.setRowCount(len(paketler))
        
        for i, paket in enumerate(paketler):
            # PostgreSQL dict format: {id, name, duration_days, price, description}
            data = [
                str(paket['id']),
                paket['name'],
                str(paket['duration_days']),
                f"{paket['price']:,.2f}",
                paket.get('description', '')
            ]
            
            for j, veri in enumerate(data):
                item = QTableWidgetItem(veri)
                item.setTextAlignment(Qt.AlignCenter)
                
                # Fiyat sütununu vurgula
                if j == 3:
                    item.setFont(QFont('Arial', 11, QFont.Bold))
                
                self.paket_tablosu.setItem(i, j, item)