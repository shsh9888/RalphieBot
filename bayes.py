'''

	Input: a string
	Output: 

'''

# -*- coding: utf-8 -*-
import os
from collections import Counter
import string
import math

script_dir = os.path.dirname(__file__)
rel_pathC = "coursesKeyWords.txt"
rel_pathH = "housingKeyWords.txt"
# rel_test = "HW3-testset.txt"

courseFP = os.path.join(script_dir, rel_pathC)
housingFP = os.path.join(script_dir, rel_pathH)

fh = open(housingFP, "r")
fc = open(courseFP, "r")

courseKW = []
housingKW = []

for line in fh.readlines():
	courseKW.append(line[:-1])

for line in fc.readlines():
	housingKW.append(line[:-1])
print (courseKW, housingKW)