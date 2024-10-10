#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import requests
from pyairtable import Api
import pandas as pd
import numpy as np
import xlwings as xw
import diccionarios as dn
import directorios as dir
import funciones as fn

# In[4]:

alertas_cols = [
    "POZO", "APERTURA", "ETAPA", "CIERRE", "TIPO DE ALERTA", "NIVEL DE ALERTA", "ATENCION", "ACTIVIDAD", "ALERTA EMITIDA",
    "RESUMEN DE LA ALERTA", "DESCRIPCION", "CAUSA", "DETALLE", "INFORMADO", "PERSONAL QUE ATIENDE", "COMENTARIO", "AREA DE OPORTUNIDAD"
]

tnp_cols = [
    'POZO', 'ETAPA', 'APERTURA', 'TIEMPO (Dias)', 'SUB-CLASIFICACION', 'CONCEPTO', 'CLASIFICACION'
]

tnpi_cols = ["POZO", "ETAPA", "FECHA", "TNPI GENERADO", "OPERACION", "SUB-OPERACION", "CAUSA", "DETALLE", "AREA DE OPORTUNIDAD"
]


# In[5]:


alertas_api_key = os.getenv('AIRTABLE_API_KEY', 'patk6ag0UsQrjK1nn.e5e08f87ff10103893fafa40d8f0210a50cd63dfb93255b8abaf258de292de89')
alertas_base_id = 'appTA2GBh37ydQWuR'
main_table_name = 'Monitoreo de alertas'
alertas_table_id = 'tblF0z5i5fu0ApizJ'
linked_table_id = 'tblARVQJHR6wNfeS0' 

api = Api(alertas_api_key)
alertas_table = api.table(alertas_base_id, alertas_table_id)

try:
    records = alertas_table.all()
    print("Records retrieved successfully")

    alertas = pd.DataFrame([record['fields'] for record in records])

    if 'APERTURA' in alertas.columns:
        alertas['APERTURA'] = pd.to_datetime(alertas['APERTURA'], errors='coerce')
        if alertas['APERTURA'].dt.tz is None:
            alertas['APERTURA'] = alertas['APERTURA'].dt.tz_localize('UTC').dt.tz_convert('America/Mexico_City')
        else:
            alertas['APERTURA'] = alertas['APERTURA'].dt.tz_convert('America/Mexico_City')

    if 'CIERRE' in alertas.columns:
        alertas['CIERRE'] = pd.to_datetime(alertas['CIERRE'], errors='coerce')
        if alertas['CIERRE'].dt.tz is None:
            alertas['CIERRE'] = alertas['CIERRE'].dt.tz_localize('UTC').dt.tz_convert('America/Mexico_City')
        else:
            alertas['CIERRE'] = alertas['CIERRE'].dt.tz_convert('America/Mexico_City')

    if alertas['APERTURA'].isna().any() or alertas['CIERRE'].isna().any():
        print("Warning: Some datetime conversions failed and resulted in NaT.")

    headers = {
    'Authorization': f'Bearer {alertas_api_key}',
    }

    response = requests.get(f'https://api.airtable.com/v0/{alertas_base_id}/{alertas_table_id}', headers=headers)
    data = response.json()

    linked_table_response = requests.get(f'https://api.airtable.com/v0/{alertas_base_id}/{linked_table_id}', headers=headers)
    linked_table_data = linked_table_response.json()

    linked_map = {record['id']: record['fields']['POZO'] for record in linked_table_data['records']}

    for record in data['records']:
        linked_id = record['fields'].get('POZO')
        if linked_id:
            record['fields']['POZO'] = linked_map.get(linked_id[0], 'Unknown')

    alertas['POZO'] = alertas['POZO'].apply(lambda x: x[0] if isinstance(x, list) and x else x)
    alertas['POZO'] = alertas['POZO'].map(linked_map).fillna('Unknown')
    alertas = alertas.sort_values(by=['POZO', 'ETAPA', 'APERTURA']).reset_index()
    alertas = alertas[alertas_cols]

    with xw.App(visible=False) as app:
        wb = xw.Book()
        ws = wb.sheets[0]
        ws.name = 'ALERTAS'
        ws.range('A1').options(index=False).value = alertas
        wb.save(dir.alerts_path_file)
        wb.close()
    
    print("Data saved to Excel successfully using xlwings")

except Exception as e:
    print("Failed to retrieve or save records:", str(e))


# In[6]:


tnp_api_key = os.getenv('AIRTABLE_API_KEY', 'patk6ag0UsQrjK1nn.e5e08f87ff10103893fafa40d8f0210a50cd63dfb93255b8abaf258de292de89')
tnp_base_id = 'appTA2GBh37ydQWuR'
tnp_table_id = 'tblOYu31lRs5zLSxR'

api = Api(tnp_api_key)
tnp_table = api.table(tnp_base_id, tnp_table_id)

try:
    records = tnp_table.all()
    print("Records retrieved successfully")

    tnp = pd.DataFrame([record['fields'] for record in records])

    tnp['APERTURA'] = pd.to_datetime(tnp['APERTURA'], format='%Y-%m-%d')

    tnp = tnp.sort_values(by=['POZO', 'ETAPA', 'APERTURA']).reset_index()
    tnp = tnp[tnp_cols]

    tnp.to_excel(dir.npt_path_file, sheet_name='TNP', index=False)
    print("Data saved to Excel successfully")

except Exception as e:
    print("Failed to retrieve or save records:", str(e))


# In[7]:


tnpi_api_key = os.getenv('AIRTABLE_API_KEY', 'patk6ag0UsQrjK1nn.e5e08f87ff10103893fafa40d8f0210a50cd63dfb93255b8abaf258de292de89')
tnpi_base_id = 'appTA2GBh37ydQWuR'
tnpi_table_id = 'tblRHiTnYaXL7QVjJ'

api = Api(tnpi_api_key)
tnpi_table = api.table(tnpi_base_id, tnpi_table_id)

try:
    records = tnpi_table.all()
    print("Records retrieved successfully")

    tnpi = pd.DataFrame([record['fields'] for record in records])
    tnpi = tnpi.drop(columns=['Creado por'], errors='ignore')

    tnpi['FECHA'] = pd.to_datetime(tnpi['FECHA'], format='%Y-%m-%d')
    tnpi_columns = {'SUBOPERACION':'SUB-OPERACION'}
    tnpi.rename(columns=tnpi_columns, inplace=True)

    tnpi = tnpi.sort_values(by=['POZO', 'ETAPA', 'FECHA']).reset_index()
    tnpi = tnpi[tnpi_cols]

    tnpi.to_excel(dir.inpt_path_file, sheet_name='TNPI', index=False)
    print("Data saved to Excel successfully")

except Exception as e:
    print("Failed to retrieve or save records:", str(e))


# #### Calculo de horas de TNPI diario y cumulativo

# In[12]:

# tnpi_totales = tnpi[['POZO', 'FECHA', 'TNPI GENERADO']].groupby(['POZO', 'FECHA']).sum().reset_index()

# # Add the cumulative sum for each POZO
# tnpi_totales['TNPI CUMULATIVO'] = tnpi_totales.groupby('POZO')['TNPI GENERADO'].cumsum()

# tnpi_totales = tnpi_totales.rename(columns={'TNPI GENERADO': 'TNPI 24h', 
#                                     'TNPI CUMULATIVO': 'TNPI total'})
# tnpi_totales


# # #### Calculo de horas de TNP diario y cumulativo

# # In[13]:


# tnp_totales = tnp.copy()
# tnp_totales = tnp_totales.rename(
#     columns = {
#         "TIEMPO (Dias)": "TNP GENERADO",
#         'APERTURA': 'FECHA'
#         })
# tnp_totales['TNP GENERADO'] = tnp_totales['TNP GENERADO'] * 24


# # In[14]:


# tnp_totales = tnp_totales[['POZO', 'FECHA', 'TNP GENERADO']].groupby(['POZO', 'FECHA']).sum().reset_index()

# tnp_totales['TNP CUMULATIVO'] = tnp_totales.groupby('POZO')['TNP GENERADO'].cumsum()

# tnp_totales = tnp_totales.rename(columns={'TNP GENERADO': 'TNP 24h', 
#                                     'TNP CUMULATIVO': 'TNP total'})
# tnp_totales


# # In[15]:


# tiempos_diarios = pd.merge(tnp_totales, tnpi_totales, on=['POZO', 'FECHA'], how='outer')


# # In[16]:


# for col in ['TNP 24h', 'TNPI 24h', 'TNP total', 'TNPI total']:
#     tiempos_diarios[col] = tiempos_diarios[col].replace(np.nan, 0)

# tiempos_diarios['TP'] = 24 - tiempos_diarios['TNPI 24h'] - tiempos_diarios['TNP 24h']
# tiempos_diarios['TP'] = tiempos_diarios['TP'].replace(np.nan, 24)
# tiempos_diarios = tiempos_diarios[['POZO', 'FECHA', 'TP', 'TNPI 24h', 'TNP 24h', 'TNPI total', 'TNP total']]
# tiempos_diarios


