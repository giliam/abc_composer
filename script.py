#!/usr/bin/python
# -*-coding:utf-8 -*
from itertools import *
from math import log10
from random import *
from read_abc import read_abc_file, write_abc
import csv
import os, os.path
import pickle
import sys

DEBUG = False

etatsPossibles = [
    "A,,","B,,","C,,","D,,","E,,","F,,","G,,",
    "A,","B,","C,","D,","E,","F,","G,",
    "A","B","C","D","E","F","G",
    "a","b","c","d","e","f","g",
    "_A,,","_B,,","_C,,","_D,,","_E,,","_F,,","_G,,",
    "_A,","_B,","_C,","_D,","_E,","_F,","_G,",
    "_A","_B","_C","_D","_E","_F","_G",
    "_a","_b","_c","_d","_e","_f","_g",
    "^A,,","^B,,","^C,,","^D,,","^E,,","^F,,","^G,,",
    "^A,","^B,","^C,","^D,","^E,","^F,","^G,",
    "^A","^B","^C","^D","^E","^F","^G",
    "^a","^b","^c","^d","^e","^f","^g"
]
etatsIndex = {note: i for i,note in enumerate(etatsPossibles)}

nbEtats = len(etatsPossibles)

rythmsPossible = []

def argmax(values):
    return max(enumerate(values), key=lambda x:x[1])

def convert_notes_id(etatsIndex, data):
    output = []
    for note in data:
        output.append(etatsIndex[note.replace('=','')])
    return output

def forward (PI, A, sequence):
    T = len(sequence)
    temps = range(T)

    proba = PI[sequence[0]]
    for t in range(T-1):
        proba *= A[sequence[t]][sequence[t+1]]
        # Multiplies the proba by the transition proba
    
    if DEBUG:
        print "---------------"
        print "FORWARD"
        print "Pour la séquence : "
        print sequence
        print "Proba de : "
        print proba
        print "---------------\n\n"

def train(filename,mm,etatsIndex):
    data = read_abc_file(filename)
    notes = convert_notes_id(etatsIndex,data[0])
    for i,note in enumerate(notes):
        if i == 0:
            continue
        if notes[i-1] == note:
            continue
        mm[notes[i-1]][note] += 1.
    return mm

def train_rythm(filename):
    data = read_abc_file(filename)
    rythms = data[1]
    for rythm in rythms:
        if rythm not in rythmsPossible:
            rythmsPossible.append(rythm)
    nbRythms = len(rythmsPossible)
    rythmsIndex = {rythm: i for i,rythm in enumerate(rythmsPossible)}
    rythms = map(lambda x: rythmsIndex[x], rythms)
    mmRythm = [[0. for i in range(nbRythms)] for j in range(nbRythms)]
    for i, rythm in enumerate(rythms):
        if i == 0:
            continue
        mmRythm[rythms[i-1]][rythm] += 1.
    for i,row in enumerate(mmRythm):
        s = sum(row)
        if s > 0:
            mmRythm[i] = [row[j]/s for j in range(nbRythms)]
    return mmRythm

def compose(tone,A,duration):
    part = [tone]
    for t in range(duration):
        
        possibles_following = [(elt,i) for i,elt in enumerate(A[part[t]]) if elt > 0]

        n = len(possibles_following)

        if n == 0:
            part.append(part[t-1])
            continue

        possibles_sumed = [possibles_following[0]]
        for i in range(1, n):
            possibles_sumed.append((possibles_sumed[i-1][0]+possibles_following[i][0], possibles_following[i][1]))

        next_note = random()
        for (proba,note) in possibles_sumed:
            if proba > next_note:
                part.append(note)
                break
    return part

def add_end_measure(nb_mesures):
    output = "|"
    if nb_mesures%4 != 3:
        output += " \\"
    output += "\n"
    return output

def represent_rythm(value):
    if int(value) == value:
        return str(int(value))
    else:
        a,b = (value).as_integer_ratio()
        return str(a)+"/"+str(b)

def convert_to_abc(part_notes, part_rythms):
    output = """X: 1
T: from midi/cs1-1pre.mid
M: 4/4
L: 1/8
Q:1/4=80
K:G % 1 sharps
V:1
"""
    rythm_count = 0
    nb_mesures = 0
    for i,note in enumerate(part_notes):
        #Adds note
        output += etatsPossibles[note]

        if rythmsPossible[part_rythms[i]] == '':
            current_value = 1.
        elif "/" in rythmsPossible[part_rythms[i]]:
            current_value = 1./int(rythmsPossible[part_rythms[i]].replace('/', ''))
        else:
            current_value = int(rythmsPossible[part_rythms[i]])
        rythm_count += current_value
        if DEBUG:
            print "new note"
            print etatsPossibles[note]
            print rythmsPossible[part_rythms[i]]
            print current_value

            print rythm_count
        if rythm_count >= 8:
            nb_mesures += 1
            if rythm_count > 8:
                if DEBUG:
                    print "greater than 8"
                    print represent_rythm(8-(rythm_count-current_value))
                    print add_end_measure(nb_mesures)
                    print etatsPossibles[note]
                    print represent_rythm(rythm_count-8)

                # Returns before rythm addition
                # Finishes properly the measure
                output += represent_rythm(8-(rythm_count-current_value))
                output += add_end_measure(nb_mesures)
                # Finishes the note
                output += etatsPossibles[note]
                output += represent_rythm(rythm_count-8)
                rythm_count = rythm_count-8
                continue
            else:
                if DEBUG:
                    print "Normal"

                output += represent_rythm(current_value)
                rythm_count = 0
            output += add_end_measure(nb_mesures)
        else:
            output += represent_rythm(current_value)
    return output

def compose_new_piece(A, B, duration):
    seed = len([name for name in os.listdir('output/') if os.path.isfile('output/'+name)])/4+1
    part_notes = compose(0, A, 50)
    part_rythms = compose(0, B, 50)
    write_abc(seed, convert_to_abc(part_notes, part_rythms))

def create_new_mm(files_list, name):
    A = [[0. for i in range(nbEtats)] for j in range(nbEtats)]

    N = len(A)
    etats = range(N)
    nb_files = len(files_list)
    for filename in files_list:
        A = train("abc/" + filename + ".abc", A, etatsIndex)
    for i,row in enumerate(A):
        s = sum(row)
        if s > 0:
            A[i] = [row[j]/s for j in range(nbEtats)]
    with open("markovchains/" + name + ".mc", "w") as file:
        pickle.dump(A, file)
    return A


def main():
    files_list = ["cs1-1pre","cs1-2all","cs1-3cou","cs1-5men","cs1-4sar","cs1-6gig"]

    files_list_all = ["cs1-1pre","cs2-1pretranspose","cs3-1pretranspose","cs4-1pretranspose","cs5-1pretranspose","cs6-1pretranspose"]
    #automate = create_new_mm(files_list_all, "suites_toutes_tonalite_sol")
    automate = create_new_mm(files_list, "suite_1_tonalite_sol")
    B = train_rythm("abc/rhythm/decoy.abc")
    compose_new_piece(automate, B, 150)
main()
