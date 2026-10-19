from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from data_base import Base

class Estudiante(Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cedula = Column(String, unique=True, index=True, nullable=False)
    creditos_acumulados = Column(Float, default=0.0)

    solicitudes = relationship("Solicitud", back_populates="estudiante")


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    actividad_nombre = Column(String, nullable=False)
    horas = Column(Integer, nullable=False)
    creditos_solicitados = Column(Float, nullable=False)
    estado = Column(String, default="PENDIENTE")  # PENDIENTE, APROBADO, RECHAZADO

    estudiante = relationship("Estudiante", back_populates="solicitudes")