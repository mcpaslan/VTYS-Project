"""
Mock data ekleme scripti
Bu script veritabanına örnek veriler ekler.
"""

import random
from datetime import datetime, timedelta
from db import get_db_connection

# Türkçe isimler ve soyisimler
FIRST_NAMES = [
    "Ahmet",
    "Mehmet",
    "Ali",
    "Mustafa",
    "Hasan",
    "Hüseyin",
    "İbrahim",
    "İsmail",
    "Ayşe",
    "Fatma",
    "Zeynep",
    "Emine",
    "Hatice",
    "Elif",
    "Merve",
    "Selin",
    "Emirhan",
    "Burak",
    "Can",
    "Deniz",
    "Ege",
    "Kaan",
    "Arda",
    "Berk",
]

LAST_NAMES = [
    "Yılmaz",
    "Kaya",
    "Demir",
    "Şahin",
    "Çelik",
    "Yıldız",
    "Yıldırım",
    "Öztürk",
    "Aydın",
    "Özdemir",
    "Arslan",
    "Doğan",
    "Kılıç",
    "Aslan",
    "Çetin",
    "Kara",
]

EXERCISE_NAMES = [
    "Bench Press",
    "Squat",
    "Deadlift",
    "Shoulder Press",
    "Barbell Row",
    "Pull-ups",
    "Dips",
    "Leg Press",
    "Calf Raises",
    "Bicep Curls",
    "Tricep Extensions",
    "Lateral Raises",
    "Crunches",
    "Plank",
    "Leg Curls",
]

PROGRAM_NAMES = [
    "Başlangıç Programı",
    "Orta Seviye Program",
    "İleri Seviye Program",
    "Kas Geliştirme Programı",
    "Güç Artırma Programı",
    "Kardiyo Programı",
]

PACKAGE_NAMES = ["Aylık Paket", "3 Aylık Paket", "6 Aylık Paket", "Yıllık Paket"]

PAYMENT_TYPES = [
    ("Nakit", "Nakit ödeme"),
    ("Kredi Kartı", "Kredi kartı ile ödeme"),
    ("Banka Havalesi", "Banka havalesi ile ödeme"),
]


def generate_tc_number():
    """11 haneli geçerli bir TC kimlik numarası üretir"""
    tc = str(random.randint(10000000000, 99999999999))
    return tc


def generate_phone():
    """Türk telefon numarası üretir"""
    return f"05{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(10, 99)}{random.randint(10, 99)}"


def seed_payment_types(conn):
    """Payment types tablosuna veri ekler"""
    cursor = conn.cursor()
    print("Payment types ekleniyor...")

    for name, description in PAYMENT_TYPES:
        cursor.execute(
            "INSERT INTO payment_types (name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (name, description),
        )

    conn.commit()
    print(f"✓ {len(PAYMENT_TYPES)} payment type eklendi")


def seed_packages(conn):
    """Packages tablosuna veri ekler"""
    cursor = conn.cursor()
    print("Packages ekleniyor...")

    packages_data = [
        ("Aylık Paket", 30, "1 aylık üyelik paketi", 500.00),
        ("3 Aylık Paket", 90, "3 aylık üyelik paketi", 1350.00),
        ("6 Aylık Paket", 180, "6 aylık üyelik paketi", 2400.00),
        ("Yıllık Paket", 365, "1 yıllık üyelik paketi", 4500.00),
    ]

    for name, duration, description, price in packages_data:
        cursor.execute(
            "INSERT INTO packages (name, duration_days, description, price) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (name, duration, description, price),
        )

    conn.commit()
    print(f"✓ {len(packages_data)} package eklendi")


def seed_exercises(conn):
    """Exercises tablosuna veri ekler"""
    cursor = conn.cursor()
    print("Exercises ekleniyor...")

    for exercise_name in EXERCISE_NAMES:
        cursor.execute(
            "INSERT INTO exercises (name) VALUES (%s) ON CONFLICT DO NOTHING",
            (exercise_name,),
        )

    conn.commit()
    print(f"✓ {len(EXERCISE_NAMES)} exercise eklendi")


def seed_programs(conn):
    """Programs tablosuna veri ekler"""
    cursor = conn.cursor()
    print("Programs ekleniyor...")

    program_descriptions = [
        "Yeni başlayanlar için temel egzersiz programı",
        "Orta seviye sporcular için gelişmiş program",
        "İleri seviye sporcular için yoğun program",
        "Kas kütlesi artırma odaklı program",
        "Güç artırma ve performans geliştirme programı",
        "Kardiyovasküler sağlık ve dayanıklılık programı",
    ]

    for i, name in enumerate(PROGRAM_NAMES):
        description = (
            program_descriptions[i] if i < len(program_descriptions) else "Açıklama"
        )
        cursor.execute(
            "INSERT INTO programs (name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (name, description),
        )

    conn.commit()
    print(f"✓ {len(PROGRAM_NAMES)} program eklendi")


def seed_program_exercises(conn):
    """Program exercises tablosuna veri ekler"""
    cursor = conn.cursor()
    print("Program exercises ekleniyor...")

    # Program ID'lerini al
    cursor.execute("SELECT id FROM programs")
    program_ids = [row["id"] for row in cursor.fetchall()]

    # Exercise ID'lerini al
    cursor.execute("SELECT id FROM exercises")
    exercise_ids = [row["id"] for row in cursor.fetchall()]

    if not program_ids or not exercise_ids:
        print("⚠ Program veya exercise bulunamadı, program_exercises eklenemedi")
        return

    # Her programa 3-6 egzersiz ekle
    for program_id in program_ids:
        num_exercises = random.randint(3, 6)
        selected_exercises = random.sample(
            exercise_ids, min(num_exercises, len(exercise_ids))
        )

        for exercise_id in selected_exercises:
            sets = random.randint(3, 5)
            reps = random.randint(8, 15)
            cursor.execute(
                """INSERT INTO program_exercises (program_id, exercise_id, sets, reps) 
                   VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (program_id, exercise_id, sets, reps),
            )

    conn.commit()
    print("✓ Program exercises eklendi")


def seed_coaches(conn):
    """Coaches tablosuna veri ekler"""
    import hashlib
    cursor = conn.cursor()
    print("Coaches ekleniyor...")

    coaches_data = [
        ("admin", "admin@gym.com", "admin123"),
        ("coach1", "coach1@example.com", "password123"),
        ("coach2", "coach2@example.com", "password123"),
        ("coach3", "coach3@example.com", "password123"),
    ]

    for username, email, password in coaches_data:
        # Şifreyi SHA256 ile hash'le (dao.py ile aynı yöntem)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO coaches (username, email, password) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (username, email, password_hash),
        )

    conn.commit()
    print(f"✓ {len(coaches_data)} coach eklendi")


def seed_users(conn, num_users=20):
    """Users tablosuna veri ekler"""
    cursor = conn.cursor()
    print(f"{num_users} user ekleniyor...")

    genders = ["Erkek", "Kadın", "Diğer"]
    genders = ["Erkek", "Kadın", "Diğer"]
    # Varsayılan olarak çoğunlukla Aktif olsun
    statuses = ["Aktif", "Aktif", "Aktif", "Pasif"]

    # Program ID'lerini al
    cursor.execute("SELECT id FROM programs")
    program_ids = [row["id"] for row in cursor.fetchall()]

    users_added = 0
    for i in range(num_users):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        password = "password123"  # Gerçek uygulamada hash'lenmeli
        phone = generate_phone()
        gender = random.choice(genders)
        tc_number = generate_tc_number()
        status = random.choice(statuses)

        # Doğum tarihi (18-65 yaş arası)
        birth_date = datetime.now() - timedelta(days=random.randint(18 * 365, 65 * 365))

        # %50 ihtimalle program atanır
        program_id = (
            random.choice(program_ids)
            if program_ids and random.random() > 0.5
            else None
        )

        try:
            cursor.execute(
                """INSERT INTO users (first_name, last_name, email, password, phone, gender, tc_number, status, birth_date, current_program_id) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    first_name,
                    last_name,
                    email,
                    password,
                    phone,
                    gender,
                    tc_number,
                    status,
                    birth_date.date(),
                    program_id,
                ),
            )
            users_added += 1
        except Exception as e:
            print(f"⚠ User eklenirken hata: {email} - {e}")

    conn.commit()
    print(f"✓ {users_added} user eklendi")


def seed_subscriptions(conn):
    """Subscriptions tablosuna veri ekler"""
    cursor = conn.cursor()
    print("Subscriptions ekleniyor...")

    # User ID'lerini al
    cursor.execute("SELECT id FROM users")
    user_ids = [row["id"] for row in cursor.fetchall()]

    # Package ID'lerini al
    cursor.execute("SELECT id, duration_days FROM packages")
    packages = cursor.fetchall()

    # Payment type ID'lerini al
    cursor.execute("SELECT id FROM payment_types")
    payment_type_ids = [row["id"] for row in cursor.fetchall()]

    if not user_ids or not packages or not payment_type_ids:
        print("⚠ User, package veya payment_type bulunamadı, subscriptions eklenemedi")
        return

    subscriptions_added = 0
    # Her kullanıcı için 0-2 abonelik ekle
    for user_id in user_ids:
        num_subs = random.randint(0, 2)
        for _ in range(num_subs):
            package = random.choice(packages)
            package_id = package["id"]
            duration_days = package["duration_days"]

            start_date = datetime.now() - timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(days=duration_days)

            # Paket fiyatından %0-20 indirim yapılabilir
            cursor.execute("SELECT price FROM packages WHERE id = %s", (package_id,))
            base_price = cursor.fetchone()["price"]
            price_sold = float(base_price) * (1 - random.uniform(0, 0.2))

            payment_type_id = random.choice(payment_type_ids)

            try:
                cursor.execute(
                    """INSERT INTO subscriptions (user_id, package_id, start_date, end_date, price_sold, payment_type_id) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        user_id,
                        package_id,
                        start_date,
                        end_date,
                        price_sold,
                        payment_type_id,
                    ),
                )
                subscriptions_added += 1
            except Exception as e:
                print(f"⚠ Subscription eklenirken hata: {e}")

    conn.commit()
    print(f"✓ {subscriptions_added} subscription eklendi")


def main():
    """Ana fonksiyon - tüm mock datayı ekler"""
    print("=" * 50)
    print("Mock Data Ekleme İşlemi Başlatılıyor...")
    print("=" * 50)

    try:
        conn = get_db_connection()
        print("✓ Veritabanı bağlantısı başarılı\n")

        # Sırayla tüm tablolara veri ekle
        seed_payment_types(conn)
        seed_packages(conn)
        seed_exercises(conn)
        seed_programs(conn)
        seed_program_exercises(conn)
        seed_coaches(conn)
        seed_users(conn, num_users=20)
        seed_subscriptions(conn)

        print("\n" + "=" * 50)
        print("✓ Tüm mock data başarıyla eklendi!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        raise
    finally:
        if "conn" in locals():
            conn.close()
            print("\n✓ Veritabanı bağlantısı kapatıldı")


if __name__ == "__main__":
    main()
