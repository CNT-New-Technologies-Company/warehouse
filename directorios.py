import os
import pandas as pd
# --------------------------------------------------------------------------------------------------------------------------------------
#                                                        # ONEDRIVE FOR EVERYONE                                                        
# --------------------------------------------------------------------------------------------------------------------------------------
one_drive = os.getenv("OneDrive")

# --------------------------------------------------------------------------------------------------------------------------------------
#                                                        # INPUT PATH AND FILES                                                        
# --------------------------------------------------------------------------------------------------------------------------------------
data_folder_path = os.path.join(one_drive, os.path.normpath(r"CNT\4. Proyectos\8. Interfaz de descarga de datos (Experimental)\2. Datos"))

single_well_logs_paths = os.path.join(one_drive, os.path.normpath(r"CNT\4. Proyectos\8. Interfaz de descarga de datos (Experimental)\2. Datos\single_well_logs"))

log_file = "logs.xlsx"
log_path_and_file = os.path.join(data_folder_path, log_file)

alerts_file = "alerts.xlsx"
alerts_path_file = os.path.join(data_folder_path, alerts_file)

npt_file = "npt.xlsx"
npt_path_file = os.path.join(data_folder_path, npt_file)

inpt_file = "inpt.xlsx"
inpt_path_file = os.path.join(data_folder_path, inpt_file)
# --------------------------------------------------------------------------------------------------------------------------------------
#                                                        # OUTPUT PATH AND FILES                                                        
# --------------------------------------------------------------------------------------------------------------------------------------
