'''
Created on Aug 8, 2016
Processing datasets. 

@author: Xiangnan He (xiangnanhe@gmail.com)
'''
import scipy.sparse as sp
import numpy as np
import re
import os
import random as rand

food_ids = set()
pos_samples = dict()

class Dataset(object):
    '''
    classdocs
    '''



    def __init__(self, path):
        '''
        Constructor
        '''
        self.trainMatrix = self.load_rating_file_as_matrix(path)
        self.testRatings = self.load_rating_file_as_list(path + ".test.rating")
        self.testNegatives = self.load_negative_file(path + ".test.negative")
        self.testNegatives = self.testNegatives[:len(self.testRatings)]
        print(len(self.testRatings))
        print(len(self.testNegatives))
        assert len(self.testRatings) == len(self.testNegatives)
        
        self.num_users, self.num_items = self.trainMatrix.shape
        # self.food_ids = set()
        # food_ids = set()
    #
    # def add_item(self,id):
    #     self.food_ids.append(id)

    def load_rating_file_as_list(self, filename):
        ratingList = []
        with open(filename, "r") as f:
            # the first line does not contain data so skip it
            f.readline()
            line = f.readline()
            k=0
            while line != None and line != "" and k<100:
                arr = line.split(";")
                u, i = int(arr[1]), int(arr[4].strip('"'))
                ratingList.append([u, i])
                if (i not in food_ids):
                    food_ids.add(i)
                line = f.readline()
                k+=1
        return ratingList
    
    def load_negative_file(self, filename):
        negativeList = []
        with open(filename, "r") as f:
            line = f.readline()
            for k in range(100):
            #while line != None and line != "":
                arr = line.split(";")
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

    
    def load_rating_file_as_matrix(self, path):
        '''
        Read .rating file and Return dok matrix.
        The first line of .rating file is: num_users\t num_items
        '''
        filename = path + ".train.rating"
        # print("reading data from file: ", filename)

        # Get number of users and items
        num_users, num_items = 0, 0
        with open(filename, "r") as f:
            line = f.readline()
            line = f.readline()
            for k in range(100):
            # while line != None and line != "":
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
            prev_user_id = None
            #while line != None and line != "":
            for k in range(100):
                arr = line.split(";")
                # quantity is the sixth column
                user, item, rating = int(arr[1]), int(arr[4].strip('"')), float(arr[5].split(",")[0])
                if user not in pos_samples:
                    pos_samples[user] = []
                pos_samples[user].append(item)
                if item not in food_ids:
                    food_ids.add(item)
                # get meta info about users and items
                meta_vector = self.get_meta_info(arr)

                if rating > 0:
                    mat[user, item] = 1.0 # should this be just rating to not lose quantity info?
                # append the meta vector to the end of the matrix

                if user != prev_user_id:
                    with open(path+'.test.rating', "a") as test_file:
                        #print("writing line in test ratings: ", line)
                        test_file.write(line)
                    with open(path+'.test.negative_ids', "a") as neg_test_file:
                        # print("writing item in test negatives: ", str(user+","+item))
                        neg_test_file.write(str(user)+","+str(item) + "\n")

                else:
                    mat[user, num_items+1:num_items+9] = meta_vector
                line = f.readline()
                prev_user_id = user
        self.construct_neg_test(path)
        print("  ")
        print("############## DONE MAKING THE MATRIX OW YEAH ######################")
        print("  ")
        return mat

    def construct_neg_test(self, path):
        with open(path+'.test.negative_ids', 'r') as f:
            with open(path+'.test.negative', 'a') as f_new:
                user_id_tuple = f.readline()
                for k in range(100):
                #while user_id_tuple != None and user_id_tuple != "":
                    user_id = int(user_id_tuple.split(",")[0])
                    pos_user_samples = []
                    if user_id in pos_samples:
                        pos_user_samples = pos_samples[user_id]
                    # options = set(food_ids).symmetric_difference(set(pos_user_samples))
                    options = list(set(food_ids) - set(pos_user_samples))
                    # print("options")
                    # print(len(options))
                    # print(len(options))
                    neg_samples = rand.sample(options, 2)
                    string_list = []
                    for i in neg_samples:
                        string_list.append(str(i))
                    f_new.write("\t".join(string_list)+"\n")
                    user_id_tuple = f.readline()


