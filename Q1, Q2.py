#!/usr/bin/env python
# coding: utf-8

# # Data Operations Analyst Assessment - Q1, Q2

# #### Q1a:  What are the top 5 most common valid procedure codes?
# #### Answer: [88175, 87491, 87591, 87798, 85018]
# #### Q1b: How many patients are associated with at least one of those procedures?
# #### Answer: 57
# #### Q2: What are the top 5 most common valid diagnosis codes?
# #### Answer: ['Z113', 'E559', 'Z01419', 'Z3481', 'N926']

# ### 1. Importing Libraries

# In[1]:


import pandas as pd
from datetime import datetime
import string
import warnings
warnings.filterwarnings("ignore")


# ### 2. Read all the csv files into pandas dataframes

# In[2]:


sample_claims = pd.read_csv('sample_claims.csv')
sample_claims


# In[3]:


valid_cpt = pd.read_csv('valid_cpt_codes.csv')
valid_cpt


# In[4]:


valid_icd = pd.read_csv('valid_icd_10_codes.csv')
valid_icd


# ### 3. Data preprocessing - check for data anomalies, perform data cleaning

# #### patient_id

# In[5]:


#drop rows where patient_id is NA since patient_id is non nullable 
#- cannot assume data belongs to the same patient/different patients 
sample_claims = sample_claims.dropna(subset=['patient_id'])


# #### claim_id

# In[6]:


#replace NA values of claim_id with 0, to not miss out on valuable info from other columns (cpt and icd10 codes)
sample_claims['claim_id'] = sample_claims['claim_id'].fillna(0)


# #### procedure_code

# In[7]:


#drop na values of procedure_code - cannot assume same/diff values
#-is non nullable 
sample_claims[['procedure_code']] = sample_claims[['procedure_code']].apply(pd.to_numeric, errors='coerce')
sample_claims = sample_claims.dropna(subset=['procedure_code'])


# #### date_service

# In[8]:


#convert date_service to datetime type, exclude records that are not in the datetime format (mm/dd/yyyy)
#delete na values since date_service is non nullable 
sample_claims['date_service'] = pd.to_datetime(sample_claims['date_service'], errors='coerce')
sample_claims = sample_claims.dropna(subset=['date_service'])


# #### date_received

# In[9]:


#date_received column to datetime
sample_claims['date_received'] =  pd.to_datetime(sample_claims['date_received'], infer_datetime_format=True)


# In[10]:


#filter jan 2021 claims
sample_claims = sample_claims[(sample_claims.date_received.dt.month == 1) & (sample_claims.date_received.dt.year == 2021)]
#drop na values - date_received is non nullable
sample_claims = sample_claims.dropna(subset=['date_received'])


# ### 4. Cast columns as datatypes mentioned in the table defenition 

# In[11]:


sample_claims = sample_claims.astype({'patient_id': 'str'})
sample_claims = sample_claims.astype({'claim_id': 'int32'})
sample_claims = sample_claims.astype({'diagnosis_codes': 'str'})
sample_claims = sample_claims.astype({'procedure_code': 'int32'})


# In[12]:


#Verify the dtypes
sample_claims.dtypes


# ### 5. Question 1a - What are the top 5 most common valid procedure codes?
# ### Answer: [88175, 87491, 87591, 87798, 85018]

# #### Extract records from sample_claims that have a valid procedure code by creating an inner join with valid_cpt dataframe

# In[13]:


valid_claims_pro = sample_claims.merge( valid_cpt, how='inner', left_on='procedure_code', right_on='code')


# In[14]:


valid_claims_pro


# #### Generate a list that identifies the top 5 most commonly used procedure_code from valid_claims_pro dataframe

# In[15]:


valid_claims_pro['procedure_code'].value_counts()[:5].index.tolist()


# In[16]:


#view top 5 most commonly occuring procedure codes with its respective frequency
valid_claims_pro['procedure_code'].value_counts()[:5].to_dict()


# ### 5. Question 1b - How many patients are associated with at least one of those procedures?
# ### Answer: 57

# #### Extract patient_id, procedure_code from valid_claims_pro into a new df, 

# In[17]:


df = valid_claims_pro[['patient_id', 'procedure_code']]


# #### Group by procedure_code, sort by size desc 

# In[18]:


df1 = df.groupby('procedure_code')


# In[19]:


df2 = df.groupby(['procedure_code']).size().sort_values(ascending=False)


# In[20]:


df2


# #### The following block of code results in the count of unique patient ids associated with any of the top 5 valid procedure codes

# In[21]:


#create empty set
s1 = set()

# a loop that iterates through the top 5 most commonly used procedure codes from df2
for i,r in df2.head(n=5).iteritems():
    
    #get patient ids of each group
    temp = df1.get_group(i)
    
    #inner loop iterates through patient ids of each group, adds to set(allows only unique additions)
    for j in temp.patient_id:
        s1.add(j)
        
#print count of the set        
print(len(s1))
    


# ### Question 2 - What are the top 5 most common valid diagnosis codes?
# ### Answer: ['Z113', 'E559', 'Z01419', 'Z3481', 'N926']

# #### Clean the diagnosis_code column: remove punctuation

# In[22]:


sample_claims['diagnosis_codes'] = sample_claims['diagnosis_codes'].str.replace('.','')


# #### Split the codes by the delimiter ^ 

# In[23]:


sample_claims['diagnosis_codes']= sample_claims['diagnosis_codes'].str.split("^")


# In[24]:


sample_claims


# #### Duplicate records such that a record exists for each diagnosis code 

# In[25]:


#explode the new column
sample_claims = sample_claims.explode('diagnosis_codes').fillna('')


# In[26]:


sample_claims


# #### Extract records from sample_claims that have a valid diagnosis code by creating an inner join with valid_icd dataframe

# In[27]:


valid_claims_dia = sample_claims.merge( valid_icd, how='inner', left_on='diagnosis_codes', right_on='code')
valid_claims_dia


# #### Generate a list that identifies the top 5 most commonly used diagnosis_codes from valid_claims_dia dataframe

# In[28]:


valid_claims_dia['diagnosis_codes'].value_counts()[:5].index.tolist()


# In[29]:


#view top 5 most commonly occuring diagnosis codes with its respective frequency
valid_claims_dia['diagnosis_codes'].value_counts()[:5].to_dict()

