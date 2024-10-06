import psycopg2
import bcrypt

# Параметры подключения к базе данных
db_params = {
    "host": "89.250.8.5",
    "port": 23010,
    "database": "ObjectDirectory",  # Замените на имя вашей базы данных
    "user": "postgres",
    "password": "ooo196911"  # Замените на пароль пользователя postgres
}

# Функция для создания пользователя
def create_admin_user(username, password, email):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    try:
        
        # Создание пользователя-администратора
        cur.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s) RETURNING id",
            (username, hashed_password, email, 'user')
        )
        user_id = cur.fetchone()[0]
        
        conn.commit()
        print(f"Пользователь {username} успешно создан с ID {user_id}")
        return user_id
    except psycopg2.Error as e:
        print(f"Ошибка при создании пользователя: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

# Функция для создания bucket'а
def create_bucket(name, owner_id):
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Создание bucket'а
        cur.execute(
            "INSERT INTO buckets (name, owner_id) VALUES (%s, %s) RETURNING id",
            (name, owner_id)
        )
        bucket_id = cur.fetchone()[0]
        
        conn.commit()
        print(f"Bucket {name} успешно создан с ID {bucket_id}")
        return bucket_id
    except psycopg2.Error as e:
        print(f"Ошибка при создании bucket'а: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

# Пример использования
if __name__ == "__main__":
    admin_username = "vasys"
    admin_password = "makaka1969"
    admin_email = "vasiavasia10000@gmail.com"
    
    admin_id = create_admin_user(admin_username, admin_password, admin_email)
    
    if admin_id:
        bucket_name = "bucket"
        #create_bucket(bucket_name, admin_id)