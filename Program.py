from Datacontainer import Datacontainer
from Classifier import Classifier

if __name__ == '__main__':

    traindata = Datacontainer("subset\\train\\pos\\", "subset\\train\\neg\\", 3, 0.03) # choosing 0.03 seems to give good informative words, but will prune away too much for punish in classifier

    print (traindata.get_most_informative_pos())
    print (traindata.get_most_informative_neg())

    #classifier = Classifier("alle\\test\\", data, 0.01)
    classifier = Classifier("subset\\test\\", traindata, 0.01)
    success_ratio = classifier.evaluate_docs()
    print (success_ratio)