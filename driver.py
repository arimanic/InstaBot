from InstaBot import InstaBot
import follower_tracker
import threading
import numpy as np
from time import sleep, time
import datetime
import pickle




### Follower tracking section

def get_followers():
    threading.Timer(np.random.uniform(7200, 10800), get_followers).start()
    username = "drewsfollowchecker"
    password = "checkfollowers"
    followbot = InstaBot(username, password, True, True)
    followbot.get_followers("andrewrimanic")
    followbot.scraper.save()
    followbot.release()
    follower_tracker.trace_gains()
    return

threading.Thread(target = get_followers).start()

### Like bot section

# Load data from previous run
try:
    likes_today, last_time = pickle.load(open("loop_data.pkl", "rb"))
except:
    last_time = datetime.datetime.now()
    likes_today = 0

username, password = np.genfromtxt('secret.txt', dtype='str', comments='#', unpack=True)
likes_per_day = 500
t = time()


while likes_today < likes_per_day:
    
    # Print the current status
    print("Likes = " +  str(likes_today) + ' Time elapsed today = ' + str(elapsed))
    
    # Daily reset
    elapsed = datetime.datetime.now() - last_time
    if elapsed.days > 0:
        last_time = datetime.datetime.now()
        likes_today = 0

    # Set up a bot to log in and like some posts
    bot = InstaBot(username, password, True, True)
    likes_today += bot.like_hashtags(np.random.randint(1, likes_per_day - likes_today))
    bot.release()
    
    # Get the time and print the like rate as well as total likes
    #elapsed = time() - t
    
    # Save the data from the last run TODO: Put this into the like loop somehow in case the program is cut midway
    pickle.dump([likes_today, last_time], open("loop_data.pkl", "wb"))

    # Delay until the next round of likes
    sleep(np.random.randint(300, 1200))




#username, password = np.genfromtxt('secret.txt', dtype='str', comments='#', unpack=True)



#bot = InstaBot(username, password, reset)
#bot.like_hashtags(800)
#bot.release()

# Sort hashtags by activity

# set a root hashtag
# scrape A LOT of hashtags
# store their amount of posts and the time the number was pulled from
# reach x amount of hashtags
# 


# Record account name and hashtag when liking photos
# Cross reference with followers gained to find which tags give most follows

# notification if certain account views story