# Importaciones necesarias
import pandas as pd
import numpy as np
import re
from typing import Optional, Union
import os

class CargadorDatos:
    """
    Clase base para cargar datos de diferentes formatos.
    Proporciona un método abstracto para leer archivos.
    """

    def __init__(self, ruta_archivo: str):
        """
        Inicializa el cargador con la ruta del archivo.

        :param ruta_archivo: Ruta al archivo a cargar.
        """
        self.ruta_archivo = ruta_archivo
        self.datos: Optional[pd.DataFrame] = None

    def leer_archivo(self) -> pd.DataFrame:
        """
        Método para leer el archivo. Debe ser implementado por subclases.

        :return: DataFrame con los datos cargados.
        :raises NotImplementedError: Si no se implementa en subclase.
        """
        raise NotImplementedError("Este método debe ser implementado en una subclase.")

class CargadorCSV(CargadorDatos):
    """
    Clase para cargar datos desde archivos CSV.
    Hereda de CargadorDatos y sobreescribe el método leer_archivo.
    """

    def leer_archivo(self) -> pd.DataFrame:
        """
        Lee el archivo CSV y lo carga en un DataFrame.

        :return: DataFrame con los datos del CSV.
        :raises ValueError: Si el archivo no existe o no es CSV.
        """
        if not os.path.exists(self.ruta_archivo):
            raise ValueError(f"El archivo {self.ruta_archivo} no existe.")
        if not self.ruta_archivo.lower().endswith('.csv'):
            raise ValueError("El archivo debe ser de tipo CSV.")
        
        # Cargar el CSV, manejando posibles errores
        try:
            self.datos = pd.read_csv(self.ruta_archivo, na_values=['', 'NaN', 'null'])
        except Exception as e:
            raise ValueError(f"Error al leer el CSV: {e}")
        
        return self.datos

# Ejemplo de subclase para JSON (para polimorfismo futuro)
class CargadorJSON(CargadorDatos):
    """
    Clase para cargar datos desde archivos JSON.
    Hereda de CargadorDatos y sobreescribe el método leer_archivo.
    """

    def leer_archivo(self) -> pd.DataFrame:
        """
        Lee el archivo JSON y lo carga en un DataFrame.

        :return: DataFrame con los datos del JSON.
        :raises ValueError: Si el archivo no existe o no es JSON.
        """
        if not os.path.exists(self.ruta_archivo):
            raise ValueError(f"El archivo {self.ruta_archivo} no existe.")
        if not self.ruta_archivo.lower().endswith('.json'):
            raise ValueError("El archivo debe ser de tipo JSON.")
        
        # Cargar el JSON
        try:
            self.datos = pd.read_json(self.ruta_archivo)
        except Exception as e:
            raise ValueError(f"Error al leer el JSON: {e}")
        
        return self.datos

class PreprocesadorDatos:
    """
    Clase responsable del preprocesamiento de datos.
    Incluye limpieza de columnas, adición de banderas de nulos y análisis de calidad.
    """

    def __init__(self, df: pd.DataFrame, umbral_nulos: float = 0.05):
        """
        Inicializa el preprocesador con el DataFrame y umbral de nulos.

        :param df: DataFrame a procesar.
        :param umbral_nulos: Umbral de porcentaje de nulos para alerta.
        """
        self.df = df.copy()
        self.umbral_nulos = umbral_nulos
        self.columnas_originales = list(self.df.columns)

    def limpiar_columnas(self) -> pd.DataFrame:
        """
        Estandariza los nombres de las columnas: minúsculas, sin caracteres especiales, espacios por _.

        :return: DataFrame con columnas limpias.
        """
        def limpiar_nombre(col: str) -> str:
            # Convertir a minúsculas
            col = col.lower()
            # Eliminar caracteres especiales
            col = re.sub(r'[^a-z0-9_ ]', '', col)
            # Reemplazar espacios por _
            col = col.replace(' ', '_')
            # Eliminar _ duplicados
            col = re.sub(r'_+', '_', col)
            # Quitar _ al inicio o final
            col = col.strip('_')
            return col

        self.df.columns = [limpiar_nombre(col) for col in self.df.columns]
        return self.df

    def agregar_banderas_nulos(self) -> pd.DataFrame:
        """
        Agrega columnas de bandera para nulos en cada columna original.

        :return: DataFrame con banderas agregadas.
        """
        for col in self.columnas_originales:
            col_limpia = self.df.columns[self.columnas_originales.index(col)]
            bandera_col = f"{col_limpia}_nan"
            self.df[bandera_col] = np.where(self.df[col_limpia].isnull(), 1, 0)
            #self.df[col + '_nan'] = self.df[col].isnull().astype(int)

        return self.df

    def analizar_calidad(self) -> dict:
        """
        Genera reporte de porcentaje de nulos y verifica umbrales para columnas críticas.

        :return: Diccionario con porcentajes de nulos por columna.
        :raises ValueError: Si columnas críticas superan umbral.
        """
        porcentajes_nulos = self.df.filter(like='_nan').mean() * 100

        # reporte = {col: round(pct, 2) for col, pct in porcentajes_nulos.items()}

        print('\n')

        # Imprimir reporte
        print("\033[4m" + "Reporte de porcentaje de nulos por columna:" + "\033[0m")
        for col, pct in porcentajes_nulos.items():
            print(f"{col:<30}: {pct:.2f}%")

        print('\n')

        # Verificar columnas críticas
        errores = 0 # Contador de errores
        for col, pct in porcentajes_nulos.items():
            if pct / 100 > self.umbral_nulos:
                # raise ValueError(
                    errores += 1
                    print(f"La columna crítica '{col}' supera el umbral de nulos ({self.umbral_nulos * 100:.2f}%) con un error del {pct:.2f}%. " + 
                        "Se recomienda descartar el dataset y recolectar nuevos datos para esta columna.")
                # )

        if errores == 0:
            print(f"Todas las columnas críticas están dentro del umbral de nulos permitido ({self.umbral_nulos * 100:.2f}%). " +
                "Se recomienda continuar con el análisis del dataset actual.")

        print('\n')

        return porcentajes_nulos

    def procesar(self) -> pd.DataFrame:
        """
        Ejecuta el pipeline completo: limpieza, banderas, análisis.

        :return: DataFrame procesado.
        """
        self.limpiar_columnas()
        self.agregar_banderas_nulos()
        self.analizar_calidad()

        return self.df


# Ejemplo de uso (para ejecución directa)
if __name__ == "__main__":
    # Cargar datos
    cargador = CargadorCSV("dataset_sucio_ventas.csv")
    df = cargador.leer_archivo()

    # Preprocesar
    preprocesador = PreprocesadorDatos(df, umbral_nulos=0.06)
    df_procesado = preprocesador.procesar()

    # Mostrar resultado (opcional)
    # print(df_procesado.head(100))
