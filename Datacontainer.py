import re
import os
import codecs
import io

class Datacontainer():
    # Class containing data for all the words and their level of "popularity"
    # As well as the 25 most "informative" words,
    # This is done for both positive and negative reviews seperately
    # Also contains static logic related to calculating this at bottom of class

    def __init__(self, pos_localpath, neg_localpath, n_words_lim, prun_val):
        self.pos_localpath = pos_localpath
        self.neg_localpath = neg_localpath
        self.n = n_words_lim
        self.prune_val = prun_val
        self.most_informative_pos = None
        self.most_informative_neg = None
        self.popularity_of_pos_words = None
        self.popularity_of_neg_words = None
        self.total_docs = None

    def get_most_informative_pos(self):
        if not self.most_informative_pos:
            self.calculate_most_informative_lists()
            return self.most_informative_pos
        return self.most_informative_pos

    def get_most_informative_neg(self):
        if not self.most_informative_neg:
            self.calculate_most_informative_lists()
            return self.most_informative_neg
        return self.most_informative_neg

    def get_popularity_of_pos_words(self):
        if not self.popularity_of_pos_words:
            self.calculate_popularity_of_words()
            return self.popularity_of_pos_words
        return self.popularity_of_pos_words

    def get_popularity_of_neg_words(self):
        if not self.popularity_of_neg_words:
            self.calculate_popularity_of_words()
            return self.popularity_of_neg_words
        return self.popularity_of_neg_words

    def get_total_docs(self):
        if not self.total_docs:
            self.calculate_popularity_of_words()
            return self.total_docs
        return self.total_docs

    def calculate_popularity_of_words(self):
        pos, no_p = Datacontainer.most_common_word_in_catalog(self.pos_localpath,self.n)
        neg, no_n = Datacontainer.most_common_word_in_catalog(self.neg_localpath,self.n)
        total_docs = no_p + no_n
        self.total_docs = total_docs

        pos_words_pruned = Datacontainer.pruner(pos, neg, total_docs, self.prune_val)
        neg_words_pruned = Datacontainer.pruner(neg, pos, total_docs, self.prune_val)

        self.popularity_of_pos_words = Datacontainer.calculate_popularity(pos_words_pruned, total_docs)
        self.popularity_of_neg_words = Datacontainer.calculate_popularity(neg_words_pruned, total_docs)

    def calculate_most_informative_lists(self):
        pos_words, no_of_pos_files\
            = (Datacontainer.most_common_word_in_catalog(self.pos_localpath, self.n))
        neg_words, no_of_neg_files \
            = (Datacontainer.most_common_word_in_catalog(self.neg_localpath, self.n))
        total_docs = no_of_neg_files + no_of_pos_files

        pos_words_pruned = Datacontainer.pruner(pos_words, neg_words, total_docs, self.prune_val)
        neg_words_pruned = Datacontainer.pruner(neg_words, pos_words, total_docs, self.prune_val)

        self.most_informative_pos \
            = Datacontainer.most_informative_word(pos_words_pruned,neg_words_pruned)
        self.most_informative_neg \
            = Datacontainer.most_informative_word(neg_words_pruned,pos_words_pruned)
        self.total_docs = no_of_pos_files + no_of_neg_files

########## STATIC LOGIC BELOW ##########

    @staticmethod
    def get_stop_words():
        stop_words = set()
        fil = io.open("stop_words.txt", encoding = "Latin-1")
        for linje in fil:
            stop_words.add(linje.rstrip("\n"))
        return stop_words

    @staticmethod
    def distinct_n_words_in_a_file(file, n):  # returns 1 upto n distinct n_words as set
        distinct_n_words = set()
        line = file.readline()
        words = re.split("[ /]", line)  # split words by space or /
        for i in range(0,len(words)):  # get to lower case and only alphanumeric
            words[i] = re.sub(r'\W+', '', words[i]).lower()
        while n > 0:
            distinct_n_words.update(Datacontainer.get_distinct_n_words_for_n(words,n))  # update set with another set
            n -= 1
        file.close()
        return distinct_n_words

    @staticmethod
    def get_distinct_n_words_for_n(words, n):
        set_out = set()
        stop_words = Datacontainer.get_stop_words()

        for i in range(0, 1 + len(words) - n):
            fancy_word = ""
            word_as_list = words[i:i + n]  # splice from i to n
            for subword in word_as_list:
                fancy_word += subword + "_"
            final_word = fancy_word.rstrip("_")
            if n == 1:  # stop_words only contains words of length 1, so this extra logic saves running time
                if not final_word in stop_words:
                    set_out.add(final_word)
            else:
                if "br" not in final_word:  # filter this HTML-stupidity
                    set_out.add(final_word)
        return set_out

    @staticmethod
    def most_common_word_in_catalog(localpath, n_word):
        dict = {}  # hash table containing words as keys and a number of occurences as values
        number_of_files_in_catalog = 0

        for filename in os.listdir(localpath):
            number_of_files_in_catalog += 1
            file = io.open(localpath + filename, encoding = "Latin-1")
            words_in_file = Datacontainer.distinct_n_words_in_a_file(file, n_word)
            for word in words_in_file:
                if word in dict:
                    dict[word] += 1  # increment number of occurences
                else:
                    dict[word] = 1  # initiliaze

        return dict, number_of_files_in_catalog

    @staticmethod
    def most_informative_word(dict_1, dict_2):  # calculating for first param dict_1
        out = {}  # hash table with words as keys and information-value as values
        for key in dict_1:
            try:
                out[key] = dict_1[key] / (dict_1[key] + dict_2[key])
            except KeyError:
                out[key] = 1
                # dict_3[key] = dict_1[key] / (dict_1[key] + 0) # dict_2 does not contain key and does not contribute to total sum, simply add 0

        sorted_vals = sorted(out, key=out.get, reverse=True)  # sort dict by values, return top 25
        return sorted_vals[:25]

    @staticmethod
    def pruner(dict_1, dict_2, total_docs, percentage = 0.03):
        out = {}  # returns dictionary where dict_1 has been pruned

        for key in dict_1:
            try:
                if (dict_1[key] + dict_2[key]) / total_docs > percentage:
                    out[key] = dict_1[key]
            except KeyError: #dict_2[key] is equal to zero, does not exist
                if dict_1[key] / total_docs > percentage:
                    out[key] = dict_1[key]
        return out

    @staticmethod
    def calculate_popularity(words_as_dict, no_of_files):
        out = {}
        for word in words_as_dict:
            out[word] = words_as_dict[word] / no_of_files
        return out