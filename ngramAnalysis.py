import os
import string
import csv
import re

N = 'newline'
s = ' '

'''
Comments refer to unigrams, but apply to all ngrams
This function returns a list of sorted ngrams given a dictionary of lists of
split words
'''
def nGramList(reviewSplits):
    # Make unigram dictionary of dictionaries
    reviewUnigrams = {'t': {}, 'f': {}, 'd': {}}
        
    for key in reviewSplits:
        for word in reviewSplits[key]:
            if word in reviewUnigrams[key].keys():
                reviewUnigrams[key][word] += 1
            elif N not in word: 
                reviewUnigrams[key][word] = 1
            
    unigramLists = {}
                
    # Sort the unigrams, use k as iterator since key is a key word in sorted
    for k in reviewUnigrams:
        unigramLists[k] = sorted(reviewUnigrams[k].items(), key = lambda x:x[1])
        unigramLists[k].reverse()
    
    return unigramLists
    
'''
returns a dictionary with dominance scores and exclusive words to the false
corpus, where false corpus can refer to either the false corpus or the
deceptive corpus

c represents the corpus key, either 'f' or 'd'
'''
def calculateDominance(unigramLists, coverageDict, c):
    # Calculate dominance score using the false corpus
    falseDominances = {}
    falseExclusives = []
    for word in coverageDict['t']:
        if word in coverageDict[c]:
            falseDominances[word] = coverageDict['t'][word]/coverageDict[c][word]
        # Only include 0 dominance words if they have freuency greater than 2 in
        # the truth corpus
        elif unigramLists['t'][word] > 10: 
            falseDominances[word] = 0
                
    # Sort the dominances
    falseDominancesSorted = sorted(falseDominances.items(), key = lambda x:x[1])
    falseDominancesSorted.reverse()
                
    # Find all grams in the false corpus that aren't in the true corpus that
    # have frequency > 2
    for word in unigramLists[c]:
        if unigramLists[c][word] > 10 and word not in coverageDict['t']:
            falseExclusives.append(word)
    
    return {'dominance': falseDominancesSorted, 'exclusives': falseExclusives}
 
'''
Uses the methodology described in Mihalcea and Strapparva's paper calculating
dominance and coverage. Terminology refers to unigrams, but applies to all ngrams
'''  
def mihalceaMethodology(unigramLists):
    # Calculate the total number of words
    corpusSizes = {'t': 0, 'f': 0, 'd': 0}
    for key in unigramLists:
        for word in unigramLists[key]:
            corpusSizes[key] += unigramLists[key][word]
        # Make the sums into floats because coverages are decimals
        corpusSizes[key] = corpusSizes[key] * 1.0
        
    # Calculate coverage
    coverageDict = {'t': {}, 'f': {}, 'd': {}}
    for key in unigramLists:
        for word in unigramLists[key]:
            coverageDict[key][word] = unigramLists[key][word]/corpusSizes[key]
        
    falseTestResults = calculateDominance(unigramLists, coverageDict, 'f')
    deceptionTestResults = calculateDominance(unigramLists, coverageDict, 'd')
    
    return {'f': falseTestResults, 'd': deceptionTestResults}
    
'''
Converts a list of tuples of ngrams with counts to a dictionary
'''
def getNgramDict(ngramList):
    ngramDict = {'t': {}, 'f': {}, 'd': {}}
    for key in ngramList:
        for word in ngramList[key]:
            ngramDict[key][word[0]] = word[1]
    return ngramDict
    
'''
Writes out top twenty ngrams to files
pre is a string with the gram prefix (e.g. uni, bi, tri, etc.)
'''
def outputNgrams(ngramLists,pre):
    # Top 20 unigram files
    for key in ngramLists:
        with open('top_' + key + '_' + pre +'grams.txt', 'w') as output:
            topTwentyNgrams = ngramLists[key][:20]
            for gram in topTwentyNgrams:
                print>>output, gram
'''
Writes out dominance results to individual files
pre is a string with the gram prefix (e.g. uni, bi, tri, etc.)
'''                
def outputDominanceResults(gramDominances, pre):
    # Do this for true vs. false, then true vs. deceptive
    for key in gramDominances:
        # Output the 20 highest dominances
        with open('largest_' + key + '_' + pre + 'gram_dominances.txt', 'w') as output:
            topTwenty = gramDominances[key]['dominance'][:20]
            for gram in topTwenty:
                print>>output, gram
        # Output the 20 lowest dominances
        with open('smallest_' + key + '_' + pre + 'gram_dominances.txt', 'w') as output:
            topTwenty = gramDominances[key]['dominance'][-20:]
            topTwenty.reverse()
            for gram in topTwenty:
                print>>output, gram
        
        # Output the words exclusive to either false or deceptive with significant
        # occurences
        with open('exclusive_' + pre + 'grams_to_' + key + '.txt.', 'w') as output:
            for gram in gramDominances[key]['exclusives']:
                print>>output, gram           

'''
output each review corpus to an individual corpus
'''
def outputReviews(reviews):
    for key in reviews:
        with open(key+'_review.txt', 'w') as output:
            print>>output, s.join(reviews[key]).replace(N, '\n')
            
    
def parseCorpus():
    with open('BLT-C_Boulder_Lies_and_Truths_Corpus.csv', 'rb') as csvfile:
        corpDict = csv.DictReader(csvfile)
        # 't' contains the true reviews, 'f' contians the false reviews,
        # and 'd' contains the deceptive reviews.
        reviews = {'t': '', 'f': '', 'd': ''}
        
        # Parse through CSV file
        for row in corpDict:
            if row['Rejected'] is not '-':
                continue
            elif row['Truth Value'] is 'T':
                reviews['t'] += row['Review'] + s + N + s
            elif row['Truth Value'] is 'F':
                reviews['f'] += row['Review'] + s + N + s
            elif row['Truth Value'] is 'D':
                reviews['d'] += row['Review'] + s + N + s
        
        # Dictionary that splits the reviews into unigrams
        reviewSplits = {'t': '', 'f': '', 'd': ''}
        reviewsForNN = {'t': '', 'f': '', 'd': ''}     
        for key in reviews:
            # Preprocessing before splitting string into individual words for
            # each type of review
            # Decapitalize and remove all punctuation except for apostrophes
            # for ngram and dominance analysis
            reviews[key] = reviews[key].lower()
            # For the Neural Net version, keep the punctuation and just 
            # separate the puncutate into their own words
            reviews[key] = reviews[key].translate(None, "<>[]{}\/-_")
            reviewsForNN[key] = re.findall(r"[\w']+|[.,!?;]", reviews[key])
            reviews[key] = reviews[key].translate(None, '!"(),.:;?@[]\{}')
            
            # Split string for each review into individual words
            reviewSplits[key] = reviews[key].split() 
            
        
        # Make bigrams
        reviewBisplits = {'t': [], 'f': [], 'd': []}
        for key in reviewSplits:
            for i in range(len(reviewSplits[key]) - 1):
                if not(N in reviewSplits[key][i] or N in reviewSplits[key][i+1]):
                    reviewBisplits[key].append(reviewSplits[key][i] + s + reviewSplits[key][i+1])
        
        unigramLists = nGramList(reviewSplits)
        bigramLists = nGramList(reviewBisplits)
        
        # Convert the lists to dictionaries
        unigramListDict = getNgramDict(unigramLists)
        bigramListDict = getNgramDict(bigramLists)
        
        # Calculate dominances as detailed in Mihalcea and Strapparava
        unigramDominances = mihalceaMethodology(unigramListDict)
        bigramDominances = mihalceaMethodology(bigramListDict)
        
        # Write out important info to files!
        outputNgrams(unigramLists, 'uni')
        outputNgrams(bigramLists, 'bi')
        
        outputDominanceResults(unigramDominances, 'uni')
        outputDominanceResults(bigramDominances, 'bi')
        
        outputReviews(reviewsForNN)
        
        

def main():
    parseCorpus()
    
if __name__ == '__main__':
    main()