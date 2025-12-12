from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import dao
from datetime import datetime, timedelta

class ProgramAtaDialog(QDialog):
    def __init__(self, uye_id, uye_adi, parent=None):
        super().__init__(parent)
        self.uye_id = uye_id
        self.uye_adi = uye_adi
        
        self.setWindowTitle(f"Program Ata - {uye_adi}")
        self.setMinimumSize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel(f"💪 {self.uye_adi} için Program Atama")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(baslik)
        
        # Form
        form_layout = QFormLayout()
        
        # Program seçimi
        self.program_combo = QComboBox()
        self.program_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Programları yükle
        programlar = dao.get_all_programs()
        if not programlar:
            QMessageBox.warning(self, "Uyarı", "Henüz hiç program oluşturulmamış!\nÖnce 'Programlar' sekmesinden program oluşturun.")
            self.reject()
            return
        
        for program in programlar:
            # PostgreSQL dict: {id, name, description}
            self.program_combo.addItem(f"{program.get('name', '')} - {program.get('description', '')}", program.get('id'))
        
        self.program_combo.currentIndexChanged.connect(self.program_secildi)
        
        # Program detayları
        self.program_detay_label = QLabel()
        self.program_detay_label.setWordWrap(True)
        self.program_detay_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
        """)
        
        # Başlangıç tarihi
        self.baslangic_date = QDateEdit()
        self.baslangic_date.setDate(QDate.currentDate())
        self.baslangic_date.setCalendarPopup(True)
        self.baslangic_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.baslangic_date.dateChanged.connect(self.tarih_degisti)
        
        # Bitiş tarihi
        self.bitis_date = QDateEdit()
        self.bitis_date.setDate(QDate.currentDate().addMonths(1))
        self.bitis_date.setCalendarPopup(True)
        self.bitis_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Notlar
        self.notlar_input = QTextEdit()
        self.notlar_input.setPlaceholderText("Programa dair notlar (opsiyonel)...")
        self.notlar_input.setMaximumHeight(100)
        self.notlar_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        form_layout.addRow("Program:", self.program_combo)
        form_layout.addRow("Detaylar:", self.program_detay_label)
        form_layout.addRow("Başlangıç Tarihi:", self.baslangic_date)
        form_layout.addRow("Bitiş Tarihi:", self.bitis_date)
        form_layout.addRow("Notlar:", self.notlar_input)
        
        layout.addLayout(form_layout)
        
        # İlk programı göster
        self.program_secildi()
        
        # Butonlar
        buton_layout = QHBoxLayout()
        
        kaydet_btn = QPushButton("💾 Kaydet")
        kaydet_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        kaydet_btn.clicked.connect(self.kaydet)
        
        iptal_btn = QPushButton("❌ İptal")
        iptal_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        iptal_btn.clicked.connect(self.reject)
        
        buton_layout.addStretch()
        buton_layout.addWidget(kaydet_btn)
        buton_layout.addWidget(iptal_btn)
        
        layout.addLayout(buton_layout)
        
        self.setLayout(layout)
    
    def program_secildi(self):
        """Program seçildiğinde detayları gösterir."""
        program_id = self.program_combo.currentData()
        if program_id:
            program = dao.get_program(program_id)
            if program:
                # PostgreSQL dict: {id, name, description}
                detay_text = f"<b>Açıklama:</b> {program.get('description', '') or 'Yok'}<br>"
                
                # Egzersiz sayısını hesapla
                egzersizler = dao.get_program_exercises(program_id)
                detay_text += f"<b>Egzersiz Sayısı:</b> {len(egzersizler)}"
                
                self.program_detay_label.setText(detay_text)
    
    def tarih_degisti(self):
        """Başlangıç tarihi değiştiğinde bitiş tarihini otomatik ayarlar."""
        baslangic = self.baslangic_date.date()
        # Varsayılan olarak 1 ay sonra
        bitis = baslangic.addMonths(1)
        self.bitis_date.setDate(bitis)
    
    def kaydet(self):
        """Programı üyeye atar."""
        program_id = self.program_combo.currentData()
        baslangic = self.baslangic_date.date().toString("yyyy-MM-dd")
        bitis = self.bitis_date.date().toString("yyyy-MM-dd")
        notlar = self.notlar_input.toPlainText().strip()
        
        # Tarih kontrolü
        if self.bitis_date.date() <= self.baslangic_date.date():
            QMessageBox.warning(self, "Uyarı", "Bitiş tarihi başlangıç tarihinden sonra olmalıdır!")
            return
        
        try:
            # Programı ata - PostgreSQL'de current_program_id güncelle
            dao.update_user(self.uye_id, current_program_id=program_id)
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"{self.uye_adi} için program başarıyla atandı!"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Program atanırken hata oluştu: {str(e)}")
    

