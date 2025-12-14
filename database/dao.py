"""
Data Access Object (DAO) module
Contains all database get/set functions for PyQt UI
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from database.db import get_db_connection
import re
import hashlib


# ==================== VALIDATION FUNCTIONS ====================


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


def email_dogrula(email: str) -> tuple[bool, str]:
    """Email adresini doğrular."""
    if not email:
        return True, "Geçerli"  # Email opsiyonel
    
    # Basit ama etkili email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Geçerli bir email adresi giriniz! (ornek@email.com)"
    
    return True, "Geçerli"


def telefon_dogrula(telefon: str) -> tuple[bool, str]:
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


# ==================== COACH AUTHENTICATION ====================


def giris_kontrol(kullanici_adi: str, sifre: str) -> str:
    """Coach giriş kontrolü (UI uyumluluğu için)"""
    coach = get_coach_by_username(kullanici_adi)
    
    if not coach:
        return "BULUNAMADI"
    
    sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
    if coach['password'] == sifre_hash:
        return "BASARILI"
    else:
        return "HATALI_SIFRE"


def kullanici_kaydet(kullanici_adi: str, sifre: str, email: str) -> bool:
    """Yeni coach kaydı oluşturur (UI uyumluluğu için)"""
    try:
        sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
        create_coach(kullanici_adi, email, sifre_hash)
        return True
    except Exception:
        return False


# ==================== USERS ====================


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a single user by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT u.*, p.name as program_name 
               FROM users u 
               LEFT JOIN programs p ON u.current_program_id = p.id 
               WHERE u.id = %s""",
            (user_id,),
        )
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()
        conn.close()


def get_all_users() -> List[Dict[str, Any]]:
    """Get all users"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT u.*, p.name as program_name 
               FROM users u 
               LEFT JOIN programs p ON u.current_program_id = p.id 
               ORDER BY u.created_at DESC"""
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_users_by_status(status: str) -> List[Dict[str, Any]]:
    """Get users by status (Aktif/Pasif)"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT u.*, p.name as program_name 
               FROM users u 
               LEFT JOIN programs p ON u.current_program_id = p.id 
               WHERE u.status = %s 
               ORDER BY u.created_at DESC""",
            (status,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def create_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: str,
    gender: str,
    tc_number: str,
    birth_date: date,
    status: str = "Aktif",
    current_program_id: Optional[int] = None,
) -> int:
    """Create a new user. Returns the new user ID"""
    conn = get_db_connection()
    email = (email or "").strip()
    if email == "":
        email = None
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO users (first_name, last_name, email, password, phone, 
               gender, tc_number, status, birth_date, current_program_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
               RETURNING id""",
            (
                first_name,
                last_name,
                email,
                password,
                phone,
                gender,
                tc_number,
                status,
                birth_date,
                current_program_id,
            ),
        )
        user_id = cur.fetchone()["id"]
        conn.commit()
        return user_id
    finally:
        cur.close()
        conn.close()


def update_user(
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    phone: Optional[str] = None,
    gender: Optional[str] = None,
    tc_number: Optional[str] = None,
    status: Optional[str] = None,
    birth_date: Optional[date] = None,
    current_program_id: Optional[int] = None,
) -> bool:
    """Update user fields. Only provided fields will be updated"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        updates = []
        values = []

        if first_name is not None:
            updates.append("first_name = %s")
            values.append(first_name)
        if last_name is not None:
            updates.append("last_name = %s")
            values.append(last_name)
        if email is not None:
            updates.append("email = %s")
            values.append(email)
        if password is not None:
            updates.append("password = %s")
            values.append(password)
        if phone is not None:
            updates.append("phone = %s")
            values.append(phone)
        if gender is not None:
            updates.append("gender = %s")
            values.append(gender)
        if tc_number is not None:
            updates.append("tc_number = %s")
            values.append(tc_number)
        if status is not None:
            updates.append("status = %s")
            values.append(status)
        if birth_date is not None:
            updates.append("birth_date = %s")
            values.append(birth_date)
        if current_program_id is not None:
            updates.append("current_program_id = %s")
            values.append(current_program_id)

        if not updates:
            return False

        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def delete_user(user_id: int) -> bool:
    """Delete a user by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


# ==================== PROGRAMS ====================


def get_program(program_id: int) -> Optional[Dict[str, Any]]:
    """Get a single program by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()
        conn.close()


def get_all_programs() -> List[Dict[str, Any]]:
    """Get all programs"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM programs ORDER BY name")
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def create_program(name: str, description: str) -> int:
    """Create a new program. Returns the new program ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO programs (name, description) VALUES (%s, %s) RETURNING id",
            (name, description),
        )
        program_id = cur.fetchone()["id"]
        conn.commit()
        return program_id
    finally:
        cur.close()
        conn.close()


def update_program(
    program_id: int, name: Optional[str] = None, description: Optional[str] = None
) -> bool:
    """Update program fields"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        updates = []
        values = []

        if name is not None:
            updates.append("name = %s")
            values.append(name)
        if description is not None:
            updates.append("description = %s")
            values.append(description)

        if not updates:
            return False

        values.append(program_id)
        query = f"UPDATE programs SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def delete_program(program_id: int) -> bool:
    """Delete a program by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM programs WHERE id = %s", (program_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


# ==================== EXERCISES ====================


def get_exercise(exercise_id: int) -> Optional[Dict[str, Any]]:
    """Get a single exercise by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()
        conn.close()


def get_all_exercises() -> List[Dict[str, Any]]:
    """Get all exercises"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM exercises ORDER BY name")
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def create_exercise(name: str) -> int:
    """Create a new exercise. Returns the new exercise ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO exercises (name) VALUES (%s) RETURNING id", (name,))
        exercise_id = cur.fetchone()["id"]
        conn.commit()
        return exercise_id
    finally:
        cur.close()
        conn.close()


def update_exercise(exercise_id: int, name: str) -> bool:
    """Update exercise name"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE exercises SET name = %s WHERE id = %s", (name, exercise_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def delete_exercise(exercise_id: int) -> bool:
    """Delete an exercise by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM exercises WHERE id = %s", (exercise_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


# ==================== PROGRAM EXERCISES ====================


def get_program_exercises(program_id: int) -> List[Dict[str, Any]]:
    """Get all exercises for a program"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT pe.*, e.name as exercise_name 
               FROM program_exercises pe 
               JOIN exercises e ON pe.exercise_id = e.id 
               WHERE pe.program_id = %s 
               ORDER BY pe.id""",
            (program_id,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def add_exercise_to_program(
    program_id: int, exercise_id: int, sets: int, reps: int
) -> int:
    """Add an exercise to a program. Returns the new program_exercise ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO program_exercises (program_id, exercise_id, sets, reps) 
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (program_id, exercise_id, sets, reps),
        )
        pe_id = cur.fetchone()["id"]
        conn.commit()
        return pe_id
    finally:
        cur.close()
        conn.close()


def update_program_exercise(
    program_exercise_id: int, sets: Optional[int] = None, reps: Optional[int] = None
) -> bool:
    """Update program exercise sets/reps"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        updates = []
        values = []

        if sets is not None:
            updates.append("sets = %s")
            values.append(sets)
        if reps is not None:
            updates.append("reps = %s")
            values.append(reps)

        if not updates:
            return False

        values.append(program_exercise_id)
        query = f"UPDATE program_exercises SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def remove_exercise_from_program(program_exercise_id: int) -> bool:
    """Remove an exercise from a program"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM program_exercises WHERE id = %s", (program_exercise_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


# ==================== PACKAGES ====================


def get_package(package_id: int) -> Optional[Dict[str, Any]]:
    """Get a single package by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM packages WHERE id = %s", (package_id,))
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()
        conn.close()


def get_all_packages() -> List[Dict[str, Any]]:
    """Get all packages"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM packages ORDER BY duration_days")
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def create_package(
    name: str, duration_days: int, description: str, price: float
) -> int:
    """Create a new package. Returns the new package ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO packages (name, duration_days, description, price) 
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (name, duration_days, description, price),
        )
        package_id = cur.fetchone()["id"]
        conn.commit()
        return package_id
    finally:
        cur.close()
        conn.close()


def update_package(
    package_id: int,
    name: Optional[str] = None,
    duration_days: Optional[int] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
) -> bool:
    """Update package fields"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        updates = []
        values = []

        if name is not None:
            updates.append("name = %s")
            values.append(name)
        if duration_days is not None:
            updates.append("duration_days = %s")
            values.append(duration_days)
        if description is not None:
            updates.append("description = %s")
            values.append(description)
        if price is not None:
            updates.append("price = %s")
            values.append(price)

        if not updates:
            return False

        values.append(package_id)
        query = f"UPDATE packages SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def delete_package(package_id: int) -> bool:
    """Delete a package by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM packages WHERE id = %s", (package_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


# ==================== SUBSCRIPTIONS ====================


def get_subscription(subscription_id: int) -> Optional[Dict[str, Any]]:
    """Get a single subscription by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT s.*, u.first_name, u.last_name, p.name as package_name, 
               pt.name as payment_type_name 
               FROM subscriptions s 
               JOIN users u ON s.user_id = u.id 
               JOIN packages p ON s.package_id = p.id 
               JOIN payment_types pt ON s.payment_type_id = pt.id 
               WHERE s.id = %s""",
            (subscription_id,),
        )
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()
        conn.close()


def get_all_subscriptions() -> List[Dict[str, Any]]:
    """Get all subscriptions"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT s.*, u.first_name, u.last_name, p.name as package_name, 
               pt.name as payment_type_name 
               FROM subscriptions s 
               JOIN users u ON s.user_id = u.id 
               JOIN packages p ON s.package_id = p.id 
               JOIN payment_types pt ON s.payment_type_id = pt.id 
               ORDER BY s.created_at DESC"""
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_user_subscriptions(user_id: int) -> List[Dict[str, Any]]:
    """Get all subscriptions for a user"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT s.*, p.name as package_name, pt.name as payment_type_name 
               FROM subscriptions s 
               JOIN packages p ON s.package_id = p.id 
               JOIN payment_types pt ON s.payment_type_id = pt.id 
               WHERE s.user_id = %s 
               ORDER BY s.start_date DESC""",
            (user_id,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def create_subscription(
    user_id: int,
    package_id: int,
    start_date: datetime,
    end_date: datetime,
    price_sold: float,
    payment_type_id: int,
) -> int:
    """Create a new subscription. Returns the new subscription ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO subscriptions (user_id, package_id, start_date, end_date, 
               price_sold, payment_type_id) 
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (user_id, package_id, start_date, end_date, price_sold, payment_type_id),
        )
        subscription_id = cur.fetchone()["id"]
        conn.commit()
        return subscription_id
    finally:
        cur.close()
        conn.close()


def update_subscription(
    subscription_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    price_sold: Optional[float] = None,
    payment_type_id: Optional[int] = None,
) -> bool:
    """Update subscription fields"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        updates = []
        values = []

        if start_date is not None:
            updates.append("start_date = %s")
            values.append(start_date)
        if end_date is not None:
            updates.append("end_date = %s")
            values.append(end_date)
        if price_sold is not None:
            updates.append("price_sold = %s")
            values.append(price_sold)
        if payment_type_id is not None:
            updates.append("payment_type_id = %s")
            values.append(payment_type_id)

        if not updates:
            return False

        values.append(subscription_id)
        query = f"UPDATE subscriptions SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def delete_subscription(subscription_id: int) -> bool:
    """Delete a subscription by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM subscriptions WHERE id = %s", (subscription_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


# ==================== PAYMENT TYPES ====================


def get_payment_type(payment_type_id: int) -> Optional[Dict[str, Any]]:
    """Get a single payment type by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM payment_types WHERE id = %s", (payment_type_id,))
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()
        conn.close()


def get_all_payment_types() -> List[Dict[str, Any]]:
    """Get all payment types"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM payment_types ORDER BY name")
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


# ==================== COACHES ====================


def get_coach(coach_id: int) -> Optional[Dict[str, Any]]:
    """Get a single coach by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM coaches WHERE id = %s", (coach_id,))
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()
        conn.close()


def get_all_coaches() -> List[Dict[str, Any]]:
    """Get all coaches"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM coaches ORDER BY username")
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_coach_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get a coach by username"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM coaches WHERE username = %s", (username,))
        result = cur.fetchone()
        return dict(result) if result else None
    finally:
        cur.close()
        conn.close()


def create_coach(username: str, email: str, password: str) -> int:
    """Create a new coach. Returns the new coach ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO coaches (username, email, password) VALUES (%s, %s, %s) RETURNING id",
            (username, email, password),
        )
        coach_id = cur.fetchone()["id"]
        conn.commit()
        return coach_id
    finally:
        cur.close()
        conn.close()


def update_coach(
    coach_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
) -> bool:
    """Update coach fields"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        updates = []
        values = []

        if username is not None:
            updates.append("username = %s")
            values.append(username)
        if email is not None:
            updates.append("email = %s")
            values.append(email)
        if password is not None:
            updates.append("password = %s")
            values.append(password)

        if not updates:
            return False

        values.append(coach_id)
        query = f"UPDATE coaches SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, values)
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def delete_coach(coach_id: int) -> bool:
    """Delete a coach by ID"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM coaches WHERE id = %s", (coach_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()
