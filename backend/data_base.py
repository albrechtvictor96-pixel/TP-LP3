from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Archivo donde se guardará la base de datos SQLite
DATABASE_URL = "sqlite:///./sistema_creditos.db"

# Crear el motor de la base de datos
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para definir los modelos
Base = declarative_base()

# Dependencia para obtener la sesión en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()