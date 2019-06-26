#! /usr/bin/python

import QuestionDatabase as qd

q = qd.QuestionDatabase(path=None)
q.update_chapter('Ashby')
q.update_chapter(2)
q.get_chapter_qlst(2)
