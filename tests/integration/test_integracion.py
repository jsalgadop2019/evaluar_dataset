# Pruebas integrales usando pytest

import pytest
import pandas as pd
import numpy as np
from app.preprocesador import PreprocesadorDatos, CargadorDatos, CargadorCSV

# Pruebas de integración

@pytest.fixture
def df_mock_sucio():
    """
    Fixture para DataFrame mock sucio.
    """
    data = {
        "Transaction ID #": [1, 2, np.nan],
        "Monto $$": [100.0, np.nan, 300.0],
        "¿Es_Fraude?": [0, 1, np.nan]
    }
    return pd.DataFrame(data)

def test_pipeline_completo_bajo_umbral(df_mock_sucio):
    """
    Prueba de integración: Pipeline completo con nulos bajo umbral.
    """
    preproc = PreprocesadorDatos(df_mock_sucio, umbral_nulos=0.4)  # 40% para no fallar
    df_procesado = preproc.procesar()
    assert "transaction_id_nan" in df_procesado.columns
    assert "monto_nan" in df_procesado.columns
    assert "es_fraude_nan" in df_procesado.columns

def test_pipeline_completo_alto_umbral(df_mock_sucio):
    """
    Prueba de integración: Pipeline completo con nulos alto umbral (debe fallar).
    """
    preproc = PreprocesadorDatos(df_mock_sucio, umbral_nulos=0.1)  # 10% para fallar en es_fraude
    preproc.limpiar_columnas()
    preproc.agregar_banderas_nulos()
    with pytest.raises(ValueError):
        preproc.analizar_calidad()

def test_integracion_con_cargador():
    """
    Prueba de integración con CargadorDatos (usa archivo real o mock).
    """
    # Para esta prueba, asumimos el archivo existe; de lo contrario, mockear
    cargador = CargadorCSV("dataset_sucio_ventas.csv")
    df = cargador.leer_archivo()
    preproc = PreprocesadorDatos(df, umbral_nulos=0.05)
    df_procesado = preproc.procesar()
    assert isinstance(df_procesado, pd.DataFrame)