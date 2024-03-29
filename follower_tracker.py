# Tracks the followers on an instagram account
from time import sleep
import pickle
import numpy as np
import matplotlib.pyplot as plt
import metrics
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class FollowerScraper:

    IDX_GAIN = 0
    IDX_LOST = 1
    IDX_GAINLOST = 2

    def __init__(self, driver, account):
        self.driver = driver
        self.account = account
        self.numfollowers = 0
        self.followers = []

        # Open the old lists. Create them if they dont exist
        try:
            data_list = pickle.load(open("follower_lists.pkl", "rb"))
            self.gained = data_list[self.IDX_GAIN]
            self.lost = data_list[self.IDX_LOST]
            self.gain_and_lost = data_list[self.IDX_GAINLOST]
        except:
            self.gained = []
            self.lost = []
            self.gain_and_lost = []

        # Get the previous list of followers
        try:
            self.prev_followers = pickle.load(open("followers.pkl", "rb"))
        except FileNotFoundError:
            print("failed to load followers")
            self.prev_followers = []

    def scrape_followers(self):
        # Load account page
        self.driver.get("https://www.instagram.com/{0}/".format(self.account))

        # Get the total number of followers to look for        
        self.numfollowers = [int(s) for s in self.driver.find_element_by_partial_link_text("followers").text.split() if s.isdigit()]

        # Click the 'Follower(s)' link
        self.driver.find_element_by_partial_link_text("follower").click()

        # Wait for the followers modal to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_1XyCr")))

        # You'll need to figure out some scrolling magic here. Something that can
        # scroll to the bottom of the followers modal, and know when its reached
        # the bottom. This is pretty impractical for people with a lot of followers
        self.scrolldown()

        # Finally, scrape the followers
        xpath = "//div[@style='position: relative; z-index: 1;']//ul/li/div/div/div/div/a"
        followers_elems = self.driver.find_elements_by_xpath(xpath)

        return [e.text for e in followers_elems]

    def scrolldown(self):

        # Select the panel to scroll in
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.TAB)
        actions.perform()
        sleep(1)
        actions.send_keys(Keys.TAB)
        actions.perform()

        # Grab the container for the scrollbar
        container = self.driver.find_element_by_class_name("isgrP")#("PZuss")

        # Variables used to track when scrolling is done
        count = 0
        condition = 50
        lastheight = 0

        while True:
            # Scroll down
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', container)

            # Get document height
            height = self.driver.execute_script("return arguments[0].scrollHeight", container)
            sleep(0.05)

            # Grab all followers
            self.followers = container.find_elements_by_class_name("Jv7Aj.mArmR.MqpiF") 

            # Count how many iterations since the height last changed
            if height == lastheight:
                count += 1
            else:
                count = 0
            
            lastheight = height
            
            # Exit if scrolling has stalled for too long
            if count > condition:
                break

        self.followers = [account.text for account in self.followers]

    def save(self):
        pickle.dump(self.followers, open("followers.pkl", "wb"))
        self.make_lists()


    # Store 3 lists, gained, lost, and gained + lost. Reference last run's full list to determine who was gained and lost
    def make_lists(self):

        # Check that followers have been scraped
        if (len(self.followers) == 0):
            return

        # Find new and lost followers
        new_gains = np.ndarray.tolist(np.setdiff1d(self.followers, self.prev_followers))
        new_loss = np.ndarray.tolist(np.setdiff1d(self.prev_followers, self.followers))

        # Print updates
        for new_follow in new_gains:
            print(new_follow + " followed you")

        for lost_follow in new_loss:
            print(lost_follow + " unfollowed you")

        # Update the full follower lists
        self.gained = self.gained + new_gains
        self.lost = self.lost + new_loss
        self.gain_and_lost = list(set(self.gained) & set(self.lost))

        # Print the total amount of followers
        print('gained ' + str(len(self.gained)) + ' followers')
        print('lost ' + str(len(self.lost)) + ' followers')
        print(str(len(self.followers)) + ' total followers')

        # Save pickle data
        self.data_list =  [self.gained, self.lost, self.gain_and_lost]
        pickle.dump(self.data_list, open("follower_lists.pkl", "wb"))        


def trace_gains(show_plot = False):
    likes = pickle.load(open("metrics.pkl", "rb"))
    gained, lost, gained_and_lost = pickle.load(open("follower_lists.pkl", "rb"))

    hashtag_data = dict()

    # Search all gained followers
    for person in gained + lost:
        gain = 0
        lose = 0
        retain = 0

        if person in gained:
            gain = 1

        if person in lost:
            lose = 1

        if gain and not lose:
            retain = 1

        # Find what you liked from them
        if person in likes.keys():
            for like in likes[person]:

                # Count the hashtags
                if like.htag in hashtag_data.keys():
                    hashtag_data[like.htag] += metrics.HashtagData(gain, lose, retain)
                else:
                    hashtag_data[like.htag] = metrics.HashtagData(gain, lose, retain)

    # Convert data to plotting format
    plot_data = []
    tags = []
    for tag in hashtag_data:
        normalize = 0
        tags.append(tag)

        for person in likes:
            for like in likes[person]:
                if like.htag == tag:
                    normalize += 1

        plot_data.append([x/normalize for x in hashtag_data[tag].tolist()])

        #print('#' + tag + ' gained ' + str(hashtag_data[tag].gained) + ' followers from ' + str(normalize) + ' likes')

    if len(hashtag_data) != 0 and len(plot_data) != 0:
        plot_data = np.array(plot_data)
        plot_data = plot_data*100
        fig = plt.figure()

        plt.bar(tags, plot_data[:,0])
        plt.bar(tags, plot_data[:,1])
        plt.bar(tags, plot_data[:,2])
        plt.legend(['gain', 'lose', 'retain'])
        plt.xticks(rotation = 45)
        plt.subplots_adjust(bottom = 0.25)
        plt.ylabel("Probability of getting a follow per like (%)")

        if show_plot:
            plt.show() 
#trace_gains(show_plot=True)