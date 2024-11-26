from venv import logger
from diccionarios import *
from load_data import *
import pandas as pd
import numpy as np
import datetime

# funciones.py

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                    # DATE AND TIME COLUMNS TRANSFORMATIONS                                            
# --------------------------------------------------------------------------------------------------------------------------------------

def convertir_a_fraccion_de_hora(tiempo):
    if isinstance(tiempo, str):
        parts = tiempo.split(':')
        if len(parts) == 2:
            horas, minutos = map(int, parts)
            fraccion_de_hora_decimal = horas + (minutos / 60)
            return fraccion_de_hora_decimal
        else:
            raise ValueError("Time format is incorrect. Expected format 'hh:mm', got: {}".format(tiempo))
    elif isinstance(tiempo, float):
        return tiempo
    else:
        raise ValueError("Unsupported data type")

def clean_time(time_str):
    if pd.isnull(time_str):
        return None
    if isinstance(time_str, pd._libs.tslibs.timestamps.Timestamp):
        return time_str.time()
    if isinstance(time_str, datetime.time):
        return time_str
    formatted_time = None
    try:
        clean_time_str = time_str.strip()
        time_parts = clean_time_str.split(':')
        formatted_time = ':'.join(time_parts[:2]) if len(time_parts) == 3 else clean_time_str
        datetime_obj = pd.to_datetime(formatted_time, format='%H:%M', errors='coerce')
        if pd.isnull(datetime_obj):
            print(f"Conversion resulted in NaT for cleaned time '{formatted_time}'")
            return None
        result_time = datetime_obj.time()
        print(f"Returning datetime.time object: {result_time}")
        return result_time
    except Exception as e:
        print(f"Failed to convert '{time_str}' (cleaned to '{formatted_time}'): {e}")
        return None

def transformar_horas(serie_duracion: pd.Series):
    secciones_de_tiempo = []

    for duracion in serie_duracion:
        sections = [
            60 * x if x * 60 <= duracion else duracion for x in range(1, int(np.ceil(duracion/60) + 1))
            ]
        secciones_de_tiempo.append(duracion)

    return secciones_de_tiempo

def asignar_turno(hora, tipo_pozo):
    if tipo_pozo == 'MARINO':
        if hora.time() >= pd.to_datetime('12:00:00').time() or hora.time() < pd.to_datetime('00:00:00').time():
            return 'DIURNO'
        else:
            return 'NOCTURNO'
    elif tipo_pozo == 'TERRESTRE':
        if hora.time() >= pd.to_datetime('08:00:00').time() and hora.time() < pd.to_datetime('20:00:00').time():
            return 'DIURNO'
        else:
            return 'NOCTURNO'
    else:
        return 'Tipo de pozo no válido'
# --------------------------------------------------------------------------------------------------------------------------------------
#                                                    # STRING COLUMNS TRANSFORMAITONS / CALCULATIONS
# --------------------------------------------------------------------------------------------------------------------------------------
def capitalize_and_strip(x):
    if pd.isna(x):
        return x
    else:
        return str(x).capitalize().strip()

def clean_notas_column(df, column_name):
    valid_values = ['TP', 'TNP', 'TP-TNPI', 'TNP-TNPI']
    df[column_name] = df[column_name].apply(lambda x: x if x in valid_values else pd.NA)
    return df

def clean_tagujero_column(df, column_name):
    valid_values = ['Entubado', 'Descubierto']
    df[column_name] = df[column_name].apply(lambda x: x if x in valid_values else pd.NA)
    return df

def clean_actividad_column(df, column_name):
    valid_values = ['Viajes', 'BHA', 'BOP', 'Perforación', 'Conexión', 'Mete', 'Circula', 'TR', 'Viajes-Term']
    df[column_name] = df[column_name].apply(lambda x: x if x in valid_values else pd.NA)
    return df

def clean_condicionante_column(df, column_name):
    valid_values = ["Rotación y bombeo", "Velocidad controlada", "Txt", "Mide y calibra", "Tubo frío", "Conectado a top drive", "Sobretorque", "Mcc", "2 tramos",
                    "Llave de fuerza", "Bombeo", "Apoyo de grúa", "Removedores de recorte", "Bombeo continuo", "Chaqueta recolectora", "Registro giroscópico", 
                    "Rotación", "Pérdida de circulación", "Mpd", "Inspección de juntas", "Alineado a mpd", "Suelo natural", "Arma lingadas en cuñas", 
                    "Tubería llena", "Quema de cuerda", "Stripeando"]
    df[column_name] = df[column_name].apply(lambda x: x if x in valid_values else pd.NA)
    return df

# def calculate_macroactividad(df):
#     last_drilled_meter = df[df['Actividad'] == 'Perforación']['Profundidad de pozo'].max()

#     df['Macroactividad'] = 'Perforación'

#     drilling_active = False

#     for index in range(len(df)):
#         if df.loc[index, 'Actividad'] == 'Perforación':
#             drilling_active = True
        
#         if df.loc[index, 'Profundidad de pozo'] > last_drilled_meter and not drilling_active:
#             df.loc[index, 'Macroactividad'] = 'Cambio de Etapa'
        
#         if df.loc[index, 'Actividad'] not in ['Perforación', 'Viajes']:
#             drilling_active = False

#     return df

def calculate_macroactividad(df):
    # Find the last drilled meter
    last_drilled_meter = df[df['Actividad'] == 'Perforación']['Profundidad de pozo'].max()

    # Initialize Macroactividad
    df['Macroactividad'] = 'Perforación'

    # Track if drilling has occurred
    drilling_active = False

    # Loop through the DataFrame to determine Macroactividad
    for index in range(len(df)):
        if df.loc[index, 'Actividad'] == 'Perforación':
            drilling_active = True
        
        # Check if we are past the last drilled meter
        if df.loc[index, 'Profundidad de pozo'] > last_drilled_meter and not drilling_active:
            df.loc[index, 'Macroactividad'] = 'Cambio de Etapa'
        
        # Safely reset drilling_active
        if df.loc[index, 'Actividad'] not in ['Perforación', 'Viajes']:
            drilling_active = False

    return df

def process_standardization_columns(df, dtype_mapping):
    for column, dtype in dtype_mapping.items():
        if column in df.columns:
            if dtype == 'datetime':
                df[column] = pd.to_datetime(df[column], errors='coerce')
            elif dtype == 'timedelta':
                df[column] = pd.to_timedelta(df[column], errors='coerce')
            elif dtype == 'int64':
                df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
            elif dtype == 'float64':
                df[column] = pd.to_numeric(df[column], errors='coerce')
            else:
                df[column] = df[column].astype(dtype)
        else:
            print(f"Warning: Column '{column}' not found in DataFrame")
    return df


# --------------------------------------------------------------------------------------------------------------------------------------
#                                                    # NUMERIC COLUMNS TRANSFORMAITONS / CALCULATIONS
# --------------------------------------------------------------------------------------------------------------------------------------

def calcular_velocidad_estandar_trips(row):
    if (row['Perforadora'] == 'Pemex') and (row['Actividad'] == 'Viajes') and (row['Sub actividad'] == 'Mete'):
        return 500
    elif (row['Perforadora'] == 'Pemex') and (row['Actividad'] == 'Viajes') and (row['Sub actividad'] == 'Levanta'):
        return 500
    elif (row['Perforadora'] == 'Opex') and (row['Actividad'] == 'Viajes') and (row['Sub actividad'] == 'Mete'):
        return 640
    elif (row['Perforadora'] == 'Opex') and (row['Actividad'] == 'Viajes') and (row['Sub actividad'] == 'Levanta'):
        return 732
    else:
        return None
    
def calcular_estandar_conexiones_perforando(row):
    actividad = row['Actividad']
    inclinacion = row['Inclinacion']
    procedimiento_mpd = row['Procedimiento MPD']

    if actividad == "Conexión":
        if inclinacion < 30:
            if procedimiento_mpd == 0:
                return 15
            else:
                return 20

        elif 30 <= inclinacion < 60:
            if procedimiento_mpd == 0:
                return 22
            else:
                return 27

        elif inclinacion >= 60:
            if procedimiento_mpd == 0:
                return 35
            else:
                return 40

    return None

def calcular_estandar_velocidad_completion(row):
    if row['Descripción actividad'] in ['aparejo', 'pistolas']:
        return 124
    else:
        if row['Perforadora'] == 'Opex':
            if row['Sub actividad'] == 'Mete':
                return 640
            elif row['Sub actividad'] == 'Levanta':
                return 732
            else:
                return None
        elif row['Perforadora'] == 'Pemex':
            if row['Sub actividad'] == 'Mete' or row['Sub actividad'] == 'Levanta':
                return 500
            else:
                return None
        else:
            return None

def calcular_profundidad_pozo(df, well_column="Pozo", depth_column="Hasta"):
    # Create a copy to avoid modifying the original DataFrame
    df_copy = df.copy()

    # Function to calculate increasing depth
    def continuous_increase(series):
        return series.cummax()

    # Apply cummax for each well to ensure "Profundidad de pozo" increases or stays the same
    df_copy['Profundidad de pozo'] = df_copy.groupby(well_column)[depth_column].transform(continuous_increase)

    return df_copy

def calculate_estandar_bha(row):
    tipo_de_bha = row['Tipo de BHA']
    tipo_de_actividad = row['Descripción actividad']
    
    if pd.isna(tipo_de_bha) or not isinstance(tipo_de_bha, (int, float, str)):
        return None

    try:
        tipo_de_bha = int(tipo_de_bha)
    except ValueError:
        return None

    if tipo_de_actividad.startswith('Arma'):
        return armado_bha_mapping.get(tipo_de_bha, None)
    else:
        return desarmado_bha_mapping.get(tipo_de_bha, None)

def llenar_columna_eficiencia(row):
    print(f"Row: {row}")
    if pd.notna(row['Eficiencia cp']):
        print(f"Returning Eficiencia cp: {row['Eficiencia cp']}")
        return row['Eficiencia cp']
    elif pd.notna(row['Eficiencia viaje']):
        print(f"Returning Eficiencia viaje: {row['Eficiencia viaje']}")
        return row['Eficiencia viaje']
    elif pd.notna(row['Eficiencia TR']):
        print(f"Returning Eficiencia TR: {row['Eficiencia TR']}")
        return row['Eficiencia TR']
    elif pd.notna(row['Eficiencia BHA']):
        print(f"Returning Eficiencia BHA: {row['Eficiencia BHA']}")
        return row['Eficiencia BHA']    
    elif pd.notna(row['Eficiencia terminacion']):
        print(f"Returning Eficiencia terminacion: {row['Eficiencia terminacion']}")
        return row['Eficiencia terminacion']
    else:
        print("Returning None")
        return None

def clip_upper_without_outliers(df, column_name):
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    filtered_data = df[(df[column_name] >= lower_bound) & (df[column_name] <= upper_bound)]
    max_value = filtered_data[column_name].max()
    df[column_name] = df[column_name].clip(upper=max_value)

    return df
# --------------------------------------------------------------------------------------------------------------------------------------
#                                                    # DATAFRAME TRANSFORMATIONS
# --------------------------------------------------------------------------------------------------------------------------------------

def drop_duplicates(df, columns):
    return df.drop_duplicates(subset=columns, keep='first')

def process_cp_columns(df):
    # Calcula las nuevas columnas
    df['Estandar cp'] = df.apply(calcular_estandar_conexiones_perforando, axis=1)
    df['Ahorro cp (min)'] = (df['Conexion fondo a fondo'] - df['Estandar cp']).round(1)
    df['Ahorro cp (hr)'] = df['Ahorro cp (min)'] / 60
    df['TNPI cp (min)'] = df['Ahorro cp (min)'].clip(lower=0)
    df['TNPI cp (hr)'] = df['TNPI cp (min)'] / 60
    df['Eficiencia cp'] = ((1 - df['TNPI cp (min)'] / df['Conexion fondo a fondo']) * 100).round(1)

    # Agrupar por 'Pozo', 'Fecha' y 'Turno'
    grouped_cp = df.groupby(['Pozo', 'Fecha', 'Turno'])
    eventos_totales_por_grupo_cp = grouped_cp.size().reset_index(name='Eventos Totales cp')
    eventos_cumplidos_por_grupo_cp = grouped_cp.apply(lambda x: (x['Conexion fondo a fondo'] < x['Estandar cp']).sum()).reset_index(name='Eventos Cumplidos cp')
    
    # Calcular la consistencia
    consistencia_por_grupo_cp = pd.merge(eventos_totales_por_grupo_cp, eventos_cumplidos_por_grupo_cp, on=['Pozo', 'Fecha', 'Turno'])
    consistencia_por_grupo_cp['Consistencia cp'] = (consistencia_por_grupo_cp['Eventos Cumplidos cp'] / consistencia_por_grupo_cp['Eventos Totales cp']) * 100
    
    # Unir los resultados al DataFrame original
    df = pd.merge(df, consistencia_por_grupo_cp, on=['Pozo', 'Fecha', 'Turno'], how='left')
    
    return df

def clean_master_data(master, dn, fn):
    # Capitalize and strip column names
    master = master[dn.orden_cols]
    master.columns = [col.capitalize().strip() for col in master.columns]
    
    # Rename columns based on dictionary provided in dn
    master = master.rename(columns=dn.nombre_columnas)
    
    # Clean and standardize 'Pozo' column
    master['Pozo'] = master['Pozo'].str.strip().str.upper()
    master['Pozo'] = master['Pozo'].replace(dn.nombre_pozos)
    master['Pozo'] = master['Pozo'].replace('-', ' ', regex=True)
    
    # Replace values in 'Etapa' column
    master['Etapa'] = master['Etapa'].replace(dn.etapas)
    
    # Map 'Tipo de pozo', 'Equipo', and 'Perforadora' columns
    master['Tipo de pozo'] = master['Pozo'].map(dn.tipo_de_pozos)
    master['Equipo'] = master['Pozo'].map(dn.pozos_equipos)
    master['Equipo'] = master['Equipo'].replace('-', ' ', regex=True)
    master['Perforadora'] = master['Pozo'].map(dn.pozo_perforadora)
    
    # Drop duplicates
    master = drop_duplicates(master, ['Pozo', 'Actividad', 'Sub actividad', 'Fecha inicio', 'Fecha fin', 'Hora inicio', 'Hora fin'])
    
    # Sort values
    master = master.sort_values(by=["Pozo", "Fecha inicio", "Hora inicio"])
    
    return master

def limpieza_y_enriquecimiento_de_tiempo(
        bitacora: pd.DataFrame
        ) -> pd.DataFrame:
    """
    Este es el primer paso donde se crea informacion,
    partiendo de los valores de las columnas
    """
    #logger.name = 'crear_columnas_datetime'
    master = bitacora.copy()
    master['Hora inicio'] = master['Hora inicio'].apply(clean_time)
    master['Hora fin'] = master['Hora fin'].apply(clean_time)
    print(master['Hora inicio'].apply(type).unique()) 

    master['Fecha inicio'] = pd.to_datetime(master['Fecha inicio'], errors='coerce', format='%Y/%m/%d')
    master['Fecha fin'] = pd.to_datetime(master['Fecha fin'], errors='coerce', format='%Y/%m/%d')

    master['Inicia'] = master.apply(
        lambda row: pd.Timestamp.combine(
        row['Fecha inicio'], 
        row['Hora inicio']) 
        if row['Hora inicio'] is not None else None, axis=1
        )

    master['Termina'] = master.apply(
        lambda row: pd.Timestamp.combine(
        row['Fecha fin'], 
        row['Hora fin'])
        if row['Hora fin'] is not None else None, axis=1
        )
    
    master['Inicia'] = pd.to_datetime(master['Inicia'], errors='coerce')
    master['Termina'] = pd.to_datetime(master['Termina'], errors='coerce')
    
    master = master.dropna(subset=['Inicia'])
    master = master.dropna(subset=['Termina'])
    
    master['Año'] = master['Inicia'].dt.year
    master['Semana'] = master['Inicia'].dt.isocalendar().week
    master['Hora'] = master['Inicia'].dt.hour

    inicia = list(pd.to_datetime(master['Inicia'], format='%Y/%m/%d').dt.date)
    termina = list(pd.to_datetime(master['Termina'], format='%Y/%m/%d').dt.date)

    hora_fin = list(pd.to_datetime(master['Hora fin'], format='%H:%M:%S').dt.time)

    # fecha = [
    #     ft if (hf != 0) and (ft > fi) else fi for hf, ft, fi in zip(
    #         hora_fin, termina, inicia
    #         )
    #         ]

    fecha = []
    for hora, fecha_inicio, fecha_final in zip(
        hora_fin, inicia, termina
    ):
        print(hora, hora == datetime.time(0,0,0))

        if fecha_inicio == fecha_final:
            fecha.append(fecha_inicio)
        
        elif hora == datetime.time(0,0,0):
            fecha.append(fecha_inicio)
        
        else:
            fecha.append(fecha_final)

    master['Fecha'] = fecha
    master['Fecha'] = pd.to_datetime(master['Fecha'], format='%Y/%m/%d').dt.date

    master['Tiempo (hr)'] = ((master['Termina'] - master['Inicia']).dt.total_seconds() / 3600).round(3)
    master['Tiempo (hr)'] = pd.to_numeric(master['Tiempo (hr)'], errors='coerce')

    return master

def basic_clipers(df: pd.DataFrame) -> None:
    """
    Realiza el clip de Metros deslizados, Metros rotados, Longitud de lingada,
    Tiempo circulado y Tiempo de bombeo
    """
    master = df.copy()
    master['Metros deslizados'] = pd.to_numeric(master['Metros deslizados'], errors='coerce')
    master['Metros rotados'] = pd.to_numeric(master['Metros rotados'], errors='coerce')

    master = clip_upper_without_outliers(master, 'Longitud de lingada')
    master = clip_upper_without_outliers(master, 'Metros rotados')
    master = clip_upper_without_outliers(master, 'Metros deslizados')
    
    master["Tiempo circulado (min)"] = master["Tiempo circulado (min)"].clip(lower=0)
    master["Tiempo de bombeo (hr)"] = master["Tiempo de bombeo (hr)"].clip(lower=0)

    return master

# def assign_microactivity(desc: str) -> str:
#     f"""
#     Dada una descripcion, regresara el nombre de la microactividad correspondiente
#     segun las referencias almacenadas en el excel {color_est_file}
#     """

#     # suugar sintax for the `for loop`
#     d_refs = {
#         'first': list(double_ref['Primaria']),
#         'second': list(double_ref['Secundaria']),
#         'activity': list(double_ref['Microactividad']),
#     }

#     for first_ref, second_ref, activity in zip(d_refs['first'], d_refs['second'], d_refs['activity']):
#         if (first_ref.lower() in desc) and (second_ref.lower() in desc):
#             return activity
    
#     s_refs = {
#         'kw': list(single_ref['Primaria']),
#         'val': list(single_ref['Microactividad'])
#     }

#     for keyword, value in zip(s_refs['kw'], s_refs['val']):
#         if keyword.lower() in desc:
#             return value
        
#     return 'Pendiente'

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                    # FUNCIONES DE LA APLICACIÓN
# --------------------------------------------------------------------------------------------------------------------------------------

def round_floats(dataframes, decimals=2):
    rounded_dataframes = []
    for df in dataframes:
        rounded_df = df.round(decimals)
        rounded_dataframes.append(rounded_df)
    
    return rounded_dataframes

def capitalize_columns_and_pozo(*dataframes):
    for df in dataframes:
        df.columns = df.columns.str.capitalize()
        
        if 'Pozo' in df.columns:
            df['Pozo'] = df['Pozo'].str.capitalize()

def calculate_productive_time(inpt, npt):
    tnpi_totales = inpt[['Pozo', 'Fecha', 'Tnpi generado']].groupby(['Pozo', 'Fecha']).sum().reset_index()
    tnpi_totales['Tnpi cumulativo'] = tnpi_totales.groupby('Pozo')['Tnpi generado'].cumsum()
    tnpi_totales = tnpi_totales.rename(columns={'Tnpi generado': 'TNPI 24h', 'Tnpi cumulativo': 'TNPI total'})

    tnp_totales = npt.copy()
    tnp_totales = tnp_totales.rename(columns={"Tiempo (dias)": "Tnp generado", 'Apertura': 'Fecha'})
    tnp_totales['Tnp generado'] = tnp_totales['Tnp generado'] * 24
    tnp_totales = tnp_totales[['Pozo', 'Fecha', 'Tnp generado']].groupby(['Pozo', 'Fecha']).sum().reset_index()
    tnp_totales['Tnp cumulativo'] = tnp_totales.groupby('Pozo')['Tnp generado'].cumsum()
    tnp_totales = tnp_totales.rename(columns={'Tnp generado': 'TNP 24h', 'Tnp cumulativo': 'TNP total'})

    # Merge TNPI and TNP data
    tiempos_diarios = pd.merge(tnp_totales, tnpi_totales, on=['Pozo', 'Fecha'], how='outer')

    for col in ['TNP 24h', 'TNPI 24h', 'TNP total', 'TNPI total']:
        tiempos_diarios[col] = tiempos_diarios[col].replace(np.nan, 0)

    tiempos_diarios['TP'] = 24 - tiempos_diarios['TNPI 24h'] - tiempos_diarios['TNP 24h']
    tiempos_diarios['TP'] = tiempos_diarios['TP'].replace(np.nan, 24)

    tiempos_diarios = tiempos_diarios[['Pozo', 'Fecha', 'TP', 'TNPI 24h', 'TNP 24h', 'TNPI total', 'TNP total']]

    return tiempos_diarios

# Example usage:
# tiempos_diarios = calculate_tnpi_tnp_totals(inpt, npt)
