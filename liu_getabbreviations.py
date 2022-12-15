################################################################
#   Section 1: Reading the Input File   ########################
################################################################


# regex will help with identifying alphabetical words
#     in a name
import re


# cleanLine is a helper function that takes a string
#     cleanLine outputs a string which has had any whitespace and new line 
#     characters removed
def cleanLine(line):
    line = line.strip()
    if '\n' in line:
        line = line[:-2]
    return line


# cleanNames accepts a string representing the file path of the input file
#     and outputs nested list containing the words that constitute each name
#     as well as a list of the original names for later use
#     cleanNames assumes that each new line in the data contains only one name
def cleanNames(namesfilepath):
    cleanednames = []
    originalnames = []

    with open(namesfilepath) as file:
        file = list(file)

        for name in file:

            # Removing whitespace, new line characters if needed and apostrophes
            #     but before the apostrophes, keeping a copy of the original name inside originalnames
            name = cleanLine(name)
            originalnames.append(name)

            name = re.sub("'",'',name)

            # Splitting the name where there is a non-alphabetical character
            #   and removing the empty string if one appears
            name = re.split(r"[^A-Za-z]+",name)
            if name[-1] == '':
                del name[-1]

            cleanednames.append(name)
    
    return cleanednames, originalnames
    



################################################################
#   Section 2: Computing the Abbreviations   ###################
################################################################


# formatScores accepts a string representing the file path of the input file
#     and a nested list of strings representing the properly-formatted names
# formattedScores outputs a nested list containing the scores corresponding 
#     to each letter in each word
def formatScores(scoresfilepath,cleanednames):
    formattedscores = []
    scoredictionary = {}

    # First importing the file that contains the scores for each value and placing
    #     them in a dictionary
    with open(scoresfilepath) as file:
        file = list(file)

        for pair in file:

            pair = cleanLine(pair)

            pair = re.split(r'[ ]+',pair)
            if pair[-1] == '':
                del pair [-1]
            
            scoredictionary.update({pair[0]:int(pair[1])})

    # Calculating the base score for each letter while placing the scores
    #     in the same nested list format as the names
    for name in cleanednames:
        formattedscores.append([])
        for word in name:
            formattedscores[-1].append([])
            for letter in word:
                formattedscores[-1][-1].append(scoredictionary[letter.upper()])

    # Moving through each letter of each word in each name to modify the score based
    #     on position. Due to needing to check if the last letter of each word is e,
    #     indices are used so that the corresponding letter in the names can be accessed
    for nameindex in range(len(formattedscores)):
        for wordindex in range(len(formattedscores[nameindex])):
            for letterindex in range(len(formattedscores[nameindex][wordindex])):
                if letterindex == 0:
                    formattedscores[nameindex][wordindex][letterindex] = 0
                elif letterindex == len(formattedscores[nameindex][wordindex])-1:
                    if cleanednames[nameindex][wordindex][letterindex].upper() == 'E':
                        formattedscores[nameindex][wordindex][letterindex] = 20
                    else:
                        formattedscores[nameindex][wordindex][letterindex] = 5
                elif letterindex >= 3:
                    formattedscores[nameindex][wordindex][letterindex] += 3
                else:
                    formattedscores[nameindex][wordindex][letterindex] += letterindex

    return formattedscores


# The subseq2OrCalculateScore function is used as a helper function within the abbreviate function

# The subseq2OrCalculateScore function is a modified subseq2 function takes in a string and computes all 2-letter pairs
#     or a list of integers and computes all 2-integer sums
# The order of the letters or integers is maintained so no
#     pairs or sums will be generated where a letter/integer from later in the string/list
#     appears before letter/integer earlier in the string/list
def subseq2OrCalculateScore(intlistorstr):
    newstr = []
    for i in range(len(intlistorstr)):
        for j in range(i+1,len(intlistorstr)) :
            newstr.append(intlistorstr[i] + intlistorstr[j])
    
    return newstr


# abbreviate takes in two nested lists, cleanednames and cleanedscores
#     which contain a nested list of strings representing the words in each name
#     and a doubly-nested list of integer scores corresponding to each letter, respectively
# abbreviate will output two nested lists, one containing the abbreviations for each word
#     and the other containing the total score for each abbreviation
def abbreviate(cleanednames,formattedscores):
    abbreviations = []
    abbreviationscores = []
    
    for nameindex in range(len(cleanednames)):
        flattenedscores = [] 
        
        # Flattening the letter scores for each word in a name into a single list
        for wordscorelist in formattedscores[nameindex]:
            for letterscore in wordscorelist:
                flattenedscores.append(letterscore)
        
        # Combining the words in a name into a single concatenated name
        concatenatedname = ''.join(cleanednames[nameindex])
        
        # The first letter of a name is not relevant to the abbreviations as it will always
        #     be the first letter in the abbreviation. Thus, the remainder of the letters
        #     are passed into a function that calculates the two letter subsequences
        #     Said function also calculates the scores for those subsequences
        
        secondandthirds = subseq2OrCalculateScore(concatenatedname[1:])
 
        # Adding back the first letter and capitalizing to bring the abbreviations to the correct format
        firstletter = concatenatedname[0] 
        abbreviations.append([(firstletter + secondandthird).upper() for secondandthird in secondandthirds])
        abbreviationscores.append(subseq2OrCalculateScore(flattenedscores[1:]))

    return abbreviations,abbreviationscores




################################################################
#   Section 3: Filtering duplicate and common abbreviations   ##
################################################################


# deduplicateWithin takes in two nested lists, one containing abbreviations
#     and the other containing the scores for those abbreviations
# It removes duplicates by updating a dictionary with each abbreviation and 
#     any new lowest score
# Returns nested lists of the same structure as its inputs, but with duplicate
#     abbreviations removed, keeping the lowest of the duplicate scores
def deduplicateWithin(abbreviations,abbreviationscores):
    Wdeduplicatedabbs = []
    Wdeduplicatedscores = []
    
    # For each name, a unique dictionary is used to store the abbreviations
    #     for that name and their scores
    for nameindex in range(len(abbreviations)):
        minabbscore = {}
        for abbindex in range(len(abbreviations[nameindex])):
            
            # storing the current abbreviation and score in variables 
            #     so as to avoid a very long if statement
            currentabbreviation = abbreviations[nameindex][abbindex]
            currentscore = abbreviationscores[nameindex][abbindex]

            # update the dictionary only if the abbreviation is not yet in it or if a new abbreviation has a lower score
            if currentabbreviation not in minabbscore or currentabbreviation in minabbscore and currentscore < minabbscore[currentabbreviation]:
                minabbscore.update({abbreviations[nameindex][abbindex]:abbreviationscores[nameindex][abbindex]})
        Wdeduplicatedabbs.append(list(minabbscore.keys()))
        Wdeduplicatedscores.append(list(minabbscore.values()))

    return Wdeduplicatedabbs,Wdeduplicatedscores


# dedeuplicateAcross takes in two nested lists, one containing abbreviations
#     and the other containing the scores for those abbreviations, both of which
#     have been filtered within each name for duplicate abbreviations
# deduplicateAcross will take those nested lists and check if any abbreviations
#     are shared between names, and then remove those abbreviations from every
#     name's list of abbreviations
# Returns nested lists of the same structure as its inputs, but with duplicate
#     abbreviations removed across every name, so that each abbreviation is unique
#     to just one name
def deduplicateAcross(Wdeduplicatedabbs,Wdeduplicatedscores):
    existingabbrs = set()
    toremove = set()

    # Renaming variables for clarity. This time it is easier to start with the completed 
    #     abbreviations and scores. Deep copying so the previous data can be seen so this is easier to debug
    AWdeduplicatedabbs = [abbs[:] for abbs in Wdeduplicatedabbs]
    AWdeduplicatedscores = [scores[:] for scores in Wdeduplicatedscores]

    # If the abbreviation already exists in the existingabbrs add it to the set toremove
    #      Otherwise, add it to existingabbrs
    for name in AWdeduplicatedabbs:
        for abb in name:
            if abb in existingabbrs:
                toremove.add(abb)
            else:
                existingabbrs.add(abb)
    
    # Going through every abbreviation in every name and marking those to be removed with 'remove'
    #     and then updating the list of abbreviations for each name with the new valid abbreviations
    for nameindex in range(len(AWdeduplicatedabbs)):
        for abbindex in range(len(AWdeduplicatedabbs[nameindex])):
            if AWdeduplicatedabbs[nameindex][abbindex] in toremove:
                AWdeduplicatedabbs[nameindex][abbindex] = "remove"
                AWdeduplicatedscores[nameindex][abbindex] = "remove"
        AWdeduplicatedabbs[nameindex] = [abb for abb in AWdeduplicatedabbs[nameindex] if abb != 'remove']
        AWdeduplicatedscores[nameindex] = [score for score in AWdeduplicatedscores[nameindex] if score != 'remove']
    
    return AWdeduplicatedabbs,AWdeduplicatedscores




################################################################
#   Section 4: Selecting best abbreviations and writing   ######
################################################################
    

# getBestAbbreviations takes in two nested lists, one containing abbreviations
#     and the other containing the scores for those abbreviations, both of which
#     have been filtered within in each name and across other names for duplicates
# Goes through each name to get the lowest abbreviation score and then goes through
#     each name again to check which abbreviations have those scores
# Returns a nested list containing the lowest scoring abbreviations for each name
def getBestAbbreviations(AWdeduplicatedabbs,AWdeduplicatedscores):
    bestforeachname = []

    for nameindex in range(len(AWdeduplicatedabbs)):
        bestforthisname = []
        lowestscore = {}

        # For the current name, going through every abbreviation to identify which
        #     abbreviation score is the lowest
        for abbindex in range(len(AWdeduplicatedabbs[nameindex])):
            
            currentabbreviation = AWdeduplicatedabbs[nameindex][abbindex]
            currentscore = AWdeduplicatedscores[nameindex][abbindex]

            if not lowestscore or lowestscore and currentscore < lowestscore['lowest']:
                lowestscore.update({'lowest':currentscore})

        # After the lowest score is identified, goes through every abbreviation again
        #     to check which abbreviations have those scores
        for abbindex in range(len(AWdeduplicatedabbs[nameindex])):
            if AWdeduplicatedscores[nameindex][abbindex] == lowestscore['lowest']:
                bestforthisname.append(AWdeduplicatedabbs[nameindex][abbindex])
        
        bestforeachname.append(bestforthisname)

    return bestforeachname

# writeOutput takes in a string representing the filepath for the file
#     to be written, a nested list of strings representing the lowest
#     scoring abbreviations for each name, and a list containing the 
#     original names
# writeOutput writes a new file to the outputfile path, containing 
#     alternating lines of the original name and the corresponding
#     abbreviations
def writeOutput(outputfilepath,bestforeachname,originalnames):
    with open(outputfilepath,'w+') as file:
        
        for nameindex in range(len(originalnames)):
                file.write(originalnames[nameindex] + '\n')

                # If there are no valid abbreviations for a given name
                #     just write an empty line
                if bestforeachname[nameindex] == []:
                    file.write('\n')
                else:
                    file.write(' '.join(bestforeachname[nameindex]) + '\n')




################################################################
#   Section 5: Main Function   #################################
################################################################


# Some default values for the filepaths
defaultscorespath = 'input/values.txt'

# main accepts 3 strings each representing file paths. One is for the names
#     to be abbreviated, another for the scores corresponding to each letter
#     and a third for the file path of the output file
# main calculates the most unique abbreviations for each name as defined
#     in the assignment sheet
# main does not return anything

def main(inputfilename = 'trees', scoresfilepath = defaultscorespath):
    namesfilepath = 'input/'+ inputfilename + '.txt'
    outputfilepath = 'output/liu_' + inputfilename + '_abbrevs.txt'

    cleanednames, originalnames = cleanNames(namesfilepath)
    formattedscores = formatScores(scoresfilepath, cleanednames)
    abbreviations, abbreviationscores = abbreviate(cleanednames, formattedscores)
    Wdeduplicatedabbs, Wdeduplicatedscores = deduplicateWithin(abbreviations, abbreviationscores)
    AWdeduplicatedabbs, AWdeduplicatedscores = deduplicateAcross(Wdeduplicatedabbs, Wdeduplicatedscores)
    bestforeachname = getBestAbbreviations(AWdeduplicatedabbs, AWdeduplicatedscores)
    writeOutput(outputfilepath,bestforeachname,originalnames)




################################################################
#   Section 6: Running from the Command Line   #################
################################################################
    

# allows running from the command line
#     the user just needs to type the name of the text file
if __name__ == '__main__':
    import sys
    inputfilename = ''
    while inputfilename == '':
        inputfilename = input('\nWhat is the input text file name? E.g., for trees.txt, type trees  \n')
    try:
        main(inputfilename)
        print('\nAbbreviations created successfully. Check the output folder for ' + 'liu_' + inputfilename + '_abbrevs.txt')
    except:
        print('\nSomething went wrong; no output file created. Please check that the input file exists in input/ and is a text file ')
