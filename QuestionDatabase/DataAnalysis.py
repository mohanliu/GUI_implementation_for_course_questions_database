#! /usr/bin/python

import QuestionDatabase as qd

class DataAnalysis(qd.QuestionDatabase):
    def __init__(self, path=None):
        qd.QuestionDatabase.__init__(self, path)
        self.qs = self.qdatabase.keys()

    def check_tag(self, tag, qlst):
        """
        To check all possible values for this tag
        Usage:
            q = DataAnalysis()
            qlst = q.qs[:3] # or a list obtained from filter function
            q.check_tag('Author', qlst)
        """
        if not qlst:
            print "UserError: Empty list"
            return
        if tag not in self.tags:
            print "UserError: tag doesn't exist"
            return

        vlst = []
        for qn in qlst:
            if tag not in self.qdatabase[qn]:
                continue
            v = self.qdatabase[qn][tag]
            if v not in vlst:
                vlst.append(v)

        return vlst

    @property
    def tags(self):
        total_tags = []
        for k in self.qdatabase.keys():
            for kk in self.qdatabase[k].keys():
                if kk not in total_tags:
                    total_tags.append(kk)

        return total_tags
        
    def filter(self, include={}, exclude={}, score = [[0, 100]], verbose=False):
        """
        Filter the database
        Usage:
            q = DataAnalysis()
            include = {'Chapter': ['Ch2'], 'TopicTag': ['BondType']}
            exclude = {'FlagTag': ['']}
            score = [[0, 0], [90, 100]]
            q.filter(include, exclude, score)
        """
        tmp = self.qdatabase.keys()

        # Print information
        if verbose: 
            print
            print "INCLUDE:"
        for ki in include.keys():
            if verbose: print "Filter key: ", ki, "   Filter value: ", include[ki]
            if ki not in self.tags:
                if verbose: print "This key doesn't exist!"
                return
        if verbose: print "EXCLUDE:"
        for ke in exclude.keys():
            if verbose: print "Filter key: ", ke, "   Filter value: ", exclude[ke]
            if ke not in self.tags:
                if verbose_only: print "This key doesn't exist!"
                return

        sc_lst = []
        for sc in score:
            if len(sc) != 2:
                print "Enter a score range using a list with two number element"
                return
            try:
                s = map(float, sc)
                l = max(0, min(sc))
                h = min(100, max(sc))
                sc_lst.append([l, h])
            except:
                print "Score range format is not correct"
                return
            if verbose: print "Score Range:", l, "~", h


        # Apply filter to select the wanted questions
        i = 0
        while i < len(tmp):
            qn = tmp[i]

            # Check whether satisfies all criteria
            flag = 0 # 0 for OK, > 0 for not OK

            for ki in include.keys():
                if ki not in self.qdatabase[qn].keys():
                    flag += 1
                else:
                    # Subcheck: 0 for at least one match, 1 for no matches
                    subflag = 1

                    for v in include[ki]:
                        if v in self.qdatabase[qn][ki]:
                            subflag *= 0

                    flag += subflag # Requires at least one match for including

            for ke in exclude.keys():
                if ke not in self.qdatabase[qn].keys():
                    flag += 0
                else:
                    # Subcheck: 0 for at least one match, 1 for no matches
                    subflag = 1

                    for v in exclude[ke]:
                        if v in self.qdatabase[qn][ke]:
                            subflag *= 0

                    flag += 1 - subflag # No match is allowed for excluding

            if 'Results' not in self.qdatabase[qn].keys():
                print "ERROR: No results key for this question."
                return

            subflag = 1
            for sl in sc_lst:
                if self.qdatabase[qn]['Results'] > sl[1] or self.qdatabase[qn]['Results'] < sl[0]:
                    continue
                else:
                    subflag *= 0
            flag += subflag

            if flag == 0:
                i += 1
            else:
                tmp.pop(i)

        return tmp
