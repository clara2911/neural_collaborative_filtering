# creates two files csv_file.train.rating and csv_file.test.rating

import numpy as np
import random as rand


class CreateDatasets:

    def __init__(self, file):
        self.csv_file = file + ".csv"
        self.train_file = file + ".train.rating"

    def split_data(self):
        with open(self.csv_file, 'r') as f:
            with open(self.train_file, 'wb') as f_train:
                    #skip the first line
                    f.readline()
                    line = f.readline()
                    while line != None and line != "":
                        f_train.write(line)
                        line = f.readline()

