from fastapi import FastAPI

# Inicializamos la aplicación Backend
app = FastAPI(title="Sistema de Créditos Extraacadémicos")

@app.get("/")
def inicio():
    return {"mensaje": "¡El backend en Python está funcionando correctamente!"}