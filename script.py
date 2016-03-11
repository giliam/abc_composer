#!/usr/bin/python
# -*-coding:utf-8 -*
from itertools import *
from math import log10
from random import *
from read_abc import read_abc_file, write_abc
import csv
DEBUG = True


etatsPossibles = [
    "A,,","B,,","C,,","D,,","E,,","F,,","G,,",
    "A,","B,","C,","D,","E,","F,","G,",
    "A","B","C","D","E","F","G",
    "_A,,","_B,,","_C,,","_D,,","_E,,","_F,,","_G,,",
    "_A,","_B,","_C,","_D,","_E,","_F,","_G,",
    "_A","_B","_C","_D","_E","_F","_G",
    "^A,,","^B,,","^C,,","^D,,","^E,,","^F,,","^G,,",
    "^A,","^B,","^C,","^D,","^E,","^F,","^G,",
    "^A","^B","^C","^D","^E","^F","^G"
]
etatsIndex = {note: i for i,note in enumerate(etatsPossibles)}

nbEtats = len(etatsPossibles)
A = [[0. for i in range(nbEtats)] for j in range(nbEtats)]

N = len(A)
etats = range(N)


def argmax(values):
    return max(enumerate(values), key=lambda x:x[1])

def convert_notes_id(data):
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

def train(filename,mm):
    data = read_abc_file(filename)
    notes = convert_notes_id(data[0])
    for i,note in enumerate(notes):
        if i == 0:
            continue
        mm[notes[i-1]][note] += 1.
    return mm

def compose(tone,A,duration):
    part = [tone]
    for t in range(duration):
        
        possibles_following = [(elt,i) for i,elt in enumerate(A[part[t]]) if elt > 0]
        n = len(possibles_following)

        if n == 0:
            part.append(part[t-1])
            continue

        possibles_sumed = [(possibles_following[0][0],0)]
        for i in range(1, n):
            possibles_sumed.append((possibles_sumed[i-1][0]+possibles_following[i][0], i))

        next_note = random()
        for proba,note in possibles_sumed:
            if proba > next_note:
                part.append(note)
                break
    return part

def convert_to_abc(part):
    output = """X: 1
T: from midi/cs1-1pre.mid
M: 4/4
L: 1/8
Q:1/4=80
K:G % 1 sharps
V:1"""
    for i,note in enumerate(part):
        output += etatsPossibles[note]
        output += "/2"
        if i%8 == 7:
            output += "|"
            if i%32 != 31:
                output += "\\"
            output += "\n"
    return output

files_list = ["cs1-1pre","cs1-2all","cs1-3cou","cs1-5men","cs1-4sar","cs1-6gig"]
nb_files = len(files_list)
for filename in files_list:
    A = train("abc/" + filename + ".abc", A)
for i,row in enumerate(A):
    s = sum(row)
    if s > 0:
        A[i] = [row[j]/s for j in range(nbEtats)]

write_abc("output.abc", convert_to_abc(compose(0,A,50)))