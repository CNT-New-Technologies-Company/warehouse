import pandas as pd
# import funciones as fn
from directorios import *

logs = pd.read_excel(log_path_and_file)
alerts = pd.read_excel(alerts_path_file)
npt = pd.read_excel(npt_path_file)
inpt = pd.read_excel(inpt_path_file)

logs.columns = logs.columns.str.capitalize()
alerts.columns = alerts.columns.str.capitalize()
alerts.Pozo = alerts.Pozo.str.capitalize()
npt.columns = npt.columns.str.capitalize()
npt.Pozo = npt.Pozo.str.capitalize()
inpt.columns = inpt.columns.str.capitalize()
inpt.Pozo = inpt.Pozo.str.capitalize()

logs["Fecha"] = pd.to_datetime(logs["Fecha"]).dt.date
inpt["Fecha"] = pd.to_datetime(inpt["Fecha"]).dt.date
npt["Apertura"] = pd.to_datetime(npt["Apertura"]).dt.date

# pt = fn.calculate_productive_time(inpt, npt)

def some_function():
    from funciones import calculate_productive_time
    # Usa calculate_productive_time dentro de esta función
    pt = calculate_productive_time(inpt, npt)