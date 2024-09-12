import pandas as pd
from directorios import *

logs = pd.read_excel(log_path_and_file)
alerts = pd.read_excel(alerts_path_file)
npt = pd.read_excel(npt_path_file)
inpt = pd.read_excel(inpt_path_file)