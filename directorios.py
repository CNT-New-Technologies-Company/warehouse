import os
import pandas as pd

# ----------------------------------------------------------------------
#                          INPUT PATH AND FILES
# ----------------------------------------------------------------------
data_folder_path = os.path.normpath(r"data")

single_well_logs_paths = os.path.join(data_folder_path, "single_well_logs")

log_file = "logs.xlsx"
log_path_and_file = os.path.join(data_folder_path, log_file)

log_file_csv = "logs.csv"
log_path_and_file_csv = os.path.join(data_folder_path, log_file_csv)

alerts_file = "alerts.xlsx"
alerts_path_file = os.path.join(data_folder_path, alerts_file)

npt_file = "npt.xlsx"
npt_path_file = os.path.join(data_folder_path, npt_file)

inpt_file = "inpt.xlsx"
inpt_path_file = os.path.join(data_folder_path, inpt_file)

# ----------------------------------------------------------------------
#                          OUTPUT PATH AND FILES
# ----------------------------------------------------------------------
