from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import threading
import pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import random
import time
import datetime
import metrics
import numpy as np
import follower_tracker
from webdriver_manager.chrome import ChromeDriverManager


# Random probability thresholds
p_like = 1/9 # Probability of liking a post
p_break = 1/300 # Probability of switching hashtags
p_follow = 1/30 # Probability of following account after liking photo


class InstaBot:
    # Starts the bot
    def __init__(self, botname, username, pw, headless = True):

        self.username = username
        self.name = botname
        self.followothers = False

        # Load metrics
        self.metrics = metrics.Metrics()
        self.metrics.load()

        # Load the hashtags to like from
        self.hashtags = np.genfromtxt("hashtags.txt", comments='#', dtype='str')
        
        # List of people to unfollow
        try:
            self.unfollow_list = pickle.load(open(self.name + "_follows.pkl", "rb"))
        except:
            self.unfollow_list = list()


        self.options = Options()
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try: # Load cookies
            cookies = pickle.load(open(self.name + "_cookies.pkl", "rb"))
        except: # No cookies found, generate them
            self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=self.options)
            self.driver.implicitly_wait(5)
            self.driver.get("https://instagram.com")

            self.driver.find_element_by_xpath("//input[@name=\"username\"]")\
                .send_keys(username)
            self.driver.find_element_by_xpath("//input[@name=\"password\"]")\
                .send_keys(pw)
            self.driver.find_element_by_xpath('//button[@type="submit"]')\
                .click()
            self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]")\
                .click()
            
            # Save cookies
            cookies = self.driver.get_cookies()
            pickle.dump(cookies , open(self.name + "_cookies.pkl","wb"))
            self.driver.close()



        # Initialize the web driver with the headless option applied now
        self.options.headless = headless
        self.options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=self.options)
        self.driver.implicitly_wait(5)
        self.driver.get("https://instagram.com")

        # Apply cookies
        for cookie in cookies:
            self.driver.add_cookie(cookie)


    # Call this to ensure all data is saved properly
    def release(self):
        # Dump the list of followers
        self.unfollow_accounts()
        pickle.dump(self.unfollow_list, open(self.name + "_follows.pkl", "wb"))
        self.metrics.save()
        self.driver.quit()

    # Likes pictures scraped from a hashtag up to maxlikes
    def like_hashtags(self, maxlikes):
        total_likes = 0
        total_follows = 0

        while total_likes != maxlikes:

            # Pick a random hashtag
            tag = random.choice(self.hashtags)
            print("Looking at #" + str(tag))

            # Go to the tag's explore page
            self.driver.get("https://www.instagram.com/explore/tags/" + tag + "/")

            # Run the like loop and record how many pictures are liked
            new_likes, new_follows = self.like_loop(maxlikes - total_likes, tag)
            total_likes += new_likes
            total_follows += new_follows

        return total_likes


    # The loop used to like posts
    def like_loop(self, maxlikes, tag):
        
        # Stats
        liked = 0 
        followed = 0
        viewed = 1


        # Click the first thumbnail
        try:
            first_thumbnail = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME,"_9AhH0")))
            first_thumbnail.click()
        except:
            return liked, followed

        print("Liking " + str(maxlikes) + " images")

        while liked != maxlikes:
            
            # wait random time on each post
            sleep(random.uniform(5.0, 10.0))

            # wait for the page to be ready
            try:
                WebDriverWait(self.driver, 30).until(lambda *args: (self.driver.execute_script("return document.readyState") == "complete"))
            except:
                print("page failed to load")
                break


            # check to switch hashtag
            if p_break > np.random.uniform():
                print("Switching to a different hashtag")
                break

            # check to like the current photo
            if p_like > np.random.uniform():

                # Like the photo          
                try:
                    like = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Like']:not([class*='glyphsSpriteHeart__filled__16__white u-__7'])")))
                    like.click()
                    liked += 1

                    # Store the like metrics
                    acct_name = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME,"sqdOP.yWX7d._8A5w5.ZIAjV"))).text
                    self.metrics.add(acct_name, metrics.LikeData(tag, datetime.datetime.now()))

                    likes_today, last_time = pickle.load(open(self.name + "_loop_data.pkl", "rb"))
                    pickle.dump([likes_today + 1, last_time], open(self.name + "_loop_data.pkl", "wb"))

                    print(str(liked) + ' Posts liked out of ' + str(viewed) + ' views, Total likes today: ' + str(likes_today+1), flush=True)
                except Exception as e: 
                    print(e)                
                    try:
                        like = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Unike']:not([class*='glyphsSpriteHeart__filled__16__white u-__7'])")))
                    except Exception as e: 
                        print(e)                
                        pass

                # Follow the account
                if p_follow > np.random.uniform() and self.followothers:
                    try:
                        acct_name = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME,"sqdOP.yWX7d._8A5w5.ZIAjV")))
                        follow = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, "sqdOP.yWX7d.y3zKF")))
                        follow.click()
                        followed += 1

                        print("now following " + acct_name.text)
                        self.unfollow_list.append((acct_name.text, datetime.datetime.now()))
                        pickle.dump(self.unfollow_list, open(self.name + '_follows.pkl', 'wb'))

                    except Exception as e: 
                        print(e)                
                        pass
            # Get the next post
            try:
                next_post = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Next')))
                next_post.click()
                viewed += 1
            except Exception as e: 
                print(e)                
                break

        return liked, followed

    # Goes through the list of accounts set to be unfollowed and unfollows
    # The ones which meet a certain time threshold
    def unfollow_accounts(self):
        updated_list = list()
        # Load pkl
        for account, follow_time in self.unfollow_list:
            #print((datetime.datetime.now() - follow_time).total_seconds())
            if (datetime.datetime.now() - follow_time).total_seconds() > 1.5*24*60*60:
                self.driver.get("https://www.instagram.com/" + account + "/")

                try:
                    unfollow = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[aria-label='Following']")))
                    unfollow.click()

                    confirm = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME,"aOOlW.-Cab_")))
                    confirm.click()

                    print("Automatically unfollowed " + account)
                except Exception as e: 
                    #print(e)      
                    # TODO handle accounts that have already been manually unfollowed
                    updated_list.append((account, follow_time))          
                    pass
            else:
                updated_list.append((account, follow_time))
            
        self.unfollow_list = updated_list

    def get_followers(self, acct_name = None):
        if acct_name is None:
            acct_name = self.username

        self.scraper = follower_tracker.FollowerScraper(self.driver, acct_name)
        self.scraper.scrape_followers()

    def set_follow_others(self, val):
        self.followothers = val

