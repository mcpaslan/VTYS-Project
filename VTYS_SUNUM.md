# 🏋️ Spor Salonu Yönetim Sistemi
## Veri Tabanı Yönetim Sistemi Dersi Sunumu

---

## 📋 Proje Özeti

**PostgreSQL** tabanlı spor salonu üyelik takip ve yönetim sistemi.

| Özellik | Teknoloji |
|---------|-----------|
| **Backend** | Python, PostgreSQL, psycopg2 |
| **Frontend** | PyQt5 |
| **Database Migration** | Alembic |
| **Containerization** | Docker |

---

## 🗄️ Veritabanı Şeması

### Ana Tablolar

```
┌─────────────────────────────────────────────────────────────┐
│                    VERITABANI ŞEMASI                        │
├─────────────────────────────────────────────────────────────┤
│  users              → Üye bilgileri                         │
│  coaches            → Antrenör/Admin kullanıcıları          │
│  packages           → Üyelik paketleri                      │
│  subscriptions      → Üyelik kayıtları                      │
│  payment_types      → Ödeme tipleri                         │
│  programs           → Antrenman programları                 │
│  exercises          → Egzersizler                           │
│  program_exercises  → Program-Egzersiz ilişkisi             │
│  access_logs        → Giriş/Çıkış kayıtları                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 Veritabanı Bağlantısı

### `db.py` - Bağlantı Yönetimi

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

def get_db_connection():
    """
    PostgreSQL veritabanına bağlantı oluşturur.
    RealDictCursor ile sonuçlar sözlük olarak döner.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "localhost"),
            database=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            port=os.getenv("PGPORT", 5432),
            cursor_factory=RealDictCursor,  # Sonuçlar dict olarak döner
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        raise e
```

**Önemli Noktalar:**
- `.env` dosyasından çevre değişkenleri yüklenir
- `RealDictCursor` ile sorgu sonuçları Python sözlüğü olarak döner
- Hata durumunda exception fırlatılır

---

## 📐 DAO (Data Access Object) Yapısı

### DAO Nedir?

**DAO**, veritabanı ile uygulama katmanı arasında **soyutlama katmanı** oluşturan bir tasarım desenidir.

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│    PyQt5 UI       │ ←→  │      dao.py       │ ←→  │    PostgreSQL     │
│   (Arayüz)        │     │  (Veri Erişimi)   │     │   (Veritabanı)    │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

| Özellik | Açıklama |
|---------|----------|
| **CRUD İşlemleri** | Create, Read, Update, Delete işlemlerini tek noktada toplar |
| **SQL Enjeksiyonu Koruması** | Parametreli sorgular kullanır |
| **Bağlantı Yönetimi** | Veritabanı bağlantılarını merkezi olarak yönetir |
| **Transaction Yönetimi** | `commit()` ve `rollback()` işlemlerini kontrollü yapar |

---

## 🔄 Transaction (İşlem) Yönetimi

### Transaction Nedir?

Bir veya daha fazla veritabanı işleminin **tek bir birim** olarak yürütülmesidir.
- ✅ Tüm işlemler başarılı → **COMMIT**
- ❌ Herhangi bir hata → **ROLLBACK**

### Örnek: Kullanıcı Oluşturma

```python
def create_user(first_name, last_name, email, ...):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO users (first_name, last_name, email, ...) 
               VALUES (%s, %s, %s, ...) 
               RETURNING id""",
            (first_name, last_name, email, ...)
        )
        user_id = cur.fetchone()["id"]
        conn.commit()  # ← TRANSACTION ONAYLANIYOR
        return user_id
    finally:
        cur.close()
        conn.close()
```

### Transaction Kullanım Tablosu

| İşlem Tipi | Transaction Kullanımı |
|------------|----------------------|
| **CREATE** (INSERT) | ✅ `conn.commit()` |
| **UPDATE** | ✅ `conn.commit()` |
| **DELETE** | ✅ `conn.commit()` |
| **READ** (SELECT) | ❌ Gerekmez |

---

## ⚠️ Hata Kontrolleri

### 1. Veri Doğrulama (Validation)

```python
def tc_dogrula(tc_no: str) -> tuple[bool, str]:
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
```

### 2. Email Doğrulama

```python
def email_dogrula(email: str) -> tuple[bool, str]:
    """Email adresini doğrular."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Geçerli bir email adresi giriniz! (ornek@email.com)"
    return True, "Geçerli"
```

### 3. Telefon Doğrulama

```python
def telefon_dogrula(telefon: str) -> tuple[bool, str]:
    """Telefon numarasını doğrular (Türkiye formatı)."""
    telefon_temiz = re.sub(r'[^0-9]', '', telefon)
    
    if len(telefon_temiz) == 11 and telefon_temiz[0] == '0':
        return True, "Geçerli"
    elif len(telefon_temiz) == 10 and telefon_temiz[0] != '0':
        return True, "Geçerli"
    else:
        return False, "Telefon numarası 10 veya 11 haneli olmalıdır!"
```

### 4. Try-Finally Yapısı ile Kaynak Yönetimi

```python
def get_user(user_id: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()   # ← Her durumda çalışır
        conn.close()  # ← Bağlantı sızıntısı önlenir
```

---

## 👁️ VIEW Kullanımı

### SQL JOIN ile Sanal Görünümler

Projede SQL `CREATE VIEW` yerine **JOIN sorguları** kullanılmaktadır:

```python
def get_all_subscriptions():
    """Tüm abonelikleri ilişkili verilerle getirir."""
    cur.execute(
        """SELECT s.*, u.first_name, u.last_name, 
                  p.name as package_name, 
                  pt.name as payment_type_name 
           FROM subscriptions s 
           JOIN users u ON s.user_id = u.id 
           JOIN packages p ON s.package_id = p.id 
           JOIN payment_types pt ON s.payment_type_id = pt.id 
           ORDER BY s.created_at DESC"""
    )
```

**Bu sorgu 4 tabloyu birleştirir:**
- `subscriptions` → Abonelik bilgileri
- `users` → Üye adı-soyadı
- `packages` → Paket adı
- `payment_types` → Ödeme tipi

### Alt Sorgu (Subquery) Örneği

```python
def get_inside_count():
    """Şu an içerideki kişi sayısını hesaplar."""
    cur.execute("""
        SELECT COUNT(*) as count FROM (
            SELECT DISTINCT ON (user_id) action_type 
            FROM access_logs 
            WHERE DATE(created_at) = CURRENT_DATE 
            ORDER BY user_id, created_at DESC
        ) as latest_actions 
        WHERE action_type = 'GİRİŞ'
    """)
```

- `DISTINCT ON (user_id)`: Her kullanıcı için tek kayıt alır
- Son aksiyonu 'GİRİŞ' olanlar = İçerideki kişiler

---

## 🔐 Kimlik Doğrulama (Authentication)

### Şifre Hash'leme

```python
import hashlib

def giris_kontrol(kullanici_adi: str, sifre: str) -> str:
    coach = get_coach_by_username(kullanici_adi)
    
    if not coach:
        return "BULUNAMADI"
    
    # SHA-256 ile şifre hash'lenir
    sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
    
    if coach['password'] == sifre_hash:
        return "BASARILI"
    else:
        return "HATALI_SIFRE"
```

**Güvenlik Önlemleri:**
- Şifreler veritabanında **hash olarak** saklanır
- SHA-256 algoritması kullanılır
- Düz metin şifre asla saklanmaz

---

## 🔧 Migration (Veritabanı Versiyonlama)

### Alembic ile Şema Yönetimi

```python
# Migration örneği: Tablolar oluşturma
def upgrade():
    op.execute("""
        CREATE TYPE gender_enum AS ENUM ('Erkek', 'Kadın', 'Diğer');
        CREATE TYPE status_enum AS ENUM ('Aktif', 'Pasif');

        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            tc_number VARCHAR(11) NOT NULL UNIQUE,
            status status_enum NOT NULL DEFAULT 'Aktif',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
```

### Migration Komutları

```bash
# Migration'ları çalıştır
alembic upgrade head

# Geri al
alembic downgrade -1

# Yeni migration oluştur
alembic revision -m "açıklama"
```

---

## 🖥️ Uygulama Geliştirme Aşamaları

### 1. Veritabanı Tasarımı
- E-R diyagramı oluşturuldu
- Tablolar ve ilişkiler belirlendi
- PostgreSQL Docker container kurulumu

### 2. Migration Yapısı
- Alembic ile veritabanı versiyonlama
- 8 adet migration dosyası

### 3. DAO Katmanı
- `dao.py` ile tüm CRUD işlemleri
- Parametreli sorgular (SQL Injection koruması)
- Transaction yönetimi

### 4. UI Geliştirme
- PyQt5 ile masaüstü arayüz
- Modüler yapı (her ekran ayrı dosya)

### 5. Entegrasyon
- UI → DAO → PostgreSQL bağlantısı
- Turnike simülasyonu (giriş/çıkış takibi)

---

## 📊 Proje Yapısı

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
│   └── program_*.py      # Program yönetimi
│
├── docker-compose.yml   # Docker yapılandırması
└── requirements.txt     # Python bağımlılıkları
```

---

## ✅ Özet: VTYS Kavramları

| Kavram | Projede Kullanımı |
|--------|-------------------|
| **CRUD İşlemleri** | `dao.py` - Create, Read, Update, Delete |
| **Transaction** | `conn.commit()` ile veri bütünlüğü |
| **JOIN** | Çoklu tablo birleştirme (subscriptions view) |
| **Subquery** | İçerideki kişi sayısı hesaplama |
| **Foreign Key** | Tablolar arası ilişkiler |
| **ENUM** | `gender_enum`, `status_enum` |
| **Constraint** | UNIQUE, NOT NULL, PRIMARY KEY |
| **Parameterized Query** | SQL Injection koruması |
| **Connection Pooling** | Her işlem için bağlantı açma/kapama |

---

## 🙏 Teşekkürler

**Sorular?**
