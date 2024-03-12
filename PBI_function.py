import pandas as pd

def rank_to_points(rank: int)->int:  
    if rank == 1:   # rank one get 3 points...etc
        return 3
    elif rank == 2:
        return 2
    else:
        return 1    

def count_multi(data: pd.DataFrame, field: str)->int:  # count the number of non empty cell in a col, i.e return the number of ticks in the  field
    rtn = (data[field].notna() & (data[field] != 'No Answer')).sum()
    return rtn

def count_single(data: pd.DataFrame, field: str)->dict:
    options = make_unique(data, field)
    fulldatas = data[field].values.tolist()
    fulldatas = [x for x in fulldatas if str(x) != 'nan']
    ranking_question = any(len(sublist) > 1 for sublist in fulldatas)  # if the sublist of fulldates contain more then one element, then it is a ranking question
    calculation = {}          
    
    i = 0
    for fulldata in fulldatas:
        
        for option in options:
            if option in fulldata: 
                if ranking_question is True:  #if ranking question, pass it to rank to points for calculation of rank         
                            
                        calculation[i] = {
                                'ans':option,
                                'points':rank_to_points(fulldata.index(option)+1),   #+1 because the first element is always 0
                                'rank' : 'rank '+str(fulldata.index(option)+1)                       }
                else:  #if not, set set points = 1, for counting the answer
                    
                       calculation[i] = {
                                'ans':option,
                                'points':1,
                                'rank' : 'rank 1'
                        }
                
            i = i +1             
          
    df = pd.DataFrame(calculation).T  
    pointsdf = df.groupby('ans')['points'].sum().reset_index() 
    rankdf = df.pivot_table(index='ans', columns='rank', aggfunc='size', fill_value=0).reset_index()
    pointsdf = pointsdf.merge(rankdf, how="left", on='ans')
    
    rtn = {}
    for index, row in pointsdf[0:len(pointsdf)].iterrows():
        rtn[row['ans']] = { 'points' : row['points'], 
                            'rank 1' : row['rank 1'],
                            'rank 2' : row['rank 2'] if 'rank 2' in row else '0',
                            'rank 3' : row['rank 3'] if 'rank 3' in row else '0'
                          }                                               
  
    return rtn        

def total_answers(rawdata: pd.DataFrame, fields: str)->int: # check how many respondents answered that question
    columns = fields['code'].tolist() # some question only have one col "Yes" /"No", some have more then one col e.g multiple choice question, but does not matter, it will work
    rawdata['Total'] = rawdata.apply(lambda row: 0 if all(pd.isna(row[col]) for col in columns) else 1, axis=1) #Add a new col "total" and set it to 1 if any of the cell in the row is not empty
    value_counts = rawdata['Total'].value_counts()
    if 1 in value_counts:
        return value_counts[1]
    else:
        return 1000000000000   # should be 0, but it has problem if divided by 0, so lets make it super big number, and when it is divided, it will be 0

def df_values_tolist(data: pd.DataFrame, field: str)-> list:
    column_values = data[field].unique().tolist()
    return column_values    
    
def make_unique(data: pd.DataFrame, field: str)-> list:
    # Check if each column is completely empty
    is_empty = data.isnull().all()
    # Iterate over the columns and fill in "No Answers" where the column is empty, because if the whole col is empty the split does not work
    for col in data.columns:
        if is_empty[col]:
            data.fillna({col:"No Answer"}, inplace=True)  
  
    data[field] = data[field].str.split('\n')
    data = data.explode(field)
    data = data.reset_index(drop=True)

    # Remove missing values and duplicates from the field column
    rtn = data[field].dropna().drop_duplicates()

    return rtn.values.tolist()

def cal_summary(field_list: pd.DataFrame, rawdata: pd.DataFrame, tally: pd.DataFrame, section: list, tablefield: str, value: str) -> pd.DataFrame:

    rawdata = tally.merge(rawdata, how="left", on=["Token", "Token"])  #marge tally with rawdata
        
    if tablefield == 'all': # don't do anything to raw data, because we want to calculate ALL respondents
        rawdata = rawdata
    else:  # fileter rawdata according to table field to get the record we want only, so we only want "Listed Comapnies"   
        rawdata = rawdata[rawdata[tablefield] == value]
  
    #filter the field_list to get the fields for the section we want only.  e.g "Cash", "Funding" 
    
    field_list = field_list.loc[field_list['section'] == section]  
    if len(field_list)==0:
        print ('Empty question list, check if this section exist '+str(section))
        exit()
    
    questions = field_list['question'].drop_duplicates()  # get q question dataframe with out duplications
  
    outputdata= []

    for question in questions:  # for each question, lets calculate the answers
        
        fields = field_list.loc[field_list['question'] == question]  #get the fields for that question
        
        total_answer = total_answers(rawdata, fields)  #calculating total answers (see total_answer function)
      
        for index, row in fields[0:len(fields)].iterrows():            
            if row['field']!=question:  # if question is not the same as field, that means the answers have more then one col, i.e mutiple choise question   
                outputdata.append({
                                
                                'AA-Question': question,
                                'AB-Answers': row['field'],
                                'Scores /  No. '+str(tablefield)+' '+str(value): count_multi(rawdata, row['code']), # therefore we have to count the ticks in each col
                                'Percent (%) '+str(tablefield)+' '+str(value): round((float(count_multi(rawdata, row['code'])) / total_answer)*100,0), #divided by total_answer to get the %
                                'Rank 1 '+str(tablefield)+' '+str(value) : '0',
                                'Rank 2 '+str(tablefield)+' '+str(value) : '0',
                                'Rank 3 '+str(tablefield)+' '+str(value) : '0',
                                'Total Answered '+str(tablefield)+' '+str(value):total_answer
                            })
            else: # if question is same a field, it is a Yes/No question, single choice question or ranking question
                countas = count_single(rawdata, row['code'])   # return the number for each choices or score (if ranking question)
             
                for counta in countas:
                    
                    outputdata.append({
                                    
                                    'AA-Question': question,
                                    'AB-Answers': counta,
                                    'Scores /  No. '+str(tablefield)+' '+str(value): countas[counta]['points'],
                                    'Percent (%) '+str(tablefield)+' '+str(value): round((float(countas[counta]['points']) / total_answer)*100,0),
                                    'Rank 1 '+str(tablefield)+' '+str(value) : countas[counta]['rank 1'],
                                    'Rank 2 '+str(tablefield)+' '+str(value) : countas[counta]['rank 2'],
                                    'Rank 3 '+str(tablefield)+' '+str(value) : countas[counta]['rank 3'],
                                    'Total Answered '+str(tablefield)+' '+str(value):total_answer
                                }) 
    return outputdata

def overall_calculations(rawdata: pd.DataFrame, field_list: pd.DataFrame, tally: pd.DataFrame, sections: list, breakdown_bys: dict) -> dict:
      
    tablefields =    {'all':['all']}  #this is the fields that need to break up, first one is all, i.e all data
    # for each of the fields that needs break down, get its value from tally, make it unique, and return as list, to do that we use db_values_tolist function
    for filter_by in breakdown_bys:
            tablefields[filter_by]=df_values_tolist(tally, filter_by)  
      
    # at this point tablefields is a dictionary with fields need to be break down 
    # start calculations section by section

    output = {}

    for section in sections:
        result_fields ={}  #this is the col title of the final results excel, depends on  the number of filters
        finaldata ={} # this is to store the final results
        
        # Now, for each fields, lets calculate the results for all the qestions
        for tablefield in tablefields:  # lopping for all filters, i.e all, then Type, then Region
            values = tablefields[tablefield]
            for value in values: # lopping each value e.g "Listed companies"
                finaldata[value] = cal_summary(field_list, rawdata, tally, section, tablefield, value) #calculating the answers for for each value e.g "Listed companies" 
                
                result_fields['Scores /  No. '+tablefield+' '+value] = None
                result_fields['Percent (%) '+tablefield+' '+value] = None
                result_fields['Rank 1 '+tablefield+' '+value] = None
                result_fields['Rank 2 '+tablefield+' '+value] = None
                result_fields['Rank 3 '+tablefield+' '+value] = None
        
        combined_data = []

        for item in finaldata['all']:
            question = item['AA-Question']
            answer = item['AB-Answers']
        
            combined_item = {
                'AA-Question': question,
                'AB-Answers': answer}

            combined_item.update(result_fields)       
            
            for tablefield in tablefields:   
                cats = tablefields[tablefield]
            
                for cat in cats:
                        
                    for sub_item in finaldata[cat]:
        
                        if sub_item['AA-Question'] == question and sub_item['AB-Answers'] == answer:
                            combined_item['Scores /  No. '+tablefield+' '+ cat] = sub_item['Scores /  No. '+tablefield+' '+ cat]
                            combined_item['Percent (%) '+tablefield+' '+ cat] = sub_item['Percent (%) '+tablefield+' '+ cat]
                            combined_item['Rank 1 '+tablefield+' '+ cat] = sub_item['Rank 1 '+tablefield+' '+ cat]
                            combined_item['Rank 2 '+tablefield+' '+ cat] = sub_item['Rank 2 '+tablefield+' '+ cat]
                            combined_item['Rank 3 '+tablefield+' '+ cat] = sub_item['Rank 3 '+tablefield+' '+ cat]
                            break
                                         
            combined_data.append(combined_item)

        data1 = pd.DataFrame(combined_data)
        data1['Scores /  No. '+tablefield+' '+ cat] = data1['Scores /  No. '+tablefield+' '+ cat].astype(float)
        
        output[section]=data1
              
    
    return output            