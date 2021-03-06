import pandas as pd
#open source data analysis and manipulation tool
import nltk
# Natural Language Toolkit
import seaborn as sns 
#Library for diagrams
from textblob import TextBlob
#Library for processing textual data
import re as regex
import re
nltk.download('punkt')  
# Natural Language Toolkit
from collections import Counter
# sklearn library for train-test,accuracy-recall-precision score and time
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
# time library for calculate time
from time import time
#precision, recall and and accuracy score from sklearn.metrics libraty  
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score

#Read .csv files into train and test data with the right encoding!
train_data = pd.read_csv('/content/SocialMedia.csv', encoding= 'unicode_escape')
test_data = pd.read_csv('/content/SocialMedia2.csv', encoding= 'unicode_escape')





train_data = train_data[train_data['Sentiment'] != 'Text']

# Analyze the 1st 5 posts of train_data file
train_data.head()

# Info for the train_data file
train_data.info()

# Analyze the 1st 5 posts of test_data file
test_data.head()

# Info for the test_data file
test_data.info()

# Diagram of the train_data file with number of posts and negantive files
sns.countplot(x='Sentiment',data=train_data)

# remove tweets with empty sentiment column

train_data = train_data[train_data['Sentiment'] != ""]

train_data.info()

#Function to clean tweets
 #Remove URLs
 #Remove usernames (mentions)
 #Remove special characters EXCEPT FROM :,)
 #Remove Numbers 



def clean_tweets(tweet):
    
    # remove URL
    tweet = re.sub(r"http\S+", "", tweet)
    
    # Remove usernames
    tweet = re.sub(r"@[^\s]+[\s]?",'',tweet)

     # remove special characters 
    tweet = re.sub('[^ a-zA-Z0-9]' , '', tweet)
    
    # remove Numbers
    tweet = re.sub('[0-9]', '', tweet)
    
    
    
    
    
    return tweet

# Apply function to Text column with clean text
train_data['Text'] = train_data['Text'].apply(clean_tweets)

#Analyze the 1st 5 posts of train_data file after cleaning with Name of column and datatype!
train_data['Text'].head()

# Function which directly tokenize the text data
from nltk.tokenize import TweetTokenizer

tt = TweetTokenizer()
train_data['Text'].apply(tt.tokenize)

from nltk.stem import PorterStemmer   #Libraries for tokenize words
from nltk.tokenize import sent_tokenize, word_tokenize

ps = PorterStemmer()

def tokenize(text):                    # funtion for tokenize words and analyze Text
    return word_tokenize(text)

def stemming(words):
    stem_words = []
    for w in words:
        w = ps.stem(w)
        stem_words.append(w)
    
    return stem_words

# apply tokenize function
train_data['text'] = train_data['Text'].apply(tokenize)

# apply steming function
train_data['tokenized'] = train_data['text'].apply(stemming)

train_data.head()  #See the 1st 5 tokenize reults

words = Counter()                       # Words analyze  (5 most common) with count of them
for idx in train_data.index:
    words.update(train_data.loc[idx, "text"])

words.most_common(5)

nltk.download('stopwords')
stopwords=nltk.corpus.stopwords.words("english")

whitelist = ["n't", "not"]
for idx, stop_word in enumerate(stopwords):
    if stop_word not in whitelist:
        del words[stop_word]
words.most_common(5)

def word_list(processed_data): # WORDLIST FUNCTION FOR ANALYZE MOST COMMON WORDS WITH PURPOSE TO IDENTIFY OUR APP THE REAL SENTIMENT
    #print(processed_data)
    min_occurrences=3 
    max_occurences=500 
    stopwords=nltk.corpus.stopwords.words("english")
    whitelist = ["n't","not"]
    wordlist = []
    
    whitelist = whitelist if whitelist is None else whitelist
    
    words = Counter()
    for idx in processed_data.index:
        words.update(processed_data.loc[idx, "text"])

    for idx, stop_word in enumerate(stopwords):
        if stop_word not in whitelist:
            del words[stop_word]
    #print(words)

    word_df = pd.DataFrame(data={"word": [k for k, v in words.most_common() if min_occurrences < v < max_occurences],
                                 "occurrences": [v for k, v in words.most_common() if min_occurrences < v < max_occurences]},
                           columns=["word", "occurrences"])
    #print(word_df)
    word_df.to_csv("wordlist.csv", index_label="idx")
    wordlist = [k for k, v in words.most_common() if min_occurrences < v < max_occurences]
    #print(wordlist)

word_list(train_data)    #TRAIN DATA INTO WORDLIST FOR ANALYZE

words = pd.read_csv("wordlist.csv") #CREATE WORDLIST CSV WITH THE MOST COMMON WORDS

import os
wordlist= []      #CREATE THE FILE WORDLIST
if os.path.isfile("wordlist.csv"):
    word_df = pd.read_csv("wordlist.csv")
    word_df = word_df[word_df["occurrences"] > 3]
    wordlist = list(word_df.loc[:, "word"])

label_column = ["label"]
columns = label_column + list(map(lambda w: w + "_bow",wordlist))
labels = []
rows = []
for idx in train_data.index:
    current_row = []
    
    # add label
    current_label = train_data.loc[idx, "Sentiment"]
    labels.append(current_label)
    current_row.append(current_label)

    # add bag-of-words
    tokens = set(train_data.loc[idx, "text"])
    for _, word in enumerate(wordlist):
        current_row.append(1 if word in tokens else 0)

    rows.append(current_row)

data_model = pd.DataFrame(rows, columns=columns)
data_labels = pd.Series(labels)


bow = data_model

import random    #Randomize the Texts
seed = 777
random.seed(seed)

def log(x):
    #can be used to write to log file
     print(x)

def test_classifier(X_train, y_train, X_test, y_test, classifier):
    log("")
    log("---------------------------------------------------------")
    log("Testing " + str(type(classifier).__name__))
    now = time()
    list_of_labels = sorted(list(set(y_train)))
    model = classifier.fit(X_train, y_train)
    log("Learing time {0}s".format(time() - now))
    now = time()
    predictions = model.predict(X_test)
    log("Predicting time {0}s".format(time() - now))

    # Calculate Accuracy, Precision, recall computation
    
    precision = precision_score(y_test, predictions, average=None, pos_label=None, labels=list_of_labels)
    recall = recall_score(y_test, predictions, average=None, pos_label=None, labels=list_of_labels)
    accuracy = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions, average=None, pos_label=None, labels=list_of_labels)
    
    log("=================== Results ===================")
    log("         Negative   Positive          ")
    log("F1       " +   str(f1))
    log("Precision" +   str(precision))
    log("Recall   " +   str(recall))
    log("Accuracy " +   str(accuracy))
    log("===============================================")

    return precision, recall, accuracy, f1

from sklearn.naive_bayes import BernoulliNB  #Print f1, Precision, Recall ,Accuracy Score got Negatives and Positives Posts
X_train, X_test, y_train, y_test = train_test_split(bow.iloc[:, 1:], bow['label'], test_size=0.3)
precision, recall, accuracy, f1 = test_classifier(X_train, y_train, X_test, y_test, BernoulliNB())

# Give text input for testing your post!
# After clean tweet and print it!

y= input("Type your post for analysis:")
x=clean_tweets(y)
print(x)

# Using textblob library for data analysis 
# After sentiment and polarity for calculate the emotion of the post and print it for testing!
text= TextBlob(y)


z = text.sentiment.polarity

print (z)

# Using if statement for printing if it is positive or negative!

if z==0: 
    print("Neutral")
elif z<0:
    print("Negative")
else:
    print("Positive")
