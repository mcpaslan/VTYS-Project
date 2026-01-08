from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import dao
from datetime import datetime

class ProgramYonetimiWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.programlari_yukle()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("💪 Antrenman Programları")
        baslik.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(baslik)
        
        # Butonlarr
        buton_layout = QHBoxLayout()
        
        self.yeni_program_btn = QPushButton("➕ Yeni Program")
        self.yeni_program_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.yeni_program_btn.clicked.connect(self.yeni_program_dialog)
        
        self.program_duzenle_btn = QPushButton("Program Düzenle")
        self.program_duzenle_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.program_duzenle_btn.clicked.connect(self.program_duzenle)
        
        self.program_sil_btn = QPushButton("🗑️ Sil")
        self.program_sil_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.program_sil_btn.clicked.connect(self.program_sil)
        
        self.yenile_btn = QPushButton("🔄 Yenile")
        self.yenile_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.yenile_btn.clicked.connect(self.programlari_yukle)
        
        buton_layout.addWidget(self.yeni_program_btn)
        buton_layout.addWidget(self.program_duzenle_btn)
        buton_layout.addWidget(self.program_sil_btn)
        buton_layout.addWidget(self.yenile_btn)
        buton_layout.addStretch()
        
        layout.addLayout(buton_layout)
        
        # Program Tablosu
        self.program_table = QTableWidget()
        self.program_table.setColumnCount(5)
        self.program_table.setHorizontalHeaderLabels([
            "ID", "Program Adı", "Hedef", "Açıklama", "Oluşturma Tarihi"
        ])
        
        # Tablo stil ayarları
        self.program_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.program_table.horizontalHeader().setStretchLastSection(True)
        self.program_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.program_table.setSelectionMode(QTableWidget.SingleSelection)
        self.program_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.program_table.setAlternatingRowColors(True)
        
        # Sütun genişlikleri
        self.program_table.setColumnWidth(0, 50)
        self.program_table.setColumnWidth(1, 200)
        self.program_table.setColumnWidth(2, 150)
        self.program_table.setColumnWidth(3, 300)
        
        layout.addWidget(self.program_table)
        
        self.setLayout(layout)
    
    def programlari_yukle(self):
        """Programları veritabanından yükler."""
        programlar = dao.get_all_programs()
        self.program_table.setRowCount(len(programlar))
        
        for row, program in enumerate(programlar):
            # PostgreSQL dict format: {id, name, description, created_at}
            self.program_table.setItem(row, 0, QTableWidgetItem(str(program.get('id', ''))))
            self.program_table.setItem(row, 1, QTableWidgetItem(program.get('name', '')))
            self.program_table.setItem(row, 2, QTableWidgetItem(program.get('description', '') or ""))
            self.program_table.setItem(row, 3, QTableWidgetItem(program.get('description', '') or ""))
            self.program_table.setItem(row, 4, QTableWidgetItem(str(program.get('created_at', ''))))
    
    def yeni_program_dialog(self):
        """Yeni program oluşturma dialogu."""
        dialog = ProgramOlusturDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.programlari_yukle()
    
    def program_duzenle(self):
        """Seçili programı düzenler."""
        secili = self.program_table.currentRow()
        if secili == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir program seçin!")
            return
        
        program_id = int(self.program_table.item(secili, 0).text())
        dialog = ProgramOlusturDialog(self, program_id)
        if dialog.exec_() == QDialog.Accepted:
            self.programlari_yukle()
    
    def program_sil(self):
        """Seçili programı siler."""
        secili = self.program_table.currentRow()
        if secili == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir program seçin!")
            return
        
        program_adi = self.program_table.item(secili, 1).text()
        cevap = QMessageBox.question(
            self, 
            "Program Sil", 
            f"'{program_adi}' programını silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if cevap == QMessageBox.Yes:
            program_id = int(self.program_table.item(secili, 0).text())
            dao.delete_program(program_id)
            QMessageBox.information(self, "Başarılı", "Program başarıyla silindi!")
            self.programlari_yukle()


class ProgramOlusturDialog(QDialog):
    def __init__(self, parent=None, program_id=None):
        super().__init__(parent)
        self.program_id = program_id
        self.egzersiz_satirlari = []
        
        self.setWindowTitle("Yeni Program Oluştur" if not program_id else "Program Düzenle")
        self.setMinimumSize(900, 700)
        self.init_ui()
        
        if program_id:
            self.program_yukle()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Program Bilgileri Grubu
        bilgi_group = QGroupBox("Program Bilgileri")
        bilgi_layout = QFormLayout()
        
        self.program_adi_input = QLineEdit()
        self.program_adi_input.setPlaceholderText("Örn: Başlangıç Programı")
        
        self.hedef_input = QLineEdit()
        self.hedef_input.setPlaceholderText("Örn: Kilo Verme, Kas Yapma")
        
        self.aciklama_input = QTextEdit()
        self.aciklama_input.setPlaceholderText("Program hakkında açıklama...")
        self.aciklama_input.setMaximumHeight(80)
        
        bilgi_layout.addRow("Program Adı:", self.program_adi_input)
        bilgi_layout.addRow("Hedef:", self.hedef_input)
        bilgi_layout.addRow("Açıklama:", self.aciklama_input)
        
        bilgi_group.setLayout(bilgi_layout)
        layout.addWidget(bilgi_group)
        
        # Egzersizler Grubu
        egzersiz_group = QGroupBox("Egzersizler")
        egzersiz_layout = QVBoxLayout()
        
        # Egzersiz ekleme butonu
        ekle_btn = QPushButton("➕ Egzersiz Ekle")
        ekle_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        ekle_btn.clicked.connect(self.egzersiz_ekle)
        egzersiz_layout.addWidget(ekle_btn)
        
        # Egzersiz listesi için scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        
        self.egzersiz_container = QWidget()
        self.egzersiz_container_layout = QVBoxLayout()
        self.egzersiz_container_layout.addStretch()
        self.egzersiz_container.setLayout(self.egzersiz_container_layout)
        
        scroll.setWidget(self.egzersiz_container)
        egzersiz_layout.addWidget(scroll)
        
        egzersiz_group.setLayout(egzersiz_layout)
        layout.addWidget(egzersiz_group)
        
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
    
    def program_yukle(self):
        """Mevcut programı yükler."""
        program = dao.get_program(self.program_id)
        if program:
            self.program_adi_input.setText(program.get('name', ''))
            self.aciklama_input.setPlainText(program.get('description', '') or "")
            self.hedef_input.setText(program.get('description', '') or "")  # PostgreSQL'de hedef yok, description kullanılıyor
            
            # Egzersizleri yükle
            egzersizler = dao.get_program_exercises(self.program_id)
            for egz in egzersizler:
                # PostgreSQL dict: {id, program_id, exercise_id, sets, reps, exercise_name}
                self.egzersiz_ekle(egz)
    
    def egzersiz_ekle(self, egzersiz_data=None):
        """Yeni egzersiz satırı ekler."""
        satir = QWidget()
        satir_layout = QHBoxLayout()
        satir_layout.setContentsMargins(0, 5, 0, 5)
        
        # Egzersiz seçimi
        egzersiz_combo = QComboBox()
        egzersiz_combo.setMinimumWidth(200)
        egzersiz_combo.setEditable(True)
        egzersizler = dao.get_all_exercises()
        for egz in egzersizler:
            # PostgreSQL dict: {id, name, muscle_group, description}
            egzersiz_combo.addItem(f"{egz.get('name', '')} ({egz.get('muscle_group', '')})", egz.get('id'))
        
        # Gün
        gun_combo = QComboBox()
        gun_combo.addItems(["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        
        # Set
        set_input = QSpinBox()
        set_input.setRange(1, 10)
        set_input.setValue(3)
        set_input.setPrefix("Set: ")
        
        # Tekrar
        tekrar_input = QLineEdit()
        tekrar_input.setPlaceholderText("Örn: 10-12")
        tekrar_input.setMaximumWidth(80)
        
        # Dinlenme
        dinlenme_input = QLineEdit()
        dinlenme_input.setPlaceholderText("Örn: 60sn")
        dinlenme_input.setMaximumWidth(80)
        
        # Sil butonu
        sil_btn = QPushButton("🗑️")
        sil_btn.setMaximumWidth(40)
        sil_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        sil_btn.clicked.connect(lambda: self.egzersiz_sil(satir))
        
        satir_layout.addWidget(QLabel("Egzersiz:"))
        satir_layout.addWidget(egzersiz_combo)
        satir_layout.addWidget(QLabel("Gün:"))
        satir_layout.addWidget(gun_combo)
        satir_layout.addWidget(set_input)
        satir_layout.addWidget(QLabel("Tekrar:"))
        satir_layout.addWidget(tekrar_input)
        satir_layout.addWidget(QLabel("Dinlenme:"))
        satir_layout.addWidget(dinlenme_input)
        satir_layout.addWidget(sil_btn)
        
        satir.setLayout(satir_layout)
        
        # Eğer mevcut egzersiz varsa değerleri doldur
        # Egzersiz verisini debug et
        # Egzersiz verisini yükle
        if egzersiz_data:
            ex_id = egzersiz_data.get('exercise_id')
            
            # Egzersiz seçimi - Tip güvenli arama
            index = -1
            # Önce standart aramayı dene
            index = egzersiz_combo.findData(ex_id)
            
            # Eğer bulunamazsa string karşılaştırması yap (int vs str sorunları için)
            if index == -1:
                for i in range(egzersiz_combo.count()):
                    item_data = egzersiz_combo.itemData(i)
                    if str(item_data) == str(ex_id):
                        index = i
                        break
            
            if index >= 0:
                egzersiz_combo.setCurrentIndex(index)
            
            # Gün verisi
            gun_text = egzersiz_data.get('day', 'Pazartesi')
            gun_index = gun_combo.findText(gun_text)
            if gun_index >= 0:
                gun_combo.setCurrentIndex(gun_index)
            
            set_input.setValue(egzersiz_data.get('sets', 3))
            tekrar_input.setText(str(egzersiz_data.get('reps', '10-12')))
            dinlenme_input.setText('60sn')
        else:
            # Yeni satır - Boş seçim
            egzersiz_combo.setCurrentIndex(-1)
        
        # Satırı kaydet
        self.egzersiz_satirlari.append({
            'widget': satir,
            'egzersiz_combo': egzersiz_combo,
            'gun_combo': gun_combo,
            'set_input': set_input,
            'tekrar_input': tekrar_input,
            'dinlenme_input': dinlenme_input
        })
        
        # Layout'a ekle (stretch'ten önce)
        self.egzersiz_container_layout.insertWidget(
            self.egzersiz_container_layout.count() - 1, 
            satir
        )
    
    def egzersiz_sil(self, satir_widget):
        """Egzersiz satırını siler."""
        # Listeden kaldır
        self.egzersiz_satirlari = [
            s for s in self.egzersiz_satirlari 
            if s['widget'] != satir_widget
        ]
        
        # Widget'ı kaldır
        satir_widget.deleteLater()
    
    def kaydet(self):
        """Programı kaydeder."""
        program_adi = self.program_adi_input.text().strip()
        hedef = self.hedef_input.text().strip()
        aciklama = self.aciklama_input.toPlainText().strip()
        
        if not program_adi:
            QMessageBox.warning(self, "Uyarı", "Lütfen program adı girin!")
            return
        
        if len(self.egzersiz_satirlari) == 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir egzersiz ekleyin!")
            return
        
        try:
            # Program oluştur veya güncelle
            if self.program_id:
                # Güncelleme - PostgreSQL'de update_program fonksiyonu kullan
                dao.update_program(self.program_id, name=program_adi, description=aciklama)
                # Eski egzersizleri sil
                dao.delete_program_exercises(self.program_id)
                program_id = self.program_id
            else:
                # Yeni program oluştur
                program_id = dao.create_program(program_adi, aciklama)
            
            # Egzersizleri ekle
            for satir in self.egzersiz_satirlari:
                combo = satir['egzersiz_combo']
                egzersiz_id = combo.currentData()
                egzersiz_adi = combo.currentText().strip()
                
                # Eğer listeden seçilmediyse (yeni giriş)
                if combo.currentIndex() == -1:
                    if not egzersiz_adi:
                        continue 
                    # Yeni egzersiz oluştur veya varsa ID'sini al
                    egzersiz_id = dao.create_exercise(egzersiz_adi)
                set_sayisi = satir['set_input'].value()
                tekrar = satir['tekrar_input'].text().strip()
                
                # PostgreSQL dao: add_exercise_to_program(program_id, exercise_id, sets, reps)
                dao.add_exercise_to_program(
                    program_id, egzersiz_id, set_sayisi, tekrar
                )
            
            QMessageBox.information(
                self, 
                "Başarılı", 
                "Program başarıyla kaydedildi!" if not self.program_id else "Program başarıyla güncellendi!"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Program kaydedilirken hata oluştu: {str(e)}")
