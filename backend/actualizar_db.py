import os
import sqlite3
from datetime import date

import bcrypt


RUTA_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cae_sqlite.db")


def agregar_columna_si_falta(cursor, nombre):
    # Revisamos las columnas existentes para poder ejecutar este script varias veces.
    columnas = cursor.execute("PRAGMA table_info(ACTIVIDADES)").fetchall()
    if not any(columna[1] == nombre for columna in columnas):
        cursor.execute(f"ALTER TABLE ACTIVIDADES ADD COLUMN {nombre} INTEGER")


def cargar_actividades(cursor):
    # TODO: confirmar con el docente los créditos y las horas de cada actividad.
    valores_provisorios = [
        (1, 2, 1),
        (2, 2, 1),
        (3, 2, 1),
        (4, 2, 1),
        (5, 2, 1),
        (6, 2, 1),
        (7, 2, 1),
        (8, 2, 1),
        (9, 2, 1),
    ]
    for id_actividad, creditos, horas in valores_provisorios:
        cursor.execute(
            "UPDATE ACTIVIDADES SET CREDITOS = ?, HORAS_REQUERIDAS = ? "
            "WHERE ID_ACTIVIDAD = ?",
            (creditos, horas, id_actividad),
        )


def convertir_contrasenhas(cursor):
    # Solo convertimos contraseñas que todavía no tienen el prefijo de bcrypt.
    usuarios = cursor.execute(
        "SELECT ID_USUARIO, CONTRASENHA FROM USUARIOS"
    ).fetchall()
    for id_usuario, contrasenha in usuarios:
        if not contrasenha.startswith(("$2a$", "$2b$", "$2y$")):
            hash_contrasenha = bcrypt.hashpw(
                contrasenha.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            cursor.execute(
                "UPDATE USUARIOS SET CONTRASENHA = ? WHERE ID_USUARIO = ?",
                (hash_contrasenha, id_usuario),
            )


def crear_revisor_si_falta(cursor, cedula, rol, nombres, apellidos, email):
    # Dejamos un usuario de prueba para cada rol revisor si todavía no hay uno.
    existe = cursor.execute(
        "SELECT 1 FROM USUARIOS WHERE ROLE_ACCESO = ? LIMIT 1", (rol,)
    ).fetchone()
    if not existe:
        contrasenha = "DireccionCAE123!"
        hash_contrasenha = bcrypt.hashpw(
            contrasenha.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        cursor.execute(
            """
            INSERT INTO USUARIOS (
                NRO_CEDULA, NOMBRES, APELLIDOS, CODIGO_MATRICULA, EMAIL,
                TELEFONO_CELULAR, CONTRASENHA, ROLE_ACCESO, CARRERA,
                FECHA_ALTA, ACTIVO
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cedula,
                nombres,
                apellidos,
                "N/A",
                email,
                "000000000",
                hash_contrasenha,
                rol,
                "N/A",
                date.today().isoformat(),
                1,
            ),
        )


def main():
    # Abrimos la base de este proyecto y aplicamos todos los cambios en una transacción.
    conexion = sqlite3.connect(RUTA_DB)
    try:
        cursor = conexion.cursor()
        agregar_columna_si_falta(cursor, "CREDITOS")
        agregar_columna_si_falta(cursor, "HORAS_REQUERIDAS")
        cargar_actividades(cursor)
        convertir_contrasenhas(cursor)
        crear_revisor_si_falta(
            cursor,
            9990001,
            "direccion_academica",
            "Usuario de prueba",
            "Direccion Academica",
            "direccion.academica@prueba.local",
        )
        crear_revisor_si_falta(
            cursor,
            9990002,
            "direccion_carrera",
            "Usuario de prueba",
            "Direccion Carrera",
            "direccion.carrera@prueba.local",
        )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
