import sys
import random
import time
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from database import dao

class TurnikeWorker(QThread):
    # Sinyaller: (Ad Soyad, Islem Tipi, Zaman, Program Adi), (Icerideki Kisi Sayisi)
    log_sinyali = pyqtSignal(str, str, str, str)
    sayac_sinyali = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.calisiyor = True
        
        # Ensure table exists
        dao.ensure_access_log_table()
        
        # Zamanlayicilar (saniye cinsinden)
        self.giris_bekleme = random.randint(120, 180)  # 2-3 dakika
        self.cikis_bekleme = 300  # 5 dakika
        
        self.gecen_sure_giris = 0
        self.gecen_sure_cikis = 0
        
    def run(self):
        while self.calisiyor:
            time.sleep(1)
            self.gecen_sure_giris += 1
            self.gecen_sure_cikis += 1
            
            # Giris Eventi
            if self.gecen_sure_giris >= self.giris_bekleme:
                self.giris_yap()
                self.gecen_sure_giris = 0
                self.giris_bekleme = random.randint(120, 180)
            
            # Cikis Eventi
            if self.gecen_sure_cikis >= self.cikis_bekleme:
                self.cikis_yap()
                self.gecen_sure_cikis = 0
                
    def get_currently_inside_ids(self):
        """Helper to find who is inside based on DB logs"""
        logs = dao.get_todays_access_logs()
        inside_ids = set()
        # Logs are ordered DESC (latest first)
        processed_users = set()
        
        for log in logs:
            uid = log['user_id']
            if uid not in processed_users:
                if log['action_type'] == 'GİRİŞ':
                    inside_ids.add(uid)
                processed_users.add(uid)
        return inside_ids

    def giris_yap(self):
        try:
            uyeler = dao.get_all_users()
            if not uyeler:
                return
            
            inside_ids = self.get_currently_inside_ids()
            
            # Rastgele bir uye sec (iceride olmayanlardan)
            disaridakiler = [u for u in uyeler if u['id'] not in inside_ids]
            
            if disaridakiler:
                uye = random.choice(disaridakiler)
                uye_id = uye['id']
                
                # DB'ye kaydet
                dao.add_access_log(uye_id, "GİRİŞ")
                
                # Bilgileri hazirla
                ad_soyad = f"{uye['first_name']} {uye['last_name']}"
                program = uye.get('program_name') or "Program Yok"
                zaman = datetime.now().strftime("%H:%M")
                
                # Signal gonder
                self.log_sinyali.emit(zaman, "GİRİŞ", ad_soyad, program)
                self.sayac_sinyali.emit(dao.get_inside_count())
                
        except Exception as e:
            print(f"Simulasyon giris hatasi: {e}")

    def cikis_yap(self):
        try:
            inside_ids = list(self.get_currently_inside_ids())
            if not inside_ids:
                return
                
            # Iceridekilerden rastgele sec
            uye_id = random.choice(inside_ids)
            uye = dao.get_user(uye_id)
            
            if uye:
                # DB'ye kaydet
                dao.add_access_log(uye_id, "ÇIKIŞ")
                
                # Bilgileri hazirla
                ad_soyad = f"{uye['first_name']} {uye['last_name']}"
                program = uye.get('program_name') or "Program Yok"
                zaman = datetime.now().strftime("%H:%M")
                
                # Signal gonder
                self.log_sinyali.emit(zaman, "ÇIKIŞ", ad_soyad, program)
                self.sayac_sinyali.emit(dao.get_inside_count())
                
        except Exception as e:
            print(f"Simulasyon cikis hatasi: {e}")

    def durdur(self):
        self.calisiyor = False
