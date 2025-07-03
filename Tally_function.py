import pandas as da
import math
import openpyxl

def lookup_df(df, search, val, re_col):
    df[search].astype(str)
    if not isinstance(val, str):
        val = str(val)
        val = val.strip().lower()
    filtered_df = df.loc[df[search] == val]
    if not filtered_df.empty:
        return filtered_df[re_col].iloc[0]
    else:
        return None

def lookup_df_int(df, search, val, re_col):
    #df[search].astype(str)
    #if not isinstance(val, str):
    #    val = str(val)
     #   val = val.strip().lower()
    filtered_df = df.loc[df[search] == val]
    if not filtered_df.empty:
        return filtered_df[re_col].iloc[0]
    else:
        return None        

#function for calculating how complete a section is, it returns % of total questions

def count_ans(row, key, max):
    i = 1
    answer = 0
    while i <= max: 
        val = row[key + str(i)]
        if da.isna(val) is False:
           answer = answer + 1
        i = i + 1
    return math.ceil(answer / max * 100)


def rank_to_points(rank):
    point_dict = {1: 15, 2: 14, 3: 13, 4: 12, 5: 11}
    return point_dict.get(rank, 10)
    
   
level_score = {
       'extremely satisfied':5,
       'very satisfied':4,
       'satisfied':3,
       'dissatisfied':2,
       'very dissatisfied':1
}

# def count_column_values(path, sheet, column_letter):
  #  workbook = openpyxl.load_workbook(path)
  # sheet = workbook[sheet]
  # column = sheet[column_letter]
  # count = 0
  # for cell in column:
  # if cell.value is not None:
  # count += 1
  # return count
  
def count_col(column, key):
    y = 4
    ans = 0
    val = column[key + str(y)]
    if da.isna(val) is True:
        ans = ans + 1
    y = y + 1
    return ans

def count_votes(voting_records, voter_appID, candidate_appID, project,  votingtype):
    condition = (voting_records['voter_app_id'] == voter_appID) & \
                (voting_records['can_app_id'] == candidate_appID) & \
                (voting_records['project'] == project)
    return len(voting_records[condition & (voting_records['votingtype'] == votingtype)])