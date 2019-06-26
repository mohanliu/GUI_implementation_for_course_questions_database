#!/user/bin/env python

import glob, os

questionlist = list()

os.chdir("./")
for file in glob.glob("C-Ch2*.tex"):
    str = os.path.join("./", file)
    questionlist.append(str)
numberquestions = len(questionlist)
print('There are %d quistions written for Ch. 2. They are:') % numberquestions
print(questionlist)

#Open base file, run loop
with open('./Callister-Ch2-Quiz-Exam_Base.tex','r') as in_file:
    template = in_file.readlines()

with open('./Callister-Ch2-Quiz-Exam.tex','w+') as out_file:
    for line in template:
##        if "Listz" in line: 
##            for i in range(0, len(questionlist),):
##                tempstr = questionlist[i]
##                line = line + tempstr[2] + '$|$2.' + tempstr[6] + tempstr[7] + ', '
        if "begin{questions}" in line: #can't find lines starting with / for some reason... I need a double // I think
            for i in range(0, len(questionlist),):
                line = line + '\\input{' + questionlist[i] +'}' + '\n\\newpage\n'
        out_file.write(line)

##with open('./C-Ch2-Homework.tex','w+') as out_file:
##    for line in template:
##        if "begin{questions}" in line: 
##            for i in range(0, len(questionlist),):
##                tempstr = questionlist[i]
##                print[tempstr[7]]
##                line = line + 'C2' + tempstr[6] + tempstr[7] + '/n'
##        out_file.write(line)
