from fastapi import FastAPI
from data_base import engine, Base
import modelos
from becal_servicio import obtener_actividades_becal

# Crear las tablas en la base de datos SQLite si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Créditos Extraacadémicos")

@app.get("/")
def inicio():
    return {"mensaje": "¡El backend con SQLite está funcionando correctamente!"}

@app.get("/actividades-becal")
def listar_actividades_becal():
    return obtener_actividades_becal()