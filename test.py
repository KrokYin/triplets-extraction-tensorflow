
import json
import nltk
import unicodedata

def find_index(sen_split, word_split):
    """
    Here are one problem: if word_split is ['Michael', 'Jackson'] while sen_split contains 'Michael' and 'Jordan'
    located in position 3 and 4 respectively('Michael' and 'Jackson' may be 10, 11), then it will return 3,5.It is
    not true !!!
    :param sen_split: all tokens of a sentence
    :param word_split: all token of a word
    :return:
    """
    index1 = -1
    index2 = -1
    for i in range(len(sen_split)):
        if str(sen_split[i]) == str(word_split[0]):
            flag = True
            k = i
            for j in range(len(word_split)):
                if word_split[j] != sen_split[k]:
                    flag = False
                if k < len(sen_split) - 1:
                    k+=1
            if flag:
                index1 = i
                index2 = i + len(word_split)
                break
    return index1, index2


sen_split = ['Many','basketball','fans','love','Michael','Jackson','while','music', 'fans', 'like',
             'Michael', 'Jordan','.']
word_split = ['Michael', 'Jackson']
index1, index2 = find_index(sen_split[6:], word_split)
print index1, index2
