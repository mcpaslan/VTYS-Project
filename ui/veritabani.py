import sqlite3
import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

class VeritabaniYoneticisi:
    def __init__(self):
        self.baglanti = sqlite3.connect('spor_salonu.db')
        self.cursor = self.baglanti.cursor()
        self.tablolari_olustur()
    
    def tablolari_olustur(self):
        # Kullanıcılar tablosu (Giriş için)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre TEXT NOT NULL,
                rol TEXT DEFAULT 'personel',
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Üyeler tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS uyeler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                tc_no TEXT UNIQUE NOT NULL,
                telefon TEXT,
                email TEXT,
                dogum_tarihi DATE,
                cinsiyet TEXT,
                kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                aktif INTEGER DEFAULT 1
            )
        ''')
        
        # Paketler tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS paketler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paket_adi TEXT NOT NULL,
                sure_gun INTEGER NOT NULL,
                fiyat REAL NOT NULL,
                aciklama TEXT
            )
        ''')
        
        # Üyelikler tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS uyelikler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uye_id INTEGER NOT NULL,
                paket_id INTEGER NOT NULL,
                baslangic_tarihi DATE NOT NULL,
                bitis_tarihi DATE NOT NULL,
                aktif INTEGER DEFAULT 1,
                FOREIGN KEY (uye_id) REFERENCES uyeler (id),
                FOREIGN KEY (paket_id) REFERENCES paketler (id)
            )
        ''')
        
        # Ödemeler tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS odemeler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uyelik_id INTEGER NOT NULL,
                tutar REAL NOT NULL,
                odeme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                odeme_tipi TEXT,
                durum TEXT DEFAULT 'tamamlandı',
                FOREIGN KEY (uyelik_id) REFERENCES uyelikler (id)
            )
        ''')
        
        # Egzersizler tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS egzersizler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                egzersiz_adi TEXT NOT NULL,
                hedef_kas_grubu TEXT,
                aciklama TEXT,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Programlar tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS programlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_adi TEXT NOT NULL,
                aciklama TEXT,
                hedef TEXT,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                aktif INTEGER DEFAULT 1
            )
        ''')
        
        # Program-Egzersiz ilişki tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS program_egzersizler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_id INTEGER,
                egzersiz_id INTEGER,
                gun TEXT,
                set_sayisi INTEGER,
                tekrar_sayisi TEXT,
                dinlenme_suresi TEXT,
                notlar TEXT,
                FOREIGN KEY (program_id) REFERENCES programlar(id),
                FOREIGN KEY (egzersiz_id) REFERENCES egzersizler(id)
            )
        ''')
        
        # Üye-Program ilişki tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS uye_programlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uye_id INTEGER,
                program_id INTEGER,
                baslangic_tarihi DATE,
                bitis_tarihi DATE,
                atayan_kullanici TEXT,
                notlar TEXT,
                aktif INTEGER DEFAULT 1,
                FOREIGN KEY (uye_id) REFERENCES uyeler(id),
                FOREIGN KEY (program_id) REFERENCES programlar(id)
            )
        ''')
        
        self.baglanti.commit()
        self.varsayilan_verileri_ekle()
    
    def varsayilan_verileri_ekle(self):
        # Varsayılan admin kullanıcısı
        try:
            sifre_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO kullanicilar (kullanici_adi, sifre, rol)
                VALUES (?, ?, ?)
            ''', ("admin", sifre_hash, "admin"))
            self.baglanti.commit()
        except sqlite3.IntegrityError:
            pass  # Kullanıcı zaten var
        
        # Mevcut paketleri kontrol et
        self.cursor.execute('SELECT COUNT(*) FROM paketler')
        paket_sayisi = self.cursor.fetchone()[0]
        
        # Eğer paket yoksa veya 4'ten fazlaysa, paketleri yeniden oluştur
        if paket_sayisi != 4:
            self.cursor.execute('DELETE FROM paketler')
            
            # Varsayılan 4 paket
            paketler = [
                ("1 Aylık", 30, 500, "Deneme paketi"),
                ("3 Aylık", 90, 1350, "%10 indirimli"),
                ("6 Aylık", 180, 2400, "%20 indirimli"),
                ("12 Aylık", 365, 4200, "%30 indirimli")
            ]
            
            for paket in paketler:
                self.cursor.execute('''
                    INSERT INTO paketler (paket_adi, sure_gun, fiyat, aciklama)
                    VALUES (?, ?, ?, ?)
                ''', paket)
            
            self.baglanti.commit()
        
        # Örnek egzersizler ekle
        self.cursor.execute('SELECT COUNT(*) FROM egzersizler')
        egzersiz_sayisi = self.cursor.fetchone()[0]
        
        if egzersiz_sayisi == 0:
            ornek_egzersizler = [
                ("Bench Press", "Göğüs", "Düz bench press hareketi"),
                ("Incline Dumbbell Press", "Göğüs", "Eğimli dumbbell press"),
                ("Cable Fly", "Göğüs", "Kablo ile açılış hareketi"),
                ("Squat", "Bacak", "Barbell squat hareketi"),
                ("Leg Press", "Bacak", "Leg press makinesi"),
                ("Leg Curl", "Bacak", "Arka bacak çalışması"),
                ("Deadlift", "Sırt", "Klasik deadlift"),
                ("Pull-up", "Sırt", "Barfiks hareketi"),
                ("Barbell Row", "Sırt", "Barbell ile kürek çekişi"),
                ("Shoulder Press", "Omuz", "Omuz press hareketi"),
                ("Lateral Raise", "Omuz", "Yanal açılış"),
                ("Front Raise", "Omuz", "Ön açılış"),
                ("Barbell Curl", "Biceps", "Barbell ile biceps çalışması"),
                ("Hammer Curl", "Biceps", "Çekiç curl hareketi"),
                ("Triceps Pushdown", "Triceps", "Kablo ile triceps çalışması"),
                ("Dips", "Triceps", "Paralel bar dips"),
            ]
            
            for egzersiz in ornek_egzersizler:
                self.cursor.execute('''
                    INSERT INTO egzersizler (egzersiz_adi, hedef_kas_grubu, aciklama)
                    VALUES (?, ?, ?)
                ''', egzersiz)
            
            self.baglanti.commit()
    
    def giris_kontrol(self, kullanici_adi, sifre):
        sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
        self.cursor.execute('''
            SELECT * FROM kullanicilar 
            WHERE kullanici_adi = ? AND sifre = ?
        ''', (kullanici_adi, sifre_hash))
        
        sonuc = self.cursor.fetchone()
        if sonuc:
            return "BASARILI"
        
        # Kullanıcı var mı kontrol et
        self.cursor.execute('''
            SELECT * FROM kullanicilar WHERE kullanici_adi = ?
        ''', (kullanici_adi,))
        
        if self.cursor.fetchone():
            return "HATALI_SIFRE"
        return "BULUNAMADI"
    
    def kullanici_kaydet(self, kullanici_adi, sifre, email):
        try:
            sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO kullanicilar (kullanici_adi, sifre, rol)
                VALUES (?, ?, ?)
            ''', (kullanici_adi, sifre_hash, "personel"))
            self.baglanti.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    # ============ VALİDASYON FONKSİYONLARI ============
    
    def tc_dogrula(self, tc_no: str) -> Tuple[bool, str]:
        """TC kimlik numarasını doğrular."""
        if not tc_no:
            return False, "TC kimlik numarası boş olamaz!"
        
        if len(tc_no) != 11:
            return False, "TC kimlik numarası 11 haneli olmalıdır!"
        
        if not tc_no.isdigit():
            return False, "TC kimlik numarası sadece rakamlardan oluşmalıdır!"
        
        if tc_no[0] == '0':
            return False, "TC kimlik numarası 0 ile başlayamaz!"
        
        return True, "Geçerli"
    
    def email_dogrula(self, email: str) -> Tuple[bool, str]:
        """Email adresini doğrular."""
        if not email:
            return True, "Geçerli"  # Email opsiyonel
        
        # Basit ama etkili email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Geçerli bir email adresi giriniz! (ornek@email.com)"
        
        return True, "Geçerli"
    
    def telefon_dogrula(self, telefon: str) -> Tuple[bool, str]:
        """Telefon numarasını doğrular (Türkiye formatı)."""
        if not telefon:
            return True, "Geçerli"  # Telefon opsiyonel
        
        # Sadece rakamları al
        telefon_temiz = re.sub(r'[^0-9]', '', telefon)
        
        # 10 veya 11 haneli olmalı (0 ile başlarsa 11, başlamazsa 10)
        if len(telefon_temiz) == 11 and telefon_temiz[0] == '0':
            return True, "Geçerli"
        elif len(telefon_temiz) == 10 and telefon_temiz[0] != '0':
            return True, "Geçerli"
        else:
            return False, "Telefon numarası 10 veya 11 haneli olmalıdır! (örn: 05XX XXX XX XX)"
    
    # ============ ÜYE İŞLEMLERİ ============
    
    def uye_ekle(self, ad, soyad, tc_no, telefon, email, dogum_tarihi, cinsiyet):
        """Yeni üye ekler - validasyonlarla birlikte."""
        # Validasyonlar
        tc_gecerli, tc_mesaj = self.tc_dogrula(tc_no)
        if not tc_gecerli:
            return None, tc_mesaj
        
        email_gecerli, email_mesaj = self.email_dogrula(email)
        if not email_gecerli:
            return None, email_mesaj
        
        telefon_gecerli, telefon_mesaj = self.telefon_dogrula(telefon)
        if not telefon_gecerli:
            return None, telefon_mesaj
        
        try:
            self.cursor.execute('''
                INSERT INTO uyeler (ad, soyad, tc_no, telefon, email, dogum_tarihi, cinsiyet)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ad, soyad, tc_no, telefon, email, dogum_tarihi, cinsiyet))
            self.baglanti.commit()
            return self.cursor.lastrowid, "Başarılı"
        except sqlite3.IntegrityError:
            return None, "Bu TC kimlik numarası zaten kayıtlı!"
    
    def uye_guncelle(self, uye_id, ad, soyad, telefon, email, dogum_tarihi, cinsiyet):
        """Üye bilgilerini günceller (TC değiştirilemez)."""
        # Validasyonlar
        email_gecerli, email_mesaj = self.email_dogrula(email)
        if not email_gecerli:
            return False, email_mesaj
        
        telefon_gecerli, telefon_mesaj = self.telefon_dogrula(telefon)
        if not telefon_gecerli:
            return False, telefon_mesaj
        
        try:
            self.cursor.execute('''
                UPDATE uyeler 
                SET ad = ?, soyad = ?, telefon = ?, email = ?, 
                    dogum_tarihi = ?, cinsiyet = ?
                WHERE id = ?
            ''', (ad, soyad, telefon, email, dogum_tarihi, cinsiyet, uye_id))
            self.baglanti.commit()
            return True, "Üye bilgileri başarıyla güncellendi!"
        except Exception as e:
            return False, f"Güncelleme hatası: {str(e)}"
    
    def uye_bilgisi_getir(self, uye_id):
        """Belirli bir üyenin tüm bilgilerini getirir."""
        self.cursor.execute('''
            SELECT id, ad, soyad, tc_no, telefon, email, dogum_tarihi, cinsiyet
            FROM uyeler WHERE id = ? AND aktif = 1
        ''', (uye_id,))
        return self.cursor.fetchone()
    
    # ============ ÜYELİK İŞLEMLERİ ============
    
    def uyelik_olustur(self, uye_id, paket_id, odeme_tipi="Nakit"):
        """Yeni üyelik oluşturur."""
        # Paket bilgilerini al
        self.cursor.execute('SELECT sure_gun, fiyat FROM paketler WHERE id = ?', (paket_id,))
        paket = self.cursor.fetchone()
        
        if paket:
            baslangic = datetime.now().date()
            bitis = baslangic + timedelta(days=paket[0])
            
            # Eski aktif üyelikleri pasif yap
            self.cursor.execute('''
                UPDATE uyelikler SET aktif = 0 
                WHERE uye_id = ? AND aktif = 1
            ''', (uye_id,))
            
            self.cursor.execute('''
                INSERT INTO uyelikler (uye_id, paket_id, baslangic_tarihi, bitis_tarihi)
                VALUES (?, ?, ?, ?)
            ''', (uye_id, paket_id, baslangic, bitis))
            
            uyelik_id = self.cursor.lastrowid
            
            # Ödeme kaydı oluştur
            self.cursor.execute('''
                INSERT INTO odemeler (uyelik_id, tutar, odeme_tipi)
                VALUES (?, ?, ?)
            ''', (uyelik_id, paket[1], odeme_tipi))
            
            self.baglanti.commit()
            return uyelik_id
        return None
    
    def uyelik_yenile(self, uye_id, paket_id, odeme_tipi="Nakit"):
        """Mevcut üyenin üyeliğini yeniler."""
        return self.uyelik_olustur(uye_id, paket_id, odeme_tipi)
    
    # ============ LİSTELEME FONKSİYONLARI ============
    
    def uyeleri_getir(self, arama=""):
        if arama:
            self.cursor.execute('''
                SELECT u.id, u.ad || ' ' || u.soyad as ad_soyad, u.tc_no, u.telefon, u.email,
                       p.paket_adi, uy.baslangic_tarihi, uy.bitis_tarihi
                FROM uyeler u
                LEFT JOIN uyelikler uy ON u.id = uy.uye_id AND uy.aktif = 1
                LEFT JOIN paketler p ON uy.paket_id = p.id
                WHERE (u.ad LIKE ? OR u.soyad LIKE ? OR u.tc_no LIKE ? OR u.telefon LIKE ?)
                AND u.aktif = 1
                ORDER BY u.id ASC
            ''', (f'%{arama}%', f'%{arama}%', f'%{arama}%', f'%{arama}%'))
        else:
            self.cursor.execute('''
                SELECT u.id, u.ad || ' ' || u.soyad as ad_soyad, u.tc_no, u.telefon, u.email,
                       p.paket_adi, uy.baslangic_tarihi, uy.bitis_tarihi
                FROM uyeler u
                LEFT JOIN uyelikler uy ON u.id = uy.uye_id AND uy.aktif = 1
                LEFT JOIN paketler p ON uy.paket_id = p.id
                WHERE u.aktif = 1
                ORDER BY u.id ASC
            ''')
        return self.cursor.fetchall()
    
    def paketleri_getir(self):
        self.cursor.execute('SELECT * FROM paketler ORDER BY id ASC')
        return self.cursor.fetchall()
    
    def odemeleri_getir(self):
        self.cursor.execute('''
            SELECT o.id, u.ad || ' ' || u.soyad as uye_ad, o.tutar,
                   o.odeme_tarihi, o.odeme_tipi, o.durum
            FROM odemeler o
            JOIN uyelikler uy ON o.uyelik_id = uy.id
            JOIN uyeler u ON uy.uye_id = u.id
            WHERE u.aktif = 1
            ORDER BY o.odeme_tarihi DESC
        ''')
        return self.cursor.fetchall()
    
    # ============ PROGRAM FONKSİYONLARI ============
    
    # Egzersiz İşlemleri
    def egzersiz_ekle(self, egzersiz_adi, hedef_kas_grubu, aciklama):
        """Yeni egzersiz ekler."""
        self.cursor.execute('''
            INSERT INTO egzersizler (egzersiz_adi, hedef_kas_grubu, aciklama)
            VALUES (?, ?, ?)
        ''', (egzersiz_adi, hedef_kas_grubu, aciklama))
        self.baglanti.commit()
        return self.cursor.lastrowid
    
    def egzersizleri_getir(self):
        """Tüm egzersizleri getirir."""
        self.cursor.execute('SELECT * FROM egzersizler ORDER BY hedef_kas_grubu, egzersiz_adi')
        return self.cursor.fetchall()
    
    def egzersiz_sil(self, egzersiz_id):
        """Egzersiz siler."""
        self.cursor.execute('DELETE FROM egzersizler WHERE id = ?', (egzersiz_id,))
        self.baglanti.commit()
    
    # Program İşlemleri
    def program_olustur(self, program_adi, aciklama, hedef):
        """Yeni program oluşturur."""
        self.cursor.execute('''
            INSERT INTO programlar (program_adi, aciklama, hedef)
            VALUES (?, ?, ?)
        ''', (program_adi, aciklama, hedef))
        self.baglanti.commit()
        return self.cursor.lastrowid
    
    def programlari_getir(self):
        """Aktif programları getirir."""
        self.cursor.execute('SELECT * FROM programlar WHERE aktif = 1 ORDER BY olusturma_tarihi DESC')
        return self.cursor.fetchall()
    
    def program_detay_getir(self, program_id):
        """Program detaylarını getirir."""
        self.cursor.execute('SELECT * FROM programlar WHERE id = ?', (program_id,))
        return self.cursor.fetchone()
    
    def program_sil(self, program_id):
        """Programı pasif yapar (soft delete)."""
        self.cursor.execute('UPDATE programlar SET aktif = 0 WHERE id = ?', (program_id,))
        self.baglanti.commit()
    
    # Program-Egzersiz İlişkilendirme
    def programa_egzersiz_ekle(self, program_id, egzersiz_id, gun, set_sayisi, tekrar_sayisi, dinlenme, notlar=""):
        """Programa egzersiz ekler."""
        self.cursor.execute('''
            INSERT INTO program_egzersizler 
            (program_id, egzersiz_id, gun, set_sayisi, tekrar_sayisi, dinlenme_suresi, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (program_id, egzersiz_id, gun, set_sayisi, tekrar_sayisi, dinlenme, notlar))
        self.baglanti.commit()
        return self.cursor.lastrowid
    
    def program_egzersizlerini_getir(self, program_id):
        """Programdaki tüm egzersizleri getirir."""
        self.cursor.execute('''
            SELECT pe.*, e.egzersiz_adi, e.hedef_kas_grubu
            FROM program_egzersizler pe
            JOIN egzersizler e ON pe.egzersiz_id = e.id
            WHERE pe.program_id = ?
            ORDER BY pe.gun, pe.id
        ''', (program_id,))
        return self.cursor.fetchall()
    
    # Üye-Program İlişkilendirme
    def uyeye_program_ata(self, uye_id, program_id, baslangic_tarihi, bitis_tarihi, atayan, notlar=""):
        """Üyeye program atar."""
        # Eski aktif programları pasif yap
        self.cursor.execute('''
            UPDATE uye_programlar SET aktif = 0 
            WHERE uye_id = ? AND aktif = 1
        ''', (uye_id,))
        
        # Yeni programı ata
        self.cursor.execute('''
            INSERT INTO uye_programlar 
            (uye_id, program_id, baslangic_tarihi, bitis_tarihi, atayan_kullanici, notlar)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (uye_id, program_id, baslangic_tarihi, bitis_tarihi, atayan, notlar))
        self.baglanti.commit()
        return self.cursor.lastrowid
    
    def uye_programini_getir(self, uye_id):
        """Üyenin aktif programını getirir."""
        self.cursor.execute('''
            SELECT up.*, p.program_adi, p.aciklama, p.hedef
            FROM uye_programlar up
            JOIN programlar p ON up.program_id = p.id
            WHERE up.uye_id = ? AND up.aktif = 1
        ''', (uye_id,))
        return self.cursor.fetchone()
    
    def uye_program_gecmisi(self, uye_id):
        """Üyenin tüm program geçmişini getirir."""
        self.cursor.execute('''
            SELECT up.*, p.program_adi, p.aciklama
            FROM uye_programlar up
            JOIN programlar p ON up.program_id = p.id
            WHERE up.uye_id = ?
            ORDER BY up.baslangic_tarihi DESC
        ''', (uye_id,))
        return self.cursor.fetchall()
    
    def uye_programini_pasif_yap(self, uye_id):
        """Üyenin aktif programını pasif yapar."""
        self.cursor.execute('''
            UPDATE uye_programlar SET aktif = 0 
            WHERE uye_id = ? AND aktif = 1
        ''', (uye_id,))
        self.baglanti.commit()
    
    # ============ SİLME VE ID YÖNETİMİ ============
    
    def uye_sil(self, uye_id):
        try:
            # Üyeyi pasif yap (hard delete yerine soft delete)
            self.cursor.execute('UPDATE uyeler SET aktif = 0 WHERE id = ?', (uye_id,))
            # İlgili üyelikleri de pasif yap
            self.cursor.execute('''
                UPDATE uyelikler SET aktif = 0 
                WHERE uye_id = ?
            ''', (uye_id,))
            self.baglanti.commit()
            
            # Hiç aktif üye kalmadıysa ID'yi sıfırla
            self.uye_id_kontrol_ve_sifirla()
            
            return True
        except Exception as e:
            print(f"Silme hatası: {e}")
            return False
    
    def uye_id_kontrol_ve_sifirla(self):
        """Aktif üye yoksa AUTO_INCREMENT'i sıfırlar."""
        try:
            # Aktif üye sayısını kontrol et
            self.cursor.execute('SELECT COUNT(*) FROM uyeler WHERE aktif = 1')
            aktif_uye_sayisi = self.cursor.fetchone()[0]
            
            if aktif_uye_sayisi == 0:
                # Tüm üyeleri sil (pasif olanları da)
                self.cursor.execute('DELETE FROM uyeler')
                # İlgili üyelikleri de sil
                self.cursor.execute('DELETE FROM uyelikler')
                # AUTO_INCREMENT'i sıfırla
                self.cursor.execute('DELETE FROM sqlite_sequence WHERE name="uyeler"')
                self.baglanti.commit()
                print("✓ Üye ID'si sıfırlandı. Yeni üyeler ID 1'den başlayacak.")
        except Exception as e:
            print(f"ID sıfırlama hatası: {e}")
    
    def kapat(self):
        self.baglanti.close()

# Basit fonksiyonlar (geriye dönük uyumluluk için)
def giris_kontrol(kullanici_adi, sifre):
    db = VeritabaniYoneticisi()
    sonuc = db.giris_kontrol(kullanici_adi, sifre)
    db.kapat()
    return sonuc