from InstaBot import InstaBot
import follower_tracker
import threading
import numpy as np
from time import sleep, time
import datetime
import pickle
import sys
import signal
from getpass import getpass
import sys
import os

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

### Follower tracking section

def track_followers():
    # Recursive call to start a new thread on a timer
    # threading.Timer(np.random.uniform(7200, 10800), track_followers).start()
    # username = "drewsfollowchecker"
    # password = "checkfollowers"
    # username, password = np.genfromtxt('secret.txt', dtype='str', comments='#', unpack=True)

    # followbot = InstaBot('followtracker', username, password, False)
    # followbot.get_followers(username)
    # followbot.scraper.save()
    # followbot.release()
    # follower_tracker.trace_gains()
    return

### Like bot section
def like_stuff(username, likes_per_day=1, followothers=False, headless_mode = True):
    # Load data from previous run
    username, password = pickle.load(open(username + '_login.pkl', 'rb'))
    try:
        likes_today, last_reset = pickle.load(open(username + "_loop_data.pkl", "rb"))
    except:
        last_reset = datetime.datetime.now()
        likes_today = 0
        pickle.dump([likes_today, last_reset], open(username + "_loop_data.pkl", "wb"))


    #while True:
        
    # Daily reset
    likes_today, last_reset = pickle.load(open(username + "_loop_data.pkl", "rb"))
    elapsed = datetime.datetime.now() - last_reset
    if elapsed.days > 0:
        print("Doing daily reset")
        last_reset = datetime.datetime.now()
        likes_today = 0
        likes_per_day = likes_per_day + np.random.randint(-5,17) # Random growth rate
        pickle.dump([likes_today, last_reset], open(username + "_loop_data.pkl", "wb"))
        elapsed = datetime.datetime.now() - last_reset


    # Print the current status
    print("Likes = " +  str(likes_today) + ' Time elapsed today = ' + str(elapsed))

    # Set up a bot to log in and like some posts
    bot = InstaBot(username, username, password, headless_mode)
    bot.set_follow_others(followothers)
    if likes_today < likes_per_day:
        likes_today += bot.like_hashtags(np.random.randint(0, likes_per_day - likes_today + 1))
                
        # Save the data from the last run 
        pickle.dump([likes_today, last_reset], open(username + "_loop_data.pkl", "wb"))
    else:
        print("Done liking for the day at " + datetime.datetime.now().strftime("%H:%M:%S"))

    bot.release()
    # Delay until the next round of likes
    threading.Timer(np.random.randint(1200, 3600), like_stuff, args=(username, likes_per_day, followothers, headless_mode)).start()

            

def main():
 #   os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
 #   os.environ['WDM_LOCAL'] = '1'       
    
    fn = sys.argv[0]
    print(fn)
    os.chdir(os.path.dirname(fn))

    print('Starting')

    print("Enter username and password. Leave password blank to use previous")
    username = input("username: ")
    password = getpass()
    if password != '':
        pickle.dump([username, password], open(username + '_login.pkl', 'wb'))        
    
    
    num_likes = input("Maximum likes per day: ")
    while (not num_likes.isnumeric() or int(num_likes) < 0):
        print("invalid input. enter a positive whole number")
        num_likes = input("Maximum likes per day: ")

    num_likes = int(num_likes)

    if num_likes > 1000:
        
        print("Warning! Recommended number of likes is below 1000/day")

        answer = ''
        while answer != 'y':
            answer = input("Continue anyways (y) or choose a new number (n)?: ")
            if answer == 'n':
                num_likes = int(input("Maximum likes per day: "))
                answer = 'y'

    # follow = input("Follow other accounts (y/n): ")
    # if follow == 'y':
    #     follow = True
    # else:
    #     follow = False
    follow = False

    headless = input("Show browser window? (y/n): ")
    if headless == 'y':
        headless = False
    else:
        headless = True

        
    # checker = threading.Thread(target = track_followers)
    # checker.daemon = True
    # checker.start()

    liker = threading.Thread(target = like_stuff, args=(username, num_likes, follow, headless))
    liker.daemon = True
    liker.start()

    print("Press Ctrl+C to end program")

    while True:
        sleep(1)

if __name__ == "__main__":
    main()

# set a root hashtag
# scrape A LOT of hashtags
# store their amount of posts and the time the number was pulled from
# reach x amount of hashtags
# 


# Record account name and hashtag when liking photos
# Cross reference with followers gained to find which tags give most follows

# notification if certain account views story