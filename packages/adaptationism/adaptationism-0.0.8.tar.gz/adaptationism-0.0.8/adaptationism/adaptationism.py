import re
import json
import pandas as pd
from nltk import sent_tokenize, word_tokenize, ngrams
import nltk
import os
import string
from collections import defaultdict
from collections import Counter

def compute_usage(corpus, gram_length):
    entropylist = defaultdict(list)
    # entropylist represents a nested breakdown of all the words associated
    # before and after the appearance of another word
    '''
    Only punctuation and special characters are removed from the corpus.
    All other elements are kept.
    '''
    removals = string.punctuation + '``'

    for com in corpus:
        ngram_statement = [str(i) for i in ngrams([iter for iter in word_tokenize(com) if iter not in removals], gram_length)]
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
                entropylist['[start]'].append(gram_clean.lower())
                recent_list.append(gram_clean.lower())
                counter += 1
            elif counter > 0:
                entropylist[str(recent_list[len(recent_list)-1])].append(str(gram_clean.lower()))
                recent_list.append(gram_clean.lower())
                counter += 1
            elif counter == len(ngram_statement):
                entropylist[str(recent_list[len(recent_list)-1])].append('[end]')
                recent_list.append('[end]')
                counter += 1


    # Usage count represents the appearance of words (in their respective order)
    # and the counts of THOSE words
    usage_count = {}
    for key in entropylist:
        count_vals = {}
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

        usage_count[str(val)] = [count_vals]

    return {'usage':usage_count, 'entropylist':entropylist}


def transition_table(corpus, gram_length=1):
    '''
    Slated improvements to this function:
    - allow for custom stopwords to be removed from the various grams being measured
    - allow the corpus to be either a list of verbatims, or a pandas dataframe
      for segementation
    '''

    '''
    Description:
    - Returns the set of transition tables (transition tables) based on the
      length of gram_length supplied by the user (default length 1)
    - 'corpus' must be a (python) list of statements
    - 'gram_length' must be a whole integer
    '''
    all_entropy = {}
    usage_info = compute_usage(corpus, gram_length)

    for key in usage_info['entropylist']:
        cond_prob_val = {}
        relative_usage = Counter(usage_info['entropylist'][key])
        relative_words_len = sum(relative_usage.values())

        for following_gram in relative_usage:
            if key in cond_prob_val:
                cond_prob_val[following_gram].append([float(relative_usage[following_gram]) / float(relative_words_len)])
            else:
                cond_prob_val[following_gram] = [[float(relative_usage[following_gram]) / float(relative_words_len)]]

        if key in all_entropy:
            all_entropy[key].append(cond_prob_val)
        else:
            all_entropy[key] = [[cond_prob_val]]

    '''forcing everyone to move to JSON read/write :) '''
    return json.dumps(all_entropy)


def gram_stats(corpus, gram_length=1):
    '''
    Slated improvements to this function:
    - None at this time
    '''

    '''Description:
    - Returns a JSON file that describes how grams (default length 1)
    - Fields of interest returned include:
        - gram,
        - % usage across corpus (by row)
    '''
    usage_info = compute_usage(corpus, gram_length)

    # iterate through all the different grams, perform pattern matching, and then
    # return the overall % appearance within the corpus
    appearance_dict = {}
    total_rows = len(corpus)
    flat_keys = list(set([item for item in usage_info['usage']]))
    removals = string.punctuation + '``'

    for key in flat_keys:
        gram_appear = 0
        new_key = key
        for r in removals:
            new_key = new_key.replace(r, '')

        for row in corpus:
            if key in row:
                gram_appear += 1

        appearance_dict[new_key] = [round(float(gram_appear) / float(total_rows), 8)]
    return json.dumps(appearance_dict)
