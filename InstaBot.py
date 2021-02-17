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

import numpy as np
hashtag_list = np.genfromtxt("hashtags.txt", comments='#', dtype='str')

class InstaBot:
    # Starts the bot
    def __init__(self, username, pw, reset):
        self.options = Options()
        self.options.headless = False
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(5)
        self.driver.get("https://instagram.com")
        self.username = username
        
        try:
            self.unfollow_list = pickle.load(open("follows.pkl", "rb"))
        except:
            self.unfollow_list = list()

        if reset:
            self.driver.find_element_by_xpath("//input[@name=\"username\"]")\
                .send_keys(username)
            self.driver.find_element_by_xpath("//input[@name=\"password\"]")\
                .send_keys(pw)
            self.driver.find_element_by_xpath('//button[@type="submit"]')\
                .click()
            self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]")\
                .click()
            pickle.dump(self.driver.get_cookies() , open("cookies.pkl","wb"))
        else:
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def release(self):
        # Dump the list of followers
        self.unfollow_accounts()
        pickle.dump(self.unfollow_list, open("follows.pkl", "wb"))

    # Likes pictures scraped from a hashtag up to maxlikes
    def like_hashtags(self, hashtags, maxlikes):
        total_likes = 0
        total_follows = 0
        t = time.time()

        while total_likes != maxlikes:
            tag = random.choice(hashtags)
            print("Looking at #" + str(tag))

            self.driver.get("https://www.instagram.com/explore/tags/" + tag + "/")
            new_likes, new_follows = self.like_loop(maxlikes - total_likes)
            total_likes += new_likes
            total_follows += new_follows

            elapsed = time.time() - t
            print("Likes per hour = " +  str(total_likes * 3600/elapsed) + ' - Total Likes = ' + str(total_likes) + 
            " Follows per hour = " +  str(total_follows * 3600/elapsed) + ' - Total Follows = ' + str(total_follows))


    # The loop used to like posts
    def like_loop(self, maxlikes):

        first_thumbnail = self.driver.find_element_by_class_name('_9AhH0')
        first_thumbnail.click()

        printflag = False # Set to true when data changes
        liked = 0 
        followed = 0
        viewed = 0
        p_like = 1/18 # Probability of liking a post
        p_break = 1/150 # Probability of switching hashtags
        p_follow = 0/5 # Probability of following account after liking photo

        while liked != maxlikes:
            
            # wait random time on each post
            sleep(random.uniform(2.0, 10.0))

            # wait for the page to be ready
            WebDriverWait(self.driver, 30).until(lambda *args: (self.driver.execute_script("return document.readyState") == "complete"))

            # check to switch hashtag
            if p_break > np.random.uniform():
                print(str(liked) + ' Posts liked out of ' + str(viewed) + ' views', flush=True)
                return liked, followed

            # check to like the current photo
            if p_like > np.random.uniform():

                # Like the photo          
                try:
                    like = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Like']:not([class*='glyphsSpriteHeart__filled__16__white u-__7'])")))
                    like.click()
                    liked += 1
                    printflag = True
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


                        # Save the followed accounts and the timestamp
                        mytime = datetime.datetime.now()
                        name = acct_name.text

                        x = (name, mytime)

                        self.unfollow_list.append(x)
                    except:
                        pass

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

        print(str(liked) + ' Posts liked out of ' + str(viewed) + ' views', flush=True)
        return liked, followed

    def scrolldown(self):
        SCROLL_PAUSE_TIME = 1

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            #sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

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






reset = 0

username, password = np.genfromtxt('secret.txt', dtype='str', comments='#', unpack=True)

bot = InstaBot(username, password, reset)
bot.like_hashtags(hashtag_list, 200)
bot.release()

# Sort hashtags by activity

# set a root hashtag
# scrape A LOT of hashtags
# store their amount of posts and the time the number was pulled from
# reach x amount of hashtags
# 
