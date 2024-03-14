import sys
sys.path.append('{FUNCTION PATH}')


import pandas as pa
from PBI_function import  overall_calculations
from openpyxl import load_workbook


project_path = '{PROJECT PATH}'
ex_path= project_path + "/Excel/"
tally_file = ex_path+'Tally.xlsx'
rawdata_file = ex_path+'rawdata.xlsx'

tally=pa.read_excel(tally_file, "Tally", usecols=['Token',  'Valid', 'BankCode', 'Size', 'Region', 'Type'])  
tally = tally[(tally['Valid']=='Y') | (tally['Valid']=='[Y]')]
rawdata = pa.read_excel(rawdata_file,'data', skiprows=[1,2])

field_list = pa.read_excel(rawdata_file, "fields", usecols=['code','section', 'type', 'field', 'question'])
field_list = field_list.loc[field_list['type'] == 'Normal']  # using normal type fields, excluding banks 

sections = ['Tally', 'Info', 'Cash', 'Funding', 'ESG', 'Digital', 'Risk', 'Supply Chain', 'RMB', 'General' ] # Sections to be calculated, refer the field_list


breakdown_bys = ['Size', 'Region', 'Type'] # break down by these fields, must be from Tally


output=overall_calculations(rawdata, field_list, tally, sections, breakdown_bys)


for out in output:
    olddf=pa.read_excel(oldresult_file, out, usecols=['AA-Question',  'AB-Answers', 'ZZ-Result 2023', 'ZZ-Result 2022'])

    output[out] =  pa.merge(output[out], olddf, on=['AA-Question',  'AB-Answers'])

    




