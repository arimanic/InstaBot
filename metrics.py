# Like metrics
import pickle
#import numpy as np
#import matplotlib.pyplot as plt

class Metrics:

    # Save metrics data
    def save(self):
        pickle.dump(self.data, open("metrics.pkl", "wb"))

    # Load existing metrics data. If it doesnt exist, create it.
    def load(self):
        try:
            self.data = pickle.load(open("metrics.pkl", "rb"))
        except FileNotFoundError:
            self.data = dict()
            self.save()


    # If hashtag data exists append to it
    # Otherwise create a new dict entry
    def add(self, acct_name, likedata):
        if acct_name in (self.data.keys()):
            self.data[acct_name].append(likedata)
        else:
            self.data[acct_name] = [likedata] # Make sure this is a list so its iterable
        
        self.save()
        

class LikeData:

    def __init__(self, tag, time):
        self.htag = tag
        self.timestamp = time


class HashtagData:
    def __init__(self, gain, lose, retain):
        self.gained = gain
        self.lost = lose
        self.retained = retain

    def __add__(self, other):
        g = self.gained + other.gained
        l = self.lost + other.lost
        r = self.retained + other.retained
        return HashtagData(g, l, r)

    def tolist (self):
        return[int(self.gained), int(self.lost), int(self.retained)]