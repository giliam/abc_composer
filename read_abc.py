#!/usr/bin/python
# -*-coding:utf-8 -*
import os.path
import re

def parse_line(line):
	notesPattern = re.compile(r'([\^|_|=]{0,2}[A-Ga-g][,]{0,2})(/?[1-9]*)')
	notes = notesPattern.findall(line)
	return notes

def read_abc_file(filename):
	if not os.path.isfile(filename):
		print "This file doesn't exist"
		return []
	lines = []
	with open(filename, "r") as file:
		content = file.readlines()
		for line in content:
			if ":" in line or "%" in line:
				continue
			else:
				#print "Parsing " + line.replace("\n","")
				lines.append(parse_line(line))
	return [[note[i] for line in lines for note in line] for i in range(2)]

if __name__ == "__main__":
	print read_abc_file("abc/cs1-1pre.abc")
	print read_abc_file("abc/cs1-5men.abc")