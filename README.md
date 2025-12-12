# Spor Salonu Yönetim Sistemi

PostgreSQL tabanlı spor salonu üyelik takip ve yönetim sistemi.

## Özellikler

- 👤 Üye Yönetimi (Kayıt, Güncelleme, Silme)
- 💳 Paket Yönetimi (Aylık, 3 Aylık, 6 Aylık, 12 Aylık)
- 💰 Ödeme Takibi
- 💪 Antrenman Programları
- 📊 İstatistikler ve Raporlama
- 🔐 Kullanıcı Girişi (Coach/Admin)

## Teknolojiler

- **Backend**: Python, PostgreSQL, psycopg2
- **Frontend**: PyQt5
- **Database Migration**: Alembic
- **Containerization**: Docker

## Kurulum

### 1. Gereksinimler

- Python 3.8+
- Docker Desktop
- Git

### 2. Projeyi Klonlayın

```bash
git clone <repository-url>
cd VTYS-Project
```

### 3. Virtual Environment Oluşturun

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 5. Çevre Değişkenlerini Ayarlayın

`.env.example` dosyasını `.env` olarak kopyalayın ve gerekli değerleri girin:

```bash
copy .env.example .env
```

`.env` dosyasını düzenleyin:
```
PGHOST=localhost
PGPORT=5432
PGDATABASE=gym_db
PGUSER=postgres
PGPASSWORD=your_password_here
```

### 6. Docker ile PostgreSQL Başlatın

```bash
docker-compose up -d
```

Veritabanının hazır olduğunu kontrol edin:
```bash
docker-compose ps
```

### 7. Veritabanı Migrasyonlarını Çalıştırın

```bash
cd database
alembic upgrade head
```

### 8. Örnek Verileri Yükleyin (Opsiyonel)

```bash
python seed_mock_data.py
```

## Çalıştırma

### UI Uygulamasını Başlatın

```bash
python ui/main.py
```

### Varsayılan Giriş Bilgileri

- **Kullanıcı Adı**: admin
- **Şifre**: admin123

## Proje Yapısı

```
VTYS-Project/
├── database/              # Veritabanı katmanı
│   ├── dao.py            # Data Access Object (CRUD işlemleri)
│   ├── db.py             # PostgreSQL bağlantı yönetimi
│   ├── migrations/       # Alembic migration dosyaları
│   └── seed_mock_data.py # Test verileri
│
├── ui/                   # PyQt5 arayüz dosyaları
│   ├── main.py           # Uygulama giriş noktası
│   ├── giris_ekrani.py   # Giriş ekranı
│   ├── ana_sayfa.py      # Ana dashboard
│   ├── uye_islemleri.py  # Üye kayıt formu
│   ├── paket_yonetimi.py # Paket listesi
│   ├── odeme_ekrani.py   # Ödeme geçmişi
│   └── program_*.py      # Program yönetimi
│
├── .env                  # Çevre değişkenleri (Git'te değil)
├── .gitignore           # Git ignore kuralları
├── docker-compose.yml   # Docker yapılandırması
├── requirements.txt     # Python bağımlılıkları
└── README.md           # Bu dosya
```

## Veritabanı Şeması

### Ana Tablolar

- `users` - Üye bilgileri
- `coaches` - Antrenör/Admin kullanıcıları
- `packages` - Üyelik paketleri
- `subscriptions` - Üyelik kayıtları
- `payment_types` - Ödeme tipleri
- `programs` - Antrenman programları
- `exercises` - Egzersizler
- `program_exercises` - Program-Egzersiz ilişkisi

## Geliştirme

### Yeni Migration Oluşturma

```bash
cd database
alembic revision -m "açıklama"
```

### Migration'ları Geri Alma

```bash
alembic downgrade -1
```

### Veritabanını Sıfırlama

```bash
docker-compose down -v
docker-compose up -d
alembic upgrade head
python seed_mock_data.py
```

## Sorun Giderme

### Docker Bağlantı Hatası

Eğer "could not connect to server" hatası alıyorsanız:

1. Docker Desktop'ın çalıştığından emin olun
2. PostgreSQL container'ının çalıştığını kontrol edin:
   ```bash
   docker-compose ps
   ```
3. Container'ı yeniden başlatın:
   ```bash
   docker-compose restart
   ```

### Import Hataları

Eğer `ModuleNotFoundError` alıyorsanız:

1. Virtual environment'ın aktif olduğundan emin olun
2. Bağımlılıkları yeniden yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

### PyQt5 Kurulum Sorunları

Windows'ta PyQt5 kurulum hatası alırsanız:

```bash
pip install --upgrade pip
pip install PyQt5 --no-cache-dir
```

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
