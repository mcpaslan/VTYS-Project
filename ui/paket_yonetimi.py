
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QDialog, QLineEdit, QSpinBox, 
                             QDoubleSpinBox, QTextEdit, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import dao


class PaketEkleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Yeni Paket Ekle')
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.ad_input = QLineEdit()
        self.ad_input.setPlaceholderText('Örn: Gold Paket')
        
        self.sure_input = QSpinBox()
        self.sure_input.setRange(1, 1000)
        self.sure_input.setSuffix(' Gün')
        self.sure_input.setValue(30)
        
        self.fiyat_input = QDoubleSpinBox()
        self.fiyat_input.setRange(0, 100000)
        self.fiyat_input.setSuffix(' TL')
        self.fiyat_input.setValue(100.00)
        
        self.aciklama_input = QTextEdit()
        self.aciklama_input.setPlaceholderText('Paket açıklaması...')
        self.aciklama_input.setFixedHeight(80)
        
        form_layout.addRow('Paket Adı:', self.ad_input)
        form_layout.addRow('Süre:', self.sure_input)
        form_layout.addRow('Fiyat:', self.fiyat_input)
        form_layout.addRow('Açıklama:', self.aciklama_input)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        iptal_btn = QPushButton('İptal')
        iptal_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        iptal_btn.clicked.connect(self.reject)
        
        kaydet_btn = QPushButton('Kaydet')
        kaydet_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        kaydet_btn.clicked.connect(self.kaydet)
        
        btn_layout.addWidget(iptal_btn)
        btn_layout.addWidget(kaydet_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def kaydet(self):
        ad = self.ad_input.text().strip()
        sure = self.sure_input.value()
        fiyat = self.fiyat_input.value()
        aciklama = self.aciklama_input.toPlainText().strip()
        
        if not ad:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen paket adını giriniz!')
            return
            
        try:
            # Veritabanına kaydet
            dao.create_package(ad, sure, aciklama, fiyat)
            QMessageBox.information(self, 'Başarılı', 'Paket başarıyla eklendi!')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Paket eklenirken bir hata oluştu:\n{str(e)}')


class PaketYonetimi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Başlık ve Butonlar (Header)
        header_layout = QHBoxLayout()
        
        baslik_layout = QVBoxLayout()
        baslik = QLabel('Üyelik Paketleri')
        baslik.setFont(QFont('Arial', 18, QFont.Bold))
        baslik.setStyleSheet('color: #2c3e50;')
        
        aciklama = QLabel('Sistemde tanımlı üyelik paketlerini görüntüleyebilir ve yönetebilirsiniz.')
        aciklama.setFont(QFont('Arial', 11))
        aciklama.setStyleSheet('color: #7f8c8d;')
        
        baslik_layout.addWidget(baslik)
        baslik_layout.addWidget(aciklama)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        yenile_btn = QPushButton('🔄 Yenile')
        yenile_btn.setFixedSize(100, 40)
        yenile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yenile_btn.clicked.connect(self.paketleri_yukle)
        
        ekle_btn = QPushButton('➕ Paket Ekle')
        ekle_btn.setFixedSize(120, 40)
        ekle_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        ekle_btn.clicked.connect(self.paket_ekle_dialog)
        
        sil_btn = QPushButton('🗑️ Paket Sil')
        sil_btn.setFixedSize(120, 40)
        sil_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        sil_btn.clicked.connect(self.paket_sil)
        
        btn_layout.addWidget(yenile_btn)
        btn_layout.addWidget(ekle_btn)
        btn_layout.addWidget(sil_btn)
        
        header_layout.addLayout(baslik_layout)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)
        
        layout.addLayout(header_layout)
        
        # Paket tablosu
        self.paket_tablosu = QTableWidget()
        self.paket_tablosu.setColumnCount(5)
        self.paket_tablosu.setHorizontalHeaderLabels(['ID', 'Paket Adı', 'Süre (Gün)', 'Fiyat (TL)', 'Açıklama'])
        self.paket_tablosu.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.paket_tablosu.setAlternatingRowColors(True)
        self.paket_tablosu.verticalHeader().setVisible(False)
        self.paket_tablosu.setStyleSheet("""
            QTableWidget {
                gridline-color: #dfe4ea;
                background-color: white;
                border: 1px solid #dfe4ea;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 13px;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                padding: 12px;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-bottom: 2px solid #dfe4ea;
            }
            QTableWidget::item:alternate {
                background-color: #fafbfd;
            }
        """)
        
        layout.addWidget(self.paket_tablosu)
        
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
            '• Paket süreleri gün bazındadır.\n'
            '• Yeni eklenen paketler anında aktif olur.\n'
            '• Paket fiyatları KDV dahildir.'
        )
        bilgi_text.setFont(QFont('Arial', 10))
        bilgi_text.setStyleSheet('color: #34495e; background: transparent; padding: 5px;')
        
        bilgi_layout.addWidget(bilgi_baslik)
        bilgi_layout.addWidget(bilgi_text)
        bilgi_widget.setLayout(bilgi_layout)
        
        layout.addWidget(bilgi_widget)
        
        self.setLayout(layout)
        
        # İlk yükleme
        self.paketleri_yukle()
    
    def paketleri_yukle(self):
        try:
            paketler = dao.get_all_packages()
            self.paket_tablosu.setRowCount(len(paketler))
            
            for i, paket in enumerate(paketler):
                # PostgreSQL dict format: {id, name, duration_days, price, description}
                try:
                    data = [
                        str(paket.get('id', '')),
                        paket.get('name', ''),
                        str(paket.get('duration_days', '')),
                        f"{float(paket.get('price', 0)):,.2f}",
                        paket.get('description', '')
                    ]
                    
                    for j, veri in enumerate(data):
                        item = QTableWidgetItem(veri)
                        item.setTextAlignment(Qt.AlignCenter)
                        
                        # Fiyat sütununu vurgula
                        if j == 3:
                            item.setFont(QFont('Arial', 11, QFont.Bold))
                            item.setForeground(Qt.darkGreen)
                        
                        self.paket_tablosu.setItem(i, j, item)
                except Exception as e:
                    print(f"Satır işleme hatası: {e}")
                    continue
                    
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Paketler yüklenirken hata oluştu:\n{str(e)}')

    def paket_ekle_dialog(self):
        dialog = PaketEkleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.paketleri_yukle()
            
    def paket_sil(self):
        """Seçili paketi siler."""
        secili_satirlar = self.paket_tablosu.selectedItems()
        if not secili_satirlar:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek için bir paket seçin!')
            return
            
        satir = secili_satirlar[0].row()
        paket_id = int(self.paket_tablosu.item(satir, 0).text())
        paket_adi = self.paket_tablosu.item(satir, 1).text()
        
        # Onay al
        reply = QMessageBox.question(
            self,
            'Paket Sil',
            f'"{paket_adi}" isimli paketi silmek istediğinize emin misiniz?\n\n'
            f'Bu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if dao.delete_package(paket_id):
                    QMessageBox.information(self, 'Başarılı', 'Paket başarıyla silindi!')
                    self.paketleri_yukle()
                else:
                    QMessageBox.warning(self, 'Hata', 'Paket silinirken bir hata oluştu!')
            except Exception as e:
                # Veritabanı constraint hatası olabilir
                QMessageBox.critical(self, 'Hata', f'Paket silinemedi!\n\nHata: {str(e)}\n\nBu paket kullanımda olabilir.')