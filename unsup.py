#Author : Krishna Vemuri
#Date : May 4th 
#Uses web search API which is deprecated
import re
import time
import nltk.tag.stanford as SPT
import random
import pandas as pd
import nltk

from json import loads as LOAD
from nltk import tree as TREE
from nltk import RegexpParser as REPARSE
from nltk.stem import WordNetLemmatizer
from urllib.request import urlopen as OPEN
from urllib.request import Request as REQUEST

from urllib.parse import urlencode as URLENCODE

_PATH_TO_MODEL = 'C:/stanford/models/english-bidirectional-distsim.tagger'
_PATH_TO_JAR = 'C:/stanford/stanford-postagger.jar'

countPosWords = 0
countNegWords = 0

POSITIVE = 1
NEGATIVE = -1
ERROR = 0

SENTIMENT = [POSITIVE,NEGATIVE,ERROR]
#Seed words
#High Precision for negative tweets
#positive_tags = ['great','honesty']
#negative_tags = ['anti','never']
#High Precision for positive tweets
#positive_tags = ['strong','great','need']
#negative_tags = ['arrogant','never','anti']
positive_tags = ['strong','need']
negative_tags = ['arrogant','never','anti']

#Operators for searching
AROUND = ' AROUND(10) '
EXCL = ' -'
SINGLE_LEAVE = 1

ALPHANUM = re.compile(r'(\d+|\s+)')
COMBINEDWORD = re.compile(r'[A-Z]+[a-z]*')
COMBINEDWORD2 = re.compile(r'[A-Z][A-Z]+')

SEARCH = {
    "Google": "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s"
    #"Altavista": ""
}

#Replaces words of follwing patterns 
replace_dict = {
    "don't": "do not",
    "won't": "will not",
    "didn't": "did not",
    "doesn't": "does not",
    "wouldn't": "would not",
    "can't": "can not",
    "We're": "We are",
    "they're": "they are",
    "what's" : "what is",
    "he'll" : "he will",
    "DONT": "Do not"
    #"can’t": "can not"
}

#Get positive tags in nice formatted way for search parameters
def getposTags():
    str = '('
    for word in positive_tags:
        str = str+'"'+word+'"'
        str = str+" OR "
    str = str[:-3]
    str = str +')'
    return str

#Get negative tags in nice formatted way for search
def getnegTags():
    str = '('
    for word in negative_tags:
        str = str+'"'+word+'"'
        str = str+" OR "
    str = str[:-3]
    str = str +')'
    return str


#JustPosWords = '('+getposTags()+EXCL+'"'+getnegTags()+'" AROUND(3) "Trump" )'
JustPosWords = '('+getposTags()+' AROUND(5) "Trump" )'
#JustNegWords = '('+getnegTags()+EXCL+'"'+getposTags()+'" AROUND(3) "Trump" )'
JustNegWords = '('+getnegTags()+' AROUND(5) "Trump" )'

#Atleast to some extent prevents blockage
def useragent():
    agents = ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6','Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
	'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)',
	'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)',
	'Mozilla/5.0 (X11; Arch Linux i686; rv:2.0) Gecko/20110321 Firefox/4.0',
	'Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)',
	'Mozilla/5.0 (Windows NT 6.1; rv:2.0) Gecko/20110319 Firefox/4.0',
	'Mozilla/5.0 (Windows NT 6.1; rv:1.9) Gecko/20100101 Firefox/4.0',
	'Opera/9.20 (Windows NT 6.0; U; en)','Opera/9.00 (Windows NT 5.1; U; en)',
	'Opera/9.64 (Windows NT 5.1; U; en) Presto/2.1.1')
    return random.choice(agents)

#Reads the tweet file and places into Pandas Dataframe
def readFile():
    try:
        df = pd.read_csv(r'C:/Users/KRISHNA/Desktop/tweet.dat',sep='|',names = ["MesgID", "CreatedAt", "Sentiment", "tweet"])
        return df
    except Exception as ex:
        print(ex)

#Makes Requests to Google. Returns the number of hits for particular phrase
def getCount(switch,phrase):
    print('Checking for phrase:'+str(phrase))
    Count = 0
    try: 
        headers = {}
        headers['User-Agent'] = useragent()
        if switch == 'err':
            return 0;
        query = URLENCODE({'q': phrase})
        URL = SEARCH['Google'] % query
        REQ = REQUEST(URL,headers=headers)
        RESP = OPEN(REQ)
        RESULTS = RESP.read().decode("utf-8")
        JSON_RES = LOAD(RESULTS)
        #Suspected Terms of Service Abuse
        if JSON_RES['responseStatus'] == 403:
            if switch == 'False':
                print("Suspicion detected by Google-Sleep for 30 seconds")
                time.sleep(30)  # Sleep 20 seconds after blockge.
                getCount('True',phrase)
            elif switch == 'True':
                print("Suspicion detected by Google-Sleep for 60 seconds")
                time.sleep(60) #Sleep, atleast safe execution
                getCount('err',phrase)
        elif JSON_RES['responseStatus'] == 200: #Everything is good
            DATA = JSON_RES['responseData']
            if len(DATA['results']) > 1 : #Looks stupid but this is how it works
                count = DATA['cursor']['estimatedResultCount'];
                Count = int(count)
            else :
                Count = 1
            time.sleep(3)
            return Count

    except Exception as ex:
        print(str(ex))


#Replace words present in dicitionary. Words that effect the Sentiment 
def replaceNT(text):
    for word in replace_dict:
        if word in text:  # Small first letter
            text = text.replace(word, replace_dict[word])
        elif word[0].title() + word[1:] in text:  # Big first letter
            text = text.replace(word[0].title() + word[1:],
                                replace_dict[word][0].title() + replace_dict[word][1:])
    return text

#start replaceTwoOrMoreChar
def replaceTwoOrMoreChar(tweet):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", tweet)
#end

def preprocess(isStanfrd,tweet):
 
    tweet = tweet.strip()
    #Replace the URL's with space 
    tweet = re.sub(r'(https?://[^\s]+)',' ',tweet)
    #Replace #Word with Word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #Replace @Word with Word
    tweet = re.sub(r'@([^\s]+)', r'\1', tweet)
    #Remove words that start with numbers
    tweet = re.sub(r'^[0-9]*','',tweet)
    #Replace n't with not 
    tweet = replaceNT(tweet)
    #Replace RT at start of tweet
    tweet = re.sub(r'^RT','',tweet)
    #Replace two or more sequence of characters to two character
    tweet = replaceTwoOrMoreChar(tweet)
    #Remove Special Characters
    tweet = re.sub(r'[^\w]', ' ', tweet)
    #Remove more than space
    tweet = re.sub('[\s]+', ' ', tweet)
    #Remove Special Characters
    tweet = re.sub(r'[^\w]', ' ', tweet)
    #Stanford or NLTK
    if isStanfrd == False:
        return tweet
    else:
        return re.split(ALPHANUM,tweet)

#Uses Stanford tagger
def par_speech_tags(tweet_split):

    #Using stanford POS Tagger to Tag words, better than NLTK default tagger
    tagger = SPT.StanfordPOSTagger(_PATH_TO_MODEL,_PATH_TO_JAR)
    tagged = tagger.tag(tweet_split)
   
    return tagged

#Seperate process for nltk
def process(text):
    
    text = nltk.word_tokenize(tweet)
    return filter_tweet(text)

#Filters the tweets and words
def filter_tweet(cleand_tweet_s):
    cleand_tweet = [] # Building a list of clear words
	
    #Handling Combined words
    for each_word in cleand_tweet_s:
        isMatch = COMBINEDWORD.search(each_word)
        if isMatch:
            isMatch = COMBINEDWORD2.search(each_word)
            if isMatch:
                for each_word_2 in re.findall(COMBINEDWORD2,each_word):
                    cleand_tweet.append(each_word_2)
            else :
                for each_word_1 in re.findall(COMBINEDWORD,each_word):
                    cleand_tweet.append(each_word_1)
        else:
            cleand_tweet.append(each_word)
    
    #Lemmatize	
    WORDNETLEMMA = WordNetLemmatizer()
    filtrd_tweet = [WORDNETLEMMA.lemmatize(each_word) for each_word in cleand_tweet]
    
    return filtrd_tweet
    
#Chunks the tweets into following patterns
def chunkingTweet(filtrd_tweet):
    trees = []
   # grammar = """ 
       # ADJN:{<JJ><N.*>*}
        #    VBN:{(<VB>|<VBG>|<VBD>|<VBN>|<VBP>|<VBZ>)(<NN>|<NNP>)}
         #   AVBN:{(<RB>|<RBR>|<RBS>)(<NN>|<NNP>)}
          #  VBAVB:{(<VB>|<VBG>|<VBD>|<VBN>|<VBP>)(<RB>|<RBR>|<RBS>)}
           # MDVB:{<MD><.+>(<VB>|<VBG>|<VBD>|<VBN>|<VBP>)}

   # """
    grammar = """ 
        ADJN:{<JJ><N.*>*}
            VBN:{(<VB>|<VBG>|<VBD>|<VBN>|<VBP>|<VBZ>)(<NN>|<NNP>)}
            AVBN:{(<RB>|<RBR>|<RBS>)(<NN>|<NNP>)}
            MDVB:{<MD><.+>(<VB>|<VBG>|<VBD>|<VBN>|<VBP>)}

    """
 
    chunkParser = REPARSE(grammar)
    rootTree = chunkParser.parse(filtrd_tweet)
    rootTree.draw()
    for tree in rootTree:
        if isinstance(tree,TREE.Tree):
            trees.append(tree)			
    chunkParser.parse(filtrd_tweet)
    return trees

#Traverses each tree and extracts the Leaves
def traverseTrees(tree):
    try:
        tree.label()
        tot_leaves = []
    except AttributeError:
        return
    if tree.label() == 'ADJN' or 'AVBN' or 'VBN' or 'AVBVB' or 'VBAVB' or 'MDVB':
        #Remove the Trump Leaves
        tot_leaves = [leaves[0] for leaves in tree.leaves() if leaves[0].lower() != 'trump'] 
        return tot_leaves
    else:
        print("Unkown Tree Created")
    return trees

#Gets the score of each Tree 
def getScoreOfPattern(leaves):
    param = '('
    for leave in leaves:
        param = param+'"'+str(leave)
        if len(leaves) == SINGLE_LEAVE :
            param = param+'")'
            break;
        else:
            param = param+'" AND '
    
    if len(leaves) != SINGLE_LEAVE :
        param = param[:-5]
        param = param+')'

    posPhrase = param+AROUND+JustPosWords
    negPhrase = param+AROUND+JustNegWords
    # +1 To avoid divide by Zero exceptions(Often due to n/w issues)
    posNodeScore = getCount('False',posPhrase)
    print("PostiveNodeScore:"+str(posNodeScore))
    if posNodeScore == 0:
        return 0
    NegNodeScore = getCount('False',negPhrase)
    print("NegNodeScore:"+str(NegNodeScore))
    if NegNodeScore == 0:
        return 0
    score = posNodeScore/(1+countPosWords) - NegNodeScore/(1+countNegWords)
    #score = posNodeScore - NegNodeScore
    
    return score
    #return 1

if __name__ == '__main__':
    
    SENTIMENT = []
    TWEET = []
    DATE = []
    prev = 'Success'
    #Read the data file into Dataframe
    dataFrame = readFile()

    columns = ['Date', 'Sentiment', 'Tweet']
    out_df = pd.DataFrame(columns=columns)

    #Count the Occurence of seed +ve words  and seed -ve words for Trump Just Once
    countPosWords = getCount('False',JustPosWords)
    countNegWords = getCount('False',JustNegWords)

    #Perform the following for each tweet
    for index,row in dataFrame.iterrows():
        
        TWEET.append(row['tweet'])
        DATE.append(row['CreatedAt'])
        
        if prev != 'Fail' :
            print(row['tweet'])
            # Clean the tweet
            cleand_tweet = preprocess(True,str(row['tweet']))
            #Lemmatising the tweet
            filtrd_tweet = filter_tweet(cleand_tweet)
            #POS Tagging the tweet
            tagged_tweet = par_speech_tags(filtrd_tweet)
            #Chunk the tweet
            trees = chunkingTweet(tagged_tweet)
            
            tree_score = 0
            tree = ''
            for tree in trees:
                tot_leaves = traverseTrees(tree)
                #Sum of all semantic phrases
                score = getScoreOfPattern(tot_leaves)
                if score != 0:
                    tree_score += score
                else: #Tree score not calculated due to n/w issues.Abandon Remaining Tree calculation
                    prev = 'Fail'
                    SENTIMENT.append(ERROR)
                    print('Error in Stanford')
            if tree_score >= 0 and tree != '' and prev!='Fail':
                print("Positive Sentiment The total score is :%f" %tree_score)
                SENTIMENT.append(POSITIVE)
            elif tree_score < 0 and tree != '' and prev!='Fail':
                print("Negative Sentiment: The total score is :%f" %tree_score)
                SENTIMENT.append(NEGATIVE)
            elif tree_score == 0: #Stanford failed to create trees . Try with nltk Tagger
                print("Using NLTK Tagger")
                # Clean the tweet
                tweet = preprocess(False,str(row['tweet']))
                # Lemmatising and tokenizing the tweet
                proc_tweet = process(tweet)
                # NLTK Pos Tagging the tweet
                tag_tweet = nltk.pos_tag(proc_tweet)
                nltk_trees = chunkingTweet(tag_tweet)
                for tree in nltk_trees:
                    tot_leaves = traverseTrees(tree)
                    print(tot_leaves)
                    #Sum of all semantic phrases
                    score = getScoreOfPattern(tot_leaves)
                    if score != 0:
                        tree_score += score
                    else: #Tree score not calculated due to n/w issues.Abandon Remaining Tree calculation
                        prev = 'Fail'
                        SENTIMENT.append(ERROR)
                        print('Error in NLTK Tagging')
                if tree_score >= 0 and tree != '' and prev!='Fail':
                    print("Positive Sentiment The total score is :%f" %tree_score)
                    SENTIMENT.append(POSITIVE)
                    prev='Success'
                elif tree_score < 0 and tree != '' and prev!='Fail':
                    print("Negative Sentiment: The total score is :%f" %tree_score)
                    SENTIMENT.append(NEGATIVE)
                    prev='Success'
                elif prev != 'Fail': #No Sentiment Calculated
                    SENTIMENT.append(ERROR)
                    print('No Sentiment Extracted')
        else:
            SENTIMENT.append(ERROR)
            print('Error in Overall')

    out_df['Date'] = DATE
    out_df['tweet'] = TWEET
    out_df['Sentiment'] = SENTIMENT

    #future Implmentation
            
                



        

    
            
