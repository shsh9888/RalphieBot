'''

	Input: a string
	Output: 

'''

# -*- coding: utf-8 -*-
import os
from collections import Counter
import string
import math
import json

import nltk

# Please download once
# nltk.download('averaged_perceptron_tagger')
from nltk.tag import pos_tag

script_dir = os.path.dirname(__file__)
wb = "wordbag.json"
wb = os.path.join(script_dir, wb)
wb = open(wb, "r")

courseKW = []
housingKW = []

wordBag = json.loads(wb.read())

# questionString = "what are the subjects offered by instructor James Martin is taking"
# questionString = "When is the subject CSCI112 CS12 taken by instructor ABC XYS"
# questionString = "When is the deadline for transcript submission"
questionString = "what are the subjects of CSCI offered in fall 2018"
# questionString = "who are the instructors teaching in fall 2018"

print (questionString)
tagged_sent = pos_tag(questionString.split())
# print tagged_sent

words = questionString.split(" ")

columns = {}

for iw, word in enumerate(words):
	if word in wordBag.keys():
		pn = []
		for ip in tagged_sent[iw+1:]:
			if ip[1] == 'NNP' or ip[1] == 'NN' or ip[1] == 'CD':
				pn.append(ip[0])
			elif ip[1] == 'IN':
				continue
			else:
				break
		columns[wordBag[word]] = [word]+pn

# propernouns = [word for word,pos in tagged_sent if pos == 'NNP']

# if len(propernouns) != 0:
# 	columns["PN"] = propernouns

print (columns)



# entry = "faculty = '"+propernouns[0]+"'"
# for pp in propernouns[1:]:
# 	entry += " OR faculty = '" + pp + "'"
# print entry