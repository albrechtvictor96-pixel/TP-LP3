from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time


class MensajeRespuesta(BaseModel):
    mensaje: str


class UsuarioRegistro(BaseModel):
    NRO_CEDULA: int
    NOMBRES: str
    APELLIDOS: str
    CODIGO_MATRICULA: str
    EMAIL: str
    TELEFONO_CELULAR: str
    CONTRASENHA: str
    CARRERA: str


class LoginSolicitud(BaseModel):
    NRO_CEDULA: int
    CONTRASENHA: str


class UsuarioRespuesta(BaseModel):
    ID_USUARIO: int
    NRO_CEDULA: int
    NOMBRES: str
    APELLIDOS: str
    CARRERA: str
    ROLE_ACCESO: str

    class Config:
        from_attributes = True


class ActividadRespuesta(BaseModel):
    ID_ACTIVIDAD: int
    NOMBRE_ACTIVIDAD: str
    ACTIVO: int
    OBSERVACIONES: Optional[str] = None
    CREDITOS: int
    HORAS_REQUERIDAS: int

    class Config:
        from_attributes = True


class SolicitudCrear(BaseModel):
    ID_ACTIVIDAD: int
    ID_USUARIO_SOLICITA: int
    OBSERVACIONES: Optional[str] = None
    FECHA_ACTIVIDAD: date
    CARGA_HORARIA_EN_MINUTOS: int
    SUPERVISADO: Optional[str] = None


class DetalleSolicitudRespuesta(BaseModel):
    ID_DETALLE_SOLICITUD_CAE: int
    ID_SOLICITUD_CAE: int
    FECHA_ACTIVIDAD: date
    ACTIVIDAD: str
    CARGA_HORARIA_EN_MINUTOS: int
    SUPERVISADO: Optional[str] = None
    ID_USUARIO_SUPERVISA: Optional[int] = None

    class Config:
        from_attributes = True


class SolicitudRespuesta(BaseModel):
    ID_SOLICITUD_CAE: int
    FECHA_SOLICITUD: date
    HORA_SOLICITUD: time
    ID_ACTIVIDAD: int
    ID_USUARIO_SOLICITA: int
    ESTADO_SOLICITUD: str
    OBSERVACIONES: Optional[str] = None
    FECHA_APROBACION_O_RECHAZO: Optional[date] = None
    ID_USUARIO_APRUEBA_O_RECHAZA: Optional[int] = None
    detalles: list[DetalleSolicitudRespuesta] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SolicitudResolucion(BaseModel):
    ESTADO_SOLICITUD: str
    OBSERVACIONES: Optional[str] = None


class ProgresoRespuesta(BaseModel):
    ID_USUARIO: int
    CREDITOS_APROBADOS: int
    META_CREDITOS: int
    CREDITOS_FALTANTES: int
    PORCENTAJE_COMPLETADO: float
    META_CUMPLIDA: bool
    CANTIDAD_PENDIENTE: int
    CANTIDAD_EN_REVISION: int
    CANTIDAD_APROBADA: int
    CANTIDAD_RECHAZADA: int