#!/usr/bin/env python
# coding: utf-8

# # Question 3

# In[1]:


import pandas as pd
from datetime import datetime
import string
import warnings
import re
warnings.filterwarnings("ignore")


# In[2]:


sample_claims = pd.read_csv('sample_claims.csv')
sample_claims


# In[3]:


valid_cpt = pd.read_csv('valid_cpt_codes.csv')
valid_icd = pd.read_csv('valid_icd_10_codes.csv')


# ## Test 1 : Checking for Null values in Non-nullable columns for all tables

# In[4]:


#function that returns columns which contain null values 
def check_na(sample_claims, not_nullable_cols_list):
    res = []
    for cols in not_nullable_cols_list:
        if len(sample_claims[sample_claims[cols].isna()].index) > 1:
            res.append(cols)
    return res


# In[5]:


#sample_claims columns
not_nullable_cols_list = ['patient_id', 'claim_id', 'procedure_code', 'date_service', 'date_received']
cols_with_nulls = check_na(sample_claims, not_nullable_cols_list)
print(cols_with_nulls)


# In[6]:


#valid_icd
not_nullable_cols_list = ['code']
cols_with_nulls = check_na(valid_icd, not_nullable_cols_list)
print(cols_with_nulls)


# In[7]:


#valid_cpt
not_nullable_cols_list = ['code', 'short_description']
cols_with_nulls = check_na(valid_cpt, not_nullable_cols_list)
print(cols_with_nulls)


# ### Result: columns 'patient_id', 'claim_id', 'procedure_code' and 'date_service' have null fields in sample_claims table while they are non-nullable columns. valid_icd_10_codes and valid_cpt_codes do not have any null values

# ## Test 2 : Checking if Claim_Ids are unique 

# In[8]:


print(len(sample_claims[sample_claims.duplicated(subset=['claim_id'])].index))


# ### Result:  we have 28 non-unique claim-ids. I have not handled this case in pre-processing because for questions 1 and 2, we do not require claim ids but it could be an issue for other scenarios. So this can be considered as a data quality issue.

# ## Test 3 : Check datatypes for integer columns - claim_id, procedure_code and code

# In[9]:


#this function returns an error message if columns are not integer
def check_dtypes(df, col):
    cnt = "All the values are integers!"
    try:
        df[[col]].apply(pd.to_numeric, errors='raise')
    except:
        cnt = "Found a datatype mismatch!"
    return cnt


# In[10]:


#procedure_code
print(check_dtypes(sample_claims, 'procedure_code'))


# In[11]:


#claim_id
print(check_dtypes(sample_claims, 'claim_id'))


# In[12]:


#code from valid_cpt_codes
print(check_dtypes(valid_cpt, 'code'))


# ### Result: procedure_code column does not have INT values

# ## Test 4 : Check for date dataypes - if date_service, date_received are logical

# In[13]:


#this function checks if columns are of datetime type
def check_dates_logical(df, col):
    cnt = "All the values are in datetime format!"
    try:
        df[[col]].apply(pd.to_datetime, errors='raise')
    except:
        cnt = "Found an illogical date value!"
    return cnt


# In[14]:


print(check_dates_logical(sample_claims, 'date_service'))


# In[15]:


print(check_dates_logical(sample_claims, 'date_received'))


# ### Result: date_service has illogical date values/non-datetime format 

# ## Test 5 : date values are chronological trending is consistent i.e. date_service should be prior to date_received

# In[16]:


#convert date_service to datetime type, exclude records that are not in the datetime format (mm/dd/yyyy)
#delete na values since date_service is non nullable 
sample_claims['date_service'] = pd.to_datetime(sample_claims['date_service'], errors='coerce')
sample_claims = sample_claims.dropna(subset=['date_service'])


# In[17]:


#date_received column to datetime
sample_claims['date_received'] =  pd.to_datetime(sample_claims['date_received'], infer_datetime_format=True)


# In[18]:


#this function checks if date_service is prior to date_received
def check_dates_chro(col1, col2, df):
    cnt = "All the values are in logical, with consistent chronological trending!"
    try:
        df[col1] < df[col2]
    except:
        cnt = "Date values are illogical, with NO consistent chronological trending!"
    return cnt


# In[19]:


print(check_dates_chro(sample_claims,'date_service','date_received'))


# ### Result: sample_claims has records that do not have chronologically consistent date values.

# ## Test 6 : Check if claims received belong to Jan - 2021 

# In[20]:


len(sample_claims[~((sample_claims.date_received.dt.month == 1) & (sample_claims.date_received.dt.year == 2021))])


# ### Result: Sample claims contains 126 records of claims that do not belong to jan 2021.

# ## Test 7 : All standardized codes are valid based on given reference material

# In[21]:


#this function checks if procedure codes are valid
def check_valid_code(col1, col2, df1, df2):
    cnt = "All procedure codes are valid"
    try:
        df1[col1] in df2[col2]
    except:
        cnt = "Invalid procedure codes!"
    return cnt


# In[22]:


print(check_valid_code('procedure_code', 'code', sample_claims, valid_cpt))


# In[23]:


#Clean the diagnosis_code column: remove punctuation
sample_claims['diagnosis_codes'] = sample_claims['diagnosis_codes'].str.replace('.','')


# In[24]:


#since multiple diagnoses codes are separated by a '^', I have seperated the codes by the delimiter, exploded the list to 
#single records for each diagnosis code
sample_claims['diagnosis_codes']= sample_claims['diagnosis_codes'].str.split("^")
#explode the new column
sample_claims = sample_claims.explode('diagnosis_codes').fillna('')
#sample_claims


# In[25]:


print(check_valid_code('diagnosis_codes', 'code', sample_claims, valid_icd))


# ### Result: sample claims contains invalid procedure codes and invalid diagnosis codes as per the reference valid codes given 
