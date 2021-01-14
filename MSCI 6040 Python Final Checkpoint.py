#!/usr/bin/env python
# coding: utf-8

# # Python

# <hr>

# Group name: Patrick Hess

# My goal with this project is to generate lines for characters of The Office - ideally coherent dialogue. My model will utilize a Markov chain and ingest all of the previous lines from The Office. Based on all of the historical lines, their likelihood, and how they are used in conjunction with other words, the model will then produce sentences based on these criteria. I also plan to use Spacy in order to implement natural language processing, in order to make the dialogue feel more real.
# 
# I have found a spreadsheet of all lines spoken throughout the entirety of the series, this includes both deleted and non-deleted scenes. The spreadsheet is far from perfect, some of the speakers' names are misspelled, there are actions within [] brakets in the lines, and I will plan to only use lines from the non-deleted scenes.
# 
# The data is available as a Google Sheet here: https://docs.google.com/spreadsheets/d/18wS5AAwOh8QO95RwHLS95POmSNKA2jjzdt0phrxeAE0/edit#gid=747974534
# 
# I plan to download it as an .xlsx and import it into a Pandas dataframe.

# **Scenario:** I am an NBC executive and all of my writers are on strike. I need to develop a model to generate lines of text for The Office until I can renegotiate a contract with the writers. 

# In[1]:


#The following are all of the packages that will need to be installed and are not included in anaconda
get_ipython().system('pip install re')
get_ipython().system('pip install markovify')
get_ipython().system('pip install spacy')


# In[2]:


#import all necessary packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

#could hide warnings if wanted


# # Exploring the data

# In[3]:


#import the excel file to a pandas data frame
all_lines = pd.read_excel(r'C:\Users\phess\OneDrive - University of Iowa\Programming in Python\officeTextGen\the-office-lines.xlsx')


# In[4]:


#episodes per season
episode_count = all_lines.groupby('season').episode.max()


# # Plot of episode count by season

# In[5]:


new_plot = episode_count.plot(kind='line', figsize=(10, 5), color='#86bf91')

#Switch off ticks
new_plot.tick_params(axis="both", which="both", bottom=False, top=False, labelbottom="on", left=False, right=False, labelleft="on")
new_plot.set_ylim(0, 30)
#Despine
new_plot.spines['right'].set_visible(False)
new_plot.spines['top'].set_visible(False)
#Draw vertical axis lines
new_plot.yaxis.grid()

#Set x-axis label
new_plot.set_xlabel("Season", labelpad=20, weight='bold', size=12)

#Set y-axis label
new_plot.set_ylabel("Number of Episodes", labelpad=20, weight='bold', size=12)

#Format y-axis label
new_plot.yaxis.set_major_formatter(StrMethodFormatter('{x:g}'))


# In[6]:


#lines per character (deleted scenes included)

lines_count = all_lines.speaker.value_counts(ascending=False).head(10)


# # Plot of lines by character

# In[7]:


#ax = lines_count.plot(kind="barh", title="Top Ten Characters by Lines Spoken", figsize=(15,7), color='#86bf91', zorder=2, width=0.85)

ax = lines_count.plot(kind='barh', figsize=(8, 10), color='#86bf91', zorder=2, width=0.85, title="Lines by Character")

#Despine
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)

#Switch off ticks
ax.tick_params(axis="both", which="both", bottom=False, top=False, labelbottom="on", left=False, right=False, labelleft="on")

#Draw vertical axis lines
vals = ax.get_xticks()
for tick in vals:
    ax.axvline(x=tick, linestyle='dashed', alpha=0.4, color='#eeeeee', zorder=1)

#Set x-axis label
ax.set_xlabel("Number of Lines", labelpad=20, weight='bold', size=12)

#Set y-axis label
ax.set_ylabel("Character", labelpad=20, weight='bold', size=12)

#Format x-axis label
ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))


# Plan to build a model for the top 4 speakers (Michael, Dwight, Jim, & Pam)

# # Cleaning the data

# In[8]:


#SCRUB A DUB DUB
clean_lines = all_lines.loc[all_lines.deleted == False, :] #only select rows that weren't deleted scenes
clean_lines['line_text'] = clean_lines['line_text'].str.replace(r"\[.*\]", "") #remove all actions (within []) from the line_text
clean_lines['speaker'] = clean_lines['speaker'].str.replace(r"\[.*\]", "") #remove all actions from speaker (within [])
clean_lines['speaker'] = clean_lines['speaker'].str.replace("Dwight.", "Dwight")
clean_lines['speaker'] = clean_lines['speaker'].str.replace("Dwight:", "Dwight") #fix spellings of Dwight


# One issue I ran into was all of the above errors - I was afraid my dataframe wasn't actually being modified. But I checked a few .shape attributes before and after running the function and verified that it was actually working.

# In[9]:


clean_lines.speaker.value_counts(ascending=False)


# In[10]:


#count of michael lines before cleaning
clean_lines[clean_lines.speaker == "Michael"].shape


# The below user-defined function takes input as a list of misspellings of Michael's name and fixes all of those misspellings. It could easily be modified to take input of which character to fix names for. But for my purposes Michael had a ton of misspellings and the other characters didn't.

# In[11]:


#use a FOR LOOP

michael_misspellings = ["Micheal", "Michel", "Micael", "Micahel", "Michae", "Michal", "Mihael", "Miichael"]
def replace_names(l):
    for misspelling in l:
        clean_lines.loc[clean_lines.speaker == misspelling, "speaker"] = "Michael"
        
replace_names(michael_misspellings)


# In[12]:


#count of michael lines after cleaning, making sure that the function works
clean_lines[clean_lines.speaker == "Michael"].shape
#there are about 24 more rows so it has worked!


# In[13]:


#create the sets of lines for a few characters. The resultant is a Series
michael_lines = clean_lines.loc[clean_lines.speaker == "Michael", 'line_text']
jim_lines = clean_lines.loc[clean_lines.speaker == "Jim", 'line_text']
pam_lines = clean_lines.loc[clean_lines.speaker == "Pam", 'line_text']
dwight_lines = clean_lines.loc[clean_lines.speaker == "Dwight", 'line_text']


# In[14]:


#Converts the Series above to one long string
michael_lines_string = michael_lines.str.cat(sep=" ")
jim_lines_string = jim_lines.str.cat(sep=" ")
pam_lines_string = pam_lines.str.cat(sep=" ")
dwight_lines_string = dwight_lines.str.cat(sep=" ")


# In[15]:


#nothing used here, just experimenting
# spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
# print('Number of stop words: %d' % len(spacy_stopwords))
# print('First ten stop words: %s' % list(spacy_stopwords)[:10])

# michael_doc = nlp(michael_lines_string)
# michael_tokens = [token.text for token in doc if not token.is_stop]
# print('Original Article: %s' % (michael_lines_string))
# print()
# print(tokens)

# jim_doc = nlp(jim_lines_string)
# jim_tokens = [token.text for token in doc if not token.is_stop]

# dwight_doc = nlp(dwight_lines_string)
# dwight_tokens = [token.text for token in doc if not token.is_stop]

# pam_doc = nlp(pam_lines_string)
# pam_tokens = [token.text for token in doc if not token.is_stop]


# # Creating and training the models

# In[16]:


import markovify as mk
import nltk
import re

class POSifiedTextNLTK(mk.Text):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


# In[17]:


from time import time
start_time = time()
michael_modelNLTK = POSifiedTextNLTK(michael_lines_string, state_size=3)
jim_modelNLTK = POSifiedTextNLTK(jim_lines_string, state_size=3)
pam_modelNLTK = POSifiedTextNLTK(pam_lines_string, state_size=3)
dwight_modelNLTK = POSifiedTextNLTK(dwight_lines_string, state_size=3)
print("Run time for training the generator : {} seconds".format(round(time()-start_time, 2)))


# In[18]:


print("Jim Lines", end="\n")
for i in range(5):
    print(jim_modelNLTK.make_sentence(tries=100), end="\n")
print(end="\n")    

print("Dwight Lines", end="\n")
for i in range(5):
    print(dwight_modelNLTK.make_sentence(tries=100), end="\n")
print(end="\n")

print("Michael Lines", end="\n")
for i in range(5):
    print(michael_modelNLTK.make_sentence(tries=100), end="\n")
print(end="\n")    

print("Pam Lines", end="\n")
for i in range(5):
    print(pam_modelNLTK.make_sentence(tries=100), end="\n")
print(end="\n")    
    #https://joshuanewlan.com/spacy-and-markovify


# In[19]:


import markovify as mk
import re
import spacy
nlp = spacy.load("en_core_web_sm")

class POSifiedText(mk.Text):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


# Next cell will take a **LONG** time (up to 10 minutes)

# In[20]:


#state size of 3 makes sentences much more coherent, but takes waaaaay longer to generate the model
from time import time
start_time = time()
michael_model = POSifiedText(michael_lines_string, state_size=3)
jim_model = POSifiedText(jim_lines_string, state_size=3)
pam_model = POSifiedText(pam_lines_string, state_size=3)
dwight_model = POSifiedText(dwight_lines_string, state_size=3)
print("Run time for training the generator : {} seconds".format(round(time()-start_time, 2)))


# As you can see I attempted to use both NLTK and Spacy. For my use case NLTK actually seems to work faster and better. The time to generate the models based on NLTK was about 76 seconds. While the time to generate the models using Spacy was much longer at 750 seconds. This is contradictory to the readme for Markovify. Also, the generated sentences using the Spacy models include many extra spaces between punctuation, which I can't seem to sort out. For my use case, NLTK seems to be the winner.

# In[21]:


print("Jim Lines", end="\n")
for i in range(5):
    print(jim_model.make_sentence(tries=100), end="\n")
print(end="\n")    

print("Dwight Lines", end="\n")
for i in range(5):
    print(dwight_model.make_sentence(tries=100), end="\n")
print(end="\n")

print("Michael Lines", end="\n")
for i in range(5):
    print(michael_model.make_sentence(tries=100), end="\n")
print(end="\n")    

print("Pam Lines", end="\n")
for i in range(5):
    print(pam_model.make_sentence(tries=100), end="\n")
print(end="\n")  
    #https://joshuanewlan.com/spacy-and-markovify


# "None" means that the model has generated a line that is too close to a real line and cannot be used

# # Exporting the models

# In[22]:


#exporting the models to json files
michael_model_json = michael_modelNLTK.to_json()
jim_model_json = jim_modelNLTK.to_json()
dwight_model_json = dwight_modelNLTK.to_json()
pam_model_json = pam_modelNLTK.to_json()


# Below cells export to cwd. I then copied them to desktop for easy importing into the flask app.

# In[23]:


import json

with open('michael_model_json.txt', 'w') as outfile:
    json.dump(michael_model_json, outfile)


# In[24]:


with open('jim_model_json.txt', 'w') as outfile:
    json.dump(jim_model_json, outfile)


# In[25]:


with open('pam_model_json.txt', 'w') as outfile:
    json.dump(pam_model_json, outfile)


# In[26]:


with open('dwight_model_json.txt', 'w') as outfile:
    json.dump(dwight_model_json, outfile)


# # Challenges

# -Getting the flask app up and running. Creating different URLs for each model was time consuming. Seems like there should be a more pythonic way
# 
# -Getting Spacy to work correctly - ended up using NLTK because it was faster and worked better.

# # Conclusions

# -Need A LOT of data to produce a decent markov model, 60 thousand rows probably wasn't enough
# 
# -It would be quite easy to build a chatbot using markovify
# 
# -Data cleaning is probably >= 50% of the work

# <hr>

# # HTML

# I was hoping to use the below cell as a front end for my flask app but never got it implemented

# <html>
#    <body>
#        <h1>Who should speak next?</h1>
#        <form action = "/" method = "post">
#          <p><input type="submit" name="michael" value="Michael"/></p>
#          <p><input type="submit" name="jim" value="Jim"/></p>
#          <p><input type="submit" name="pam" value="Pam"/></p>
#          <p><input type="submit" name="dwight" value="Dwight"></p>
#          <p><input type="submit" name="models" value="Download Models"></p>
#       </form>
#    </body>
# </html>

# <hr>

# # Flask

# In[28]:


#None of this is used, just experimenting with using the buttons above
# from flask import Flask
# app = Flask(__name__)

# @app.route('/')
# def script_gen():
#    if form.validate_on_submit():
#         if 'michael' in request.form:
#             pass # do something
#         elif 'jim' in request.form:
#             pass # do something else
#         elif 'pam' in request.form:
#             pass # do something
#         elif 'dwight' in request.form:
#             pass # do something else

# if __name__ == '__main__':
#    app.run()

