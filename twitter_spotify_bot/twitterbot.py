import tweepy
import time
import sys
import spotipy
import spotipy.util as util

# NOTE: I put my keys in the keys.py to separate them
# from this main file.
# Please refer to keys_format.py to see the format.
from keys import *
from key_spotify import *

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
FILE_NAME = 'last_seen_id.txt'
hashtag = ""
playlist = ''

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def get_tweets():
    #print('retrieving tweets...')
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(
                        last_seen_id,
                        tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if hashtag in mention.full_text.lower():
            print('found'+hashtag)
            if isFollowed(mention.author.screen_name):
                if add_to_playlist(getURI(mention)):
                    api.update_status('@' + mention.user.screen_name +
                    ' Added!', mention.id)
                else:
                    api.update_status('@' + mention.user.screen_name +
                    ' Could not add the track.. Make sure the URL or URI works and resubmit.', mention.id)
            else:
                api.update_status('@' + mention.user.screen_name +
                    ' You must follow this account before you submit.', mention.id)
        elif '#' in mention.full_text.lower():
            api.update_status('@' + mention.user.screen_name +
                ' You did not includ a vaild hashtag.', mention.id)
            

def add_to_playlist(track):
    token = util.prompt_for_user_token(SPOTIFY_ACCOUNT, SCOPE, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
    try:
        if token:
            sp = spotipy.Spotify(auth=token)
            sp.trace = False
            playlist = sp.user_playlist(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST)
            tracks = playlist['tracks']
            totalTracks = tracks['total']
            if totalTracks > 0:
                latestAdd = tracks['items'][0]
                latestTrackId = latestAdd['track']['id']
            if totalTracks >= 200:
                print("REMOVE")
                sp.user_playlist_remove_all_occurrences_of_tracks(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST, [latestTrackId])
            try:
                sp.user_playlist_remove_all_occurrences_of_tracks(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST, [track])
                sp.user_playlist_add_tracks(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST,[track])
                return True
            except:
                sp.user_playlist_add_tracks(SPOTIFY_ACCOUNT, SPOTIFY_PLAYLIST,[track])
                return True
        else:
            print("Can't get token for", SPOTIFY_ACCOUNT)
            return False
    except:
        print("Can't add track to playlist")
        return False

def getURI(tweet):
    tweet = str(tweet).split(" ")
    for i in tweet:
        i = i.strip()
        if i.find("https://open.spotify.com/track/") != -1:
            i = i[i.find("https://open.spotify.com/track/"):len(i)]
            tweet = i[31:i.find("?")]
        elif i.find("spotify:track:") != -1:
            i = i[i.find("spotify:track:"):len(i)]
            tweet = i[14:len(i)]
    return tweet

def isFollowed(user):
    friend = False
    for follower in tweepy.Cursor(api.followers, screen_name=playlist).items():
        if user == follower.screen_name:
            friend = True
            print("Is Friends")
    return friend




while True:
    get_tweets()    
    time.sleep(60)
