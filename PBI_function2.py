import pandas as pd

#simon note for test
def rank_to_points(rank: int)->int:  
    # return the points according to the rank (rank 1 is 3 points...etc)  
    points_mapping = {1: 3, 2: 2}
    return points_mapping.get(rank, 1)  


def make_unique(data: pd.DataFrame, field: str)-> list:
    # This function returns the unique value(s) in the colmun in a form of a list
    # This function will also handle if it is a ranking question 
    # Ranking question appear as line break in each cell

    # Check if each column is completely empty
    is_empty = data.isnull().all()

    # Iterate over the columns and fill in "No Answers" where the column is empty, because if the whole col is empty the split does not work
    for col in data.columns:
        if is_empty[col]:
            data.fillna({col:"No Answer"}, inplace=True)  
  
    data[field] = data[field].str.split('\n')   # splite the value in by line break (if any)
    data = data.explode(field) # make it into a list,  note, the 1st element is the first choice, ....etc
    data = data.reset_index(drop=True)

    # Remove missing values and duplicates from the field column
    rtn = data[field].dropna().drop_duplicates()  # without empty and duplicatiom

    return rtn.values.tolist()  # return the results in a list


def count_multi(data: pd.DataFrame, field)->int:  # count the number of non empty cell in a col, i.e return the number of ticks in the  field
    rtn = (data[field].notna() & (data[field] != 'No Answer')).sum()
    return rtn

def count_multi_points(data: pd.DataFrame, field: str)->int:  # count the number of non empty cell in a col, i.e return the number of ticks in the  field
    data[field] = pd.to_numeric(data[field], errors='coerce')
    count_greater_than_one = ((data[field].notna()) & 
                           (data[field] != 'No Answer') & 
                           (data[field] > 1)).sum()
    
    rtn = data[field][data[field].notna() & (data[field] != 'No Answer')].mean() * 20
    return  rtn
def count_single(data: pd.DataFrame, field: str)->dict:

    # return the number for each answer option 
    # if it is a ranking question, return the points for each option
    options = make_unique(data, field)  # see the function above, this will give the answers options (i.e Yes or No,)
    fulldatas = data[field].values.tolist() # get all the data in the col and make it into a list
    fulldatas = [x for x in fulldatas if str(x) != 'nan'] # take out all the empty answers (as no need to count)
    ranking_question = any(len(sublist) > 1 for sublist in fulldatas)  # if the sublist of fulldates contain more then one element, then it is a ranking question
    
    calculation = {}  # get ready to store the calculation results          
    

    i = 0          
    for fulldata in fulldatas:  # looping the fulldatas  eg .['Yes','Yes','No', 'Yes'....etc]
        fulldata = fulldata[:3]
        for option in options: #looping the unique option e.g['Yes' or 'No']
            
                if option in fulldata: 
                    if ranking_question is True:  #if ranking question, pass it to rank to points for calculation of rank         
                                
                            calculation[i] = {
                                    'ans':option,
                                    'points':rank_to_points(fulldata.index(option)+1),   #+1 because the first element is always 0
                                    'rank' : 'rank '+str(fulldata.index(option)+1)
                                                                            }
                    else:  #if not, set set points = 1, for counting the answer
                        
                        calculation[i] = {
                                    'ans':option,
                                    'points':1,    # if not a ranking question, assign point 1 for counting
                                    'rank' : 'rank 1' # let it be rank 1 
                                    
                            }
                    
                i = i +1             
          
    df = pd.DataFrame(calculation).T   # Turn it intoa dataframe 

    pointsdf = df.groupby('ans')['points'].sum().reset_index()  # calcuating the points (if not ranking question, this will be the number of counts)
 
   
    rankdf = df.pivot_table(index='ans', columns='rank', aggfunc='size', fill_value=0).reset_index()  # using pivot table to count the numbers of rank 1, 2 and 3 (for non ranking questions always rank 1)
    pointsdf = pointsdf.merge(rankdf, how="left", on='ans') #merge the two, so now we have a dataframe with points, rank 1, rank 2, rank 3 (or rank 4, 5 ...etc)
    
    rtn = {}  #turn this dataframe back to a dictionary and return the results
    for index, row in pointsdf[0:len(pointsdf)].iterrows():
        rtn[row['ans']] = { 'points' : row['points'], 
                            'rank 1' : row['rank 1'],
                            'rank 2' : row['rank 2'] if 'rank 2' in row else '0',  #if not ranking question, then no rank 2 and rank 3, so set to 0
                            'rank 3' : row['rank 3'] if 'rank 3' in row else '0',
                            'rank_weight' : 3 if  ranking_question is True else 1
                           }                                               
  
    return rtn        

def total_answers(data: pd.DataFrame, field: str)->int: # check how many respondents answered that question
    columns = field['code'].tolist() # some question only have one col "Yes" /"No", some have more then one col e.g multiple choice question, but does not matter, it will work
    data['Total'] = data.apply(lambda row: 0 if all(pd.isna(row[col]) or row[col] == "No Answer" for col in columns) else 1, axis=1) #Add a new col "total" and set it to 1 if any of the cell in the row is not empty
    value_counts = data['Total'].value_counts()  
    if 1 in value_counts:
        return value_counts[1]
    else:
        return 1000000000000   # should be 0, but it has problem if divided by 0, so lets make it super big number, and when it is divided, it will be 0

def df_values_tolist(data: pd.DataFrame, field: str)-> list:
    column_values = data[field].unique().tolist()
    return column_values    
    


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
                if(question=='Scores1'):
                    score_v = count_multi_points(rawdata, row['code'])
                else:
                    score_v =  count_multi(rawdata, row['code'])
                     
                
                outputdata.append({
                                
                                'QNo' : row['QNo'],
                                'AA-Question': question,
                                'AB-Answers': row['field'],
                                'Scores /  No. '+str(tablefield)+' '+str(value): score_v, # therefore we have to count the ticks in each col
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
                                    
                                    'QNo' : row['QNo'],
                                    'AA-Question': question,
                                    'AB-Answers': counta,
                                    'Scores /  No. '+str(tablefield)+' '+str(value): countas[counta]['points'],
                                    'Percent (%) '+str(tablefield)+' '+str(value): round((float(countas[counta]['points']) / (total_answer * countas[counta]['rank_weight']))*100,0),
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
                result_fields['Total Answered '+tablefield+' '+value] = None
        
        combined_data = []

        for item in finaldata['all']:
            QNo = item['QNo']
            question = item['AA-Question']
            answer = item['AB-Answers']
        
            combined_item = {
                'QNo': QNo,
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
                            combined_item['Total Answered '+tablefield+' '+ cat] = sub_item['Total Answered '+tablefield+' '+ cat]
                            break
                                         
            combined_data.append(combined_item)

        data1 = pd.DataFrame(combined_data)
        data1['Scores /  No. '+tablefield+' '+ cat] = data1['Scores /  No. '+tablefield+' '+ cat].astype(float)

        output[section]=data1

  
    
    return output            