import bcrypt
from datetime import date, datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from data_base import get_db
import modelos
import esquemas

app = FastAPI(title="Sistema de Créditos Extraacadémicos (CAE)")

# Permitimos que el frontend local se conecte desde cualquier puerto HTTP.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reglas de la Resolución 33/2020: horas por crédito y máximo por actividad.
REGLAS_CAE = {
    1: {"nombre": "Asignaturas electivas", "horas_por_credito": 16, "maximo_creditos": 5},  # 16 h, máximo 5
    2: {"nombre": "Cursos o talleres", "horas_por_credito": 16, "maximo_creditos": 5},  # 16 h, máximo 5
    3: {"nombre": "Conferencias, congresos y seminarios", "horas_por_credito": 16, "maximo_creditos": 4},  # 16 h, máximo 4
    4: {"nombre": "Ayudantías de cátedra o de laboratorio", "horas_por_credito": 16, "maximo_creditos": 4},  # 16 h, máximo 4
    5: {"nombre": "Pasantías extracurriculares", "horas_por_credito": 48, "maximo_creditos": 4},  # 48 h, máximo 4
    6: {"nombre": "Investigación", "horas_por_credito": 32, "maximo_creditos": 8},  # 32 h, máximo 8
    7: {"nombre": "Extensión universitaria", "horas_por_credito": 32, "maximo_creditos": 4},  # 32 h, máximo 4
    8: {"nombre": "Compromiso social", "horas_por_credito": 32, "maximo_creditos": 2},  # 32 h, máximo 2
}
# La actividad 9 no figura en el reglamento; queda sin regla y no otorga créditos.


def calcular_creditos(id_actividad: int, minutos: int) -> float:
    # Truncamos cada solicitud a un decimal, sin redondear hacia arriba.
    regla = REGLAS_CAE.get(id_actividad)
    if regla is None:
        return 0.0
    horas_por_credito = regla["horas_por_credito"]
    decimos = abs(minutos) * 10 // (60 * horas_por_credito)
    return (decimos if minutos >= 0 else -decimos) / 10


def preparar_solicitud_respuesta(solicitud):
    # Calculamos los créditos con todos los detalles de la solicitud, sin aplicar topes.
    respuesta = esquemas.SolicitudRespuesta.model_validate(solicitud)
    minutos = sum(
        detalle.CARGA_HORARIA_EN_MINUTOS for detalle in solicitud.detalles
    )
    respuesta.CREDITOS_CALCULADOS = calcular_creditos(
        solicitud.ID_ACTIVIDAD,
        minutos,
    )
    return respuesta


def hashear_contrasenha(contrasenha):
    # Guardamos la contraseña como hash para no conservar el texto original.
    return bcrypt.hashpw(contrasenha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_contrasenha(contrasenha, hash_contrasenha):
    # Comparamos la contraseña ingresada con el hash guardado.
    return bcrypt.checkpw(contrasenha.encode("utf-8"), hash_contrasenha.encode("utf-8"))


def verificar_rol_usuario(db, id_usuario, roles_permitidos):
    # Buscamos quién realiza la acción y comprobamos que tenga uno de los roles permitidos.
    usuario = db.query(modelos.Usuario).filter(
        modelos.Usuario.ID_USUARIO == id_usuario
    ).first()
    if not usuario or usuario.ROLE_ACCESO not in roles_permitidos:
        raise HTTPException(status_code=403, detail="El usuario no tiene permiso para esta acción.")
    return usuario


@app.get("/", response_model=esquemas.MensajeRespuesta)
def inicio():
    return {"mensaje": "El backend con la base de datos CAE está activo."}


@app.post("/registro", response_model=esquemas.UsuarioRespuesta, status_code=201)
def registrar_usuario(datos: esquemas.UsuarioRegistro, db: Session = Depends(get_db)):
    # Exigimos una contraseña mínima antes de guardarla en la base.
    if len(datos.CONTRASENHA) < 6:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 6 caracteres.",
        )

    # Evitamos que una cédula registrada se use para crear otra cuenta.
    usuario_existente = db.query(modelos.Usuario).filter(
        modelos.Usuario.NRO_CEDULA == datos.NRO_CEDULA
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=409, detail="La cédula ya está registrada.")

    # Todo registro nuevo queda como estudiante y se activa en la fecha actual.
    nuevo_usuario = modelos.Usuario(
        NRO_CEDULA=datos.NRO_CEDULA,
        NOMBRES=datos.NOMBRES,
        APELLIDOS=datos.APELLIDOS,
        CODIGO_MATRICULA=datos.CODIGO_MATRICULA,
        EMAIL=datos.EMAIL,
        TELEFONO_CELULAR=datos.TELEFONO_CELULAR,
        CONTRASENHA=hashear_contrasenha(datos.CONTRASENHA),
        ROLE_ACCESO="estudiante",
        CARRERA=datos.CARRERA,
        FECHA_ALTA=date.today(),
        ACTIVO=1,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@app.post("/login", response_model=esquemas.UsuarioRespuesta)
def iniciar_sesion(datos: esquemas.LoginSolicitud, db: Session = Depends(get_db)):
    # Buscamos la cuenta por cédula y verificamos su contraseña guardada.
    usuario = db.query(modelos.Usuario).filter(
        modelos.Usuario.NRO_CEDULA == datos.NRO_CEDULA
    ).first()
    if not usuario or not verificar_contrasenha(
        datos.CONTRASENHA, usuario.CONTRASENHA
    ):
        raise HTTPException(status_code=401, detail="Cédula o contraseña incorrecta.")
    return usuario


# ==========================================
# ENDPOINTS DE USUARIOS
# ==========================================

@app.get("/usuarios/", response_model=List[esquemas.UsuarioRespuesta])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(modelos.Usuario).all()


# ==========================================
# ENDPOINTS DE ACTIVIDADES
# ==========================================

@app.get("/actividades/", response_model=List[esquemas.ActividadRespuesta])
def listar_actividades(db: Session = Depends(get_db)):
    return db.query(modelos.Actividad).all()


# ==========================================
# ENDPOINTS DE SOLICITUDES CAE
# ==========================================

@app.post("/solicitudes/", response_model=esquemas.SolicitudRespuesta)
def crear_solicitud(solicitud: esquemas.SolicitudCrear, db: Session = Depends(get_db)):
    # Solo un estudiante puede presentar una solicitud.
    verificar_rol_usuario(db, solicitud.ID_USUARIO_SOLICITA, ["estudiante"])

    # La actividad debe existir y estar habilitada en el catálogo.
    actividad = db.query(modelos.Actividad).filter(
        modelos.Actividad.ID_ACTIVIDAD == solicitud.ID_ACTIVIDAD
    ).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada.")
    if not actividad.ACTIVO:
        raise HTTPException(status_code=400, detail="La actividad no está activa.")

    # Rechazamos fechas futuras y cargas horarias que no sean positivas.
    if solicitud.FECHA_ACTIVIDAD > date.today():
        raise HTTPException(status_code=400, detail="La fecha de actividad no puede ser futura.")
    if solicitud.CARGA_HORARIA_EN_MINUTOS <= 0:
        raise HTTPException(status_code=400, detail="La carga horaria debe ser mayor a cero.")

    # Una actividad no se puede repetir el mismo día, salvo que la anterior fuera rechazada.
    solicitud_duplicada = db.query(modelos.SolicitudCAE).join(
        modelos.DetalleSolicitudCAE
    ).filter(
        modelos.SolicitudCAE.ID_USUARIO_SOLICITA == solicitud.ID_USUARIO_SOLICITA,
        modelos.SolicitudCAE.ID_ACTIVIDAD == solicitud.ID_ACTIVIDAD,
        modelos.DetalleSolicitudCAE.FECHA_ACTIVIDAD == solicitud.FECHA_ACTIVIDAD,
        modelos.SolicitudCAE.ESTADO_SOLICITUD != "RECHAZADA",
    ).first()
    if solicitud_duplicada:
        raise HTTPException(status_code=409, detail="Ya existe una solicitud para esa actividad y fecha.")

    # Guardamos la solicitud y su detalle juntos para que no quede un registro incompleto.
    nueva_solicitud = modelos.SolicitudCAE(
        FECHA_SOLICITUD=date.today(),
        HORA_SOLICITUD=datetime.now().time(),
        ID_ACTIVIDAD=solicitud.ID_ACTIVIDAD,
        ID_USUARIO_SOLICITA=solicitud.ID_USUARIO_SOLICITA,
        ESTADO_SOLICITUD="PENDIENTE",
        OBSERVACIONES=solicitud.OBSERVACIONES
    )
    try:
        db.add(nueva_solicitud)
        db.flush()
        nuevo_detalle = modelos.DetalleSolicitudCAE(
            ID_SOLICITUD_CAE=nueva_solicitud.ID_SOLICITUD_CAE,
            FECHA_ACTIVIDAD=solicitud.FECHA_ACTIVIDAD,
            ACTIVIDAD=actividad.NOMBRE_ACTIVIDAD,
            CARGA_HORARIA_EN_MINUTOS=solicitud.CARGA_HORARIA_EN_MINUTOS,
            SUPERVISADO=solicitud.SUPERVISADO
        )
        db.add(nuevo_detalle)
        db.commit()
        db.refresh(nueva_solicitud)
    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="No se pudo guardar la solicitud y su detalle.",
        ) from error

    return preparar_solicitud_respuesta(nueva_solicitud)


@app.get("/solicitudes/", response_model=List[esquemas.SolicitudRespuesta])
def listar_solicitudes(
    id_usuario: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
):
    # Aplicamos solo los filtros que la persona haya enviado.
    consulta = db.query(modelos.SolicitudCAE)
    if id_usuario is not None:
        consulta = consulta.filter(modelos.SolicitudCAE.ID_USUARIO_SOLICITA == id_usuario)
    if estado is not None:
        consulta = consulta.filter(modelos.SolicitudCAE.ESTADO_SOLICITUD == estado)
    return [preparar_solicitud_respuesta(solicitud) for solicitud in consulta.all()]


@app.get("/solicitudes/{id_solicitud}", response_model=esquemas.SolicitudRespuesta)
def obtener_solicitud(id_solicitud: int, db: Session = Depends(get_db)):
    # Devolvemos la solicitud junto con sus detalles o indicamos que no existe.
    solicitud = db.query(modelos.SolicitudCAE).filter(
        modelos.SolicitudCAE.ID_SOLICITUD_CAE == id_solicitud
    ).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    return preparar_solicitud_respuesta(solicitud)


@app.put("/solicitudes/{id_solicitud}/revision", response_model=esquemas.SolicitudRespuesta)
def iniciar_revision(
    id_solicitud: int,
    id_usuario: int,
    db: Session = Depends(get_db),
):
    # La revisión está reservada para los dos roles de dirección.
    verificar_rol_usuario(db, id_usuario, ["direccion_academica", "direccion_carrera"])

    # Solo se puede iniciar la revisión de una solicitud pendiente.
    solicitud = db.query(modelos.SolicitudCAE).filter(
        modelos.SolicitudCAE.ID_SOLICITUD_CAE == id_solicitud
    ).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    if solicitud.ESTADO_SOLICITUD != "PENDIENTE":
        raise HTTPException(status_code=409, detail="La solicitud no está pendiente.")
    solicitud.ESTADO_SOLICITUD = "EN_REVISION"
    db.commit()
    db.refresh(solicitud)
    return preparar_solicitud_respuesta(solicitud)


@app.put("/solicitudes/{id_solicitud}/resolucion", response_model=esquemas.SolicitudRespuesta)
def resolver_solicitud(
    id_solicitud: int,
    datos: esquemas.SolicitudResolucion,
    id_usuario: int,
    db: Session = Depends(get_db),
):
    # Solo las direcciones pueden aprobar o rechazar.
    verificar_rol_usuario(db, id_usuario, ["direccion_academica", "direccion_carrera"])

    # Limitamos la resolución a los estados admitidos y exigimos motivo al rechazar.
    if datos.ESTADO_SOLICITUD not in ["APROBADA", "RECHAZADA"]:
        raise HTTPException(status_code=400, detail="El estado debe ser APROBADA o RECHAZADA.")
    if datos.ESTADO_SOLICITUD == "RECHAZADA" and not (
        datos.OBSERVACIONES and datos.OBSERVACIONES.strip()
    ):
        raise HTTPException(status_code=400, detail="Las observaciones son obligatorias al rechazar.")

    # Una solicitud ya resuelta no se puede volver a resolver.
    solicitud = db.query(modelos.SolicitudCAE).filter(
        modelos.SolicitudCAE.ID_SOLICITUD_CAE == id_solicitud
    ).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    if solicitud.ESTADO_SOLICITUD not in ["PENDIENTE", "EN_REVISION"]:
        raise HTTPException(status_code=409, detail="La solicitud ya fue resuelta.")
    solicitud.ESTADO_SOLICITUD = datos.ESTADO_SOLICITUD
    solicitud.OBSERVACIONES = datos.OBSERVACIONES
    solicitud.FECHA_APROBACION_O_RECHAZO = date.today()
    solicitud.ID_USUARIO_APRUEBA_O_RECHAZA = id_usuario
    db.commit()
    db.refresh(solicitud)
    return preparar_solicitud_respuesta(solicitud)


@app.get("/progreso/{id_usuario}", response_model=esquemas.ProgresoRespuesta)
def obtener_progreso(id_usuario: int, db: Session = Depends(get_db)):
    # El progreso corresponde a una cuenta estudiante existente.
    usuario = db.query(modelos.Usuario).filter(
        modelos.Usuario.ID_USUARIO == id_usuario
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario.ROLE_ACCESO != "estudiante":
        raise HTTPException(status_code=403, detail="El progreso solo está disponible para estudiantes.")

    # Sumamos los minutos de cada solicitud aprobada y calculamos sus créditos.
    solicitudes_aprobadas = db.query(modelos.SolicitudCAE).filter(
        modelos.SolicitudCAE.ID_USUARIO_SOLICITA == id_usuario,
        modelos.SolicitudCAE.ESTADO_SOLICITUD == "APROBADA",
    ).all()
    creditos_por_id = {id_actividad: 0.0 for id_actividad in REGLAS_CAE}
    for solicitud in solicitudes_aprobadas:
        minutos = sum(
            detalle.CARGA_HORARIA_EN_MINUTOS for detalle in solicitud.detalles
        )
        if solicitud.ID_ACTIVIDAD in creditos_por_id:
            creditos_por_id[solicitud.ID_ACTIVIDAD] += calcular_creditos(
                solicitud.ID_ACTIVIDAD,
                minutos,
            )

    # Limitamos cada categoría a su máximo y armamos el detalle para la pantalla.
    creditos_por_categoria = []
    for id_actividad, regla in REGLAS_CAE.items():
        creditos_obtenidos = min(
            creditos_por_id[id_actividad],
            regla["maximo_creditos"],
        )
        creditos_por_categoria.append({
            "ID_ACTIVIDAD": id_actividad,
            "NOMBRE_ACTIVIDAD": regla["nombre"],
            "CREDITOS_OBTENIDOS": creditos_obtenidos,
            "MAXIMO_CREDITOS": regla["maximo_creditos"],
        })
    # El total general descarta decimales después de aplicar los topes.
    creditos_aprobados = int(
        sum(categoria["CREDITOS_OBTENIDOS"] for categoria in creditos_por_categoria)
    )

    # Contamos en una consulta las solicitudes de cada estado.
    cantidades = db.query(
        modelos.SolicitudCAE.ESTADO_SOLICITUD,
        func.count(modelos.SolicitudCAE.ID_SOLICITUD_CAE),
    ).filter(
        modelos.SolicitudCAE.ID_USUARIO_SOLICITA == id_usuario
    ).group_by(modelos.SolicitudCAE.ESTADO_SOLICITUD).all()
    conteo = {estado: cantidad for estado, cantidad in cantidades}

    # Calculamos cuánto falta y limitamos el porcentaje a un máximo de 100.
    meta_creditos = 20
    creditos_faltantes = max(meta_creditos - creditos_aprobados, 0)
    porcentaje = min(creditos_aprobados / meta_creditos * 100, 100)
    return {
        "ID_USUARIO": id_usuario,
        "CREDITOS_APROBADOS": creditos_aprobados,
        "META_CREDITOS": meta_creditos,
        "CREDITOS_FALTANTES": creditos_faltantes,
        "PORCENTAJE_COMPLETADO": porcentaje,
        "META_CUMPLIDA": creditos_aprobados >= meta_creditos,
        "CANTIDAD_PENDIENTE": conteo.get("PENDIENTE", 0),
        "CANTIDAD_EN_REVISION": conteo.get("EN_REVISION", 0),
        "CANTIDAD_APROBADA": conteo.get("APROBADA", 0),
        "CANTIDAD_RECHAZADA": conteo.get("RECHAZADA", 0),
        "CREDITOS_POR_CATEGORIA": creditos_por_categoria,
    }