
#Author : Krishna Vemuri
#Data   : April 4th 2016
#Download tweets.

import json
import codecs
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from dateutil import parser
from datetime import datetime as dt

#consumer key, consumer secret, access token, access secret.
ckey=""
csecret=""
atoken=""
asecret=""

MAX_TWEETS = 1800
track_list = ['trump']
PATH = "C:/Users/KRISHNA/Desktop/TWEET/trump_20160424.dat"

class listener(StreamListener):

    def __init__(self, api=None, path=None):
        self.api = api
        self.path = path
        self.counter = 1500
        self.output  = codecs.open(path,'w','utf-8')
        #self.cur_date = dt.strptime("20160419","%Y%m%d");
        
    def on_data(self,data):
        tweet = json.loads(data)
        try:
            date = parser.parse(tweet['created_at']).strftime('%Y%m%d');
            line = str(self.counter)+" , "+date+" , "+tweet['text']
            self.output.write(line)
            self.output.write("\r\n")
            self.counter+=1
          
            if ( self.counter > MAX_TWEETS ):
                self.output.close()
                self.counter=0
                print("Reached Max Limit")
                return(False)

        except KeyError: #In case of key missing for some reasons
            self.output.write("\r\n")
            #self.counter+=1

    def on_timeout(self):
        sys.stderr.write("Timeout, Error \r\n")
        time.sleep(60)
        return(False)

    def on_error(self, status):
        print(status)

def main():

    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    print("Streaming started...")
    twitterStream = Stream(auth, listener(path=PATH)) 
    twitterStream.filter(track=track_list)
    
if __name__ == '__main__':

    main()
