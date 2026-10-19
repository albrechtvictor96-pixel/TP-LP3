from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from data_base import engine, Base, get_db
import modelos
import esquemas

app = FastAPI(title="Sistema de Créditos Extraacadémicos (CAE)")


@app.get("/")
def inicio():
    return {"mensaje": "¡El backend con la base de datos CAE está activo!"}


# ==========================================
# ENDPOINTS DE USUARIOS
# ==========================================

@app.get("/usuarios/", response_model=List[esquemas.UsuarioRespuesta])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(modelos.Usuario).all()


# ==========================================
# ENDPOINTS DE ACTIVIDADES
# ==========================================

@app.get("/actividades/")
def listar_actividades(db: Session = Depends(get_db)):
    return db.query(modelos.Actividad).all()


# ==========================================
# ENDPOINTS DE SOLICITUDES CAE
# ==========================================

@app.post("/solicitudes/", response_model=esquemas.SolicitudRespuesta)
def crear_solicitud(solicitud: esquemas.SolicitudCrear, db: Session = Depends(get_db)):
    # 1. Verificar que el usuario exista
    usuario = db.query(modelos.Usuario).filter(modelos.Usuario.ID_USUARIO == solicitud.ID_USUARIO_SOLICITA).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # 2. Verificar que la actividad exista en el catálogo de la BD
    actividad = db.query(modelos.Actividad).filter(modelos.Actividad.ID_ACTIVIDAD == solicitud.ID_ACTIVIDAD).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada.")

    # 3. Crear la Solicitud principal
    nueva_solicitud = modelos.SolicitudCAE(
        FECHA_SOLICITUD=datetime.now().date(),
        HORA_SOLICITUD=datetime.now().time(),
        ID_ACTIVIDAD=solicitud.ID_ACTIVIDAD,
        ID_USUARIO_SOLICITA=solicitud.ID_USUARIO_SOLICITA,
        ESTADO_SOLICITUD="PENDIENTE",
        OBSERVACIONES=solicitud.OBSERVACIONES
    )
    db.add(nueva_solicitud)
    db.commit()
    db.refresh(nueva_solicitud)

    # 4. Crear el detalle asociado a la solicitud
    nuevo_detalle = modelos.DetalleSolicitudCAE(
        ID_SOLICITUD_CAE=nueva_solicitud.ID_SOLICITUD_CAE,
        FECHA_ACTIVIDAD=solicitud.FECHA_ACTIVIDAD,
        ACTIVIDAD=actividad.NOMBRE_ACTIVIDAD,
        CARGA_HORARIA_EN_MINUTOS=solicitud.CARGA_HORARIA_EN_MINUTOS,
        SUPERVISADO=solicitud.SUPERVISADO
    )
    db.add(nuevo_detalle)
    db.commit()

    return nueva_solicitud


@app.get("/solicitudes/", response_model=List[esquemas.SolicitudRespuesta])
def listar_solicitudes(db: Session = Depends(get_db)):
    return db.query(modelos.SolicitudCAE).all()