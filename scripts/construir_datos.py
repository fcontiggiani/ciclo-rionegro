"""Construye las series del visor de ciclos de Río Negro.

Lee los archivos crudos de ``data/raw/`` y genera ``data/series.json``. Con
``--incrustar`` también reemplaza el bloque de datos dentro de ``index.html``.
El procedimiento es el siguiente:

* desacumula la recaudación de Ingresos Brutos y el gasto total de la
  Administración Pública No Financiera, que la DNAP publica acumulados en el año;
* empalma el IPIM nacional del INDEC: base 1993 hasta octubre de 2015 y base
  diciembre de 2015 = 100 desde entonces, cubriendo noviembre y diciembre de 2015
  con las variaciones del IPC de la Ciudad de Buenos Aires;
* deflacta IIBB, remuneraciones y gasto con el IPIM, en pesos constantes del
  promedio de 2025;
* desestacionaliza IIBB, remuneraciones y gasto con STL robusto sobre el
  logaritmo (el empleo ya viene desestacionalizado por la fuente);
* recorta las cuatro series a la ventana común.

Uso::

    python scripts/construir_datos.py              # solo genera data/series.json
    python scripts/construir_datos.py --incrustar  # además actualiza index.html
"""

from __future__ import annotations  # Permite anotaciones de tipo modernas en Python 3.10

import argparse  # Lee los argumentos de la línea de comandos
import json  # Escribe el archivo JSON con las series
import re  # Localiza el bloque de datos dentro de index.html
from datetime import date  # Registra la fecha de generación
from pathlib import Path  # Maneja rutas de archivos de forma portable

import numpy as np  # Cálculo numérico (logaritmos y exponenciales)
import pandas as pd  # Manipulación de series de tiempo
from statsmodels.tsa.seasonal import STL  # Descomposición estacional STL (Cleveland et al., 1990)

RAIZ = Path(__file__).resolve().parents[1]  # Carpeta raíz del repositorio
RAW = RAIZ / "data" / "raw"  # Carpeta con los archivos crudos
SALIDA = RAIZ / "data" / "series.json"  # Archivo JSON resultante
PAGINA = RAIZ / "index.html"  # Página autocontenida que lleva los datos incrustados
ANIO_BASE = 2025  # Año cuyos precios promedio sirven de base para los valores constantes
INICIO = pd.Timestamp("2011-01-01")  # Primer mes de la ventana común (el gasto trimestral empieza en 2011 T1)


# ---------------------------------------------------------------------------
# Lectura y transformaciones básicas
# ---------------------------------------------------------------------------
def leer_mensual(archivo: str, columna: str) -> pd.Series:
    """Lee una columna mensual de un CSV con índice ``indice_tiempo`` en formato AAAA-MM."""
    df = pd.read_csv(RAW / archivo)  # Carga el archivo completo
    indice = pd.PeriodIndex(df["indice_tiempo"], freq="M")  # Convierte las fechas en períodos mensuales
    return pd.Series(df[columna].to_numpy(dtype=float), index=indice, name=columna)  # Devuelve la serie numérica


def desacumular(archivo: str) -> pd.Series:
    """Convierte montos acumulados en el año (I, I+II, ...) en montos de cada trimestre, en millones."""
    df = pd.read_csv(RAW / archivo)  # Carga los acumulados publicados por la DNAP
    factor = df["unidad"].map({"miles": 1e-3, "millones": 1.0})  # Factor para expresar todo en millones de pesos
    assert factor.notna().all(), "unidad desconocida en " + archivo  # Verifica que todas las unidades sean reconocidas
    df["acum_mill"] = df["acumulado"] * factor  # Acumulado en millones de pesos corrientes
    df = df.sort_values(["anio", "trimestre"])  # Ordena cronológicamente
    df["previo"] = df.groupby("anio")["acum_mill"].shift(1).fillna(0.0)  # Acumulado del trimestre anterior del mismo año
    df["monto"] = df["acum_mill"] - df["previo"]  # Monto del trimestre = diferencia de acumulados
    assert (df["monto"] > 0).all(), "monto trimestral no positivo en " + archivo  # Un monto negativo delataría un error de unidades
    indice = pd.PeriodIndex.from_fields(year=df["anio"], quarter=df["trimestre"], freq="Q")  # Índice trimestral
    serie = pd.Series(df["monto"].to_numpy(), index=indice)  # Serie trimestral en millones corrientes
    assert serie.index.is_unique and len(serie) == (serie.index[-1] - serie.index[0]).n + 1, "faltan trimestres"  # Sin huecos
    return serie  # Devuelve la serie desacumulada


def ipim_empalmado() -> tuple[pd.Series, dict]:
    """Empalma el IPIM base 1993 con el IPIM dic-2015 = 100 y devuelve el índice mensual y los factores usados."""
    viejo = leer_mensual("api_mensual.csv", "ipim_1993").dropna()  # IPIM base 1993 (hasta 2015-10)
    nuevo = leer_mensual("api_mensual.csv", "ipim_dic2015").dropna()  # IPIM dic-2015 = 100 (desde 2015-12)
    caba = leer_mensual("api_mensual.csv", "ipc_caba_jul2012").dropna()  # IPC CABA, usado solo como puente
    oct15, nov15, dic15 = (pd.Period(p, "M") for p in ("2015-10", "2015-11", "2015-12"))  # Meses del puente
    var_nov = caba[nov15] / caba[oct15]  # Variación de noviembre 2015 tomada del IPC CABA
    var_dic = caba[dic15] / caba[nov15]  # Variación de diciembre 2015 tomada del IPC CABA
    nivel_dic_viejo = viejo[oct15] * var_nov * var_dic  # Nivel de diciembre 2015 expresado en base 1993
    enlace = nivel_dic_viejo / nuevo[dic15]  # Coeficiente que lleva la base dic-2015 a la base 1993
    puente = pd.Series({nov15: viejo[oct15] * var_nov}, dtype=float)  # Noviembre 2015 estimado
    largo = pd.concat([viejo, puente, nuevo * enlace]).sort_index()  # Serie continua en base 1993
    assert largo.index.is_unique and (largo.index.to_series().diff().dropna() == 1 * largo.index.freq).all(), "IPIM con huecos"  # Continuidad
    base = largo[largo.index.year == ANIO_BASE].mean()  # Promedio del año base
    info = {"var_nov_2015": round(var_nov - 1, 5), "var_dic_2015": round(var_dic - 1, 5)}  # Supuestos del puente, para documentar
    return largo / base, info  # Índice con promedio del año base = 1


def desestacionalizar(serie: pd.Series, periodo: int) -> pd.Series:
    """Quita la estacionalidad con STL robusto sobre el logaritmo y devuelve la serie en niveles."""
    log = np.log(serie.astype(float))  # Trabaja en logaritmos: la estacionalidad se vuelve aditiva
    ajuste = STL(log.to_numpy(), period=periodo, seasonal=periodo * 2 + 1, robust=True).fit()  # Descomposición robusta
    return pd.Series(np.exp(log.to_numpy() - ajuste.seasonal), index=serie.index)  # Nivel sin componente estacional


def a_lista(serie: pd.Series, decimales: int) -> dict:
    """Convierte una serie en listas de fechas (AAAA-MM, primer mes del período) y valores redondeados."""
    meses = serie.index.asfreq("M", how="start") if serie.index.freqstr.startswith("Q") else serie.index  # Primer mes del trimestre
    return {  # Estructura que lee la página
        "fechas": [p.strftime("%Y-%m") for p in meses],  # Fechas como texto año-mes
        "valores": [round(float(v), decimales) for v in serie.to_numpy()],  # Valores redondeados
    }


# ---------------------------------------------------------------------------
# Construcción del JSON
# ---------------------------------------------------------------------------
def construir_json() -> dict:
    """Arma el diccionario con las cuatro series, sus metadatos y los supuestos del deflactor."""
    deflactor_m, puente = ipim_empalmado()  # IPIM mensual con promedio del año base = 1
    deflactor_t = deflactor_m.groupby(deflactor_m.index.asfreq("Q")).mean()  # Promedio trimestral del IPIM

    empleo = leer_mensual("api_mensual.csv", "asalariados_desest").dropna()  # Asalariados privados registrados (s.e.)
    salario_nom = leer_mensual("salario_rn_mensual.csv", "remuneracion_promedio")  # Remuneración promedio corriente
    iibb_nom = desacumular("iibb_rn_trim_acumulado.csv")  # IIBB trimestral, millones corrientes
    gasto_nom = desacumular("gasto_rn_trim_acumulado.csv")  # Gasto total APNF trimestral, millones corrientes

    salario = desestacionalizar(salario_nom / deflactor_m.reindex(salario_nom.index), 12)  # Real y desestacionalizada
    iibb = desestacionalizar(iibb_nom / deflactor_t.reindex(iibb_nom.index), 4)  # Real y desestacionalizada
    gasto = desestacionalizar(gasto_nom / deflactor_t.reindex(gasto_nom.index), 4)  # Real y desestacionalizada
    for nombre, s in {"salario": salario, "iibb": iibb, "gasto": gasto}.items():  # Controla que el deflactor cubra todo
        assert s.notna().all(), f"faltan valores del deflactor para {nombre}"  # Un NaN indicaría meses sin IPIM

    fin_m = min(empleo.index[-1], salario.index[-1], iibb.index[-1].asfreq("M", how="end"), gasto.index[-1].asfreq("M", how="end"))  # Último mes común
    ini_m = pd.Period(INICIO, "M")  # Primer mes común
    recorte_m = lambda s: s[(s.index >= ini_m) & (s.index <= fin_m)]  # Ventana común para series mensuales
    recorte_t = lambda s: s[(s.index >= ini_m.asfreq("Q")) & (s.index <= fin_m.asfreq("Q"))]  # Ventana común trimestral
    empleo, salario = recorte_m(empleo), recorte_m(salario)  # Recorta las series mensuales
    iibb, gasto = recorte_t(iibb), recorte_t(gasto)  # Recorta las series trimestrales

    base = f"$ de {ANIO_BASE}"  # Texto de la unidad en pesos constantes
    nota_def = (f"Deflactada con el IPIM nacional (INDEC), promedio {ANIO_BASE} = 1; noviembre y diciembre de 2015 "  # Nota común
                f"se cubren con el IPC CABA ({puente['var_nov_2015']:+.2%} y {puente['var_dic_2015']:+.2%}). "
                "Desestacionalizada con STL robusto sobre el logaritmo.")
    return {  # Estructura final del archivo series.json
        "actualizado": date.today().isoformat(),  # Fecha de generación
        "ventana": [ini_m.strftime("%Y-%m"), fin_m.strftime("%Y-%m")],  # Ventana común de las cuatro series
        "deflactor": {"serie": "IPIM nivel general (INDEC)", "base": f"promedio {ANIO_BASE} = 1", **puente},  # Supuestos
        "series": {  # Bloque de series
            "emp": {  # Empleo privado registrado
                "nombre": "Empleo privado registrado",  # Nombre corto
                "descripcion": "Asalariados registrados del sector privado, Río Negro, desestacionalizado",  # Descripción
                "rol": "Referencia",  # Papel en el análisis
                "frecuencia": "M",  # Frecuencia mensual
                "unidad": "miles de asalariados",  # Unidad de medida
                "fuente": "SIPA (OEDE), vía API Series de Tiempo (154.2_RNEGROGRO_S_0_0_9)",  # Fuente
                "nota": "Serie desestacionalizada por la fuente. Indicador coincidente de la actividad provincial.",  # Nota
                **a_lista(empleo, 3),  # Fechas y valores
            },
            "iibb": {  # Recaudación de Ingresos Brutos
                "nombre": "Recaudación de IIBB",  # Nombre corto
                "descripcion": "Impuesto sobre los Ingresos Brutos, Río Negro, real y desestacionalizada",  # Descripción
                "rol": "Recaudación",  # Papel en el análisis
                "frecuencia": "T",  # Frecuencia trimestral
                "unidad": f"millones de {base} por trimestre",  # Unidad de medida
                "fuente": "DNAP, Recursos tributarios de origen provincial (información de la ARTRN)",  # Fuente
                "nota": "Montos trimestrales obtenidos al desacumular los acumulados anuales publicados. " + nota_def,  # Nota
                **a_lista(iibb, 1),  # Fechas y valores
            },
            "sal": {  # Remuneración promedio
                "nombre": "Remuneración promedio",  # Nombre corto
                "descripcion": "Remuneración promedio de los asalariados registrados del sector privado, Río Negro, real y desestacionalizada",  # Descripción
                "rol": "Salarios",  # Papel en el análisis
                "frecuencia": "M",  # Frecuencia mensual
                "unidad": f"{base} por mes",  # Unidad de medida
                "fuente": "SIPA (OEDE), Remuneraciones por provincia (serie mensual)",  # Fuente
                "nota": "Remuneración por todo concepto (incluye SAC). " + nota_def,  # Nota
                **a_lista(salario, 0),  # Fechas y valores
            },
            "gasto": {  # Gasto público provincial
                "nombre": "Gasto público provincial",  # Nombre corto
                "descripcion": "Gasto total devengado de la Administración Pública No Financiera, Río Negro, real y desestacionalizado",  # Descripción
                "rol": "Gasto",  # Papel en el análisis
                "frecuencia": "T",  # Frecuencia trimestral
                "unidad": f"millones de {base} por trimestre",  # Unidad de medida
                "fuente": "DNAP, Ejecuciones presupuestarias provinciales (APNF)",  # Fuente
                "nota": "Ejecución provisoria; montos trimestrales obtenidos al desacumular los acumulados anuales. " + nota_def,  # Nota
                **a_lista(gasto, 1),  # Fechas y valores
            },
        },
    }


def incrustar_en_pagina(texto_json: str) -> None:
    """Reemplaza el bloque <script id="datos-series"> de index.html por los datos nuevos."""
    html = PAGINA.read_text(encoding="utf-8")  # Lee la página completa
    patron = re.compile(r'(<script type="application/json" id="datos-series">)(.*?)(</script>)', re.S)  # Bloque de datos
    if not patron.search(html):  # Verifica que el bloque exista antes de reemplazar
        raise RuntimeError("index.html no contiene el bloque de datos 'datos-series'")  # Aborta sin tocar el archivo
    seguro = texto_json.replace("</", "<\\/")  # Escapa "</" para que el JSON no cierre la etiqueta <script>
    html = patron.sub(lambda m: m.group(1) + seguro + m.group(3), html, count=1)  # Sustituye solo el contenido
    PAGINA.write_text(html, encoding="utf-8")  # Guarda la página actualizada


def main() -> None:
    """Genera el JSON y, si se pide, lo incrusta en la página."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])  # Define la interfaz de comandos
    parser.add_argument("--incrustar", action="store_true", help="actualizar también index.html")  # Opción de incrustación
    args = parser.parse_args()  # Lee los argumentos recibidos
    datos = construir_json()  # Arma el contenido del JSON
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))  # Serializa en JSON compacto
    SALIDA.write_text(texto, encoding="utf-8")  # Escribe data/series.json
    if args.incrustar:  # Si se pidió actualizar la página
        incrustar_en_pagina(texto)  # Copia los mismos datos dentro de index.html
    print(f"Ventana común: {datos['ventana'][0]} a {datos['ventana'][1]}")  # Informa la ventana resultante
    for clave, s in datos["series"].items():  # Recorre las series exportadas
        print(f"{clave}: {s['fechas'][0]} a {s['fechas'][-1]} ({len(s['fechas'])} obs.)")  # Resume cada serie


if __name__ == "__main__":  # Ejecuta solo si el archivo se llama directamente
    main()  # Llama al programa principal
