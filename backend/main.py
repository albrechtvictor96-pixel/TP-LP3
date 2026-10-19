from fastapi import FastAPI
from becal_servicio import obtener_actividades_becal

app = FastAPI(title="Sistema de Créditos Extraacadémicos")

@app.get("/")
def inicio():
    return {"mensaje": "¡El backend en Python está funcionando correctamente!"}

@app.get("/actividades-becal")
def listar_actividades_becal():
    return obtener_actividades_becal()