# Pipeline de Preprocesamiento de Datos para Detección de Fraude

Este repositorio contiene una solución modular y extensible en Python para la ingesta, limpieza y preprocesamiento inicial de un dataset de transacciones financieras (`dataset_sucio_ventas.csv`), con el objetivo de prepararlo para tareas de Machine Learning, particularmente detección de fraude.

La implementación sigue estrictamente los requerimientos funcionales y técnicos solicitados, utilizando Programación Orientada a Objetos (POO), buenas prácticas de código y pruebas automatizadas.

## Estructura del Proyecto
    ├── .github/
        ├── workflows/
            └── flake8-pytest.yml     # Workflow de GitHub Actions para CI
    ├── app/
        └── preprocesador.py          # Código principal (clases y lógica)
    ├── tests
        ├── integration
            └── test_integracion.py
        ├── unit
            └── test_unitarias.py
    └── dataset_sucio_ventas.csv      # Dataset de ejemplo (sucio)
    └── README.md                     # Este archivo
    └── requirements.txt              # Dependencias del proyecto (opcional, generado si es necesario)

## Funcionalidades Implementadas

### A. Ingesta de Datos (Data Ingestion)
- **Diseño polimórfico**: Se implementa una clase base abstracta `CargadorDatos` con subclases específicas.
- Actualmente soportado: `CargadorCSV` para lectura de archivos CSV.
- Extensible: Se incluye ejemplo de `CargadorJSON` para futuros formatos.

### B. Limpieza de Metadatos (Sanitization)
- Estandarización de nombres de columnas:
  - Todo a minúsculas.
  - Eliminación de caracteres especiales (`$`, `#`, `@`, `?`, etc.).
  - Reemplazo de espacios por guiones bajos `_`.
  - Ejemplo: `Monto $$` → `monto`, `¿Es_Fraude?` → `es_fraude`.

### C. Ingeniería de Características para Datos Faltantes (Null Flagging)
- Para cada columna se crea una columna adicional de bandera:
  - `{columna}_nan = 1` si el valor es nulo, `0` en caso contrario.
- Permite al modelo aprender patrones asociados a la ausencia de información.

### D. Análisis de Calidad y Toma de Decisiones (Quality Gate)
- Generación automática de reporte de porcentaje de valores nulos por columna.
- Validación de columnas críticas:
  - `monto`
  - `es_fraude`
- Si alguna supera el umbral definido (por defecto **5%**), se lanza una excepción controlada recomendando **descartar el dataset** y solicitar nuevos datos.

## Requisitos Técnicos Cumplidos

- **Programación Orientada a Objetos**: Separación clara de responsabilidades en clases.
- **Polimorfismo**: `CargadorDatos` como base extensible.
- **Calidad de código**:
  - Cumple con PEP8.
  - Uso de type hints.
  - Docstrings en todas las clases y métodos.
- **Testing**:
  - Pruebas unitarias (limpieza de columnas, banderas de nulos).
  - Pruebas de integración (flujo completo del pipeline).
  - Uso de `pytest` y fixtures.
- **Integración Continua (CI)**:
  - Workflow de GitHub Actions que ejecuta:
    - Instalación de dependencias.
    - Linter con `flake8`.
    - Ejecución completa de pruebas.

## Cómo Ejecutar el Programa

### 1. Clonar el repositorio

    bash

    git clone https://github.com/jsalgadop2019/evaluar_dataset.git

    cd evaluar_dataset

### 2. Instalar dependencias

    bash

    pip install pandas numpy pytest flake8

### 3. Ejecutar el pipeline principal

    bash

    python app/preprocesador.py

Esto realizará:

- Lectura del archivo `dataset_sucio_ventas.csv`.

- Limpieza de columnas.

- Adición de banderas de nulos.

- Análisis de calidad con reporte en consola.

- Si el dataset pasa el quality gate, retorna el DataFrame procesado.

### 4. Ejecutar pruebas

    bash

    pytest tests/integration/ -v
    pytest tests/unit/ -v

### 5. Verificar CI (GitHub Actions)

Al hacer `push` o `pull` request a la rama `main`, GitHub Actions ejecutará automáticamente:

- Linter (`flake8`)

- Todas las pruebas

## Configuración del Umbral de Nulos

Puedes modificar el umbral de calidad al instanciar el preprocesador:

    python

    preprocesador = PreprocesadorDatos(df, umbral_nulos=0.10)  # 10% en lugar de 5%

## Extensibilidad

- Para agregar soporte a nuevos formatos (JSON, Parquet, Excel), solo crea una nueva clase que herede de `CargadorDatos` y sobrescriba `leer_archivo()`.

- El resto del pipeline funciona independientemente del origen de los datos.
