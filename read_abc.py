#!/usr/bin/python
# -*-coding:utf-8 -*
import os.path
import re
import os

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

def write_abc(seed,data):
	filename = "output/" + str(seed) + ".abc"
	with open(filename, "w") as file:
		file.write(data)
	os.system(" ".join(["abcm2ps", filename, "-O", "output/" + str(seed) + ".ps"]))
	os.system(" ".join(["ps2pdf", "output/" + str(seed) + ".ps", "output/" + str(seed) + ".pdf"]))
	#os.system(" ".join(["acroread", "output/" + str(seed) + ".pdf"]))
	os.system(" ".join(["abc2midi", filename, "-o", "output/" + str(seed) + ".mid"]))
	os.system(" ".join(["timidity", "output/" + str(seed) + ".mid"]))

if __name__ == "__main__":
	print read_abc_file("abc/cs1-1pre.abc")
	print read_abc_file("abc/cs1-5men.abc")