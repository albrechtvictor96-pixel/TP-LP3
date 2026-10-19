from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class UsuarioRespuesta(BaseModel):
    ID_USUARIO: int
    NRO_CEDULA: int
    NOMBRES: str
    APELLIDOS: str
    CARRERA: str
    ROLE_ACCESO: str

    class Config:
        from_attributes = True


class SolicitudCrear(BaseModel):
    ID_ACTIVIDAD: int
    ID_USUARIO_SOLICITA: int
    OBSERVACIONES: Optional[str] = None
    FECHA_ACTIVIDAD: date
    CARGA_HORARIA_EN_MINUTOS: int
    SUPERVISADO: Optional[str] = None


class SolicitudRespuesta(BaseModel):
    ID_SOLICITUD_CAE: int
    FECHA_SOLICITUD: date
    ESTADO_SOLICITUD: str
    OBSERVACIONES: Optional[str] = None

    class Config:
        from_attributes = True