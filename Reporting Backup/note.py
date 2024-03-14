#For  "Copy"  to PowerBI, do not run this file

# sections = ['Tally', 'Cash', 'Funding', 'ESG', 'Digital', 'Risk', 'Supply Chain', 'RMB', 'General' ] # Sections to be calculated, refer the field_list


import sys
sys.path.insert(1, '//192.168.0.209/share-editorial-research/# Treasury Review/Treasury Review 2024/Reporting/Overall') 

import summaryBi as da
A_tally = da.output['Tally']
A_info = da.output['Info']
B_cash = da.output['Cash']
C_funding = da.output['Funding']
D_esg = da.output['ESG']
F_digital = da.output['Digital']
G_risk = da.output['Risk']
H_supply_chain = da.output['Supply Chain']
I_rmb = da.output['RMB']
J_general = da.output['General']



# Note for data person

# 1. Tally's Y column should labled as "Valid"  not "Legit"
# 2. The break down column (e.g Location) in tally must be all filled in 
# 3. The filename of the tally should be Tally.xlsx and the name of the sheet should be called "Tally"
# 4. The filename of the rawdata should be rawdata.xlsx and the name of the sheet should be called "data" and the fields sheet should be called "fields"
# 5. Both tally.xlsx and rawdata.xlsx should be inside the working folder called "Excel"
