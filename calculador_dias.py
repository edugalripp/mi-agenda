import json
import re
from datetime import date, datetime, timedelta

def extraer_fecha_de_issue(cuerpo_issue: str) -> str | None:
    """Extrae la fecha AAAA-MM-DD generada por la plantilla YAML."""
    patron = r"### Fecha (?:límite|planeada \(Opcional\))\s+(\d{4}-\d{2}-\d{2})"
    coincidencia = re.search(patron, cuerpo_issue)
    return coincidencia.group(1) if coincidencia else None

def calcular_dias(fecha_objetivo_str: str, ruta_festivos: str = "docs/festivos.json") -> dict:
    """Calcula días totales, lectivos y festivos (incluyendo findes) hasta la fecha."""
    with open(ruta_festivos, "r", encoding="utf-8") as f:
        datos = json.load(f)
        festivos_lista = set(datos.get("festivos_2026_2027", []))

    hoy = date.today()
    fecha_objetivo = datetime.strptime(fecha_objetivo_str, "%Y-%m-%d").date()

    dias_totales = (fecha_objetivo - hoy).days

    # Si la fecha ya pasó o es hoy
    if dias_totales <= 0:
        return {"totales": dias_totales, "lectivos": 0, "festivos": 0}

    dias_festivos = 0
    dias_lectivos = 0

    # Recorremos desde mañana (día 1) hasta el día de la entrega incluido
    for i in range(1, dias_totales + 1):
        dia_actual = hoy + timedelta(days=i)
        dia_str = dia_actual.strftime("%Y-%m-%d")

        # weekday(): 0 es Lunes ... 5 es Sábado, 6 es Domingo
        es_finde = dia_actual.weekday() in (5, 6)
        es_festivo = dia_str in festivos_lista

        if es_finde or es_festivo:
            dias_festivos += 1
        else:
            dias_lectivos += 1

    return {
        "totales": dias_totales,
        "lectivos": dias_lectivos,
        "festivos": dias_festivos
    }

# --- Ejemplo de prueba rápida ---
if __name__ == "__main__":
    simulacion_issue = """
    ### Tipo de evento
    Proyecto / TFG
    
    ### Asignatura o Proyecto
    Defensa TFG
    
    ### Fecha límite
    2026-12-15
    """
    fecha = extraer_fecha_de_issue(simulacion_issue)
    if fecha:
        resultado = calcular_dias(fecha)
        print(f"Fecha: {fecha} -> Totales: {resultado['totales']} | "
              f"Lectivos: {resultado['lectivos']} | Festivos/Findes: {resultado['festivos']}")
