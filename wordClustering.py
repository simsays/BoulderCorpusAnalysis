import os
import string
from nltk.corpus import wordnet as wn
import glob

'''
Loops through every definition of each word of the synsets and returns
the highest score (maxScore is 1)
'''
def calcWNScore(word1, word2):
    syn1 = wn.synsets(word1)
    syn2 = wn.synsets(word2)
    maxScore = 0
    for meaning1 in syn1:
        for meaning2 in syn2:
            score = meaning1.path_similarity(meaning2)
            if score is None:
                score = 0
            if score > maxScore:
                maxScore = score
    return maxScore

'''
Uses a use-it or lose-it recursive methodology to find the closest matching
set of words
Returns the set of words and its score (maxScore is 3)
'''
def findClosestWords(wordList, closestWords, score):
    if len(wordList) is 0:
        return closestWords, score
    if len(closestWords) < 3:
        # Define use it
        useItWords = closestWords[:]
        useItWords.append(wordList[0])
        if len(useItWords) is 1:
            useItScore = 0
        else:
            useItScore = calcWNScore(useItWords[0],useItWords[1])
            if len(closestWords) > 2:
                useItScore += calcWNScore(useItWords[0],useItWords[2])
                useItScore += calcWNScore(useItWords[1],useItWords[2])
        
        # Define lose it
        loseItWords = closestWords
        if len(closestWords) > 1:
            loseItScore = calcWNScore(loseItWords[0], loseItWords[1])
        else:
            loseItScore = 0
        
        # Recursive call
        recursiveLoseItWords, recursiveLoseItScore = findClosestWords(wordList[1:], loseItWords, loseItScore)
        recursiveUseItWords, recursiveUseItScore = findClosestWords(wordList[1:], useItWords, useItScore)
        
        if recursiveUseItScore < recursiveLoseItScore:
            return recursiveLoseItWords, recursiveLoseItScore
        else:
            return recursiveUseItWords, recursiveUseItScore
    else:
        return closestWords, score
        
'''
Extracts the words from the file and sends them into findClosestWords
Then outputs the closest set of words and its score (out of 3) into a
corresponding cluster text file
'''
def clusterWords(listPath):
    with open(listPath) as f:
        tupleList = [tuple(i.split(',')) for i in f]
        wordList = []
        for tup in tupleList:
            wordList.append(tup[0].translate(None, string.punctuation))
        closestWords, score = findClosestWords(wordList, [], 0)
        
        with open('cluster_' + listPath, 'w') as output:
            print>>output, closestWords
            print>>output, score
    
'''
Loops through each unigram dominance file and calls clusterWords on it
'''
def main():
    fileList = glob.glob('*unigram_dominances.txt')
    for fileName in fileList:
        clusterWords(fileName)
    
if __name__ == '__main__':
    main()