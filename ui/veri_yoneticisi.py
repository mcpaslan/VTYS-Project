import hashlib
from datetime import datetime, timedelta

class VeriYoneticisi:
    def __init__(self):
        # In-memory veri yapıları
        self.kullanicilar = []
        self.uyeler = []
        self.paketler = []
        self.uyelikler = []
        self.odemeler = []
        
        # ID sayaçları
        self.kullanici_id = 1
        self.uye_id = 1
        self.paket_id = 1
        self.uyelik_id = 1
        self.odeme_id = 1
        
        self.varsayilan_verileri_ekle()
    
    def varsayilan_verileri_ekle(self):
        # Varsayılan admin kullanıcısı
        sifre_hash = hashlib.sha256("admin123".encode()).hexdigest()
        self.kullanicilar.append({
            'id': self.kullanici_id,
            'kullanici_adi': 'admin',
            'sifre': sifre_hash,
            'rol': 'admin',
            'olusturma_tarihi': datetime.now()
        })
        self.kullanici_id += 1
        
        # Varsayılan paketler
        paketler = [
            ("1 Aylık", 30, 500, "Deneme paketi"),
            ("3 Aylık", 90, 1350, "%10 indirimli"),
            ("6 Aylık", 180, 2400, "%20 indirimli"),
            ("12 Aylık", 365, 4200, "%30 indirimli")
        ]
        
        for paket in paketler:
            self.paketler.append({
                'id': self.paket_id,
                'paket_adi': paket[0],
                'sure_gun': paket[1],
                'fiyat': paket[2],
                'aciklama': paket[3]
            })
            self.paket_id += 1
    
    def giris_kontrol(self, kullanici_adi, sifre):
        sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
        
        # Kullanıcıyı bul
        kullanici = None
        for k in self.kullanicilar:
            if k['kullanici_adi'] == kullanici_adi:
                kullanici = k
                break
        
        if kullanici:
            if kullanici['sifre'] == sifre_hash:
                return "BASARILI"
            else:
                return "HATALI_SIFRE"
        return "BULUNAMADI"
    
    def kullanici_kaydet(self, kullanici_adi, sifre, email):
        # Kullanıcı adı zaten var mı kontrol et
        for k in self.kullanicilar:
            if k['kullanici_adi'] == kullanici_adi:
                return False
        
        sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
        self.kullanicilar.append({
            'id': self.kullanici_id,
            'kullanici_adi': kullanici_adi,
            'sifre': sifre_hash,
            'rol': 'personel',
            'olusturma_tarihi': datetime.now()
        })
        self.kullanici_id += 1
        return True
    
    def uye_ekle(self, ad, soyad, tc_no, telefon, email, dogum_tarihi, cinsiyet):
        # TC no zaten var mı kontrol et
        for u in self.uyeler:
            if u['tc_no'] == tc_no:
                return None
        
        uye_id = self.uye_id
        self.uyeler.append({
            'id': uye_id,
            'ad': ad,
            'soyad': soyad,
            'tc_no': tc_no,
            'telefon': telefon,
            'email': email,
            'dogum_tarihi': dogum_tarihi,
            'cinsiyet': cinsiyet,
            'kayit_tarihi': datetime.now(),
            'aktif': 1
        })
        self.uye_id += 1
        return uye_id
    
    def uyelik_olustur(self, uye_id, paket_id):
        # Paket bilgilerini al
        paket = None
        for p in self.paketler:
            if p['id'] == paket_id:
                paket = p
                break
        
        if paket:
            baslangic = datetime.now().date()
            bitis = baslangic + timedelta(days=paket['sure_gun'])
            
            uyelik_id = self.uyelik_id
            self.uyelikler.append({
                'id': uyelik_id,
                'uye_id': uye_id,
                'paket_id': paket_id,
                'baslangic_tarihi': baslangic,
                'bitis_tarihi': bitis,
                'aktif': 1
            })
            self.uyelik_id += 1
            
            # Ödeme kaydı oluştur
            self.odemeler.append({
                'id': self.odeme_id,
                'uyelik_id': uyelik_id,
                'tutar': paket['fiyat'],
                'odeme_tarihi': datetime.now(),
                'odeme_tipi': 'Nakit',
                'durum': 'tamamlandı'
            })
            self.odeme_id += 1
            
            return uyelik_id
        return None
    
    def uyeleri_getir(self, arama=""):
        sonuclar = []
        
        for uye in self.uyeler:
            # Aktif üyeliği bul
            aktif_uyelik = None
            for uyelik in self.uyelikler:
                if uyelik['uye_id'] == uye['id'] and uyelik['aktif'] == 1:
                    aktif_uyelik = uyelik
                    break
            
            # Paket bilgisini al
            paket_adi = None
            baslangic_tarihi = None
            bitis_tarihi = None
            
            if aktif_uyelik:
                for paket in self.paketler:
                    if paket['id'] == aktif_uyelik['paket_id']:
                        paket_adi = paket['paket_adi']
                        break
                baslangic_tarihi = aktif_uyelik['baslangic_tarihi']
                bitis_tarihi = aktif_uyelik['bitis_tarihi']
            
            # Arama filtresi
            if arama:
                arama_lower = arama.lower()
                if (arama_lower not in uye['ad'].lower() and 
                    arama_lower not in uye['soyad'].lower() and 
                    arama_lower not in uye['tc_no'] and 
                    arama_lower not in (uye['telefon'] or '')):
                    continue
            
            sonuclar.append((
                uye['id'],
                uye['ad'],
                uye['soyad'],
                uye['tc_no'],
                uye['telefon'],
                uye['email'],
                paket_adi,
                baslangic_tarihi,
                bitis_tarihi
            ))
        
        return sonuclar
    
    def paketleri_getir(self):
        sonuclar = []
        for paket in self.paketler:
            sonuclar.append((
                paket['id'],
                paket['paket_adi'],
                paket['sure_gun'],
                paket['fiyat'],
                paket['aciklama']
            ))
        return sonuclar
    
    def odemeleri_getir(self):
        sonuclar = []
        
        for odeme in self.odemeler:
            # Üyelik bilgisini bul
            uyelik = None
            for u in self.uyelikler:
                if u['id'] == odeme['uyelik_id']:
                    uyelik = u
                    break
            
            if uyelik:
                # Üye bilgisini bul
                uye = None
                for uy in self.uyeler:
                    if uy['id'] == uyelik['uye_id']:
                        uye = uy
                        break
                
                if uye:
                    uye_ad = f"{uye['ad']} {uye['soyad']}"
                    sonuclar.append((
                        odeme['id'],
                        uye_ad,
                        odeme['tutar'],
                        odeme['odeme_tarihi'],
                        odeme['odeme_tipi'],
                        odeme['durum']
                    ))
        
        # Tarihe göre ters sırala (en yeni önce)
        sonuclar.reverse()
        return sonuclar
    
    def uye_sil(self, uye_id):
        for uye in self.uyeler:
            if uye['id'] == uye_id:
                uye['aktif'] = 0
                break
    
    def kapat(self):
        # In-memory için gerekli değil, ama geriye dönük uyumluluk için
        pass

# Basit fonksiyonlar (geriye dönük uyumluluk için)
_global_veri_yoneticisi = None

def giris_kontrol(kullanici_adi, sifre):
    global _global_veri_yoneticisi
    if _global_veri_yoneticisi is None:
        _global_veri_yoneticisi = VeriYoneticisi()
    return _global_veri_yoneticisi.giris_kontrol(kullanici_adi, sifre)
