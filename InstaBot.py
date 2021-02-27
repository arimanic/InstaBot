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

class InstaBot:
    # Starts the bot
    def __init__(self, username, pw, reset, headless = True):

        # Initialize the web driver
        self.options = Options()
        self.options.headless = headless
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(5)
        self.driver.get("https://instagram.com")
        self.username = username

        # Load metrics
        self.metrics = metrics.Metrics()
        self.metrics.load()

        # Load the hashtags to like from
        self.hashtags = np.genfromtxt("hashtags.txt", comments='#', dtype='str')
        
        # List of people to unfollow
        try:
            self.unfollow_list = pickle.load(open("follows.pkl", "rb"))
        except:
            self.unfollow_list = list()

        # Choose a fresh login or to use cookies. If using headless mode you must use cookies
        if reset and not self.options.headless:
            self.driver.find_element_by_xpath("//input[@name=\"username\"]")\
                .send_keys(username)
            self.driver.find_element_by_xpath("//input[@name=\"password\"]")\
                .send_keys(pw)
            self.driver.find_element_by_xpath('//button[@type="submit"]')\
                .click()
            self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]")\
                .click()
            
            # Save cookies
            pickle.dump(self.driver.get_cookies() , open("cookies.pkl","wb"))
        else:

            # Load the cookies and add them all to the web driver
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    # Call this to ensure all data is saved properly
    def release(self):
        # Dump the list of followers
        self.unfollow_accounts()
        pickle.dump(self.unfollow_list, open("follows.pkl", "wb"))
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

        printflag = False # Set to true when data changes
        
        # Stats
        liked = 0 
        followed = 0
        viewed = 0

        # Random probability thresholds
        p_like = 1/21 # Probability of liking a post
        p_break = 1/200 # Probability of switching hashtags
        p_follow = 0/5 # Probability of following account after liking photo

        # Click the first thumbnail
        first_thumbnail = self.driver.find_element_by_class_name('_9AhH0')
        first_thumbnail.click()

        while liked != maxlikes:
            
            # wait random time on each post
            sleep(random.uniform(3.0, 10.0))

            # wait for the page to be ready
            WebDriverWait(self.driver, 30).until(lambda *args: (self.driver.execute_script("return document.readyState") == "complete"))

            # check to switch hashtag
            if p_break > np.random.uniform():
                break

            # check to like the current photo
            if p_like > np.random.uniform():

                # Like the photo          
                try:
                    like = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Like']:not([class*='glyphsSpriteHeart__filled__16__white u-__7'])")))
                    like.click()
                    liked += 1
                    printflag = True

                    # Store the like metrics
                    acct_name = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME,"sqdOP.yWX7d._8A5w5.ZIAjV"))).text
                    self.metrics.add(acct_name, metrics.LikeData(tag, datetime.datetime.now()))

                except:
                    try:
                        like = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Unike']:not([class*='glyphsSpriteHeart__filled__16__white u-__7'])")))
                    except:
                        pass

                # Follow the account
                if p_follow > np.random.uniform():
                    try:
                        acct_name = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME,"sqdOP.yWX7d._8A5w5.ZIAjV")))
                        follow = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, "sqdOP.yWX7d.y3zKF")))
                        follow.click()
                        followed += 1

                    except:
                        pass
            # Get the next post
            try:
                next_post = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Next')))
                next_post.click()
                viewed += 1
            except :
                break

            # Write info to console
            if printflag:
                print(str(liked) + ' Posts liked out of ' + str(viewed) + ' views', flush=True)
                printflag = False

        return liked, followed

    # Goes through the list of accounts set to be unfollowed and unfollows
    # The ones which meet a certain time threshold
    def unfollow_accounts(self):
        updated_list = list()

        for account, follow_time in self.unfollow_list:
            print((datetime.datetime.now() - follow_time).total_seconds())
            if (datetime.datetime.now() - follow_time).total_seconds() > 3*24*60*60:
                self.driver.get("https://www.instagram.com/" + account + "/")

                try:
                    unfollow = WebDriverWait(self.driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[aria-label='Following']")))
                    unfollow.click()

                    confirm = WebDriverWait(self.driver, 4).until(EC.element_to_be_clickable((By.CLASS_NAME,"aOOlW.-Cab_")))
                    confirm.click()

                except:
                    pass
            else:
                updated_list.append((account, follow_time))
            
        self.unfollow_list = updated_list

    def get_followers(self, acct_name = None):
        if acct_name is None:
            acct_name = self.username

        self.scraper = follower_tracker.FollowerScraper(self.driver, acct_name)
        self.scraper.scrape_followers()

