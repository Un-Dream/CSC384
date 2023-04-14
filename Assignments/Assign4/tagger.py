import os
import sys
import argparse
import time



TAGS = [#BNC Basic Tags = 61
        "AJ0", "AJC", "AJS", "AT0", "AV0", "AVP", "AVQ",
        "CJC", "CJS", "CJT", "CRD",
        "DPS", "DT0", "DTQ", 
        "EX0", 
        "ITJ", 
        "NN0", "NN1", "NN2", "NP0", 
        "ORD",
        "PNI", "PNP", "PNQ", "PNX", "POS", "PRF", "PRP", "PUL", "PUN", "PUQ", "PUR",
        "TO0",
        "UNC", 
        'VBB', 'VBD', 'VBG', 'VBI', 'VBN', 'VBZ', 
        'VDB', 'VDD', 'VDG', 'VDI', 'VDN', 'VDZ', 
        'VHB', 'VHD', 'VHG', 'VHI', 'VHN', 'VHZ', 
        'VM0', 'VVB', 'VVD', 'VVG', 'VVI', 'VVN', 'VVZ',
        'XX0', 
        'ZZ0', 
        
        #Ambiguity tags
        'AJ0-AV0', 'AJ0-VVN', 'AJ0-VVD', 'AJ0-NN1', 'AJ0-VVG', 
        'AVP-PRP', 'AVQ-CJS', 'CJS-PRP', 'CJT-DT0', 'CRD-PNI',
        'NN1-NP0', 'NN1-VVB', 'NN1-VVG', 'NN2-VVZ', 'VVD-VVN', 
       
        #reverse ambiguity tags
        'AV0-AJ0', 'VVN-AJ0', 'VVD-AJ0', 'NN1-AJ0', 'VVG-AJ0', 
        'PRP-AVP', 'CJS-AVQ', 'PRP-CJS', 'DT0-CJT', 'PNI-CRD', 
        'NP0-NN1', 'VVB-NN1', 'VVG-NN1', 'VVZ-NN2', 'VVN-VVD']

import numpy
# P = 0.000000001
P = numpy.finfo(numpy.float64).eps

def generate_matrices(training_list):
    """Generates the matrices for the Viterbi algorithm."""
    """Return the initial, transition, and emission matrices."""
    """The initial matrix is a dictionary of tag:probability."""
    """The transition matrix is a dictionary of tag:probability.""" 
    """The emission matrix is a dictionary of tag:dictionary 
            with the dictionary being word:probability."""
            

    #initial matrix
    initial = {}

    #transition matrix
    transition = {}

    #emission matrix
    emission = {}

    all_tags = []
    tag_counts = {}

    tag_pairs_counts = {}
    word_tag_counts = {}

    lookin = ['.', '?', '!', '"', "'"]
    # lookin = ['.', '?', '!']
    # lookin = ['.', '?', '!', '"', "'", ",", ":", "-"]

    num_lines = 0
    sentences = []
    initial_tag_count = {}
    initial_tag_count = {tag: 0 for tag in TAGS}
    just_end = True
    
    for file in training_list:
        with open(file) as f:
            train_data = f.read().splitlines()


        sentence_tags = []
        line = 0
        cur_sentence = []
        cur_word_num = 0
        for state in train_data:
            
            line+=1

            # print(state)

            word, tag = state.split(' : ')
            word = word.strip()
            tag = tag.strip()
            cur_word_num += 1

            # print(word, tag)
            

            if word != '' or tag != '':

                if just_end:
                    initial_tag_count[tag] +=1
                    just_end = False

                sentence_tags.append(tag)
                all_tags.append(tag)
                cur_sentence.append(word)

                if tag not in tag_counts:
                    tag_counts[tag] = 1
                else:
                    tag_counts[tag] += 1

                
                #Emission matrix
                if word not in word_tag_counts:
                    word_tag_counts[word] = {tag: 1}
                elif tag not in word_tag_counts[word]:
                    word_tag_counts[word][tag] = 1
                else:
                    word_tag_counts[word][tag] += 1
            # else:
            #     print("Error: word or tag is empty")
            #     print("word is {}".format(word))
            #     print("tag is {}".format(tag))
            #     print("line is {}".format(line))
            #     break


            #End of sentence
            if word in lookin:

                #Transition matrix
                for i in range(len(sentence_tags) - 1):
                    tag_pair = (sentence_tags[i], sentence_tags[i + 1])
                    if tag_pair not in tag_pairs_counts:
                        tag_pairs_counts[tag_pair] = 1
                    else:
                        tag_pairs_counts[tag_pair] += 1
            
                num_lines += 1
                sentence_tags = []
                sentences.append(cur_sentence)
                cur_sentence = []
                just_end = True

            #     lookin = ['.', '?', '!']
            #     cur_word_num = 0
            
            # #if start with "or  ' and beginning of sentence
            # if cur_word_num == 1:
            #     if word in ['"', "'"]:
            #         lookin = ['"', "'"]
            #     else:
            #         lookin = ['.', '?', '!']




                

    #Initial matrix
    initial = dict.fromkeys(TAGS, P)
    for tag, count in initial_tag_count.items():
        initial[tag] = count #/ num_lines



    
    
    #Transition matrix
    transition = dict.fromkeys(TAGS, dict.fromkeys(TAGS, P))
    # print(transition)
    for pair, count in tag_pairs_counts.items():
        transition[pair[0]][pair[1]] = count #/ tag_counts[pair[1]]


    # print("Transition matrix is {}".format(transition))


    #Emission matrix
    #set to very small probability
    # emission = dict.fromkeys(TAGS, 0.000000001)
    for word, tag_count in word_tag_counts.items():
        emission[word] = dict.fromkeys(TAGS, P)
        for tag, count in tag_count.items():
            emission[word][tag] = count #/ tag_count[tag]



    #normalize the three matrix

    #initial
    initial_sum = sum(initial.values())
    for tag, prob in initial.items():
        initial[tag] = prob / initial_sum
    
    #transition
    for tag, tag_prob in transition.items():
        tag_sum = sum(tag_prob.values())
        for tag2, prob in tag_prob.items():
            transition[tag][tag2] = prob / tag_sum
    
    #emission
    for word, tag_prob in emission.items():
        tag_sum = sum(tag_prob.values())
        for tag, prob in tag_prob.items():
            emission[word][tag] = prob / tag_sum


    # print("Initial matrix is {}".format(initial))
    # print("Transition matrix is {}".format(transition))

    # print(*sentences[:-10], sep = "\n")


    # print("Length of all_tags is {}".format(len(all_tags)))
    # print("Length of tag_counts is {}".format(len(tag_counts)))
    # print("Length of tag_pairs_counts is {}".format(len(tag_pairs_counts)))
    # print("Length of word_tag_counts is {}".format(len(word_tag_counts)))
    # print("Number of lines is {}".format(num_lines))
    


    return initial, transition, emission



def viterbi(obs, start_p, trans_p, emit_p):
    V = [{}]
    path = {}
    states = TAGS

    PROB = 1

    # Initialize base cases (t == 0)
    sum = 0
    for y in states:
        if obs[0] in emit_p:
            V[0][y] = start_p[y] * emit_p[obs[0]][y]
        else:
            V[0][y] = start_p[y] #* (1 / len(start_p))  # use method 1 for unknown words at start
        path[y] = [y]

        #normalize
        sum += V[0][y]

    # print(sum)
    for i in V[0]:
        V[0][i] /= sum

    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}

        sum = 0 #for normalization
        # print(obs[t])
        for y in states:
            # if obs[t] in emit_p:
            emit_prob = 0
            
            if y == 'PUN':
                if obs[t] in ['.', '?', '!', ';', ',', ':', '-']:
                    emit_prob = PROB # assign PUN tag to punctuation marks
            elif y == 'PUQ':
                if obs[t] in ['"', "'"]:
                    emit_prob = PROB # assign PUQ tag to quotation marks
                
            elif y == 'PUL':
                if obs[t] in ['(', '[', '{']:
                    emit_prob = PROB # assign PUL tag to opening brackets

            elif y == 'PUR':
                if obs[t] in [')', ']', '}']:
                    emit_prob = PROB # assign PUR tag to closing brackets
                
            elif y == 'CRD':
                if obs[t].isdigit():
                    emit_prob = PROB
            elif y == 'XX0':
                if obs[t] in ['n\'t', 'not', 'Not']:
                    emit_prob = PROB
            elif y == 'CJC':
                if obs[t] in ['but', 'But', 'and']:
                    emit_prob = PROB
            
            
            elif obs[t] in emit_p:
                emit_prob = emit_p[obs[t]][y]
            elif obs[t].lower() in emit_p:
                emit_prob = emit_p[obs[t].lower()][y]
            

            elif obs[t][0].isupper():
                # emit_prob = emit_p[obs[t]][y]
                if y == 'NN0':
                    emit_prob = PROB
                

            else:
                emit_prob = 1.0 # unknown word

            (prob, state) = max((V[t-1][y0] * trans_p[y0][y] * emit_prob, y0) for y0 in states)

            # print(prob)
            V[t][y] = prob
            newpath[y] = path[state] + [y]
            sum += prob

        #normalize
        # print(sum)
        if sum != 0:
            for i in V[t]:
                V[t][i] /= sum

        # Update the path   
        path = newpath

        #normalize probs


    # Find the highest probability endpoint and its path
    (prob, state) = max((V[-1][y], y) for y in states)
    return (prob, path[state])


def viterbi_parse_file(filename):
    sentences = []
    sentence = []
    # lookin = ['.', '?', '!', '"', "'", ",", ":", "-"]
    # lookin = ['.', '?', '!']
    lookin = ['.', '?', '!', '"', "'"]
    with open(filename, 'r') as f:
        cur_word_num = 0
        for line in f:
            line = line.strip()
            cur_word_num += 1

            sentence.append(line)

            if line in lookin:
                sentences.append(sentence)
                sentence = []

            #     lookin = ['.', '?', '!']
            #     cur_word_num = 0
            
            # #if start with "or  ' and beginning of sentence
            # if cur_word_num == 1:
            #     if line in ['"', "'"]:
            #         lookin = ['"', "'"]
            #     else:
            #         lookin = ['.', '?', '!']


    if len(sentence) > 0:
        sentences.append(sentence)

    return sentences


def compare_files(file1_path, file2_path):
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()


    #write to file if not equal
    with open('error.txt', 'w') as f:
        num_same_lines = 0
        num_words = 0
        for line1, line2 in zip(lines1, lines2):
            # if line1.strip() == line2.strip():
            num_words += 1
            if line1 == line2:
                num_same_lines += 1

            else:
                a,b = line1.split(" : ")
                
                f.write(str(num_words) + " : " + line2.strip() + " --  " + b)
    f.close()



    return (num_same_lines / len(lines1)) * 100, num_same_lines, len(lines1)




def rules(word):
    if word[0].isupper():
        return 'NPO'
    elif word.isdigit():
        return 'CD'
    elif word.isupper():
        return 'NPO'
    elif word.islower():
        return 'JJ'
    
    #last three letters ing
    elif word[-3:] == 'ing':
        return "VHG"
    else:
        return 'NN'



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trainingfiles",
        action="append",
        nargs="+",
        required=True,
        help="The training files."
    )
    parser.add_argument(
        "--testfile",
        type=str,
        required=True,
        help="One test file."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file."
    )
    args = parser.parse_args()

    training_list = args.trainingfiles[0]


    # A = "training1.txt"
    # if A not in training_list:
    #     training_list.append(A)

    # B = "training2.txt"
    # if B not in training_list:
    #     training_list.append(B)



    s = time.time()
    initial, transition, emission = generate_matrices(training_list)

    sentences = viterbi_parse_file(args.testfile)

    # print(*sentences[:10], sep = "\n")

    # print(initial["AJ0"])
    # print(transition[("AJ0", "NN1")])
    # print(emission["Detective"])
    # print(emission["Detective"]["AJ0"])

    with open(args.outputfile, 'w') as f:
        for sentence in sentences:
            prob, path = viterbi(sentence, initial, transition, emission)

            for word, tag in zip(sentence, path):
                f.write(word + ' : ' + tag + '\n')
    f.close()


    # for sentence in sentences:
    #     prob, path, state = viterbi(sentence, initial, transition, emission)
    #     print(' '.join(sentence))
    #     print(' '.join(path))
    #     print(f'Probability: {prob}')
    #     print('')


    # percent, matches, total = compare_files("training2.txt", args.outputfile)
    # print("The accuracy is {}%" .format(percent))
    # print("Total matches: {}/{}".format(matches, total))
    # print("Time taken is {}".format(time.time() - s))
    # compare_files(args.testfile, args.outputfile)


    # print("training files are {}".format(training_list))

    # print("test file is {}".format(args.testfile))

    # print("output file is {}".format(args.outputfile))


    # print("Starting the tagging process.")
