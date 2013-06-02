# -*- coding: utf-8 -*-
import sys, os, math, string, random
from time import time

MINLEN = 3
mutation_rate = 0.01
crossover_rate = 0.8
max_iterations = 50


def main(grid, lines):
#######################select horizontal and vertical words##############################################
   
    grid = grid.rstrip().splitlines()
    while grid and not grid[0]:
        del grid[0]
    findIntersections(grid)
    # Extract horizontal words
    horizontal = []
    word = []
    predefined = {}
    for ligne in range(len(grid)):
        for colonne in range(len(grid[ligne])):
            char = grid[ligne][colonne]
            if not char.isspace():
                word.append((ligne, colonne))
                if char != "#":
                    predefined[ligne, colonne] = char
            elif word:
                if len(word) > MINLEN:
                    horizontal.append(word[:])
                del word[:]
        if word:
            if len(word) > MINLEN:
                horizontal.append(word[:])
            del word[:]

    # Extract vertical words
    vertical = []
    validcolonne = True
    colonne = 0
    while validcolonne:
        validcolonne = False
        for ligne in range(len(grid)):
            if colonne >= len(grid[ligne]):
                if word:
                    if len(word) > MINLEN:
                        vertical.append(word[:])
                    del word[:]
            else:
                validcolonne = True
                char = grid[ligne][colonne]
                if not char.isspace():
                    word.append((ligne, colonne))
                    if char != "#":
                        predefined[ligne, colonne] = char
                elif word:
                    if len(word) > MINLEN:
                        vertical.append(word[:])
                    del word[:]
        if word:
            if len(word) > MINLEN:
                vertical.append(word[:])
            del word[:]
        colonne += 1

    hnames = ["h%d" % i for i in range(len(horizontal))]
    vnames = ["v%d" % i for i in range(len(vertical))]
  
    wordsbylen = {}
    chromosome_parent1_list = []
    chromosome_parent2_list = []
    chromosome_child_1 = []
    chromosome_child_2 = []
    generation_list = []
    new_generation_list= []
    iterations = 0
    fit=max_iterations
    solution_found = False
    new_generation_pair = []
    
    for hword in horizontal:
        wordsbylen[len(hword)] = []
    for vword in vertical:
        wordsbylen[len(vword)] = []

    for line in lines:
        line = line.strip()
        l = len(line)
        if l in wordsbylen:
            wordsbylen[l].append(line.upper())
            
    for i in range(max_iterations):
        #we get a list of two lists: the first one is the generated chromosome and the second is a list containing lengths of words
        temp=generate_parent(horizontal,vertical,wordsbylen)
        chromosome_parent1_list=temp[0]#we take the generated chromosome
        chromosome_parent1=" ".join(x for x in chromosome_parent1_list)# list to string
        length_words=temp[1]#we take the list containing the lengths of words
        generation_list.append(chromosome_parent1_list)#generation_list is a list of chromosomes(chromosome=list of genes and gene=word)
    
    startDate = time()
    while solution_found != True:
        iterations = 0
        while iterations != max_iterations:
            #we pick two chromosomes from the generation list
            chromosome_parent1_list = random.choice(generation_list)
            chromosome_parent2_list = random.choice(generation_list)
            
            #crossover operation
            chromosome_child_1 = crossover(chromosome_parent1_list,chromosome_parent2_list,length_words)
            chromosome_child_2 = mutate(chromosome_child_1,wordsbylen,length_words)
            
            #new_generation_list is a list of new chromosomes created by mutation and crossover(chromosome=list of genes and gene=word)
            new_generation_list.append(chromosome_child_2)
            iterations += 1
            
        #faire une liste de paires (chromosome,fitness(chromosome))
        #et la sorter en fonction de la valeur de fitness
        for i in new_generation_list:
            string= "".join(x for x in i)
            new_generation_pair.append((i,fitness(string,grid)))
            x = fitness(string,grid)
            
        
        #we sort chromosome in fonction of the value of their fitness
        new_generation_pair.sort(key=lambda x: x[1])
        
        n_best = []
        i = 0
        for pair in new_generation_pair:
            if not pair in n_best:
                n_best.append(pair) 
                i += 1
            if i == 250:
                break
        print "\n\n List of top 10  pairs (chromosome, fitness) is : \n"
        for k in range(10):
            print str(n_best[k]) + "\n"

        #we check if we have a solution among the new generation
        for i in n_best:
            fit = i[1]
            if fit == 0:
                print "fitness is :" + str(fit)+ "\n"
                solution_found = True
                chromosome_solution = i #we keep the chromosome solution
                print "************************************************************"
                print "Solution chromosome is :"
                print chromosome_solution
                print "************************************************************"
            else:
                del generation_list[:]
                for k in n_best:
                    generation_list.append(k[0]) #we're going to create the new child generation from the 10 best chromosome in generation_list
        # print the computation time every 10 interations
        if iterations%10 == 0: 
            delta1 = time() - startDate
            elapsedTime = round(delta1,1)
            print "Intermediate time (every ten iterations ) = " + str(elapsedTime) + " sec \n\n"
    
    delta = time() - startDate
    elapsedTime = round(delta,1)
    print "Final time = " + str(elapsedTime)
        
def generate_parent(horizontal,vertical,wordsbylen):
    full_horizontal_parent1 = []
    full_vertical_parent1 = []
    full_horizontal_parent2 = []
    full_vertical_parent2 = []
    length_words = []
    chromosome = []
    for hi, hword in enumerate(horizontal):
        words = wordsbylen[len(hword)]
        random.shuffle(words)
        full_horizontal_parent1.append(random.choice(words))
        random.shuffle(words)
        full_horizontal_parent2.append(random.choice(words))
        length_words.append(len(hword))
    for vi, vword in enumerate(vertical):
        words = wordsbylen[len(vword)]
        random.shuffle(words)
        full_vertical_parent1.append(random.choice(words))
        random.shuffle(words)
        full_vertical_parent2.append(random.choice(words))
        length_words.append(len(vword))
    chromosome_parent1_list=full_horizontal_parent1+full_vertical_parent1
    chromosome.append(chromosome_parent1_list)
    chromosome.append(length_words)
    return chromosome
  

    
##################################################write in the grid 0 where there are no conflicts letter and 1 where there is one conflict letter############################################
def findIntersections(grid):
    intersectionList = []
    horizontalPositions = []
    verticalPositions = []
    x = 0
    y = 0
    v_check = False
    h_check = False
    for raw in range(len(grid)):
        for column in range(len(grid[raw])):
            char = grid[raw][column]
            if not char.isspace():
                # check if the cell belongs to a minimum 3-chars length horizontal word 
                for pos0 in range(column-2, column+3):
                    if pos0 >= 0 and pos0 < len(grid[raw]):
                        if not grid[raw][pos0].isspace():
                            y = y+1 
                            if(y == 3):
                                h_check = True
                        else:
                            y = 0     
                            
                # check if the cell belongs to a minimum 3-chars length vertical word 
                for pos in range(raw-2, raw+3): 
                    if pos >= 0 and pos < len(grid):
                        if not grid[pos][column].isspace():  
                            x = x+1
                            if(x == 3):
                                v_check = True
                        else:
                            x = 0           
                if(v_check == True and h_check== True):
                    intersectionList.append((raw, column))
                x = 0  
                y = 0
                h_check = False
                v_check = False
    print "\nThe length of the intersection list is : " + str(len(intersectionList)) + '\n'
    return intersectionList

# counts the number of existing conflicts in the chromosome    
# The chromosome contains only the valid words in the grid 
def countConflicts2(chromosome,grid):
    nbrConflicts = 0
    horizontal_list = []
    vertical_list = []
    conflicts_dict = []
    n = 0
    #########################################
    word = []
    for ligne in range(len(grid)):
        for colonne in range(len(grid[ligne])):
            char = grid[ligne][colonne]
            if not char.isspace():
                word.append((ligne, colonne))
            elif word:
                if len(word) > MINLEN:
                    mot = ""
                    for i in range(len(word)):
                        mot = mot + chromosome[n] 
                        n = n + 1
                    horizontal_list.append(word[:])
                del word[:]
            
        if word:
            if len(word) > MINLEN: 
                mot = ""
                for i in range(len(word)):
                    mot = mot + chromosome[n] 
                    n = n + 1
                horizontal_list.append(word[:])
            del word[:]
    
    #########################################
    validcolonne = True
    colonne = 0
    while validcolonne:
        validcolonne = False
        for ligne in range(len(grid)):
            if colonne >= len(grid[ligne]):
                if word:
                    if len(word) > MINLEN:
                        mot = ""
                        for i in range(len(word)):
                            mot = mot + chromosome[n] 
                            n += 1
                        vertical_list.append(word[:])   
                    del word[:]
            else:
                validcolonne = True
                char = grid[ligne][colonne]
                if not char.isspace():
                    word.append((ligne, colonne))
                elif word:
                    if len(word) > MINLEN:
                        vertical_list.append(word[:])
                    del word[:]
        if word:
            if len(word) > MINLEN:
                vertical_list.append(word[:])
            del word[:]
        colonne += 1
    
    for sublist in horizontal_list:
        for pair in sublist:
            conflicts_dict.append(pair)
    y = len(conflicts_dict)
    
    conf_list = []
    flattened_list = []
    for sublist in vertical_list:
        for pair in sublist:
            flattened_list.append(pair)

    for sublist in vertical_list:
        for pair in sublist:
            if pair in conflicts_dict:
                x = conflicts_dict.index(pair)
                z = y + flattened_list.index(pair)
                if chromosome[x]  != chromosome[z]:
                    conf_list.append((pair, chromosome[x], chromosome[z]))
                    nbrConflicts += 1   
            conflicts_dict.append(pair)
    return nbrConflicts
     

##################################################encode and put horizontal and vertical words in a same string############################################
# Do probablistic crossover operation.
def crossover(chromosome_list_parent1,chromosome_list_parent2,length_words):
    chromosome_child = []
    crossover_point = random.randint(0,len(length_words))
    if(random.random() <= crossover_rate):
		chromosome_child = chromosome_list_parent1[:crossover_point] + chromosome_list_parent2[crossover_point:]
    else:
        chromosome_child = chromosome_list_parent1
    return chromosome_child
     
# Do probablistic mutation operation.
def mutate(chromosome_child,wordsbylen,length_words):
    for i in range(len(length_words)):
    	if(random.random() <= mutation_rate):
            words = wordsbylen[len(chromosome_child[i])]
            random.shuffle(words)
            chromosome_child[i]=random.choice(words)
    return chromosome_child
   
def fitness(chromosome_child,grid):
    #check conflicts
    fit = countConflicts2(chromosome_child,grid)
    return fit
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: encode_decode.py <maskfile> <wordsfile>")
    main(open(sys.argv[1]).read(), open(sys.argv[2]))
