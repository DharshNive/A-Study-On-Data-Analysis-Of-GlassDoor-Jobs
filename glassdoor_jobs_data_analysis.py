# -*- coding: utf-8 -*-
"""Glassdoor Jobs Data Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1muEE_3ObkjUdRM0HscIwMC9NCSF1liq3
"""

!pip install plotly
#free and open-source graphing library for Python.

!pip install seaborn
#library for making statistical graphics in Python

!pip install nltk
# Natural Language Toolkit, is a Python package that you can use for NLP.
# A lot of the data that you could be analyzing is unstructured data and contains human-readable text.

!pip install gensim
#Python library for representing documents as semantic vectors

!pip install yellowbrick
# Python project that extends the scikit-learn API with visual analysis and diagnostic tools.

# Commented out IPython magic to ensure Python compatibility.
#importing libraries
import pandas as pd
import numpy as np
import nltk
#Pandas and NumPy libraries, which are widely used for data manipulation and analysis.
#The nltk library is imported for natural language processing tasks.

import gensim #topic modeling and document similarity analysis
import gc # garbage collection
import string #string manipulation
import re #regular expressions.
import yellowbrick
#provides visualizations and diagnostic tools for machine learning tasks.

#import plotly.plotly as py
import plotly.graph_objs as go
#from plotly.offline import iplot, init_notebook_mode
from plotly.subplots import make_subplots
# The plotly library for creating interactive and high-quality visualizations.
# The go module provides access to the graph objects, while make_subplots is used to create subplots.

#cufflinks.go_offline(connected=True)
#init_notebook_mode(connected=True)
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

# The matplotlib.pyplot and seaborn libraries are imported for data visualization purposes.
# The line %matplotlib inline is a Jupyter Notebook magic command that ensures the plots are displayed inline within the notebook.

df_ny = pd.read_csv('Cleaned_DS_Jobs.csv')
df_sf = pd.read_csv('Cleaned_DS_Jobs.csv')
df_tx = pd.read_csv('Cleaned_DS_Jobs.csv')
df_wa = pd.read_csv('Cleaned_DS_Jobs.csv')

# The code reads data from the CSV file 'Cleaned_DS_Jobs.csv'
# creates four separate DataFrames (df_ny, df_sf, df_tx, and df_wa) that hold the same data.
# The purpose of creating separate DataFrames might be to analyze or
# compare job data for different locations (NY, SF, TX, WA) within the cleaned dataset.

data_df = pd.concat([df_ny , df_sf , df_tx,df_wa] , axis = 0 , ignore_index = True)
#Concatenating the data files

del df_ny , df_sf , df_tx ,df_wa
gc.collect()
# better memory management and potentially improving the performance of the program.

#Beginning the Cleaning and analysis of the data
data_df.head()

data_df.tail(5)

#Return a tuple representing the dimensionality of the DataFrame.
#Tuple of array dimensions.
data_df.shape

#Information of the data
data_df.info()

#First let's convert min_salary and max_salary columns to int
data_df['min_salary'] = data_df['min_salary'].apply(lambda x : int(x))
data_df['max_salary'] =data_df['max_salary'].apply(lambda x : int(x))

#While collecting the data if no salary is found I replaced the value by -1 so lets store that data in different data frame
index_missing = data_df[(data_df['min_salary'] == -1)].index
test_df = data_df.iloc[index_missing, :].reset_index(drop = True)
data_df.drop(index_missing , axis = 0 , inplace = True)
data_df = data_df.reset_index(drop = True)
#We will use this data as our test set.

#Now we have train and test set there are duplicates in the data
#This is because our scraper was not perfect and could have a assimilated multiple entries
cols = [col for col in data_df.columns if col not in ['Day' , 'Month']]
#For training data
train_series = data_df.duplicated(cols , keep = 'first')
data_df =data_df[~train_series].reset_index(drop = True)
test_series = test_df.duplicated(cols , keep = 'first')
test_df = test_df[~test_series].reset_index(drop = True)

#Unique Job Title
print(data_df['Job Title'].unique())

#the avg minimal salaries for job titles
import numpy as np
states = data_df['Job Title'].unique().tolist()
fig = go.Figure()
min_sal =  data_df.groupby('Job Title')['min_salary']
max_sal =  data_df.groupby('Job Title')['max_salary']
fig.add_trace(go.Bar(x = states,
                    y = min_sal.mean(),
                    name = 'min salary' , marker_color = 'Magenta'))

fig.add_trace(go.Bar(x = states,
                    y = max_sal.mean(),
                    name = 'max salary' , marker_color = 'SkyBlue'))
fig.update_layout(template = 'ggplot2', barmode = 'group')
fig.show()

#Let's see the job title representation in graphical manner
day_fig = go.Figure([go.Bar(x = data_df['Job Title'].value_counts().index.to_list() ,
                    y = data_df['Job Title'].value_counts().to_list() , marker_color = 'skyblue')])
day_fig.update_layout(template = 'ggplot2' , title = 'JOB TITLE REPRESENTATION')

#Now's let's explore the industry column
#This column has Nan Values

ind = data_df[~data_df['Industry'].isnull()]
print(f"Number of Unique Industries : {ind.Industry.nunique()}")

#Name of the industries
ind.Industry.value_counts()

#top 8 industries with max number of jobs

fig = go.Figure()
fig.add_traces(go.Pie(values = ind.Industry.value_counts()[:8].to_list(),
                    labels= ind.Industry.value_counts()[:8].index.to_list(),
                    name = 'Industry',textposition = 'inside' , textinfo = 'percent+label'))
fig.update_layout(template = 'plotly_white',title = 'Industries with most number of Data Science Related jobs' )
fig.show()

#Lets take a look at minimal average salary for the top 8 industries
fig = go.Figure()
fig.add_trace(go.Bar(x = ind.groupby("Industry")['min_salary'].mean().to_list(),
y = ind.groupby("Industry")['min_salary'].mean().index.to_list(), marker_color = 'goldenrod',
orientation = 'h' , name = "Min Avg Salary"
))
fig.add_trace(go.Bar(x = ind.groupby("Industry")['max_salary'].mean().to_list(),
y = ind.groupby("Industry")['max_salary'].mean().index.to_list(), marker_color = 'deepskyblue'
,orientation = 'h' ,name = "Max Avg Salary"))
fig.update_layout( template = 'plotly_dark',
    title = 'Minimal And Maximal Average Annual Salaries according to industries' ,barmode = 'group')
fig.show()

#Now let's explore companies

print(f"Number of Unique Company Names : {data_df['Company Name'].nunique()}")

# Companies which have highest number of job postings

fig = go.Figure()
fig.add_trace(go.Bar(y = data_df['Company Name'].value_counts()[:20].to_list(),
x= data_df['Company Name'].value_counts()[:20].index.to_list(),
marker_color = 'deepskyblue' , name = "Company"))
fig.update_layout(title= 'Companies with Max Number of Job Postings related to data science',
                template = 'plotly_dark')
fig.show()

#Let's take a look at Avg Minimal and Maximal salaries for companies
def Plot_Company_salaries(companies,title):
    fig = go.Figure()
    min_sal = []
    max_sal = []
    for company in companies:
        min_sal.append(data_df[data_df['Company'] == company]['Min_Salary'].mean())
        max_sal.append(data_df[data_df['Company'] == company]['Max_Salary'].mean())



    fig.add_trace(go.Bar(x = min_sal ,y = companies , marker_color = 'deepskyblue'
    , name  = 'Minimal Salary' , orientation = 'h'))
    fig.add_trace(go.Bar( x= max_sal,y = companies , marker_color = 'red' ,
    name = 'Maximal Salary', orientation = 'h'))

    fig.update_layout(title = title,
    barmode = 'group' , template = 'plotly_dark')
    fig.show()

#Distribution of ratings of companies

ratings =data_df[~data_df['Rating'].isnull()]['Rating']
sns.distplot(ratings,kde = True , rug = True)
plt.axvline(np.median(ratings),color='r', linestyle='--')
plt.grid(True)
plt.title("Distribution of Ratings")
plt.show()

#Minimal Salaries distribution
sns.distplot(data_df['min_salary'] , kde = True , rug = True)
plt.axvline(np.median(data_df['min_salary']),color='r', linestyle='--')
plt.axvline(np.mean(data_df['min_salary']),color='g', linestyle='--')
plt.grid(True)
plt.title("Distribution of minimal Salaries")
plt.show()

#Maximal Salaries distribution
sns.distplot(data_df['max_salary'] , kde = True , rug = True)
plt.axvline(np.median(data_df['max_salary']),color='r', linestyle='--')
plt.axvline(np.mean(data_df['max_salary']),color='g', linestyle='--')
plt.grid(True)
#plt.figure(figsize=(100,100))
plt.title("Distribution of Maximum Salaries")
plt.show()

#Average annual salaries for job titles having most jobs

titles = ['Data Scientist' ,'Data Analyst' ,'Data Engineer']
min_sal = []
max_sal = []
for title in titles:
    min_sal.append(data_df[data_df['Job Title'] == title]['min_salary'].mean())
    max_sal.append(data_df[data_df['Job Title'] == title]['max_salary'].mean())

fig = go.Figure()
fig.add_trace(go.Bar(x = min_sal ,y = titles , marker_color = 'deepskyblue',
orientation = 'h' , name = 'Min Salary'))
fig.add_trace(go.Bar(x = max_sal ,y = titles , marker_color = 'magenta',
orientation = 'h' , name = 'Max Salary'))
fig.update_layout(title = 'Annual Avergae Salaries for Job titles having most jobs',
barmode = 'group' ,template = 'plotly_white')
fig.show()

#Now let's take average of minimal and maximal salary find its median

data_df['avg_sal'] = (data_df['min_salary'] + data_df['max_salary'])//2
print(f"Median average annual salary is {data_df['avg_sal'].median()}")

#Constructing the binary feature which will tell weather the job pays higher or lower than median salary
median_sal = data_df['avg_sal'].median()
data_df['is_higher'] = [1 if i > median_sal else 0 for i in data_df.avg_sal]

data_df.to_csv("train_data.csv" , index = False)
test_df.to_csv('test_data.csv' , index = False)