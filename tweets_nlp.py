#!/usr/bin/env python
# encoding: utf-8
#Author - Yifan Wang irvingw@bu.edu

import tweepy #https://github.com/tweepy/tweepy
import json
import os 
import io
import sys 
from google.cloud import language 
from google.cloud.language import enums 
from google.cloud.language import types 
  
#Twitter API credentials
consumer_key = "-------------------------"
consumer_secret = "--------------------------------------------------"
access_key = "--------------------------------------------------"
access_secret = "---------------------------------------------"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.curdir, 'ec601-project-2-5172714cb435.json') 
screen_name = "@RobertDowneyJr"
#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

#initialize a list to hold all the tweepy Tweets
alltweets = []

#make initial request for most recent tweets (200 is the maximum allowed count)
new_tweets = api.user_timeline(screen_name = screen_name,count=10)

#save most recent tweets
alltweets.extend(new_tweets)

#save the id of the oldest tweet less one
oldest = alltweets[-1].id - 1

#keep grabbing tweets until there are no tweets left to grab
while len(new_tweets) > 0:

#all subsiquent requests use the max_id param to prevent duplicates
    new_tweets = api.user_timeline(screen_name = screen_name,count=10,max_id=oldest)
        
    #save most recent tweets
    alltweets.extend(new_tweets)
    #update the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    if(len(alltweets) > 15):
        break
    print "...%s tweets downloaded so far" % (len(alltweets))
       
#write tweet objects to JSON
file = open('tweet.txt', 'a+') 
print "Writing tweet objects to TXT please wait..."
for status in alltweets:
    json.dump(status.text,file,sort_keys = True,indent = 4)
    
#close the file
print "Done"
file.close()
client = language.LanguageServiceClient() 
input_file = "tweet.txt"
with io.open(input_file, "r") as inp: 
    docu = inp.read() 
      
text = types.Document(content = docu,  
   type = enums.Document.Type.PLAIN_TEXT) 
  
annotation = client.analyze_sentiment(document = text) 
  
score = annotation.document_sentiment.score 
magnitude = annotation.document_sentiment.magnitude 

f = open("tweet_nlp.txt", 'w')
sys.stdout = f

for index, sentence in enumerate(annotation.sentences): 
    sentence_sentiment = sentence.sentiment.score 
    print('Sentence #{} Sentiment score: {}'.format( 
                     index + 1, sentence_sentiment)) 
ent = client.analyze_entities(document = text) 
  
entity = ent.entities 
  
print('Score: {}, Magnitude: {}'.format(score, magnitude)) 

for e in entity: 
    print(e.name, e.metadata, e, type, e.salience) 

tokens = client.analyze_syntax(text).tokens 
  
for token in tokens: 
    speech_tag = enums.PartOfSpeech.Tag(token.part_of_speech.tag) 
    print(u'{}: {}'.format(speech_tag.name, token.text.content)) 

f.close()

