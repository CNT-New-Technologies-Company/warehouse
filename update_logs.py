#!/usr/bin/env python
# coding: utf-8

# ##### <blockquote> **Core** <br> Librerias, diccionarios y directorios </blockquote>

# In[1]:


import os
import re
import shutil
import datetime
import importlib

import numpy as np
import pandas as pd

import diccionarios as dn
import directorios as dir
import funciones as fn


# In[2]:


# importlib.reload(dn)
# importlib.reload(dir)
# importlib.reload(fn)


# ##### <blockquote> **Paso 1** <br> Mover las bitacoras de carpeta raíz a carpeta de pozo </blockquote>

# In[3]:


files = os.listdir(dir.single_well_logs_paths)

for file in files:
    if file.endswith('.xlsx'):
        pozo_name = file.split('_')[0]
        # TIP: Extrae el nombre del pozo del nombre del archivo (Esto asume que el nombre del pozo está al principio y separado por un espacio, ajusta según sea necesario)

        pozo_folder_path = os.path.join(dir.single_well_logs_paths, pozo_name)
        # TIP: Crear el path a la carpeta del pozo, asumiendo que la carpeta ya existe y tiene el mismo nombre que el pozo

        if not os.path.exists(pozo_folder_path):
            os.makedirs(pozo_folder_path)
        # TIP: Verifica si la carpeta existe, si no, la crea

        full_file_path = os.path.join(dir.single_well_logs_paths, file)
        new_file_path = os.path.join(pozo_folder_path, file)
        # TIP: Obtener la ruta completa del archivo y la nueva ruta en la carpeta del pozo

        shutil.move(full_file_path, new_file_path)
        # TIP: Mover el archivo a la carpeta del pozo
        
        print(f"Se movio: {file} a la carpeta {pozo_folder_path}")


# ##### <blockquote> **Paso 2** <br> Lee las bitácoras dentro de las carpetas del directorio "bitacoras_directory" leer "directorios.py" con pd.read_excel() </blockquote>

# In[4]:


dataframes = []

for subdir, dirs, files in os.walk(dir.single_well_logs_paths):
    for file in files:
        if file.endswith('.xlsx'):
            file_path = os.path.join(subdir, file)
            print("Attempting to open:", file_path)
            df = pd.read_excel(file_path, skiprows=1)

            parts = file.split('_')
            pozo_name = parts[0] if len(parts) > 0 else 'Desconocido'

            
            match = re.search(r'Etapa[_ ]([^_]+)', file, re.IGNORECASE)
            if match:
                etapa_pozo = match.group(1).strip()  
            else:
                etapa_pozo = 'Desconocido'

            df['Pozo'] = pozo_name
            df['Etapa'] = etapa_pozo

            dataframes.append(df)

master = pd.concat(dataframes, ignore_index=True)


# ##### <blockquote> Transformación de dato fuente, ordenamiento y mapeo de variables </blockquote>

# In[5]:


master = fn.clean_master_data(master, dn, fn)


# #### Datetime columns transformations ####

# In[6]:


master['Hora inicio'] = master['Hora inicio'].apply(fn.clean_time)
master['Hora fin'] = master['Hora fin'].apply(fn.clean_time)
print(master['Hora inicio'].apply(type).unique()) 


# In[7]:


master['Fecha inicio'] = pd.to_datetime(master['Fecha inicio'], errors='coerce', format='%Y/%m/%d')
master['Fecha fin'] = pd.to_datetime(master['Fecha fin'], errors='coerce', format='%Y/%m/%d')

master['Inicia'] = master.apply(lambda row: pd.Timestamp.combine(
                                    row['Fecha inicio'], 
                                    row['Hora inicio']) 
                                    if row['Hora inicio'] is not None else None, axis=1)

master['Termina'] = master.apply(lambda row: pd.Timestamp.combine(
                                    row['Fecha fin'], 
                                    row['Hora fin'])
                                    if row['Hora fin'] is not None else None, axis=1)

master['Fecha'] = pd.to_datetime(master['Inicia'], format='%Y/%m/%d').dt.date
master['Año'] = master['Inicia'].dt.year
master['Semana'] = master['Inicia'].dt.isocalendar().week
master['Hora'] = master['Inicia'].dt.hour


# In[8]:


master['Inicia'] = pd.to_datetime(master['Inicia'], errors='coerce')
master['Termina'] = pd.to_datetime(master['Termina'], errors='coerce')

master = master.dropna(subset=['Inicia'])
master = master.dropna(subset=['Termina'])


# In[9]:


master['Fecha'] = pd.to_datetime(master['Inicia'], format='%Y/%m/%d').dt.date
master['Año'] = master['Inicia'].dt.year
master['Semana'] = master['Inicia'].dt.isocalendar().week
master['Hora'] = master['Inicia'].dt.hour


# #### String columns transformations ####

# In[10]:


master['Turno'] = master.apply(lambda row: fn.asignar_turno(row['Inicia'], row['Tipo de pozo']), axis=1)


# In[11]:


master['Color'] = pd.to_numeric(master['Color'], errors='coerce')


# In[12]:


master['Profundidad de conexion'] = master['Profundidad de conexion'].str.replace(',', '').astype(float)


# In[13]:


master['Actividad'].unique()


# In[14]:


master = fn.clean_actividad_column(master, 'Actividad')


# In[15]:


master = fn.clean_tagujero_column(master, 'Tipo agujero')


# In[16]:


master = fn.clean_condicionante_column(master, 'Condicionante')


# In[17]:


master = fn.clean_notas_column(master, 'Notas')


# In[18]:


string_columns_master = [key for key, value in dn.dtype_mapping.items() if value == 'str']
master[string_columns_master] = master[string_columns_master].applymap(fn.capitalize_and_strip)


# #### Numeric columns transformations ####

# In[19]:


master['Tiempo (hr)'] = ((master['Termina'] - master['Inicia']).dt.total_seconds() / 3600).round(3)
master['Tiempo (hr)'] = pd.to_numeric(master['Tiempo (hr)'], errors='coerce')


# In[20]:


master['Actividad'] = master['Actividad'].fillna('Tiempo')
master['Sub Actividad'] = master['Sub actividad'].fillna('Tiempo')


# In[21]:


master['Metros deslizados'] = pd.to_numeric(master['Metros deslizados'], errors='coerce')
master['Metros rotados'] = pd.to_numeric(master['Metros rotados'], errors='coerce')


# In[22]:


master = fn.clip_upper_without_outliers(master, 'Longitud de lingada')


# In[23]:


master = fn.clip_upper_without_outliers(master, 'Metros rotados')


# In[24]:


master = fn.clip_upper_without_outliers(master, 'Metros deslizados')


# In[25]:


master["Tiempo circulado (min)"] = master["Tiempo circulado (min)"].clip(lower=0)


# In[26]:


master["Tiempo de bombeo (hr)"] = master["Tiempo de bombeo (hr)"].clip(lower=0)


# In[27]:


numeric_columns_master = master.select_dtypes('float64').columns.tolist()
master[numeric_columns_master] = master[numeric_columns_master].round(3).fillna(pd.NA)


# #### Columns not in log ####

# In[28]:


master = fn.calcular_profundidad_pozo(master, "Pozo", "Hasta")
master['Profundidad de pozo'] = pd.to_numeric((master['Profundidad de pozo']))


# In[29]:


# master = fn.calculate_macroactividad(master)


# #### KPI columns complements ####

# In[30]:


master['Estandar BHA'] = master.apply(fn.calculate_estandar_bha, axis=1)
master['Eficiencia BHA'] = ((master['Tiempo (hr)']/master['Estandar BHA'])*100).clip(upper=100)
master['TNPI BHA (hr)']  = (master['Estandar BHA'] - master['Tiempo (hr)']).round(1).clip(lower=0)


# In[31]:


master['Estandar cp'] = master.apply(fn.calcular_estandar_conexiones_perforando, axis=1)
master['Ahorro cp (min)'] = (master['Conexion fondo a fondo'] - master['Estandar cp']).round(1)
master['Ahorro cp (hr)'] = master['Ahorro cp (min)']/60
master['TNPI cp (min)'] = master['Ahorro cp (min)'].clip(lower=0)
master['TNPI cp (hr)'] = master['TNPI cp (min)']/60
master['Eficiencia cp'] = ((1-master['TNPI cp (min)']/master['Conexion fondo a fondo'])*100).round(1)

grouped_cp = master.groupby(['Pozo', 'Fecha', 'Turno'])
eventos_totales_por_grupo_cp = grouped_cp.size().reset_index(name='Eventos Totales cp')
eventos_cumplidos_por_grupo_cp = grouped_cp.apply(lambda grouped_cp: (grouped_cp['Conexion fondo a fondo'] < grouped_cp['Estandar cp']).sum()).reset_index(name='Eventos Cumplidos cp')
consistencia_por_grupo_cp = pd.merge(eventos_totales_por_grupo_cp, eventos_cumplidos_por_grupo_cp, on=['Pozo', 'Fecha', 'Turno'])
consistencia_por_grupo_cp['Consistencia cp'] = (consistencia_por_grupo_cp['Eventos Cumplidos cp'] / consistencia_por_grupo_cp['Eventos Totales cp']) * 100
master = pd.merge(master, consistencia_por_grupo_cp, on=['Pozo', 'Fecha', 'Turno'], how='left')


# In[32]:


master['Estandar viaje'] = master.apply(fn.calcular_velocidad_estandar_trips, axis=1)
master['Tiempo teorico viajes (hr)'] = (master['Metros viajados']/master['Estandar viaje'])
master['Ahorro en viajes (hr)'] = master['Tiempo (hr)'] - master['Tiempo teorico viajes (hr)']
master['TNPI viajes (hr)'] = master['Ahorro en viajes (hr)'].clip(lower=0)
master['Puntaje viaje'] = ((1-master['TNPI viajes (hr)']/master['Tiempo (hr)'])*100).round(1)
master['Eficiencia viaje'] = master['Puntaje viaje'].clip(upper=100)

grouped = master.groupby(['Pozo', 'Fecha', 'Turno'])
eventos_totales_por_grupo_viajes = grouped.size().reset_index(name='Eventos Totales')
eventos_cumplidos_por_grupo_viajes = grouped.apply(lambda group: (group['Velocidad (m/h)'] > group['Estandar viaje']).sum()).reset_index(name='Eventos Cumplidos')
consistencia_por_grupo_viajes = pd.merge(eventos_totales_por_grupo_viajes, eventos_cumplidos_por_grupo_viajes, on=['Pozo', 'Fecha', 'Turno'])
consistencia_por_grupo_viajes['Consistencia viajes'] = (consistencia_por_grupo_viajes['Eventos Cumplidos'] / consistencia_por_grupo_viajes['Eventos Totales']) * 100
master = pd.merge(master, consistencia_por_grupo_viajes, on=['Pozo', 'Fecha', 'Turno'], how='left')


# In[33]:


master['Estandar TR'] = master['Diametro de TR'].map(dn.casing_velocidad_std)
master['Tiempo teorico TR (hr)'] = (master['Metros viajados']/master['Estandar TR'])
master['Ahorro en TR (hr)'] = master['Tiempo (hr)'] - master['Tiempo teorico TR (hr)']
master['TNPI TR (hr)'] = master['Ahorro en TR (hr)'].clip(lower=0)
master['Puntaje TR'] = ((1-master['TNPI TR (hr)']/master['Tiempo (hr)'])*100).round(1)
master['Eficiencia TR'] = master['Puntaje TR'].clip(upper=100)

grouped = master.groupby(['Pozo', 'Fecha', 'Turno'])
eventos_totales_por_grupo_tr = grouped.size().reset_index(name='Eventos Totales TR')
eventos_cumplidos_por_grupo_tr = grouped.apply(lambda group: (group['Velocidad (m/h)'] > group['Estandar TR']).sum()).reset_index(name='Eventos Cumplidos TR')
consistencia_por_grupo_TR = pd.merge(eventos_totales_por_grupo_tr, eventos_cumplidos_por_grupo_tr, on=['Pozo', 'Fecha', 'Turno'])
consistencia_por_grupo_TR['Consistencia TR'] = (consistencia_por_grupo_TR['Eventos Cumplidos TR'] / consistencia_por_grupo_TR['Eventos Totales TR']) * 100
master = pd.merge(master, consistencia_por_grupo_TR, on=['Pozo', 'Fecha', 'Turno'], how='left')


# In[34]:


master['Estandar terminacion'] = master.apply(fn.calcular_estandar_velocidad_completion, axis=1)
master['Tiempo teorico terminacion (hr)'] = (master['Metros viajados']/master['Estandar terminacion'])
master['Ahorro en terminacion (hr)'] = master['Tiempo (hr)'] - master['Tiempo teorico terminacion (hr)']
master['TNPI terminacion (hr)'] = master['Ahorro en terminacion (hr)'].clip(lower=0)
master['Puntaje terminacion'] = ((1-master['TNPI terminacion (hr)']/master['Tiempo (hr)'])*100).round(1)
master['Eficiencia terminacion'] = master['Puntaje terminacion'].clip(upper=100)

grouped = master.groupby(['Pozo', 'Fecha', 'Turno'])
eventos_totales_por_grupo_terminacion = grouped.size().reset_index(name='Eventos Totales terminacion')
eventos_cumplidos_por_grupo_terminacion = grouped.apply(lambda group: (group['Velocidad (m/h)'] > group['Estandar terminacion']).sum()).reset_index(name='Eventos Cumplidos terminacion')
consistencia_por_grupo_terminacion = pd.merge(eventos_totales_por_grupo_terminacion, eventos_cumplidos_por_grupo_terminacion, on=['Pozo', 'Fecha', 'Turno'])
consistencia_por_grupo_terminacion['Consistencia terminacion'] = (consistencia_por_grupo_terminacion['Eventos Cumplidos terminacion'] / consistencia_por_grupo_terminacion['Eventos Totales terminacion']) * 100
master = pd.merge(master, consistencia_por_grupo_terminacion, on=['Pozo', 'Fecha', 'Turno'], how='left')


# In[35]:


numeric_columns_master = master.select_dtypes('float64').columns.tolist()


# In[36]:


master[numeric_columns_master] = master[numeric_columns_master].round(3).fillna(np.nan)


# In[37]:


master['eficiencia'] = master['Eficiencia cp'].fillna(master['Eficiencia viaje']).fillna(master['Eficiencia TR']).fillna(master['Eficiencia BHA']).fillna(master['Eficiencia terminacion'])


# In[38]:


master['estandar'] = master['Estandar cp'].fillna(master['Estandar viaje']).fillna(master['Estandar TR']).fillna(master['Estandar BHA']).fillna(master['Estandar terminacion'])


# In[39]:


master['tnpi'] = master['TNPI cp (hr)'].fillna(master['TNPI viajes (hr)']).fillna(master['TNPI TR (hr)']).fillna(master['TNPI BHA (hr)']).fillna(master['TNPI terminacion (hr)'])


# ##### --------------------------------------------------------------------------------------------------------------------------------------
# #####                                                       Cumulative days (Pozo / Etapa)
# ##### --------------------------------------------------------------------------------------------------------------------------------------

# In[40]:


master = master.sort_values(by=['Pozo', 'Etapa', 'Fecha'])

master_reverse = master.groupby(['Pozo', 'Etapa']).apply(lambda x: x[::-1]).reset_index(drop=True)

unique_dates_pozo_reverse = master_reverse.drop_duplicates(subset=['Pozo', 'Fecha']).copy()
unique_dates_pozo_reverse['Cumdays pozo'] = unique_dates_pozo_reverse.groupby('Pozo').cumcount(ascending=False) + 1

unique_dates_etapa_reverse = master_reverse.drop_duplicates(subset=['Pozo', 'Etapa', 'Fecha']).copy()
unique_dates_etapa_reverse['Cumdays etapa'] = unique_dates_etapa_reverse.groupby(['Pozo', 'Etapa']).cumcount(ascending=False) + 1

master_reverse = master_reverse.merge(unique_dates_pozo_reverse[['Pozo', 'Fecha', 'Cumdays pozo']], on=['Pozo', 'Fecha'], how='left')
master_reverse = master_reverse.merge(unique_dates_etapa_reverse[['Pozo', 'Etapa', 'Fecha', 'Cumdays etapa']], on=['Pozo', 'Etapa', 'Fecha'], how='left')

master_reverse = master_reverse.sort_values(by=['Pozo', 'Etapa', 'Fecha'])


# In[41]:


master_reverse = master_reverse[dn.output_cols]


# In[42]:


excel_path = os.path.join(dir.log_path_and_file)
master_reverse.to_excel(excel_path, sheet_name='Bitacoras', index=False, engine='openpyxl')


# In[43]:


print("bitacora maestra guardada con éxito en:", excel_path)


# ##### --------------------------------------------------------------------------------------------------------------------------------------
# #####                                                       POST-NOTEBOOK EXPERIMENTATION
# ##### --------------------------------------------------------------------------------------------------------------------------------------
