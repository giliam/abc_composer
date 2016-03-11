#!/usr/bin/python
# -*-coding:utf-8 -*
from itertools import *
from math import log10
from random import *
from read_abc import read_abc_file
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

files_list = ["cs1-1pre","cs1-2all","cs1-3cou","cs1-5men","cs2-1pre", "cs3-1pre"]
nb_files = len(files_list)
for filename in files_list:
    A = train("abc/" + filename + ".abc", A)
for i,row in enumerate(A):
    s = sum(row)
    if s > 0:
        A[i] = [row[j]/s for j in range(nbEtats)]

compose(0,A,10)