# -*- coding: utf-8 -*-

#import operator
#import os
import numpy as np
import pkg_resources

class namesex_light:
    def __init__(self):
        #pkg_resources.resource_filename('namesex_light','models/lr_raw.pickle')
        #self.gname_count = dict()
        #self.gnameug_count = dict()
        self.feat_dict = dict()
        #self.num_gname = 0
        self.num_feature = 0
        #self.lrmodel = None
        self.lrmodelintcp = None
        self.lrmodelcoef = None

        self.load_model()


    def feature_coding(self, aname):
        tmpfeat = list()
        has_other = 0
        if aname in self.feat_dict:
            tmpfeat.append(self.feat_dict[aname])

        for achar in aname:
            if achar in self.feat_dict:
                tmpfeat.append(self.feat_dict[achar])

        if len(tmpfeat) == 0:
            tmpfeat.append(self.feat_dict["_Other_Value_"])
        return tmpfeat

    def gen_feat_array(self, namevec):
        #name_given_int = list()
        x_array = np.zeros((len(namevec), self.num_feature), "int")
        for id, aname in enumerate(namevec):
            #name_given_int.append(self.feature_coding(aname))
            x_array[id, self.feature_coding(aname)] = 1
        return x_array


    def predict(self, namevec, predprob = False):
        #use scikit-learn to predict
        #from sklearn import linear_model
        if len(self.feat_dict) == 0:
            print("Warning: No feature table! Maybe load_model() first?")
        x_array = self.gen_feat_array(namevec)

        #if predprob == True:
        #    ypred = self.lrmodel.predict_proba(x_array)
        #else:
        #    ypred = self.lrmodel.predict(x_array)
        tmp1 = np.matmul(x_array, self.lrmodelcoef) + self.lrmodelintcp
        ypred = 1/(1+np.exp(-tmp1))
        ypred = ypred.squeeze()
        if predprob == True:
            return ypred
        else:
            return np.asarray(ypred >= 0.5, "int")


    def load_model(self, filename = pkg_resources.resource_filename('namesex_light','model/logic_light.pickle')):
        import pickle
        with open(filename, "rb") as f:
            model = pickle.load(f)

        self.lrmodelcoef = model["lrmodelcoef"]
        self.lrmodelintcp = model["lrmodelintcp"]
        self.feat_dict = model["feat_dict"]
        self.num_feature = model["num_feature"]

if __name__ == "__main__":
    import csv
    #from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
    import pickle

    #mode = "evaluate" # look at performance using a train-test split
    #mode = "train_production" #train a model for production
    #only this is working for now
    mode = "explore"

    #load data
    f = open('namesex_data_v2.csv', 'r', newline='', encoding = 'utf8')
    mydata = csv.DictReader(f)
    sexlist = []
    namelist = []
    foldlist = []
    for arow in mydata:
        sexlist.append(int(arow['sex'].strip()))
        gname = arow['gname'].strip()
        namelist.append(gname)
        foldlist.append(int(arow['fold'].strip()))

    sexlist = np.asarray(sexlist)
    namelist = np.asarray(namelist)
    foldlist = np.asarray(foldlist)


    if mode == "explore":
        sex_train = sexlist[foldlist != 9]
        sex_test = sexlist[foldlist == 9]

        name_train = namelist[foldlist != 9]
        name_test = namelist[foldlist == 9]

        nsl = namesex_light()
        #nsl.train(name_train, sex_train, c2=10)
        nsl.load_model()
        ypred = nsl.predict(name_test, predprob = True)
        ypred2 = nsl.predict(name_test, predprob=False)

        ind1 = sex_test == ypred2
        acc = np.mean(ind1)
        print("accuracy = ", acc)

