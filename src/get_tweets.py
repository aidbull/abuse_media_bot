import tweepy
import time
import itertools
import pytz

from datetime import datetime, timedelta
from tweepy import OAuthHandler
from configs import tw_config as conf
from database import actions as db


def limit_handled(cursor):
    
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
        except tweepy.TweepError:
            time.sleep(60 * 15)
            continue

def get_tweets():

    auth = OAuthHandler(conf.twitter['cons_key'], conf.twitter['cons_secret'])
    auth.set_access_token(conf.twitter['acs_token'], conf.twitter['acs_secret'])

    try:
        api = tweepy.API(auth)
    except Exception as e:
        print('Authentication error %s' % e)
        return e

    query_list = list(itertools.product(conf.twitter.who, conf.twitter.act))

    today = datetime.now(pytz.timezone('Europe/Moscow'))
    yesterday = today - timedelta(hours=2)
    print(today.strftime("%Y-%m-%d %H:%M:%S"))
    snc_time = yesterday.strftime("%Y-%m-%d")
    print(snc_time)
    for i, j in enumerate(query_list):
        qwr = j[0] + "+" + j[1]
        print(qwr)
        for status in limit_handled(tweepy.Cursor(api.search, q=qwr, since=snc_time,tweet_mode='extended', lang='ru', result_type="recent").items()) :
            if ('RT @' and '@' not in status.full_text):
                print('current qwr: ' + qwr + '\n')
                tw_cont = status.full_text
                ttoday = datetime.now(pytz.timezone('Europe/Moscow'))
                dtime = ttoday.strftime("%Y-%m-%d %H:%M:%S")
                print(tw_cont)
                for url in status.entities['urls']:
                    print("ADDING NEW")
                    print(dtime)
                    print(url)
                    db.db_insert(dtime,tw_cont, url['expanded_url'])
    print("PAUSING " + str(datetime.now(pytz.timezone('Europe/Moscow'))))
    time.sleep(60*120)

def main():
    
    while True:
        try:
            get_tweets()
        except Exception as e:
            print('Something bad has happened: %s' % e)
            return None


if __name__ == "__main__":
    main()