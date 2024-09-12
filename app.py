####################     External Core     ####################
import base64
import time
import streamlit as st
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objects as go
import sweetviz as sv
from plotly.subplots import make_subplots
from PIL import Image
from datetime import datetime

####################     Internal Core     ####################
import funciones as fn

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

tab1, tab2, tab3, tab4 = st.tabs(["Bitácoras", "Tiempos no productivos invisibles", "Tiempos no productivos", "Alertas"])

tab_titles_font_size = "10px"

####################     Data     ####################

from load_data import *
@st.cache_data

def data():
    return logs, alerts, npt, inpt

logs, alerts, npt, inpt = fn.round_floats([logs, alerts, npt, inpt])

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
        value=(start_date, end_date)
    )

    if well_selector and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])

        logs_well_filtered = logs[logs['Pozo'].isin(well_selector)]

        logs_date_filtered = logs_well_filtered[logs_well_filtered['Fecha'].between(start_date, end_date)]

        st.write("Datos filtrados:")
        st.dataframe(logs_date_filtered)
   
    else:
        st.warning("Por favor, selecciona un pozo y rango de tiempo valido.")


    open_report = st.button("Abrir reporte")
    if open_report:
        if 'logs_date_filtered' in locals() and not logs_date_filtered.empty:
            with st.spinner('Generando reporte...'):
                data_report = sv.analyze(logs_date_filtered)
                data_report.show_html('Reporte de datos CNT.html')
                message_placeholder = st.empty()
                message_placeholder.success('Reporte generado con éxito!')
                time.sleep(3)
                message_placeholder.empty()
        else:
            st.warning("No se ha seleccionado un pozo o rango de tiempo válido para generar el reporte.")
    
####################     Tab 2     ####################

with tab2:
    st.write('Work in progress')

