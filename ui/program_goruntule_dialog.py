from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import dao

class ProgramGoruntuleDialog(QDialog):
    def __init__(self, uye_id, uye_adi, parent=None):
        super().__init__(parent)
        self.uye_id = uye_id
        self.uye_adi = uye_adi
        
        self.setWindowTitle(f"Program Görüntüle - {uye_adi}")
        self.setMinimumSize(900, 600)
        self.init_ui()
        self.program_yukle()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel(f"💪 {self.uye_adi} - Antrenman Programı")
        baslik.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(baslik)
        
        # Program bilgileri
        self.bilgi_label = QLabel()
        self.bilgi_label.setWordWrap(True)
        self.bilgi_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                border: 2px solid #3498db;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.bilgi_label)
        
        # Tab widget (günlere göre)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #5dade2;
                color: white;
            }
        """)
        
        layout.addWidget(self.tab_widget)
        
        # Butonlar
        buton_layout = QHBoxLayout()
        
        yazdir_btn = QPushButton("🖨️ Yazdır")
        yazdir_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yazdir_btn.clicked.connect(self.yazdir)
        
        kapat_btn = QPushButton("❌ Kapat")
        kapat_btn.setStyleSheet("""
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
        kapat_btn.clicked.connect(self.accept)
        
        buton_layout.addWidget(yazdir_btn)
        buton_layout.addStretch()
        buton_layout.addWidget(kapat_btn)
        
        layout.addLayout(buton_layout)
        
        self.setLayout(layout)
    
    def program_yukle(self):
        """Üyenin programını yükler."""
        # PostgreSQL'de üyenin programını al
        uye = dao.get_user(self.uye_id)
        
        if not uye or not uye.get('current_program_id'):
            QMessageBox.information(
                self,
                "Bilgi",
                f"{self.uye_adi} için atanmış aktif bir program bulunamadı."
            )
            self.reject()
            return
        
        program_id = uye.get('current_program_id')
        program = dao.get_program(program_id)
        
        if not program:
            QMessageBox.warning(self, "Hata", "Program bilgisi alınamadı!")
            self.reject()
            return
        
        program_adi = program.get('name', '')
        aciklama = program.get('description', '')
        
        # Bilgi etiketini doldur
        bilgi_text = f"<b>Program:</b> {program_adi}<br>"
        bilgi_text += f"<b>Açıklama:</b> {aciklama or 'Yok'}<br>"
        
        self.bilgi_label.setText(bilgi_text)
        
        # Egzersizleri yükle
        egzersizler = dao.get_program_exercises(program_id)
        
        if not egzersizler:
            QMessageBox.warning(
                self,
                "Uyarı",
                "Bu programa henüz egzersiz eklenmemiş!"
            )
            return
        
        # Tüm egzersizleri tek bir tab'de göster (PostgreSQL'de gün bilgisi yok)
        tab = self.egzersiz_tab_olustur("Tüm Egzersizler", egzersizler)
        self.tab_widget.addTab(tab, "💪 Egzersizler")
    
    def egzersiz_tab_olustur(self, baslik, egzersizler):
        """Egzersiz listesi için tab oluşturur."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Başlık
        baslik_label = QLabel(f"💪 {baslik}")
        baslik_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(baslik_label)
        
        # Egzersiz tablosu
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Egzersiz", "Kas Grubu", "Set", "Tekrar"
        ])
        
        table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        # Sütun genişlikleri
        table.setColumnWidth(0, 250)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 100)
        
        # Egzersizleri ekle
        table.setRowCount(len(egzersizler))
        for row, egz in enumerate(egzersizler):
            # PostgreSQL dict: {id, program_id, exercise_id, sets, reps, exercise_name}
            table.setItem(row, 0, QTableWidgetItem(egz.get('exercise_name', '')))
            table.setItem(row, 1, QTableWidgetItem(''))  # Kas grubu bilgisi yok
            table.setItem(row, 2, QTableWidgetItem(str(egz.get('sets', ''))))
            table.setItem(row, 3, QTableWidgetItem(str(egz.get('reps', ''))))
        
        layout.addWidget(table)
        
        widget.setLayout(layout)
        return widget
    
    def yazdir(self):
        """Programı yazdırır."""
        # Basit bir yazdırma dialog'u
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            # HTML formatında program oluştur
            html = self.program_html_olustur()
            
            # Yazdır
            document = QTextDocument()
            document.setHtml(html)
            document.print_(printer)
            
            QMessageBox.information(self, "Başarılı", "Program yazdırıldı!")
    
    def program_html_olustur(self):
        """Program için HTML oluşturur."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
                th {{ background-color: #34495e; color: white; }}
                tr:nth-child(even) {{ background-color: #ecf0f1; }}
            </style>
        </head>
        <body>
            <h1>💪 {self.uye_adi} - Antrenman Programı</h1>
            {self.bilgi_label.text()}
            <hr>
        """
        
        # Her gün için tablo ekle
        for i in range(self.tab_widget.count()):
            gun = self.tab_widget.tabText(i)
            html += f"<h2>📅 {gun}</h2>"
            html += "<table>"
            html += "<tr><th>Egzersiz</th><th>Kas Grubu</th><th>Set</th><th>Tekrar</th><th>Dinlenme</th><th>Notlar</th></tr>"
            
            # Tab'daki tabloyu al
            tab_widget = self.tab_widget.widget(i)
            table = tab_widget.findChild(QTableWidget)
            
            if table:
                for row in range(table.rowCount()):
                    html += "<tr>"
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        html += f"<td>{item.text() if item else ''}</td>"
                    html += "</tr>"
            
            html += "</table>"
        
        html += "</body></html>"
        return html
