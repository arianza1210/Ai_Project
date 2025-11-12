import pandas as pd

file_path = "LayananeService_new.xlsx"
xls = pd.ExcelFile(file_path)
print(xls.sheet_names)
