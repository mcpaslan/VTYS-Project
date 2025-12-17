from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTabWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from uye_islemleri import UyeIslemleri
from paket_yonetimi import PaketYonetimi
from odeme_ekrani import OdemeEkrani
from database import dao
from uye_guncelle_dialog import UyeGuncelleDialog
from uyelik_yenile_dialog import UyelikYenileDialog
from program_yonetimi import ProgramYonetimiWidget
from program_ata_dialog import ProgramAtaDialog
from program_goruntule_dialog import ProgramGoruntuleDialog
from datetime import datetime
from PyQt5.QtWidgets import QListWidget
from turnike_simulasyon import TurnikeWorker


class AnaSayfa(QMainWindow):
    def __init__(self, kullanici_adi):
        super().__init__()
        self.kullanici_adi = kullanici_adi
        
        self.setWindowTitle("Spor Salonu Yönetim Sistemi")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1000, 600)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
        """)
        
        self.initUI()
    
    def initUI(self):
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        
        # Üst Bar (Header)
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab Widget (Ana içerik)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
                border-radius: 10px;
                margin: 10px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 15px 30px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background-color: #2c3e50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #dfe4ea;
            }
        """)
        
        # Sekmeleri oluştur
        self.uye_islemleri_widget = UyeIslemleri()
        self.paket_yonetimi_widget = PaketYonetimi()
        self.odeme_widget = OdemeEkrani()
        self.uye_listesi_widget = self.create_uye_listesi()
        self.program_yonetimi_widget = ProgramYonetimiWidget()
        
        self.tabs.addTab(self.create_dashboard(), '🏠 Ana Sayfa')
        self.tabs.addTab(self.uye_islemleri_widget, '👤 Üye İşlemleri')
        self.tabs.addTab(self.uye_listesi_widget, '📋 Üye Listesi')
        self.tabs.addTab(self.paket_yonetimi_widget, '💳 Paket Yönetimi')
        self.tabs.addTab(self.odeme_widget, '💰 Ödemeler')
        self.tabs.addTab(self.program_yonetimi_widget, '💪 Programlar')
        
        main_layout.addWidget(self.tabs)

        # Durum çubuğu
        self.statusBar().showMessage(f'Hoş geldiniz, {self.kullanici_adi}!')
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
        """)
    
    def create_header(self):
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e,
                    stop:1 #2c3e50
                );
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Sol taraf - Logo ve başlık
        left_layout = QHBoxLayout()
        
        logo = QLabel("🏋️", header)
        logo.setFont(QFont('Arial', 40))
        logo.setStyleSheet("background: transparent; color: white;")
        
        title_layout = QVBoxLayout()
        title = QLabel("SPOR SALONU YÖNETİM SİSTEMİ", header)
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        
        subtitle = QLabel("Üyelik Takip Paneli", header)
        subtitle.setFont(QFont('Arial', 10))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        left_layout.addWidget(logo)
        left_layout.addLayout(title_layout)
        left_layout.addStretch()
        
        # Sağ taraf - Kullanıcı bilgisi ve çıkış
        right_layout = QHBoxLayout()
        
        user_label = QLabel(f"👤 {self.kullanici_adi}", header)
        user_label.setFont(QFont('Arial', 12, QFont.Bold))
        user_label.setStyleSheet("color: white; background: transparent; padding: 10px;")
        
        cikis_btn = QPushButton("🚪 Çıkış Yap", header)
        cikis_btn.setFixedSize(120, 40)
        cikis_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                color: white;
                border: 2px solid white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.3);
            }
        """)
        cikis_btn.clicked.connect(self.cikis_yap)
        
        right_layout.addWidget(user_label)
        right_layout.addWidget(cikis_btn)
        
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        header.setLayout(layout)
        
        return header
    
    def create_dashboard(self):
        # Tabloyu garantile
        dao.ensure_access_log_table()
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Istatistik kartlari
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Toplam uye sayisi (sadece aktif)
        uyeler = dao.get_all_users()
        toplam_uye = len(uyeler)
        
        # Aktif uyelikler (status == 'Aktif')
        aktif_uyelik = sum(1 for u in uyeler if u.get('status') == 'Aktif')  
        
        stats_layout.addWidget(self.create_stat_card("Toplam Uye", str(toplam_uye), "#2c3e50"))
        stats_layout.addWidget(self.create_stat_card("Aktif Uyelik", str(aktif_uyelik), "#34495e"))
        
        # Icerideki Uye Karti (Turnike Simulasyonu)
        self.icerideki_label = self.create_stat_card("İçerideki Üye", "0", "#e67e22")
        stats_layout.addWidget(self.icerideki_label)
        
        # Paket Sayisi
        stats_layout.addWidget(self.create_stat_card("Paket Sayisi", str(len(dao.get_all_packages())), "#16213e"))
        
        layout.addLayout(stats_layout)
        
        # --- CANLI TURNIKE LOGLARI ---
        log_layout = QVBoxLayout()
        log_baslik = QLabel("📡 Canlı Turnike Logları")
        log_baslik.setFont(QFont('Arial', 14, QFont.Bold))
        log_baslik.setStyleSheet("color: #2c3e50; margin-top: 10px;")
        
        # QTableWidget Olarak Degistirildi
        self.log_tablosu = QTableWidget()
        self.log_tablosu.setColumnCount(4)
        self.log_tablosu.setHorizontalHeaderLabels(['Zaman', 'Eylem', 'Üye', 'Program'])
        
        # Tablo ayarlari
        self.log_tablosu.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.log_tablosu.verticalHeader().setVisible(False)
        self.log_tablosu.setAlternatingRowColors(True)
        self.log_tablosu.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_tablosu.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_tablosu.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-family: 'Arial';
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        self.log_tablosu.setFixedHeight(250)
        
        log_layout.addWidget(log_baslik)
        log_layout.addWidget(self.log_tablosu)
        layout.addLayout(log_layout)
        
        # Baslangic verilerini yukle
        self.loglari_yukle()
        self.icerideki_label.layout().itemAt(1).widget().setText(str(dao.get_inside_count()))
        
        # Worker baslat (Eger zaten calismiyorsa)
        if not hasattr(self, 'turnike_worker'):
            self.turnike_worker = TurnikeWorker()
            self.turnike_worker.log_sinyali.connect(self.log_ekle)
            self.turnike_worker.sayac_sinyali.connect(self.icerideki_guncelle)
            self.turnike_worker.start()
        
    
        
        info_label = QLabel("Yukarıdaki menüden işlem yapmak istediğiniz bölümü seçebilirsiniz.")
        info_label.setFont(QFont('Arial', 12))
        info_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        

        # Yenile butonu
        refresh_btn = QPushButton('Yenile')
        refresh_btn.setFixedSize(120, 45)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.dashboard_yenile)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    def dashboard_yenile(self):
        """Dashboard istatistiklerini yenile."""
        try:
            # Ana Sayfa tab'ini yeniden olustur
            self.tabs.removeTab(0)
            self.tabs.insertTab(0, self.create_dashboard(), 'Ana Sayfa')
            self.tabs.setCurrentIndex(0)
        except Exception as e:
            print(f"Dashboard yenileme hatasi: {e}")
    
    def create_stat_card(self, baslik, deger, renk):
        card = QWidget()
        card.setFixedHeight(120)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {renk};
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        baslik_label = QLabel(baslik)
        baslik_label.setFont(QFont('Arial', 12, QFont.Bold))
        baslik_label.setStyleSheet("color: white; background: transparent;")
        
        deger_label = QLabel(deger)
        deger_label.setFont(QFont('Arial', 28, QFont.Bold))
        deger_label.setStyleSheet("color: white; background: transparent;")
        
        layout.addWidget(baslik_label)
        layout.addWidget(deger_label)
        layout.addStretch()
        
        card.setLayout(layout)
        return card

    def loglari_yukle(self):
        """Bugunun loglarini DB'den yukle"""
        # DB'den [Newest, ..., Oldest] geliyor
        logs = dao.get_todays_access_logs()
        self.log_tablosu.setRowCount(0)
        
        # En yeni log en ustte olmali.
        # DB'den gelen listeyi ters cevirirsek [Oldest, ..., Newest] olur.
        # log_ekle_tablo methodu insertRow(0) yapiyor (EN USTE EKLİYOR).
        # Yani sirayla:
        # 1. Oldest -> Tablo[0]
        # 2. 2nd Oldest -> Tablo[0] (Oldest asagi duser)
        # ...
        # Son. Newest -> Tablo[0].
        # Sonuc: [Newest, ..., Oldest]. Bu istedigimiz sey.
        
        for log in reversed(logs):
             zaman = log.get('time_str', '')
             islem = log.get('action_type', '')
             ad_soyad = f"{log.get('first_name', '')} {log.get('last_name', '')}"
             program = log.get('program_name') or "Program Yok"
             self.log_ekle_tablo(zaman, islem, ad_soyad, program)

    def log_ekle(self, zaman, islem, ad_soyad, program):
        """Worker'dan gelen sinyal ile tabloya ekle. Signal imzasi: str, str, str, str"""
        self.log_ekle_tablo(zaman, islem, ad_soyad, program)

    def log_ekle_tablo(self, zaman, islem, ad_soyad, program):
        """Tabloya satir ekleme islemi (En uste)"""
        self.log_tablosu.insertRow(0)
        
        item_zaman = QTableWidgetItem(zaman)
        item_islem = QTableWidgetItem(islem)
        item_ad = QTableWidgetItem(ad_soyad)
        item_prog = QTableWidgetItem(program)
        
        # Renklendirme
        if islem == "GİRİŞ":
            item_islem.setForeground(Qt.darkGreen)
            item_islem.setText("🟢 GİRİŞ")
        else:
            item_islem.setForeground(Qt.red)
            item_islem.setText("🔴 ÇIKIŞ")
            
        item_islem.setFont(QFont('Arial', 12, QFont.Bold))
        item_zaman.setTextAlignment(Qt.AlignCenter)
        item_islem.setTextAlignment(Qt.AlignCenter)
        
        self.log_tablosu.setItem(0, 0, item_zaman)
        self.log_tablosu.setItem(0, 1, item_islem)
        self.log_tablosu.setItem(0, 2, item_ad)
        self.log_tablosu.setItem(0, 3, item_prog)
        
        # Temizlik
        if self.log_tablosu.rowCount() > 100:
            self.log_tablosu.removeRow(100)
            
    def icerideki_guncelle(self, sayi):
        """Icerideki uye sayisini gunceller."""
        # Kartin icindeki 2. label (deger labeli) guncellenecek
        try:
             layout = self.icerideki_label.layout()
             deger_label = layout.itemAt(1).widget()
             if isinstance(deger_label, QLabel):
                 deger_label.setText(str(sayi))
        except Exception as e:
            print(f"Sayac guncelleme hatasi: {e}")
    

    def create_uye_listesi(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Arama bölümü
        arama_layout = QHBoxLayout()
        arama_label = QLabel('🔍 Ara:')
        arama_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText('Ad, soyad, TC veya telefon ile ara...')
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
        self.arama_input.textChanged.connect(self.uye_ara)
        
        yenile_btn = QPushButton('🔄 Yenile')
        yenile_btn.setFixedSize(100, 40)
        yenile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yenile_btn.clicked.connect(self.uyeleri_yukle)
        
        arama_layout.addWidget(arama_label)
        arama_layout.addWidget(self.arama_input)
                
        duzenle_btn = QPushButton('Duzenle')
        duzenle_btn.setFixedSize(120, 40)
        duzenle_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        duzenle_btn.clicked.connect(self.uye_duzenle)
        
        yenile_uyelik_btn = QPushButton('Uyelik Yenile')
        yenile_uyelik_btn.setFixedSize(140, 40)
        yenile_uyelik_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        yenile_uyelik_btn.clicked.connect(self.uyelik_yenile)
        
        program_ata_btn = QPushButton('Program Ata')
        program_ata_btn.setFixedSize(140, 40)
        program_ata_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        program_ata_btn.clicked.connect(self.program_ata)
        
        program_goruntule_btn = QPushButton('Program Görüntüle')
        program_goruntule_btn.setFixedSize(160, 40)
        program_goruntule_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        program_goruntule_btn.clicked.connect(self.program_goruntule)
        
        arama_layout.addWidget(duzenle_btn)
        arama_layout.addWidget(yenile_uyelik_btn)
        arama_layout.addWidget(program_ata_btn)
        arama_layout.addWidget(program_goruntule_btn)
                
        sil_btn = QPushButton('Sil')
        sil_btn.setFixedSize(100, 40)
        sil_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        sil_btn.clicked.connect(self.secili_uye_sil)
        
        arama_layout.addWidget(sil_btn)
        arama_layout.addWidget(yenile_btn)
        layout.addLayout(arama_layout)
        
        # Tablo
        self.uye_tablosu = QTableWidget()
        self.uye_tablosu.setColumnCount(9)
        self.uye_tablosu.setHorizontalHeaderLabels(['ID', 'Ad Soyad', 'TC No', 
                                                     'Telefon', 'E-posta', 'Paket', 
                                                     'Başlangıç', 'Bitiş', 'Durum'])
        
        # Sütun genişliklerini ayarla
        self.uye_tablosu.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.uye_tablosu.setColumnWidth(0, 50)  # ID
        self.uye_tablosu.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        
        self.uye_tablosu.setAlternatingRowColors(True)
        self.uye_tablosu.setStyleSheet("""
            QTableWidget {
                gridline-color: #dfe4ea;
                background-color: white;
                border: 1px solid #dfe4ea;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        layout.addWidget(self.uye_tablosu)
        
        self.uyeleri_yukle()
        
        widget.setLayout(layout)
        return widget
    
    def uyeleri_yukle(self):
        uyeler = dao.get_all_users()
        self._uyeleri_tabloya_yukle(uyeler)
    
    def _uyeleri_tabloya_yukle(self, uyeler):
        """Helper method to load users into table"""
        self.uye_tablosu.setRowCount(len(uyeler))
        
        for i, uye in enumerate(uyeler):
            # PostgreSQL dict format: {id, first_name, last_name, tc_number, phone, email, program_name, ...}
            id_val = str(uye.get('id', ''))
            ad_soyad = f"{uye.get('first_name', '')} {uye.get('last_name', '')}"
            tc_no = uye.get('tc_number', '')
            telefon = uye.get('phone', '') or '-'
            email = uye.get('email', '') or '-'
            program_name = uye.get('program_name', '') or '-'
            
            # Üyelik bilgilerini al
            subscriptions = dao.get_user_subscriptions(uye.get('id'))
            baslangic = subscriptions[0].get('start_date', '') if subscriptions else '-'
            bitis = subscriptions[0].get('end_date', '') if subscriptions else '-'
            
            # Durum hesapla (Bitiş tarihi >= Şu an ise Aktif)
            durum = 'Pasif'
            durum_renk = Qt.red
            
            if subscriptions:
                end_date = subscriptions[0].get('end_date')
                if end_date and isinstance(end_date, datetime):
                    if datetime.now() <= end_date:
                        durum = 'Aktif'
                        durum_renk = Qt.darkGreen
            
            data = [id_val, ad_soyad, tc_no, telefon, email, program_name, str(baslangic), str(bitis), durum]
            
            for j, veri in enumerate(data):
                item = QTableWidgetItem(str(veri) if veri else "-")
                item.setTextAlignment(Qt.AlignCenter)
                
                # Durum sütunu renklendirme
                if j == 8:
                    item.setForeground(durum_renk)
                    item.setFont(QFont('Arial', 11, QFont.Bold))
                
                self.uye_tablosu.setItem(i, j, item)
    
    def uye_ara(self):
        arama = self.arama_input.text()
        # PostgreSQL'de arama fonksiyonu yok, tüm üyeleri al ve filtrele
        uyeler = dao.get_all_users()
        
        if arama:
            arama_lower = arama.lower()
            uyeler = [
                u for u in uyeler 
                if arama_lower in (u.get('first_name', '') + ' ' + u.get('last_name', '')).lower()
                or arama_lower in u.get('tc_number', '')
                or arama_lower in u.get('phone', '')
            ]
        
        self._uyeleri_tabloya_yukle(uyeler)
    
    def secili_uye_sil(self):
        # Seçili satırı al
        secili_satirlar = self.uye_tablosu.selectedItems()
        if not secili_satirlar:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek için bir üye seçin!')
            return
        
        # İlk sütundaki ID'yi al
        satir = secili_satirlar[0].row()
        uye_id = int(self.uye_tablosu.item(satir, 0).text())
        uye_ad = self.uye_tablosu.item(satir, 1).text()
        
        # Onay al
        reply = QMessageBox.question(
            self, 
            'Üye Sil', 
            f'"{uye_ad}" isimli üyeyi silmek istediğinize emin misiniz?\n\n'
            f'Bu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if dao.delete_user(uye_id):
                QMessageBox.information(self, 'Başarılı', 'Üye başarıyla silindi!')
                self.uyeleri_yukle()  # Listeyi yenile
            else:
                QMessageBox.warning(self, 'Hata', 'Üye silinirken bir hata oluştu!')
    
    def cikis_yap(self):
        reply = QMessageBox.question(self, 'Çıkış', 
                                     'Çıkış yapmak istediğinize emin misiniz?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.close()
            # Giriş ekranını göster
            from giris_ekrani import GirisEkrani
            self.giris = GirisEkrani()
            self.giris.show()
    

    def uye_duzenle(self):
        """Seçili üyeyi düzenle."""
        secili_satirlar = self.uye_tablosu.selectedItems()
        if not secili_satirlar:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlemek için bir üye seçin!')
            return
        
        satir = secili_satirlar[0].row()
        uye_id = int(self.uye_tablosu.item(satir, 0).text())
        
        # Güncelleme dialog'unu aç
        dialog = UyeGuncelleDialog(uye_id, self)
        dialog.uye_guncellendi.connect(self.uyeleri_yukle)
        dialog.exec_()
    
    def uyelik_yenile(self):
        """Seçili üyenin üyeliğini yenile."""
        secili_satirlar = self.uye_tablosu.selectedItems()
        if not secili_satirlar:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen üyelik yenilemek için bir üye seçin!')
            return
        
        satir = secili_satirlar[0].row()
        uye_id = int(self.uye_tablosu.item(satir, 0).text())
        uye_ad = self.uye_tablosu.item(satir, 1).text()
        
        # Yenileme dialog'unu aç (db parametresi kaldırıldı)
        dialog = UyelikYenileDialog(uye_id, uye_ad, self)
        dialog.uyelik_yenilendi.connect(self.uyeleri_yukle)
        dialog.exec_()
    
    def program_ata(self):
        """Seçili üyeye program atar."""
        secili_satirlar = self.uye_tablosu.selectedItems()
        if not secili_satirlar:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen program atamak için bir üye seçin!')
            return
        
        satir = secili_satirlar[0].row()
        uye_id = int(self.uye_tablosu.item(satir, 0).text())
        uye_ad = self.uye_tablosu.item(satir, 1).text()
        
        dialog = ProgramAtaDialog(uye_id, uye_ad, self)
        dialog.exec_()
    
    def program_goruntule(self):
        """Seçili üyenin programını görüntüler."""
        secili_satirlar = self.uye_tablosu.selectedItems()
        if not secili_satirlar:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen program görüntülemek için bir üye seçin!')
            return
        
        satir = secili_satirlar[0].row()
        uye_id = int(self.uye_tablosu.item(satir, 0).text())
        uye_ad = self.uye_tablosu.item(satir, 1).text()
        
        dialog = ProgramGoruntuleDialog(uye_id, uye_ad, self)
        dialog.exec_()
    
    def closeEvent(self, event):
        # Worker'i durdur
        if hasattr(self, 'turnike_worker'):
            self.turnike_worker.durdur()
            self.turnike_worker.wait()
        event.accept()