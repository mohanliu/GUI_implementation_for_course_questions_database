#! /usr/bin/python

import os
import yaml
import re
from os import remove
from shutil import move


def get_chapter_qlst(chp):
    """
    Return a list of filenames. Each element refer to a file with quesiton.
    """
    qlst = []

    current_chp = 'Ch' + str(chp)
    chp_path = os.path.join('.', current_chp)

    chp_file = os.path.join(chp_path, \
            'Callister-' + current_chp + '-Quiz-Exam.tex') # Main latex file in the chapter

    if not os.path.exists(chp_file):
        return

    with open(chp_file, 'r') as f:
        for line in f:
            if '\input{' and current_chp and '.tex}' in line:
                fn = line.strip().replace('\\input{./','').replace('}','') # Get raw file name 
                qlst.append(fn)
    
    return qlst

def modify_tex(chp):
    """
    Modify the outcomes block for each question
    """
    chp_name = 'Ch' + str(chp)
    qlst = get_chapter_qlst(chp) # List of questions

    if not qlst:
        return
    
    for q in qlst:
	newfile = os.path.join('.', chp_name, q) # Full path of the file 
        bkfile = newfile + '.bk'
        move(newfile, bkfile)
        
        with open(newfile, 'w') as nf:
            with open(bkfile, 'r') as of:
                for line in of:
                    if '\\begin{outcomes}' in line:
                        nf.write(line)
                        break
                    else:
                        nf.write(line)

	        for line in of:
	            if 'Class-Term' in line:
                        nf.write('                Class-Term & Instructor & Assessment & Results (Full/Partial/No Credit) \\\\\n')
    
	            elif '&' in line:
	            	# Read the outcome for this question
	            	tmp = '                '
	            	ol = line.strip().split('&')
                        tmp += ' & '.join([ v.strip() for v in ol[:3]])
	            	raw_score = ol[ 3 ].strip().replace('\\\\','')
	            	
	            	if 'ignore' in raw_score:
	            	    tmp += ' &  \\\\\n'
	            	else:
                            # Store the credit data into dictionary
	            	    credits = re.findall('\d+', raw_score)

	            	    if not credits:
	            	        tmp += ' &  \\\\\n'

	            	    elif len(credits) == 3:
                                tmp += ' & ' + '/'.join([v+'\%' for v in credits])
                                tmp += '\\\\\n'

	            	    elif len(credits) == 2:
                                credits.append('0')
                                tmp += ' & ' + '/'.join([v+'\%' for v in credits])
                                tmp += '\\\\\n'
	            			
	            	    elif len(credits) == 1:
                                credits.append('0')
                                credits.append('0')
                                tmp += ' & ' + '/'.join([v+'\%' for v in credits])
                                tmp += '\\\\\n'

	            	    else:
	            	        print "Not implemented Error for this format: "+line.strip()
	            	        tmp += ' &  \\\\\n'
	            			
                        nf.write(tmp)

                    elif '\end{outcomes}' in line:
                        nf.write(line)
                        break

                    else:
                        nf.write(line)

                for line in of:
                    nf.write(line)

def remove_backup(chp):
    """
    Remove the backup files
    """
    chp_name = 'Ch' + str(chp)

    qlst = get_chapter_qlst(chp) # List of questions
    if not qlst:
        return
    
    for q in qlst:
	newfile = os.path.join('.', chp_name, q) # Full path of the file 
        bkfile = newfile + '.bk'
        remove(bkfile)

if __name__ == "__main__":
    modify_tex(2)
    remove_backup(2)
