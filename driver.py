from InstaBot import InstaBot
import follower_tracker
import threading
import numpy as np
from time import sleep, time
import datetime
import pickle

### Follower tracking section

def track_followers():
    # Recursive call to start a new thread on a timer
    threading.Timer(np.random.uniform(7200, 10800), track_followers).start()
    username = "drewsfollowchecker"
    password = "checkfollowers"
    followbot = InstaBot('followtracker', username, password, False)
    followbot.get_followers("andrewrimanic")
    followbot.scraper.save()
    followbot.release()
    follower_tracker.trace_gains()
    return

### Like bot section
def like_stuff():
    # Load data from previous run
    try:
        likes_today, last_reset = pickle.load(open("loop_data.pkl", "rb"))
    except:
        last_reset = datetime.datetime.now()
        likes_today = 0

    username, password = np.genfromtxt('secret.txt', dtype='str', comments='#', unpack=True)
    likes_per_day = 600

    while True:
        
        # Daily reset
        likes_today, last_reset = pickle.load(open("loop_data.pkl", "rb"))
        elapsed = datetime.datetime.now() - last_reset
        if elapsed.days > 0:
            print("Doing daily reset")
            last_reset = datetime.datetime.now()
            likes_today = 0
            pickle.dump([likes_today, last_reset], open("loop_data.pkl", "wb"))
            elapsed = datetime.datetime.now() - last_reset


        # Print the current status
        print("Likes = " +  str(likes_today) + ' Time elapsed today = ' + str(elapsed))
    
        if likes_today < likes_per_day:
            # Set up a bot to log in and like some posts
            bot = InstaBot(username, username, password, True)
            likes_today += bot.like_hashtags(np.random.randint(0, likes_per_day - likes_today + 1))
            bot.release()
                    
            # Save the data from the last run 
            pickle.dump([likes_today, last_reset], open("loop_data.pkl", "wb"))
        else:
            print("Done liking for the day")

        # Delay until the next round of likes
        sleep(np.random.randint(1200, 3600))

            


#threading.Thread(target = track_followers).start()
threading.Thread(target = like_stuff).start()


# set a root hashtag
# scrape A LOT of hashtags
# store their amount of posts and the time the number was pulled from
# reach x amount of hashtags
# 


# Record account name and hashtag when liking photos
# Cross reference with followers gained to find which tags give most follows

# notification if certain account views story