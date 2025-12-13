import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer
from PyQt5.QtGui import QFont, QPixmap, QImage
from database.dao import kullanici_kaydet


class KayitEkrani(QWidget):
    geriClicked = pyqtSignal()
    
    def __init__(self, parent=None, video_cap=None, video_timer=None):
        super().__init__()
        self.setWindowTitle("Spor Salonu - Kayıt Ol")
        
        # Paylaşılan video capture ve timer'ı kullan
        self.shared_cap = video_cap
        self.shared_timer = video_timer
        
        # Video arka plan ekle
        self.setupVideoBackground()
        
        self.initUI()
    
    def setupVideoBackground(self):
        # Video label oluştur (OpenCV ile video göstermek için)
        self.videoLabel = QLabel(self)
        self.videoLabel.setGeometry(0, 0, 1400, 800)
        self.videoLabel.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.videoLabel.setScaledContents(True)
        self.videoLabel.setStyleSheet("background-color: black;")
        
        # Paylaşılan video capture varsa onu kullan, yoksa yeni oluştur
        if self.shared_cap is not None and self.shared_cap.isOpened():
            self.cap = self.shared_cap
            # Paylaşılan timer'ı bu ekran için de kullan
            if self.shared_timer:
                # Timer'ın callback'ini değiştir
                self.shared_timer.timeout.disconnect()
                self.shared_timer.timeout.connect(self.updateVideoFrame)
            
            # İlk frame'i göster
            self.updateVideoFrame()
            
            self.videoLabel.show()
            self.videoLabel.lower()
        else:
            # Video dosyasını yükle (paylaşılan capture yoksa)
            video_path = os.path.join(os.path.dirname(__file__), "arka_plan.mp4")
            if os.path.exists(video_path):
                # OpenCV ile video oku
                self.cap = cv2.VideoCapture(video_path)
                if self.cap.isOpened():
                    # Video FPS'ini al
                    fps = self.cap.get(cv2.CAP_PROP_FPS)
                    if fps <= 0:
                        fps = 30  # Varsayılan FPS
                    
                    # Timer ile video frame'lerini güncelle
                    self.videoTimer = QTimer(self)
                    self.videoTimer.timeout.connect(self.updateVideoFrame)
                    self.videoTimer.start(int(1000 / fps))  # ms cinsinden
                    
                    # İlk frame'i göster
                    self.updateVideoFrame()
                    
                    self.videoLabel.show()
                    self.videoLabel.lower()
                else:
                    print(f"Video açılamadı: {video_path}")
                    self.videoLabel.setStyleSheet("background-color: #1a1a2e;")
                    self.videoLabel.show()
                    self.videoLabel.lower()
                    self.cap = None
            else:
                print(f"Video dosyası bulunamadı: {video_path}")
                self.videoLabel.setStyleSheet("background-color: #1a1a2e;")
                self.videoLabel.show()
                self.videoLabel.lower()
                self.cap = None
        
        # Arka plan için yarı saydam overlay
        self.overlay = QWidget(self)
        self.overlay.setGeometry(0, 0, 1400, 800)
        self.overlay.setStyleSheet("background-color: rgba(26, 26, 46, 0.3);")
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.overlay.show()
        self.overlay.lower()
    
    def updateVideoFrame(self):
        # Paylaşılan capture kullan
        cap = self.cap if hasattr(self, 'cap') and self.cap is not None else self.shared_cap
        if cap is None or not cap.isOpened():
            return
        
        ret, frame = cap.read()
        if ret:
            # OpenCV BGR formatını RGB'ye çevir
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Frame'i QImage'e çevir
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # QPixmap'e çevir ve label'a göster
            pixmap = QPixmap.fromImage(q_image)
            # Label boyutuna göre ölçekle
            scaled_pixmap = pixmap.scaled(
                self.videoLabel.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            self.videoLabel.setPixmap(scaled_pixmap)
        else:
            # Video bitti, başa sar
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def showEvent(self, event):
        super().showEvent(event)
        # Video label'ı en arkaya gönder ve boyutlandır
        if hasattr(self, 'videoLabel'):
            size = self.size()
            self.videoLabel.setGeometry(0, 0, size.width(), size.height())
            self.videoLabel.lower()
            self.videoLabel.raise_()  # Önce yukarı getir
            self.videoLabel.lower()   # Sonra en arkaya gönder
            self.videoLabel.show()
        if hasattr(self, 'overlay'):
            size = self.size()
            self.overlay.setGeometry(0, 0, size.width(), size.height())
            self.overlay.lower()
            self.overlay.show()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Video label'ı pencere boyutuna göre ayarla
        size = event.size()
        if hasattr(self, 'videoLabel'):
            self.videoLabel.setGeometry(0, 0, size.width(), size.height())
            self.videoLabel.lower()
        if hasattr(self, 'overlay'):
            self.overlay.setGeometry(0, 0, size.width(), size.height())
            self.overlay.lower()
    
    def initUI(self):
        # Ana widget'ı şeffaf yap
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background: transparent;")
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Merkezi container
        center_widget = QWidget()
        center_widget.setMaximumWidth(900)
        center_widget.setStyleSheet("background: transparent;")
        
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(40, 40, 40, 40)
        center_layout.setSpacing(25)
        
        # Başlık bölümü
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignCenter)
        
        self.baslikLabel = QLabel("Yeni Hesap Oluştur", self)
        self.baslikLabel.setFont(QFont('Arial', 28, QFont.Bold))
        self.baslikLabel.setAlignment(Qt.AlignCenter)
        self.baslikLabel.setStyleSheet("color: white; background: transparent;")
        
        self.aciklamaLabel = QLabel("Sistem kullanıcısı olarak kayıt olun", self)
        self.aciklamaLabel.setFont(QFont('Arial', 13))
        self.aciklamaLabel.setAlignment(Qt.AlignCenter)
        self.aciklamaLabel.setStyleSheet("color: #bbbbbb; background: transparent; margin-bottom: 15px;")
        
        header_layout.addWidget(self.baslikLabel)
        header_layout.addWidget(self.aciklamaLabel)
        
        # Form kartı
        form_card = QWidget()
        form_card.setStyleSheet("""
            QWidget {
                background-color: rgba(44, 62, 80, 0.3);
                border-radius: 15px;
                border: 2px solid rgba(233, 69, 96, 0.3);
            }
        """)
        
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 35, 40, 35)
        form_layout.setSpacing(18)
        
        # Grid layout for inputs (2 columns)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setVerticalSpacing(18)
        
        # Kullanıcı Adı
        kullanici_label = QLabel("Kullanıcı Adı *")
        kullanici_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.kullaniciAdiInput = QLineEdit()
        self.kullaniciAdiInput.setPlaceholderText("Kullanıcı adınızı giriniz")
        self._styleLineDefault(self.kullaniciAdiInput)
        
        # Email
        email_label = QLabel("E-posta *")
        email_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.emailInput = QLineEdit()
        self.emailInput.setPlaceholderText("ornek@email.com")
        self._styleLineDefault(self.emailInput)
        
        # Şifre
        sifre_label = QLabel("Şifre *")
        sifre_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.sifreInput = QLineEdit()
        self.sifreInput.setPlaceholderText("En az 6 karakter")
        self.sifreInput.setEchoMode(QLineEdit.Password)
        self._styleLineDefault(self.sifreInput)
        
        # Şifre Tekrar
        sifre_tekrar_label = QLabel("Şifre Tekrar *")
        sifre_tekrar_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.sifreTekrarInput = QLineEdit()
        self.sifreTekrarInput.setPlaceholderText("Şifrenizi tekrar giriniz")
        self.sifreTekrarInput.setEchoMode(QLineEdit.Password)
        self._styleLineDefault(self.sifreTekrarInput)
        
        # Grid'e ekle
        grid_layout.addWidget(kullanici_label, 0, 0)
        grid_layout.addWidget(self.kullaniciAdiInput, 1, 0)
        grid_layout.addWidget(email_label, 0, 1)
        grid_layout.addWidget(self.emailInput, 1, 1)
        grid_layout.addWidget(sifre_label, 2, 0)
        grid_layout.addWidget(self.sifreInput, 3, 0)
        grid_layout.addWidget(sifre_tekrar_label, 2, 1)
        grid_layout.addWidget(self.sifreTekrarInput, 3, 1)
        
        form_layout.addLayout(grid_layout)
        
        # Bilgi mesajı
        info_label = QLabel("* işaretli alanlar zorunludur")
        info_label.setStyleSheet("color: #95a5a6; font-size: 11px; background: transparent; margin-top: 5px;")
        form_layout.addWidget(info_label)
        
        form_card.setLayout(form_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.geriButton = QPushButton("◀ Geri", self)
        self.geriButton.setFixedHeight(55)
        self.geriButton.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.geriButton.clicked.connect(self.geriClicked.emit)
        
        self.kayitButton = QPushButton("✓ Kayıt Ol", self)
        self.kayitButton.setFixedHeight(55)
        self.kayitButton.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e94560,
                    stop:1 #d63447
                );
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d63447,
                    stop:1 #c23047
                );
            }
            QPushButton:pressed {
                background-color: #b02030;
            }
        """)
        self.kayitButton.clicked.connect(self.kayitOl)
        
        button_layout.addWidget(self.geriButton, 1)
        button_layout.addWidget(self.kayitButton, 2)
        
        # Center layout'a ekle
        center_layout.addLayout(header_layout)
        center_layout.addWidget(form_card)
        center_layout.addSpacing(10)
        center_layout.addLayout(button_layout)
        center_layout.addStretch()
        
        center_widget.setLayout(center_layout)
        
        # Ana layout'a merkezi container'ı ekle
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(center_widget)
        container_layout.addStretch()
        
        main_layout.addLayout(container_layout)
        self.setLayout(main_layout)
        
        # Video label'ı tekrar en arkaya gönder
        if hasattr(self, 'videoLabel'):
            self.videoLabel.lower()
            self.videoLabel.show()
        if hasattr(self, 'overlay'):
            self.overlay.lower()
            self.overlay.show()
    
    def _styleLineDefault(self, lineEdit):
        lineEdit.setFixedHeight(45)
        lineEdit.setStyleSheet("""
            QLineEdit {
                background-color: rgba(31, 40, 51, 0.8);
                color: white;
                border: 2px solid rgba(45, 64, 89, 0.8);
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #e94560;
                background-color: rgba(31, 40, 51, 1);
            }
            QLineEdit::placeholder {
                color: #7f8c8d;
            }
        """)
    
    def kayitOl(self):
        kullaniciAdi = self.kullaniciAdiInput.text().strip()
        email = self.emailInput.text().strip()
        sifre = self.sifreInput.text()
        sifreTekrar = self.sifreTekrarInput.text()
        
        # Doğrulama
        if not kullaniciAdi or not email or not sifre or not sifreTekrar:
            self.uyariGoster("Lütfen tüm zorunlu alanları doldurun!")
            return
        
        if len(kullaniciAdi) < 3:
            self.uyariGoster("Kullanıcı adı en az 3 karakter olmalıdır!")
            return
        
        if "@" not in email or "." not in email:
            self.uyariGoster("Geçerli bir e-posta adresi girin!")
            return
        
        if len(sifre) < 6:
            self.uyariGoster("Şifre en az 6 karakter olmalıdır!")
            return
        
        if sifre != sifreTekrar:
            self.uyariGoster("Şifreler eşleşmiyor!")
            return
        
        # Veritabanına kaydet
        if kullanici_kaydet(kullaniciAdi, sifre, email):
            self.basariGoster("Kayıt başarılı! Giriş yapabilirsiniz.")
            self.formuTemizle()
            self.geriClicked.emit()
        else:
            self.uyariGoster("Bu kullanıcı adı zaten kullanılıyor!")
    
    def formuTemizle(self):
        self.kullaniciAdiInput.clear()
        self.emailInput.clear()
        self.sifreInput.clear()
        self.sifreTekrarInput.clear()
    
    def uyariGoster(self, mesaj):
        mbox = QMessageBox(self)
        mbox.setStyleSheet("""
            QMessageBox {
                background-color: #1f2833;
                min-width: 300px;
                max-width: 400px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 13px;
                min-width: 250px;
                max-width: 350px;
                min-height: 40px;
                padding: 8px 12px;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #d63447;
            }
        """)
        mbox.setIcon(QMessageBox.Warning)
        mbox.setWindowTitle("⚠️ Uyarı")
        mbox.setText(mesaj)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec_()
    
    def basariGoster(self, mesaj):
        mbox = QMessageBox(self)
        mbox.setStyleSheet("""
            QMessageBox {
                background-color: #1f2833;
                min-width: 300px;
                max-width: 400px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 13px;
                min-width: 250px;
                max-width: 350px;
                min-height: 40px;
                padding: 8px 12px;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        mbox.setIcon(QMessageBox.Information)
        mbox.setWindowTitle("✓ Başarılı")
        mbox.setText(mesaj)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec_()