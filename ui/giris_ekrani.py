import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)
from PyQt5.QtCore import (
    Qt,
    QPropertyAnimation,
    QRect,
    QEasingCurve,
    QParallelAnimationGroup,
    QUrl,
    QTimer,
)
from PyQt5.QtGui import QFont, QPixmap, QImage

from kayit_ol import KayitEkrani
from database.dao import giris_kontrol
from ana_sayfa import AnaSayfa


class GirisEkrani(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spor Salonu Yönetim Sistemi - Giriş")

        # Ana sayfa
        self.anaSayfa = None
        # Kayıt ekranı referansı
        self.kayitEkrani = None

        # Video arka plan ekle
        self.setupVideoBackground()

        self.initUI()
        self.resize(1400, 800)
        self.setMinimumSize(1000, 600)

    def setupVideoBackground(self):
        # Video label oluştur (OpenCV ile video göstermek için)
        self.videoLabel = QLabel(self)
        self.videoLabel.setGeometry(0, 0, 1400, 800)
        self.videoLabel.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.videoLabel.setScaledContents(True)
        self.videoLabel.setStyleSheet("background-color: black;")

        # Initialize video-related attributes
        self.cap = None
        self.videoTimer = None

        # Video dosyasını yükle
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

        # Arka plan için yarı saydam overlay
        self.overlay = QWidget(self)
        self.overlay.setGeometry(0, 0, 1400, 800)
        self.overlay.setStyleSheet("background-color: rgba(26, 26, 46, 0.3);")
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.overlay.show()
        self.overlay.lower()

    def updateVideoFrame(self):
        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            # OpenCV BGR formatını RGB'ye çevir
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Frame'i QImage'e çevir
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888
            )

            # QPixmap'e çevir ve label'a göster
            pixmap = QPixmap.fromImage(q_image)
            # Label boyutuna göre ölçekle
            scaled_pixmap = pixmap.scaled(
                self.videoLabel.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            self.videoLabel.setPixmap(scaled_pixmap)
        else:
            # Video bitti, başa sar
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def showEvent(self, event):
        super().showEvent(event)
        # Video label'ı en arkaya gönder ve boyutlandır
        if hasattr(self, "videoLabel"):
            size = self.size()
            self.videoLabel.setGeometry(0, 0, size.width(), size.height())
            self.videoLabel.lower()
            self.videoLabel.raise_()  # Önce yukarı getir
            self.videoLabel.lower()  # Sonra en arkaya gönder
            self.videoLabel.show()
        if hasattr(self, "overlay"):
            size = self.size()
            self.overlay.setGeometry(0, 0, size.width(), size.height())
            self.overlay.lower()
            self.overlay.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Video label'ı pencere boyutuna göre ayarla
        size = event.size()
        if hasattr(self, "videoLabel"):
            self.videoLabel.setGeometry(0, 0, size.width(), size.height())
            self.videoLabel.lower()
        if hasattr(self, "overlay"):
            self.overlay.setGeometry(0, 0, size.width(), size.height())
            self.overlay.lower()

    def initUI(self):
        # Ana widget'ı şeffaf yap
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background: transparent;")

        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(0)

        # Logo ve başlık bölümü
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)

        self.baslikLabel = QLabel("SPOR SALONU", self)
        self.baslikLabel.setFont(QFont("Arial", 28, QFont.Bold))
        self.baslikLabel.setAlignment(Qt.AlignCenter)
        self.baslikLabel.setStyleSheet("color: white; background: transparent;")

        self.altBaslikLabel = QLabel("Üyelik Takip Sistemi", self)
        self.altBaslikLabel.setFont(QFont("Arial", 14))
        self.altBaslikLabel.setAlignment(Qt.AlignCenter)
        self.altBaslikLabel.setStyleSheet("color: #bbbbbb; background: transparent;")

        logo_layout.addWidget(self.baslikLabel)
        logo_layout.addWidget(self.altBaslikLabel)
        logo_layout.addSpacing(30)

        # Giriş formu
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(15)

        # Kullanıcı adı
        self.kullaniciAdiInput = QLineEdit(self)
        self.kullaniciAdiInput.setPlaceholderText("👤 Kullanıcı Adı")
        self.kullaniciAdiInput.setFixedSize(400, 50)
        self._styleLineDefault(self.kullaniciAdiInput)
        self.kullaniciAdiInput.textChanged.connect(
            lambda: self._styleLineDefault(self.kullaniciAdiInput)
        )

        # Şifre
        self.sifreInput = QLineEdit(self)
        self.sifreInput.setPlaceholderText("🔒 Şifre")
        self.sifreInput.setEchoMode(QLineEdit.Password)
        self.sifreInput.setFixedSize(400, 50)
        self._styleLineDefault(self.sifreInput)
        self.sifreInput.textChanged.connect(
            lambda: self._styleLineDefault(self.sifreInput)
        )
        self.sifreInput.returnPressed.connect(self.girisYap)

        # Giriş butonu
        self.girisButton = QPushButton("Giriş Yap", self)
        self.girisButton.setFixedSize(400, 50)
        self.girisButton.setStyleSheet(
            """
            QPushButton {
                background-color: #e94560;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #d63447;
            }
            QPushButton:pressed {
                background-color: #c23047;
            }
        """
        )
        self.girisButton.clicked.connect(self.girisYap)

        form_layout.addWidget(self.kullaniciAdiInput, alignment=Qt.AlignCenter)
        form_layout.addWidget(self.sifreInput, alignment=Qt.AlignCenter)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.girisButton, alignment=Qt.AlignCenter)

        # Alt bölüm
        alt_layout = QHBoxLayout()
        alt_layout.setAlignment(Qt.AlignCenter)

        self.sifremiUnuttumLabel = QLabel(
            "<a href='#' style='color: #bbbbbb;'>Şifremi unuttum</a>", self
        )
        self.sifremiUnuttumLabel.setStyleSheet("background: transparent;")
        self.sifremiUnuttumLabel.setOpenExternalLinks(False)

        spacer = QLabel(" | ", self)
        spacer.setStyleSheet("color: #666; background: transparent;")

        self.hesapYokLabel = QLabel("Hesabınız yok mu?", self)
        self.hesapYokLabel.setStyleSheet("color: #bbbbbb; background: transparent;")

        self.kayitOlLabel = QLabel(
            "<a href='kayit' style='color: #e94560;'>Kayıt Ol</a>", self
        )
        self.kayitOlLabel.setStyleSheet("background: transparent; font-weight: bold;")
        self.kayitOlLabel.setOpenExternalLinks(False)
        self.kayitOlLabel.linkActivated.connect(self.kayitEkraninaGec)

        alt_layout.addWidget(self.sifremiUnuttumLabel)
        alt_layout.addWidget(spacer)
        alt_layout.addWidget(self.hesapYokLabel)
        alt_layout.addWidget(self.kayitOlLabel)

        # Ana layout'a ekle
        main_layout.addLayout(logo_layout)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(alt_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Video label'ı tekrar en arkaya gönder
        # initUI'dan sonra video label'ını düzgün yerleştir
        if hasattr(self, "videoLabel"):
            self.videoLabel.raise_()
            self.videoLabel.lower()
            self.videoLabel.show()
        if hasattr(self, "overlay"):
            self.overlay.raise_()
            self.overlay.lower()
            self.overlay.show()

    def _styleLineDefault(self, lineEdit):
        lineEdit.setStyleSheet(
            """
            QLineEdit {
                background-color: #1f2833;
                color: white;
                border: 2px solid #2d4059;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #e94560;
            }
        """
        )

    def _styleLineHata(self, lineEdit):
        lineEdit.setStyleSheet(
            """
            QLineEdit {
                background-color: #1f2833;
                color: white;
                border: 2px solid #ff3333;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """
        )

    def girisYap(self):
        kullaniciAdi = self.kullaniciAdiInput.text().strip()
        sifre = self.sifreInput.text()

        if not kullaniciAdi or not sifre:
            self.uyariGoster("Lütfen tüm alanları doldurun!")
            return

        sonuc = giris_kontrol(kullaniciAdi, sifre)

        if sonuc == "BULUNAMADI":
            self._styleLineHata(self.kullaniciAdiInput)
            self.uyariGoster("Kullanıcı bulunamadı!")
        elif sonuc == "HATALI_SIFRE":
            self._styleLineHata(self.sifreInput)
            self.uyariGoster("Hatalı şifre!")
        else:
            self.girisBasarili(kullaniciAdi)

    def girisBasarili(self, kullaniciAdi):
        self.hide()
        self.anaSayfa = AnaSayfa(kullaniciAdi)
        self.anaSayfa.show()

    def kayitEkraninaGec(self):
        # Kayıt ekranını yeniden oluştur
        # Video capture ve timer'ı paylaş
        if self.kayitEkrani:
            self.kayitEkrani.close()

        # Paylaşılan video capture ve timer'ı geçir (None olabilir)
        video_cap = self.cap if hasattr(self, "cap") else None
        video_timer = self.videoTimer if hasattr(self, "videoTimer") else None
        self.kayitEkrani = KayitEkrani(video_cap=video_cap, video_timer=video_timer)
        self.kayitEkrani.setGeometry(self.geometry())
        self.kayitEkrani.geriClicked.connect(self.kayitEkranindanDon)
        self.kayitEkrani.show()
        self.hide()

    def kayitEkranindanDon(self):
        if self.kayitEkrani:
            # Timer callback'ini tekrar giriş ekranına bağla
            if hasattr(self, "videoTimer") and self.videoTimer is not None:
                try:
                    self.videoTimer.timeout.disconnect()
                except TypeError:
                    pass  # No connections to disconnect
                self.videoTimer.timeout.connect(self.updateVideoFrame)

            self.kayitEkrani.close()
            self.kayitEkrani = None

        self.show()
        self.kullaniciAdiInput.clear()
        self.sifreInput.clear()
        self._styleLineDefault(self.kullaniciAdiInput)
        self._styleLineDefault(self.sifreInput)

    def uyariGoster(self, mesaj):
        mbox = QMessageBox(self)
        mbox.setStyleSheet(
            """
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
        """
        )
        mbox.setIcon(QMessageBox.Warning)
        mbox.setWindowTitle("Uyarı")
        mbox.setText(mesaj)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec_()
