import sqlite3
from encryption import CryptoManager
import hmac
import hashlib
from encryption import hash_password

def check_master_password_exists() -> bool:
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    
    # Сначала создаем таблицу, если её нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)
    
    # Затем проверяем существование записи
    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE id = 1)")
    exists = cursor.fetchone()[0]
    conn.close()
    return bool(exists)

def verify_master_password(input_password: str) -> bool:
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return False
        
    stored_hash = result[0]
    salt = bytes.fromhex(stored_hash[:32])  # Первые 32 символа - соль в hex
    stored_key = stored_hash[32:]
    
    # Генерируем хеш из введенного пароля с той же солью
    new_key = hashlib.pbkdf2_hmac(
        'sha512',
        input_password.encode(),
        salt,
        100000,
        dklen=64
    ).hex()
    
    return hmac.compare_digest(new_key, stored_key)

def save_master_password(password: str):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()

    # Создаем таблицу users, если её нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)

    # Хешируем пароль
    hashed = hash_password(password)

    # Сохраняем/обновляем мастер-пароль
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, password_hash)
        VALUES (1, ?)
    """, (hashed,))
    
    conn.commit()
    conn.close()

class DatabaseManager:
    def __init__(self, master_password: str):
        self.conn = sqlite3.connect('passwords.db')
        self.crypto = CryptoManager(master_password)
        self.create_table()

    def export_to_file(self, filename: str):
        """Экспорт с шифрованием и HMAC-проверкой"""
        data = self.conn.execute("SELECT * FROM passwords").fetchall()
        encrypted_data = []
        hmac_key = self.crypto.generate_hmac_key()

        for row in data:
            encrypted_row = self.crypto.encrypt(f"{row[1]},{row[2]},{row[3]},{row[4]}")
            row_hmac = hmac.new(hmac_key, encrypted_row.encode(), hashlib.sha256).hexdigest()
            encrypted_data.append(f"{encrypted_row}:{row_hmac}")

        with open(filename, 'w') as f:
            f.write("\n".join(encrypted_data))


    def import_from_file(self, filename: str):
        """Импорт с проверкой HMAC"""
        hmac_key = self.crypto.generate_hmac_key()
        with open(filename, 'r') as f:
            for line in f:
                encrypted_data, received_hmac = line.strip().split(':')
                calculated_hmac = hmac.new(hmac_key, encrypted_data.encode(), hashlib.sha256).hexdigest()
                
                if not hmac.compare_digest(received_hmac, calculated_hmac):
                    raise SecurityError("Ошибка целостности данных!")
                
                decrypted_data = self.crypto.decrypt(encrypted_data)
                service, username, encrypted_pass, date = decrypted_data.split(',')
                
                self.conn.execute(
                    "INSERT INTO passwords (service, username, password, last_updated) VALUES (?, ?, ?, ?)",
                    (service, username, encrypted_pass, date)
                )
        self.conn.commit()

    def create_table(self):
        """Создание всех необходимых таблиц"""
        # Таблица для паролей
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                last_updated TEXT
            )
        """)

        # Таблица для мастер-пароля
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_password(self, service, username, password):
        encrypted_pass = self.crypto.encrypt(password)
        query = """INSERT INTO passwords (service, username, password, last_updated)
                   VALUES (?, ?, ?, datetime('now'))"""
        self.conn.execute(query, (service, username, encrypted_pass))
        self.conn.commit()

    def get_all_passwords(self):
        cursor = self.conn.execute("SELECT id, service, username, password, last_updated FROM passwords")
        return cursor.fetchall()
    
    def update_password(self, record_id, service, username, password):
        encrypted_pass = self.crypto.encrypt(password)
        query = """UPDATE passwords 
                   SET service = ?, username = ?, password = ?, last_updated = datetime('now') 
                   WHERE id = ?"""
        self.conn.execute(query, (service, username, encrypted_pass, record_id))
        self.conn.commit()

    def get_password_by_id(self, record_id):
        cursor = self.conn.execute("SELECT * FROM passwords WHERE id = ?", (record_id,))
        return cursor.fetchone()
        
    def delete_password(self, record_id):
        self.conn.execute("DELETE FROM passwords WHERE id = ?", (record_id,))
        self.conn.commit()
        