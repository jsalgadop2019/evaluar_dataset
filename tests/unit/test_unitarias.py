# Pruebas unitarias usando pytest

import pytest
import pandas as pd
import numpy as np
from app.preprocesador import PreprocesadorDatos, CargadorDatos, CargadorCSV

# Pruebas unitarias

def test_limpiar_columnas():
    """
    Prueba unitaria para la limpieza de nombres de columnas.
    """
    df_mock = pd.DataFrame(columns=["Monto $$", "Nombre Cliente (RAW)", "¿Es_Fraude?"])
    preproc = PreprocesadorDatos(df_mock)
    df_limpio = preproc.limpiar_columnas()
    columnas_esperadas = ["monto", "nombre_cliente_raw", "es_fraude"]
    assert list(df_limpio.columns) == columnas_esperadas

def test_agregar_banderas_nulos():
    """
    Prueba unitaria para adición de banderas de nulos.
    """
    df_mock = pd.DataFrame({"col1": [1, np.nan, 3], "col2": [np.nan, "b", "c"]})
    preproc = PreprocesadorDatos(df_mock)
    preproc.columnas_originales = ["col1", "col2"]
    df_con_banderas = preproc.agregar_banderas_nulos()
    assert "col1_nan" in df_con_banderas.columns
    assert "col2_nan" in df_con_banderas.columns
    assert list(df_con_banderas["col1_nan"]) == [0, 1, 0]
    assert list(df_con_banderas["col2_nan"]) == [1, 0, 0]