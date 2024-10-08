import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Database
    DB_HOST = '89.250.8.5'
    DB_PORT = 23010
    DB_NAME = 'ObjectDirectory'
    DB_USER = 'postgres'
    DB_PASSWORD = 'ooo196911'
    
    # RocksDB
    ROCKSDB_PATH = os.path.join(BASE_DIR, 'data', 'rocksdb')
    
    # Object Storage
    OBJECT_STORAGE_PATH = os.path.join(BASE_DIR, 'data', 'objects')
    
    # JWT
    JWT_SECRET_KEY = "your-secret-key"  # В реальном приложении используйте безопасный способ хранения ключа
    JWT_ALGORITHM = "HS256"
    BLOCK_STORAGE_PATH = os.path.join(BASE_DIR, 'data', 'blocks')
    
    # Server
    GRPC_SERVER_PORT = 23009
    MAX_WORKERS = 3
    
    # Logging
    LOG_FILE = os.path.join(BASE_DIR, 'server.log')
    LOG_LEVEL = 'ERROR'

config = Config()