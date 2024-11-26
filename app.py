####################     External Core     ####################
import base64
import subprocess
import time
import streamlit as st
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objects as go
import sweetviz as sv
from load_data import *
from plotly.subplots import make_subplots
from PIL import Image
from datetime import datetime

####################     Internal Core     ####################
import funciones as fn
import diccionarios as dn
import directorios as dir

####################     Page config     ####################
app_title = "CN-Tools"
img=Image.open('1. Imagenes/CNT.png')
img_tab=Image.open('1. Imagenes/CNT_2.png')

st.set_page_config(
    page_title = app_title,
    page_icon = img_tab,
    layout = "wide")

st.markdown(
    """
    <style>
    .toolbar {
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    .stPlotly {
        background-color: transparent !important;
    }
    .stPlotly .js-plotly-plot {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def wrap_ticks(tick_text, max_width=15):
    wrapped_text = []
    for text in tick_text:
        if len(text) > max_width:
            index = max_width
            while index > 0 and text[index] != ' ':
                index -= 1
            wrapped_text.append(text[:index] + "<br>" + text[index:])
        else:
            wrapped_text.append(text)
    return wrapped_text

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

cols_img = st.columns(5)
img2=Image.open('1. Imagenes/CNT Warehouse.png')
cols_img[2].image(img2,width=300)

tab1, tab2 = st.tabs(["Bitácoras", "Alertas-TNP-TNPI"])

tab_titles_font_size = "10px"

####################     Data     ####################

# def data():
#     return logs, alerts, npt, inpt

def reload_logs():
    return pd.read_excel(dir.log_path_and_file)

def reload_alerts():
    return pd.read_excel(dir.alerts_path_file)

def reload_npt():
    return pd.read_excel(dir.npt_path_file)

def reload_inpt():
    return pd.read_excel(dir.inpt_path_file)

logs, alerts, npt, inpt = fn.round_floats([logs, alerts, npt, inpt])

fn.capitalize_columns_and_pozo(logs, alerts, npt, inpt)
summ_24h = fn.calculate_productive_time(inpt, npt)

####################     Tab 1     ####################

with tab1:
    # Tab control buttons
    tab1_main_cols = st.columns(2)

    wells = ["Todos"] + sorted(logs['Pozo'].unique())
    well_selector = tab1_main_cols[0].multiselect(
        "Pozos", wells, 
        placeholder="Selecciona un pozo"
        )
    if "Todos" in well_selector:
        well_selector = wells[1:]
    
    start_date = datetime.now().date()
    end_date = datetime.now().date()
    date_range = tab1_main_cols[1].date_input(
        "Selecciona un periodo de tiempo:",
        value=(start_date, end_date),
        key=1
    )

    if well_selector and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
    
        logs_well_filtered = logs[logs['Pozo'].isin(well_selector)]
    
        # Convert 'Fecha' column to datetime.date
        logs_well_filtered['Fecha'] = logs_well_filtered['Fecha'].dt.date
    
        logs_date_filtered = logs_well_filtered[logs_well_filtered['Fecha'].between(start_date.date(), end_date.date())]
    
        st.write("Datos filtrados:")
        st.dataframe(logs_date_filtered)
   
    else:
        st.warning("Por favor, selecciona un pozo y rango de tiempo valido.")


    open_report = st.button("Abrir reporte", key=2)
    if open_report:
        if 'logs_date_filtered' in locals() and not logs_date_filtered.empty:
            with st.spinner('Generando reporte...'):
                data_report = sv.analyze(logs_date_filtered)
                data_report.show_html('Reporte de datos CNT.html')
                st.success('Reporte generado con éxito!')
                time.sleep(3)
                st.empty()
        else:
            st.warning("No se ha seleccionado un pozo o rango de tiempo válido para generar el reporte.")
    
    compiler = st.button('Actualizar bitacora', key=3)
    if compiler:
        with st.spinner('Actualizando todos los registros...'):
            subprocess.run(['python', 'update_logs.py'], check=True)
            logs = reload_logs()
        st.success("Datos actualizados con éxito.")
        time.sleep(3)    
        st.empty()

####################     Tab 2     ####################

with tab2:
    # Tab control buttons
    tab2_main_cols = st.columns(2)
    wells = ["Todos"] + sorted(inpt['Pozo'].unique())
    well_selector = tab2_main_cols[0].multiselect(
        "Pozos", wells, 
        placeholder="Selecciona un pozo"
        )
    if "Todos" in well_selector:
        well_selector = wells[1:]
    
    start_date = datetime.now().date()
    end_date = datetime.now().date()
    date_range = tab2_main_cols[1].date_input(
        "Selecciona un periodo de tiempo:",
        value=(start_date, end_date),
        key=4
    )

    if well_selector and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])

        alerts_well_filtered = alerts[alerts['Pozo'].isin(well_selector)]
        npt_well_filtered = npt[npt['Pozo'].isin(well_selector)]
        inpt_well_filtered = inpt[inpt['Pozo'].isin(well_selector)]
        summ_24h_well_filtered = summ_24h[summ_24h['Pozo'].isin(well_selector)]

        alerts_date_filtered = alerts_well_filtered[alerts_well_filtered['Apertura'].between(start_date, end_date)]
        npt_date_filtered = npt_well_filtered[npt_well_filtered['Apertura'].between(start_date, end_date)]
        inpt_date_filtered = inpt_well_filtered[inpt_well_filtered['Fecha'].between(start_date, end_date)]
        inpt_date_filtered = inpt_well_filtered[inpt_well_filtered['Fecha'].between(start_date, end_date)]
        summ_24h_date_filtered = summ_24h_well_filtered[summ_24h_well_filtered['Fecha'].between(start_date, end_date)]

        st.write("Datos filtrados:")
        with st.expander("Alertas"):
            st.dataframe(alerts_date_filtered, height=300, use_container_width=True)
        with st.expander("Tiempos no productivos"):
            st.dataframe(npt_date_filtered, height=300, use_container_width=True)
        with st.expander("Tiempos no productivos invisibles"):
            st.dataframe(inpt_date_filtered, height=300, use_container_width=True)
        with st.expander("Resumen de tiempos 24 horas"):
            st.dataframe(summ_24h_date_filtered, height=300, use_container_width=True)

    else:
        st.warning("Por favor, selecciona un pozo y rango de tiempo valido.")
    
    compiler_2 = st.button('Actualizar tablas', key=5)
    if compiler_2:
        with st.spinner('Actualizando todos los registros...'):
            subprocess.run(['python', 'call_tablas_at.py'], check=True)
            alerts = reload_alerts()
            npt = reload_npt()
            inpt = reload_inpt()
        st.success("Datos actualizados con éxito.")
        time.sleep(3)    
        st.empty()