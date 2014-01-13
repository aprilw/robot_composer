"""April Wensel
gen_score.py

The following code implements a genetic algorithm that generates
4-bar melodies.  Individuals are stored as lists of 64 tuples.  The
first element of each tuple is a pitch value, and the second is a
style value.  The style value determines whether the note is a
rest, the end of a note, or included in a link to the next note.  The
fittest set of 64 tuples chosen are sent to output.

The driver function to be called is genetic_algorithm().

Features used for fitness were inspired by both
Towsey 2001 and Milkie and Chestnutt 2001."""

#from __future__ import generators
#from utils import *

import math, random, sys, time, bisect, string, copy

def fitness(seq,wts):
    """Evaluates the sequence of seq given the weights of
    features given in wts"""

    #initialize counts
    bad = 0.0
    good = 0.0
    diff = 0.0
    reward = 1.0
    pow_two = 0
    same_length = 0
    not_rests = 0
    num_notes = 0
    on_beat = 0
    in_c = 0
    cmajor = [0,2,4,6,7,9,11]
    pitches = set()
    order_pitches = []
    
    prev_bin = (-1,-1)
    prev_pitch = -1
    
    for bin in seq:
        # count non-rests
        if bin[1] != 0:
            not_rests +=1
        if prev_pitch > -1 and bin[1] != 0:
            if prev_bin[1] < 2 :
                # measure difference in adjacent pitches
                pitch_diff = abs(prev_pitch - bin[0])
                prev_pitch = bin[0]

                # keep track of pitches 
                pitches.add(prev_pitch)
                order_pitches.append(prev_pitch)
                
                #count pitches in c major
                if (prev_pitch % 12) in cmajor:
                    in_c += 1

                #punish greater than 2 whole step difference
                if pitch_diff > 4:
                    diff += pow(pitch_diff, 2)
        elif prev_pitch == -1 and bin[1] != 0:
            prev_pitch = bin[0]

            # keep track of pitches
            pitches.add(prev_pitch)
            order_pitches.append(prev_pitch)

            #count pitches in c major
            if (prev_pitch % 12) in cmajor:
                    in_c += 1
        prev_bin = bin

    # difference in pitches works against fitness
    bad += diff

    prev_bin = (-1,-1)
    prev_length = -1
    length = 0
    diff = 0.0
    lengths = set()
    for bin in seq:
        # new note
        if prev_bin[1] < 2 and bin[1] != 0:
            length = 1
            #print "note",bin[0]
            #end of note
            if bin[1] == 1:
                if prev_length > -1:
                    #similar note length
                    if(abs(prev_length - length)==0):
                        same_length +=1
                prev_length = length
                #print "len:",length
                if length == 1 or length == 2 or length == 4 \
                   or length == 8 or length == 16:
                        pow_two +=1
                num_notes +=1
                lengths.add(length)
                
                length = 0
                
        # end of note
        elif bin[1] == 1 or bin == seq[len(seq)-1]:
            length += 1
            #similar note length
            if(abs(prev_length - length)==0):
                same_length +=1
            prev_length = length
            
            if length == 1 or length == 2 or length == 4 \
                   or length == 8 or length == 16:
                        pow_two +=1
            num_notes +=1
            lengths.add(length)
           
            length = 0
            
        # end caused by preceding a rest
        elif bin[1] == 0:
            # not first note and last note not rest
            if prev_length > -1 and prev_bin[1] > 0:
                if(abs(prev_length - length)==0):
                    same_length +=1
            prev_length = length
            #print "len:",length
            if length == 1 or length == 2 or length == 4 \
                   or length == 8 or length == 16:
                        pow_two +=1
            num_notes +=1
            lengths.add(length)
            
            length = 0
        #continuing linked note
        else:
            length +=1
        prev_bin = bin
            
    pitch_var = len(pitches)/num_notes
    rhythm_var = len(lengths)/16

    # notes start on 1st or 3rd beat
    for i in range(len(seq)):
        #not first, is on 1st or 3rd beat, not linked from before, not rest 
        if (i == 1 or i>1 and (i % 4 == 1 or i%4==3) and seq[i-1][1] < 2) \
           and seq[i][1] !=0:
            on_beat += 1

    good = wts[0]*pow_two + wts[1]*same_length + wts[2]*not_rests + \
           wts[3]*in_c + wts[4]*num_notes + wts[5]*on_beat
    
    bad+=  wts[6]*pitch_var + wts[7]*rhythm_var

    # adjust so final weights are easier to look at
    good *= 100
    
    # prevent divide by 0
    if bad == 0:
        return good/1
    else:
        return good/bad
        

def genetic_algorithm(wts=[10,10,1,20,5,10,1,1],ngen=1000, pmut=0.0):
    """see Artificial Intelligence: A Modern Approach"""
    def reproduce(p1, p2):
        """Combines 2 individuals"""
        c = random.randrange(len(p1))
        return p1[:c] + p2[c:]

    def mutate(child):
        "Changes a random bin's pitch and style"""
        newPitch = random.randint(36,83)
        newStyle = random.randint(0,3)
        place = random.randint(0,len(child)-1)
        
        temp = copy.deepcopy(child[place])
        child[place] = (newPitch,newStyle)
    
        return child

    def generate_population(pop_size,spec_length):
        """Create random population of individuals"""
        pop = []
        for i in range(pop_size):
            spec = []
            for j in range(spec_length):
                spec.append((random.randint(36,83),random.randint(0,3)))
            pop.append(spec)
        print pop
        return pop

    fitness_fn = fitness
    # create initial population of 4 bars of 16th note values
    population = generate_population(50, 16*4)
    for i in range(ngen):
        new_population = []
        for i in range(len(population)):
            p1, p2 = random_weighted_selection(population, 2, fitness_fn,wts)
            child = reproduce(p1, p2)
            if random.uniform(0,1) > pmut:
                child = mutate(child)
            new_population.append(child)
        population = new_population
    winner = argmax(population, fitness_fn,wts)
    print fitness_fn(winner,wts)

    r = random.uniform(0,500)
    filename = "test_pitch" + str(wts) + "_" + str(ngen) + "_" + str(pmut)+ ".txt" 
    f = open(filename, 'w')

    for tup in winner:
        f.write(str(tup[0]) + "\n")

    filename = "test_style" + str(wts) + "_" + str(ngen) + "_" + str(pmut)+  ".txt"
    f = open(filename, 'w')

    for tup in winner:
        f.write(str(tup[1]) + "\n")
    return winner

def argmax(seq, fn, wts):
    """Return an element with highest fn(seq[i], wts) score; tie goes to first one.
    >>> argmax(['one', 'to', 'three'], len, wts)
    'one'
    (adapted from Artifical Intelligence: A Modern Approach)
    """
    best = seq[0]; best_score = fn(best, wts)
    for x in seq:
        x_score = fn(x, wts)
        if x_score > best_score:
            best, best_score = x, x_score
    return best

def random_weighted_selection(seq, n, weight_fn,wts):
    """Pick n elements of seq, weighted according to weight_fn.
    That is, apply weight_fn to each element of seq, add up the total.
    Then choose an element e with probability weight[e]/total.
    Repeat n times, with replacement. """
    totals = []; runningtotal = 0
    for item in seq:
        runningtotal += weight_fn(item,wts)
        totals.append(runningtotal)
    
    selections = []
    for s in range(n):
        r = random.uniform(0,totals[-1])
        
        for i in range(len(seq)):
            if totals[i] >= r:
                selections.append(seq[i])
                break
    if len(selections) < 2:
        print totals, " r:", r
    return selections
    

