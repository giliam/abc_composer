#!/usr/bin/python
# -*-coding:utf-8 -*
from itertools import *
from math import log10
import csv
DEBUG = True


etatsPossibles = [
    "La,,","Si,,","Do,,","Re,,","Mi,,","Fa,,","Sol,,",
    "La,","Si,","Do,","Re,","Mi,","Fa,","Sol,",
    "La","Si","Do","Re","Mi","Fa","Sol",
    "_La,,","_Si,,","_Do,,","_Re,,","_Mi,,","_Fa,,","_Sol,,",
    "_La,","_Si,","_Do,","_Re,","_Mi,","_Fa,","_Sol,",
    "_La","_Si","_Do","_Re","_Mi","_Fa","_Sol",
    "^La,,","^Si,,","^Do,,","^Re,,","^Mi,,","^Fa,,","^Sol,,",
    "^La,","^Si,","^Do,","^Re,","^Mi,","^Fa,","^Sol,",
    "^La","^Si","^Do","^Re","^Mi","^Fa","^Sol"
]
nbEtats = len(etatsPossibles)
PI = [1./nbEtats for i in range(nbEtats)]
A = [[1./nbEtats for i in range(nbEtats)] for j in range(nbEtats)]

visibles = ["La","Si","Do","Re","Mi","Fa","Sol",
"_La","_Si","_Do","_Re","_Mi","_Sol","^Fa"]
nbVisibles = len(visibles)

E = [[] for i in range(nbEtats)]

notes_gammes = {note:[] for note in etatsPossibles}
with open('gammes_data.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        for note in row:
            notes_gammes[note].append(row[0])

    for i,note in enumerate(etatsPossibles):
        note_m = note.replace(',','')            
        for j,gamme in enumerate(visibles):
            if gamme in notes_gammes[note_m]:
                E[i].append(1./len(notes_gammes[note_m]))
            else:
                E[i].append(0)

N = len(A)
S = len(visibles)
etats = range(N)


def argmax(values):
    return max(enumerate(values), key=lambda x:x[1])

def forward (PI, A, E, sequence):
    T = len(sequence)
    temps = range(T)

    alpha = [[0. for t in temps] for i in etats]
    for i in etats:
        alpha[i][0] = PI[i] * E[i][sequence[0]]

    for t in range(1,T):
        for j in etats:
            for i in etats:
                alpha[j][t] += alpha[i][t-1]*A[i][j]
            alpha[j][t] *= E[j][sequence[t]]
    proba = 0.
    for j in etats:
        proba += alpha[j][T-1]
    if DEBUG:
        print "---------------"
        print "FORWARD"
        print "Pour la séquence : "
        print sequence
        print "Proba de : "
        print proba
        print "---------------\n\n"
    return proba,alpha


def backward (PI, A, E, sequence):
    T = len(sequence)
    temps = range(T)

    beta = [[0. for t in temps] for i in etats]
    for i in etats:
        beta[i][T-1] = 1

    for t in range(T-2, -1, -1):
        for j in etats:
            r = 0
            for i in etats:
                r += beta[i][t+1]*A[j][i]*E[i][sequence[t+1]]
    proba = 0.
    for i in etats:
        proba += PI[i]*E[i][sequence[0]]*beta[i][0]
    if DEBUG:
        print "---------------"
        print "BACKWARD"
        print "Pour la séquence : "
        print sequence
        print "Proba de : "
        print proba
        print "---------------\n\n"
    return beta

def viterbi(PI,A,E,sequence):
    T = len(sequence)
    temps = range(T)

    delta = [[0. for t in temps] for i in etats]
    for i in etats:
        delta[i][0] = PI[i] * E[i][sequence[0]]
    psi = [[0. for t in temps] for i in etats]
    for t in range(0,T-1):
        for j in etats:
            for i in etats:
                psi[j][t],delta[j][t+1] = argmax([delta[i][t]*A[i][j] for i in etats])
                delta[j][t+1] *= E[j][sequence[t+1]]
    path = [0. for j in temps]
    proba = 1
    for t in range(T-1, -1, -1):
        path[t],p = argmax([delta[j][t] for j in etats])
        proba *= p
    return path,proba

def baum_welch(PI,A,E,sequence):
    T = len(sequence)
    temps = range(T)

    xi = [[[0. for t in temps] for i in etats] for j in etats]
    gamma = [[0. for i in etats] for t in temps]
    proba,alpha = forward(PI,A,E,sequence)
    beta = backward(PI,A,E,sequence)
    
    for t in range(T-1):
        for i in etats:
            s = 0.
            for j in etats:
                xi[i][j][t] = alpha[i][t]*A[i][j]*E[j][sequence[t+1]]*beta[j][t+1]/proba
                s += xi[i][j][t]
            gamma[t][i] = s

    

    nPI = gamma[0]
    nA = [[0. for i in etats] for j in etats]
    nE = [[E[j][i] for i in range(S)] for j in etats]

    sGamma = [0. for i in etats]
    for i in etats:
        for t in range(T-1):
            sGamma[i] += gamma[t][i]
        for j in etats:
            sXi = 0.
            for t in range(T-1):
                sXi += xi[i][j][t]
            nA[i][j] = sXi/sGamma[i]
    print gamma
    for j in etats:
        for o in range(S):
            s = 0.
            print o
            for t in range(T):
                print t
                if o == sequence[t]:
                    s += gamma[t][j]
            nE[j][o] = s/(sGamma[j]+gamma[T-1][j])
            print "--"
    print E
    print nE
    nProba,nAlpha = forward(nPI,nA,nE,sequence)

    print "---------------"
    print "BAUM WELCH"
    print "Pour la séquence : "
    print sequence
    print "AVANT"
    print "Proba de : "
    print proba
    print "APRES"
    print "Proba de : "
    print nProba
    print "---------------\n\n"

bf = False
vi = False
bw = False
if bf:
    backward(PI,A,E,[0])
    backward(PI,A,E,[0,1])
    backward(PI,A,E,[1])
    backward(PI,A,E,[2])
    forward(PI,A,E,[0])
    forward(PI,A,E,[0,1])
    forward(PI,A,E,[1])
    forward(PI,A,E,[2])
if vi:
    viterbi(PI,A,E,[0,1])
if bw:
    baum_welch(PI,A,E,[0,1])
