from sqlalchemy import Column, Integer, String, SmallInteger, Date, Time, ForeignKey, BLOB
from sqlalchemy.orm import relationship
from data_base import Base

class Usuario(Base):
    __tablename__ = "USUARIOS"

    ID_USUARIO = Column(Integer, primary_key=True, index=True, autoincrement=True)
    NRO_CEDULA = Column(Integer, unique=True, nullable=False)
    NOMBRES = Column(String(120), nullable=False)
    APELLIDOS = Column(String(120), nullable=False)
    CODIGO_MATRICULA = Column(String(10), nullable=False)
    EMAIL = Column(String(120), nullable=False)
    TELEFONO_CELULAR = Column(String(18), nullable=False)
    CONTRASENHA = Column(String(60), nullable=False)
    ROLE_ACCESO = Column(String(18), nullable=False)
    CARRERA = Column(String(120), nullable=False)
    FECHA_ALTA = Column(Date, nullable=False)
    ACTIVO = Column(SmallInteger, nullable=False)

    solicitudes = relationship("SolicitudCAE", back_populates="usuario_solicita", foreign_keys="[SolicitudCAE.ID_USUARIO_SOLICITA]")


class Actividad(Base):
    __tablename__ = "ACTIVIDADES"

    ID_ACTIVIDAD = Column(Integer, primary_key=True, index=True, autoincrement=True)
    NOMBRE_ACTIVIDAD = Column(String(180), nullable=False)
    ACTIVO = Column(SmallInteger, nullable=False)
    OBSERVACIONES = Column(String(180))

    solicitudes = relationship("SolicitudCAE", back_populates="actividad")


class SolicitudCAE(Base):
    __tablename__ = "SOLICITUDES_CAESS"

    ID_SOLICITUD_CAE = Column(Integer, primary_key=True, index=True, autoincrement=True)
    FECHA_SOLICITUD = Column(Date, nullable=False)
    HORA_SOLICITUD = Column(Time, nullable=False)
    ID_ACTIVIDAD = Column(Integer, ForeignKey("ACTIVIDADES.ID_ACTIVIDAD"), nullable=False)
    ID_USUARIO_SOLICITA = Column(Integer, ForeignKey("USUARIOS.ID_USUARIO"), nullable=False)
    ESTADO_SOLICITUD = Column(String(20), nullable=False)
    OBSERVACIONES = Column(String(256))
    FECHA_APROBACION_O_RECHAZO = Column(Date)
    ID_USUARIO_APRUEBA_O_RECHAZA = Column(Integer, ForeignKey("USUARIOS.ID_USUARIO"), nullable=True)

    # Relaciones
    usuario_solicita = relationship("Usuario", foreign_keys=[ID_USUARIO_SOLICITA], back_populates="solicitudes")
    actividad = relationship("Actividad", back_populates="solicitudes")
    detalles = relationship("DetalleSolicitudCAE", back_populates="solicitud")


class DetalleSolicitudCAE(Base):
    __tablename__ = "DETALLE_SOLICITUDES_CAES"

    ID_DETALLE_SOLICITUD_CAE = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_SOLICITUD_CAE = Column(Integer, ForeignKey("SOLICITUDES_CAESS.ID_SOLICITUD_CAE"), nullable=False)
    FECHA_ACTIVIDAD = Column(Date, nullable=False)
    ACTIVIDAD = Column(String(256), nullable=False)
    CARGA_HORARIA_EN_MINUTOS = Column(Integer, nullable=False)
    SUPERVISADO = Column(String(64))
    ID_USUARIO_SUPERVISA = Column(Integer, ForeignKey("USUARIOS.ID_USUARIO"), nullable=True)

    solicitud = relationship("SolicitudCAE", back_populates="detalles")