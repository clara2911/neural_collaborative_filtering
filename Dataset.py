'''
Created on Aug 8, 2016
Processing datasets. 

@author: Xiangnan He (xiangnanhe@gmail.com)
'''
import scipy.sparse as sp
import numpy as np
import re

class Dataset(object):
    '''
    classdocs
    '''

    def __init__(self, path):
        '''
        Constructor
        '''
        self.trainMatrix = self.load_rating_file_as_matrix(path + ".train.rating")
        self.testRatings = self.load_rating_file_as_list(path + ".test.rating")
        self.testNegatives = self.load_negative_file(path + ".test.negative")
        assert len(self.testRatings) == len(self.testNegatives)
        
        self.num_users, self.num_items = self.trainMatrix.shape
        
    def load_rating_file_as_list(self, filename):
        ratingList = []
        with open(filename, "r") as f:
            # the first line does not contain data so skip it
            f.readline()
            line = f.readline()
            while line != None and line != "":
                arr = line.split("\t")
                user, item = int(arr[0]), int(arr[1])
                ratingList.append([user, item])
                line = f.readline()
        return ratingList
    
    def load_negative_file(self, filename):
        negativeList = []
        with open(filename, "r") as f:
            line = f.readline()
            while line != None and line != "":
                arr = line.split("\t")
                negatives = []
                for x in arr[1: ]:
                    negatives.append(int(x))
                negativeList.append(negatives)
                line = f.readline()
        return negativeList

    def get_meta_info(self, arr):
        age_groups = {"18-24":1,"25-34":2,"35-44":3,"45-54":4,"55-64":5,"65-":6, "NA":0}
        qual_classes = {"Q_1-3":1, "Q_4-7":2, "Q_8-10":3}
        easy_classes= {"E_1-3":1, "E_4-7":2, "E_8-10":3}
        meta_vector = np.zeros(8)
        k_group = int(arr[7][3])
        meta_vector[k_group-1] = 1

        age_group = re.sub('["\n\r]', '', arr[6])
        if age_group in age_groups:
            meta_vector[5] = age_groups[age_group]
        else:
            exit("%%%%%%%%%% ERROR, AGE_GROUP NOT FOUND: "+age_group)

        qual_class = re.sub('["\n\r]', '', arr[8])
        if qual_class in qual_classes:
            meta_vector[6] = qual_classes[qual_class]
        else:
            exit("%%%%%%%%%%%%% ERROR, QUAL_CLASS NOT FOUND: "+qual_class)
        easy_class = re.sub('["\n\r]', '', arr[9])
        if easy_class in easy_classes:
            meta_vector[7] = easy_classes[easy_class]
        else:
            exit("%%%%%%%%%% ERROR, EASY CLASS NOT FOUND: "+easy_class)
        return meta_vector

    
    def load_rating_file_as_matrix(self, filename):
        '''
        Read .rating file and Return dok matrix.
        The first line of .rating file is: num_users\t num_items
        '''
        print("reading data from file: ", filename)
        # Get number of users and items
        num_users, num_items = 0, 0
        with open(filename, "r") as f:
            line = f.readline()
            line = f.readline()
            while line != None and line != "":
                arr = line.split(";")
                u, i = int(arr[1]), int(arr[4].strip('"'))
                num_users = max(num_users, u)
                num_items = max(num_items, i)
                line = f.readline()
        # Construct matrix
        mat = sp.dok_matrix((num_users+1, num_items+10), dtype=np.float32)
        with open(filename, "r") as f:
            # skip the first line because its not data
            line = f.readline()
            line = f.readline()
            while line != None and line != "":
                arr = line.split(";")
                # quantity is the sixth column
                user, item, rating = int(arr[1]), int(arr[4].strip('"')), float(arr[5].split(",")[0])

                # get meta info about users and items
                meta_vector = self.get_meta_info(arr)

                if rating > 0:
                    mat[user, item] = 1.0 # should this be just rating to not lose quantity info?
                # append the meta vector to the end of the matrix
                mat[user, num_items+1:num_items+9] = meta_vector
                line = f.readline()
        print("  ")
        print("done making the matrix! Ow yeah")
        print("  ")
        return mat
