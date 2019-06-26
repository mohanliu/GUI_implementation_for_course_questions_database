#! /usr/bin/python

import os
import yaml
import re
import glob

class QuestionDatabase:
    def __init__(self, path=None, yaml_path=None):
    	"""
    	Constructor of QuestionDatabase class
    	"""
        if path == None:
            print "Must input the directory of the questions chapter folders"
            exit()
        else:
            self.global_path = path

        if yaml_path == None:
            cwd = os.path.dirname(os.path.realpath(__file__))
            self.yaml_file = os.path.join(cwd, 'qDatabase.yml')
        else:
            self.yaml_file = os.path.join(yaml_path, 'qDatabase.yml')

        self.read_yaml()

    def get_chapter_qlst(self, chp):
    	"""
    	Return a list of filenames. Each element refer to a file with quesiton.
    	"""
        qlst = []

        home = os.getcwd()

        if chp == 'Ashby':
            current_chp = chp
            filenames = "Ashby*.tex"
        else:
            current_chp = 'Ch' + str(chp)
            filenames = "C-Ch" + str(chp) + "*.tex"

        chp_path = os.path.join(self.global_path, current_chp)
        os.chdir(chp_path)

        for fn in glob.glob(filenames):
            qlst.append(fn)

        os.chdir(home)

        #chp_file = os.path.join(chp_path, \
        #        'Callister-' + current_chp + '-Quiz-Exam.tex') # Main latex file in the chapter

        #if not os.path.exists(chp_file):
        #    return
    
        #with open(chp_file, 'r') as f:
        #    for line in f:
        #        if '\input{' and current_chp and '.tex}' in line:
        #            fn = line.strip().replace('\\input{./','').replace('}','') # Get raw file name 
        #            qlst.append(fn)
        
        return qlst

    def reset_chapter(self, chp):
    	"""
    	Delete the information for a certain chapter
    	"""
        if chp != 'Ashby':
    	    chp_name = 'Ch' + str(chp)
        else:
            chp_name = chp

        for k in self.qdatabase.keys():
            if self.qdatabase[k][ 'Chapter' ] == chp_name:
                del self.qdatabase[k]

    def update_chapter(self, chp):
    	"""
    	Update the database for a certain chapter & write to yml file
    	"""
        self.reset_chapter(chp) # Reset the previous chapter dictionary

        if chp != 'Ashby':
    	    chp_name = 'Ch' + str(chp)
        else:
            chp_name = chp

    	qlst = self.get_chapter_qlst(chp) # List of questions
        if not qlst:
            return
   	
    	for q in qlst:
    	    qdict = {} # Information for a single question
    	    pk = q.replace('.tex','') # Primary key for this question
    	    file = os.path.join(self.global_path, chp_name, q) # Full path of the file 
    	    
    	    qdict[ 'FullPath' ] = file
            qdict[ 'Chapter' ] = chp_name

    	    with open(file, 'r') as f:
    	        # Pass the content of the question and start checking outcomes
    	        for line in f:
    	            if '\\begin{FileID}' in line:
    	                break # Quit loop once file we find the outcome block

    	        # Read general information
    	        for line in f:
    	            if '\end{FileID}' in line: 
    	            	break  # Quit loop after we have all the information
                        
    	            if '\#' in line:
    	            	line = line.strip().split('\\\\')[0].strip()  # Remove everything after double-blackslash (including comments)
    	            	tags = line.split('\#')
                        
    	            	for t in tags:
    	            	    if not t:
    	            	        continue 

    	                    tag = t.strip()

    	            	    if tag[-1] == '&':
    	            		tag = tag[ :-1 ] # remove & sign
    	            		
                            key = tag.split(':')[0] # Read the tag name
                            
    	            	    try:
    	            	        value = tag.split(':')[1].strip() # Assign tag value
    	            	    except:
    	            	        value = ''

                            qdict[ key ] = value

                # Check flagtag
                if 'FlagTag' in qdict.keys():
                    qdict[ 'FlagTag' ] = 'Yes'
                else:
                    qdict[ 'FlagTag' ] = 'No'


    	        # Pass the content of the question and start checking outcomes
    	        for line in f:
    	            if '\\begin{outcomes}' in line:
    	                break # Quit loop once file we find the outcome block
	
    	        # Read outcome information
    	        outcome = []
    	        for line in f:
    	            if '\end{outcomes}' in line:
    	            	break # Quit loop after read all the outcome information
	
    	            if 'Class-Term' in line:
    	            	continue # Ignore the header of the tabular
	
    	            if '&' in line:
    	            	# Read the outcome for this question
    	            	tmp = {} 
    	            	try:
    	            	    ol = line.strip().split('&')
    	            	    tmp[ 'Class-Term' ]     = ol[ 0 ].strip()
    	            	    tmp[ 'TermInstructor' ] = ol[ 1 ].strip()
    	            	    tmp[ 'Assessment' ]     = ol[ 2 ].strip()
    	            	    raw_score = ol[ 3 ].strip().replace('\\\\','')
	
    	            	except:
    	            	    print "Outcome format is not correct!"
    	            	    print file
    	            	
    	            	score = {}
    	            	if 'ignore' in raw_score:
    	            	    tmp[ 'score' ] = {}
    	            	else:
                            # Store the credit data into dictionary
    	            	    credits = re.findall('\d+', raw_score)

    	            	    if not credits:
    	            	        score = {}

    	            	    elif len(credits) == 3:
    	            	        score[ 'FullCredit' ]    = int(credits[0])
    	            	        score[ 'PartialCredit' ] = int(credits[1])
    	            	        score[ 'NoCredit' ]      = int(credits[2])

    	            	    elif len(credits) == 2:
    	            	        score[ 'FullCredit' ]    = int(credits[0])
    	            	        score[ 'PartialCredit' ] = int(credits[1])
    	            	        score[ 'NoCredit' ]      = 0
    	            			
    	            	    elif len(credits) == 1:
    	            	        score[ 'FullCredit' ]    = int(credits[0])
    	            	        score[ 'PartialCredit' ] = 0
    	            	        score[ 'NoCredit' ]      = 0

    	            	    else:
                                print q
    	            	        print "Not Implemented Error for this format: "+line.strip()
    	            	        score = {}
    	            			
		            tmp[ 'Score' ] = score
    	                outcome.append(tmp)

    	        qdict[ 'Outcome' ] = outcome

                # Include information for the most recent outcome
                try:
                    recent_outcome =  outcome[-1]
                except:
                    recent_outcome = {}

                try:
                    qdict[ 'Class-Term' ] = recent_outcome[ 'Class-Term' ] 
                except:
                    qdict[ 'Class-Term' ] = ''

                try:
                    qdict[ 'Results' ] = float(recent_outcome[ 'Score' ][ 'FullCredit' ]) * 1 +\
                                         float(recent_outcome[ 'Score' ][ 'PartialCredit']) * 0.5 +\
                                         float(recent_outcome[ 'Score' ][ 'NoCredit' ]) * 0
                except:
                    qdict[ 'Results' ] = 0.0

                try:
                    qdict[ 'Assessment' ] = recent_outcome[ 'Assessment' ]
                except:
                    qdict[ 'Assessment' ] = ''

            self.qdatabase[ pk ] = qdict

    	self.write_yaml()

    def read_yaml(self):
        """
        Read data from yaml file
        """
        if not os.path.exists(self.yaml_file):
            self.qdatabase = {}
        else:
            with open(self.yaml_file, 'r') as f:
                try:
                    self.qdatabase = yaml.load(f)
                except yaml.YAMLError as e:
                    print e

    def write_yaml(self):
        """
        Write data into yaml file
        """
    	with open(self.yaml_file, 'w') as f:
            yaml.dump(self.qdatabase, f, default_flow_style = False)


if __name__ == "__main__":
    q = QuestionDatabase()
