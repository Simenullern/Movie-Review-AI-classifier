from Datacontainer import Datacontainer
import os
import math
import codecs
import io

class Classifier():
    # Class holds logic for classifying a file and giving a success-rate for folder

    def __init__(self, localpath, datacontainer, epsillon = 0.02):
        self.localpath = localpath
        self.pos_populs = datacontainer.get_popularity_of_pos_words()
        self.neg_populs = datacontainer.get_popularity_of_neg_words()
        self.num_of_files = datacontainer.get_total_docs()
        self.epsillon = epsillon

    def evaluate_docs(self):
        correct_classifies = 0

        for directory in os.listdir(self.localpath):
            for filename in (os.listdir(self.localpath + directory)):
                file = io.open(self.localpath + directory + "\\" + filename, encoding = "Latin-1")
                c = self.classify_file(file)
                if c > 0 and directory == "pos":
                    correct_classifies += 1
                elif c < 0 and directory == "neg":
                    correct_classifies += 1

        return str(round(correct_classifies * 100 / self.num_of_files, 2)) + " % hit ratio"

    def classify_file(self, file):
        unique_words = Datacontainer.distinct_n_words_in_a_file(file, 1)
        pos_score = 0
        neg_score = 0

        for word in unique_words:
            if word in self.pos_populs:
                pos_score += math.log(self.pos_populs[word])
                if not word in self.neg_populs: #these happen rarely unless prun-value is low
                    #print ("punish")
                    neg_score -= self.epsillon #punish
            if word in self.neg_populs:
                neg_score += math.log(self.neg_populs[word])
                if not word in self.pos_populs:
                    #print ("punish")
                    pos_score -= self.epsillon
        file.close()

        if pos_score > neg_score:
            return 1
        else:
            return -1