import json
import pandas as pd
from nltk import sent_tokenize, word_tokenize, ngrams
import nltk
import os
import string
from collections import defaultdict

def transition_table(corpus, gram_length):
    '''
    Slated improvements to this function:
    - allow for custom stopwords to be removed from the various grams being measured
    - other?
    '''

    '''
    Description of function:
    - Returns the set of transition tables (transition tables) based on the
      length of gram_length supplied by the user
    - 'corpus' must be a (python) list of statements
    - 'gram_length' must be a whole integer
    '''
    entropylist = defaultdict(list)

    '''
    Only punctuation and special characters are removed from the corpus.
    All other elements are kept.
    '''
    removals = string.punctuation + '``'

    for com in corpus:
        ngram_statement = [str(i) for i in ngrams([iter for iter in word_tokenize(str(com)) if iter not in removals], gram_length)]
        counter = 0
        recent_list = []
        for gram in ngram_statement:

            '''
            This manipulation of the length of each gram is done because
            of the formatting that is applied to the string format when
            being passed through word_tokenize.
            '''
            gram_clean = gram[2:len(gram)-3]

            if counter == 0:
                '''
                Depending on the position and length of the gram, it is
                necessary to denote the beginning of a statement.
                '''
                entropylist['[start]'].append([gram_clean.lower()])
                recent_list.append([gram_clean.lower()])
                counter += 1
            else:
                entropylist[str(recent_list[len(recent_list)-1])].append(str(gram_clean.lower()))
                recent_list.append([gram_clean.lower()])
                counter += 1

    # create the conditional probability list to calculate odds based on the word
    all_entropy = {}
    for key in entropylist:
        count_vals = {}
        words_connect = len(entropylist[key])

        '''
        Increment the appearance of the grams that appear within the gram.
        This will allow us to then determine the conditional probability of the
        appearnace of the next phrase in a sequence.
        '''
        for val in entropylist[key]:
            if str(val) in count_vals:
                count_vals[str(val)] += 1
            else:
                count_vals[str(val)] = 1

        cond_prob_val = {}
        for count_info in count_vals:
            cond_prob_val[count_info] = float(count_vals[count_info]) / float(words_connect)
        all_entropy[key] = [cond_prob_val]

    return json.dumps(all_entropy)
