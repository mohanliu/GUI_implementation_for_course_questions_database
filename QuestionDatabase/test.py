#! /usr/bin/python

import QuestionDatabase as qd
import os

q = qd.QuestionDatabase(path=os.path.join('..'))
q.update_chapter('Ashby')
q.update_chapter(2)
