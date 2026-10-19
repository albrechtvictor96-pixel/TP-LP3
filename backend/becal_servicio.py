import pandas as pd
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "becal.csv")

def obtener_actividades_becal():
    if not os.path.exists(CSV_PATH):
        return {"error": "El archivo becal.csv no se encuentra en la carpeta backend."}

    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8", sep=";")
    except Exception:
        try:
            df = pd.read_csv(CSV_PATH, encoding="latin-1", sep=",")
        except Exception as e:
            return {"error": f"No se pudo leer el archivo CSV: {str(e)}"}

    df.columns = [col.strip() for col in df.columns]
    datos = df.head(20).fillna("").to_dict(orient="records")
    return {"total_registros": len(df), "muestra": datos}