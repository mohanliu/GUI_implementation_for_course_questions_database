#! /usr/bin/env python

from Tkinter import *
import DataAnalysis as da
import tkMessageBox
import tkFileDialog
import ttk
import os

tag_list = ['Class-Term', 'TypeTag', 'TopicTag',\
            'AuthorTag', 'UseTag', 'SourceTag', 'FlagTag', 'Assessment']
chapter_list = map(str, range(1,23)) + ['Ashby']

class MyCanvas():
    """
    A Canvas with both horizontal and vertical scrollbars
    Input: 
        frame: current frame for this canvas
        height: height of the canvas (width is automatically set to expand)
        bg: background color for the canvas
    """
    def __init__(self, frame, height=200, bg=None):
        """
        Constructor of MyCanvas object
        """
        self.height = height
        self.bg = bg

        # Create x and y scrollbars
        self.vscrollbar = Scrollbar(frame, orient=VERTICAL)
        self.hscrollbar = Scrollbar(frame, orient=HORIZONTAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.hscrollbar.pack(fill=X, side=BOTTOM, expand=FALSE)

        # Creat a canvas and connect to scrollbars
        self.canvas = Canvas(frame, height=height, bg=bg, highlightthickness=0, 
               yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)

        # Create a interior that can be controlled by scrollbars
        self.interior = interior = Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=interior, anchor=NW)

        # Track changes to the canvas and frame width and sync them, also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        #self.canvas.bind('<Configure>', _configure_canvas)


        # Enable mouse wheel scroll
        def _on_mousewheel(event):
            self.canvas.yview_scroll(-1*(event.delta/120), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)


class ResultWindow(Frame):
    """
    A window includes all the filter results
    """
    def __init__(self, master=None, results=[]):
        """
        Constructor of the result window
        """
        self.master = master
        self.master.title('FilterResult') # Window title
        self.question_frame = Frame(master)
        self.mycanvas = MyCanvas(self.question_frame, 320) # Create a Mycanvas object to hold the results
        self.question_frame.pack(fill=X)

        # Put all the information into the window
        r = 0
        results.sort()
        for pk in results:
            pk_var = StringVar()
            pk_var.set(pk)
            button = Button(self.mycanvas.interior, text=pk, command=lambda pk=pk: self.show_details(pk))
            button.grid(row=r, column=0)
            r += 1

    def show_details(self, pk):
        """
        Show all the details of a question into a tkMessageBox 
        """
        msg_lst = []
        for t in self.qd.tags:
            if t not in self.qd.qdatabase[pk]:
                msg_lst.append(t+': ')
            else:
                msg_lst.append(t+': '+str(self.qd.qdatabase[pk][t]))
        msg = '\n'.join(msg_lst)
        tkMessageBox.showinfo(pk,msg)


class Window(Frame):
    """
    Main window for the filter 
    """
    def __init__(self, master=None):
        """
        Constructor of the Window object
        """

        # Initialize the database
        cwd = os.path.dirname(os.path.realpath(__file__))
        pathfile = os.path.join(cwd, '_path_to_folders')
        if not os.path.exists(pathfile):
            path = tkFileDialog.askdirectory()
            with open(pathfile, 'w') as f:
                f.write(path)
        else:
            with open(pathfile, 'r') as f:
                for l in f:
                    path = l.strip()
        self.qd = da.DataAnalysis(path=path)
        self.qd.slct_tags = tag_list

        #Initialize the filter dictionaries
        self.include = {} # dictionary store including VARs
        self.exclude = {} # dictionary store excluding VARs
        self.include_boxes = {} # dictionary store excluding buttons
        self.exclude_boxes = {} # dictionary store excluding buttons
        self.subwindows = [] # list of filter results window
        for tag in self.qd.slct_tags:
            self.include[ tag ] = []
            self.exclude[ tag ] = []
            self.include_boxes[ tag ] = []
            self.exclude_boxes[ tag ] = []

        # Initialize the frame and master
        Frame.__init__(self, master)   
        self.master = master

        # Create a frame for the Chapter selection
        self.chp_frame = Frame(master)
        self.chp_frame.pack(fill=X)

        # Create a frame for key selections
        self.tags_frame = Frame(master)
        self.mycanvas1 = MyCanvas(self.tags_frame, 320)
        self.tags_frame.pack(fill=X)

        # Create a frame for score range entries
        self.score_frame = Frame(master)
        self.score_frame.pack(fill=BOTH, expand=True, anchor=W)

        # Create a frame for the Display messages
        self.display_frame = Frame(master)
        self.mycanvas2 = MyCanvas(self.display_frame, 100, 'lightgreen')
        self.display_frame.pack(fill=BOTH, anchor=W, expand=True)


        # Create a frame for control buttons
        self.button_frame = Frame(master)
        self.button_frame.pack(fill=BOTH, expand=True, anchor=W)

        # Initilize the window
        self.init_window()


    #Creation of init_window
    def init_window(self):
        """
        Initialization of the window
        """
        self.master.title("FilterForQuestions")

        # Create the chapter selection 
        inlabel = Label(self.chp_frame, text='Select a chapter', font=('system',18,'roman'))
        inlabel.grid(row=0, column=0, padx=30, pady=20, sticky=W)
        
        # Chapter selection box
        self.chpvar = StringVar()
        chs = ttk.Combobox(self.chp_frame,state='readonly',  textvariable=self.chpvar, values=chapter_list, width=8)
        chs.bind('<<ComboboxSelected>>', self.set_chapter)
        chs.grid(row=0, column=1, sticky=W)

        # Create update chapter button
        updt_but = Button(self.chp_frame, text='Update', command=self.update_chapter_data)
        updt_but.grid(row=0, column=2, padx=12)

        # Create filter tags 
        self.vars = [] # list for whether the tags are selected 
        r = 1 # a flag for 
        for tag in self.qd.slct_tags:
            var = IntVar()
            tag_var = StringVar()
            tag_var.set(tag)
            chk = Checkbutton(self.mycanvas1.interior, text=tag, variable=var, command=lambda tag=tag, var=var, r=r: self.reset(tag, var, r))
            chk.config(font=('Helvetica', 11))
            chk.grid(row=r, column=0, sticky=W)
            detail_button = Button(self.mycanvas1.interior, text='details', command=lambda tag=tag: self.show_values(tag))
            detail_button.grid(row=r, column=1)

            r += 2
            self.vars.append(var)

        # Initialize a message
        self.msg = Message(self.mycanvas2.interior, bg=self.mycanvas2.bg, width=2000)
        self.msg.pack(side=LEFT, fill=BOTH, anchor=W, expand=True)

        # Score range selection initialization
        self.score_vars = {} # Store score vars
        self.score_entries = {} # Store score entries
        self.score_buttons = {} # Store delete buttons

        score_lbl = Label(self.score_frame, text='Score range', font=('Helvetica',15, 'bold')) # Label
        score_lbl.grid(row=0, column=0, padx=10, sticky=W)


        # Create Add button to add more score ranges
        r = 0
        ab = Button(self.score_frame, text='Add', command=self.add_score)
        ab.grid(row=r, column=1, padx = 5)
        self.score_row = r

        # Control button function (for show, filter, and output)
        Button(self.button_frame, text='Show Filter ', font=('Verdana', 11), padx=20, pady=8, command=self.show_filter).pack(side=LEFT, fill=X, expand=True)
        Button(self.button_frame, text='Apply Filter', font=('Verdana', 11), padx=20, pady=8, command=self.do_filter).pack(side=LEFT, fill=X, expand=True)
        Button(self.button_frame, text='Save To File', font=('Verdana', 11), padx=20, pady=8, command=self.output_filter).pack(side=LEFT, fill=X, expand=True)
        Button(self.button_frame, text='   Exit     ', font=('Verdana', 11), padx=20, pady=8, command=self.client_exit).pack(side=LEFT, fill=X, expand=True)

    @property
    def chapter_status(self):
        """
        Check whether chapter has been selected
        """
        if not hasattr(self, 'chp'):
            tkMessageBox.showerror("Error", "Please select a chapter first!")
            return False
        else:
            return True

    def set_chapter(self, event):
        """
        Set values for class attribute 
        """
        self.chp = self.chpvar.get()
        if self.chp == "Ashby":
            self.chpname = "Ashby"
        else:
            self.chpname = "Ch"+str(self.chp)

    def update_chapter_data(self):
        """
        Update database for selected chapter
        """
        if not self.chapter_status:
            return

        self.qd.update_chapter(self.chp)

    def show_values(self, tag):
        """
        Display possible options for a selected tag
        """
        if not self.chapter_status:
            return

        # List of possible options
        chp_filter = self.qd.filter(include={'Chapter':[self.chpname]})
        lst = self.qd.check_tag(tag, chp_filter)

        output = ''
        for l in lst:
            output += l+'\n'

        # Update message 
        self.msg.config(text=output, bg=self.mycanvas2.bg, font=('times', 15))

        # Move scrollbars to original locations
        self.mycanvas2.canvas.xview_moveto(0.0)
        self.mycanvas2.canvas.yview_moveto(0.0)

    def include_values(self, tag, r):
        """
        Add option list: to select which values to be included for this tag
        """
        if not self.chapter_status:
            return

        # Make the tag checkbox checked
        index = self.qd.slct_tags.index(tag)
        self.vars[index].set(1)

        # List of options
        chp_filter = self.qd.filter(include={'Chapter':[self.chpname]})
        options = self.qd.check_tag(tag, chp_filter)

        # Add a Combobox for selection 
        vin = StringVar()
        self.include[ tag ].append(vin) # Save Var to a dict
        opt_in = ttk.Combobox(self.mycanvas1.interior, textvariable=vin, values=options)
        opt_in.grid(row=r, column=2 + len(self.include[ tag ]), sticky=W+E)
        max_width = max(map(lambda v:len(v.strip()),options))
        opt_in.config(width=min(18, max_width))
        self.include_boxes[ tag ].append(opt_in) # Save Combobox object into dict

    def exclude_values(self, tag, r):
        """
        Add option list: to select which values to be excluded for this tag
        """
        if not self.chapter_status:
            return

        # Make the tag checkbox checked
        index = self.qd.slct_tags.index(tag)
        self.vars[index].set(1)

        # List of options
        chp_filter = self.qd.filter(include={'Chapter':[self.chpname]})
        options = self.qd.check_tag(tag, chp_filter)

        # Add a Combobox for selection 
        vex = StringVar()
        self.exclude[ tag ].append(vex) # Save Var to a dict
        opt_ex = ttk.Combobox(self.mycanvas1.interior, textvariable=vex, values=options)
        opt_ex.grid(row=r+1, column=2 + len(self.exclude[ tag ]), sticky=W+E)
        max_width = max(map(lambda v:len(v.strip()),options))
        opt_ex.config(width=min(18, max_width))
        self.exclude_boxes[ tag ].append(opt_ex) # Save Combobox object into dict

    def reset(self, tag, var, r):
        """
        Reset the include/exclude selections
        If the tag is unchecked:
            Clear the dictionaries for this tag
            Remove the comboboxes for this tag
        If the tag is unchecked:
            Initialize the selections
        """
        if var.get() == 0:
            self.include[ tag ] = []
            self.exclude[ tag ] = []
            for bi in self.include_boxes[ tag ]:
                bi.destroy()
            for bx in self.exclude_boxes[ tag ]:
                bx.destroy()
        else:
            in_but = Button(self.mycanvas1.interior, text=r'+', fg='white', bg='blue', command=lambda tag=tag, r=r: self.include_values(tag, r))
            in_but.grid(row=r, column=2, sticky=W+E)
            ex_but = Button(self.mycanvas1.interior, text=r'-', fg='white', bg='red', command=lambda tag=tag, r=r: self.exclude_values(tag, r))
            ex_but.grid(row=r+1, column=2, sticky=W+E)
            self.include_boxes[ tag ].append(in_but)
            self.exclude_boxes[ tag ].append(ex_but)

    def add_score(self):
        """
        Control score range selections
        """
        ls = StringVar() # VAR for low score
        hs = StringVar() # VAR for high score
        r = self.score_row # Total rows of score range entries

        # Score range entries
        el = Entry(self.score_frame, textvariable=ls, width=5)
        el.config(borderwidth=3)
        el.grid(row=r, column=2, padx=15)
        eh = Entry(self.score_frame, textvariable=hs, width=5)
        eh.config(borderwidth=3)
        eh.grid(row=r, column=3, padx=15)

        # Delete button to delete this score range 
        db = Button(self.score_frame, text='Delete', command=lambda r=r: self.delete_score(r))
        db.grid(row=r, column=4, padx=15)

        # Save Var, entries and buttons into dictionaries
        self.score_vars[r] = [ls, hs]
        self.score_entries[r] = [el, eh]
        self.score_buttons[r] = db

        # Update the total rows of score range entries
        self.score_row = r + 1

    def delete_score(self, r):
        """
        Delete a score range entry
        """
        if not r < 0:
            del self.score_vars[r]
            self.score_entries[r][0].destroy()
            self.score_entries[r][1].destroy()
            self.score_buttons[r].destroy()
            self.score_row -= 1

    def save_filter(self):
        """
        Save include/exclude selections into dicts
        Save score ranges into list
        ( Remove duplicates )
        """
        if not self.chapter_status:
            return

        # Save include dict
        self.include_dict = {}
        self.include_dict[ 'Chapter' ] = [self.chpname]
        for k in self.include.keys():
            tmp = []
            for v in self.include[ k ]:
                if v:
                    if v.get() != '' and v.get() not in tmp:
                        tmp.append(v.get())
            if tmp:
                self.include_dict[ k ] = tmp

        # Save exclude dict
        self.exclude_dict = {}
        for k in self.exclude.keys():
            tmp = []
            for v in self.exclude[ k ]:
                if v:
                    if v.get() != '' and v.get() not in tmp:
                        tmp.append(v.get())
            if tmp:
                self.exclude_dict[ k ] = tmp

        # Save VALID score ranges 
        self.score_lst = []
        for sl in self.score_vars.keys():
            err = 0
            try:
                l = float(self.score_vars[sl][0].get())
            except:
                l = 0
                err += 1

            try:
                h = float(self.score_vars[sl][1].get())
            except:
                h = 100
                err += 1
            
            if not h < l and [l, h] not in self.score_lst and err != 2:
                # Only save valid entries
                #   1. low score < high score
                #   2. The score range is unique
                #   3. At least one entry is valid
                self.score_lst.append([l, h])

        # Default score range
        if not self.score_lst:
            self.score_lst = [[0, 100]]

    def show_filter(self):
        """
        Display filter information
        """
        if not self.chapter_status:
            return
        self.save_filter()
       
        ml = []
        ml.append('INCLUDE')
        for k in self.include_dict.keys():
            ml.append('  '+k+': '+ ', '.join(self.include_dict[k]))

        ml.append('EXCLUDE')
        for k in self.exclude_dict.keys():
            ml.append('  '+k+': '+ ', '.join(self.exclude_dict[k]))

        ml.append('Score Range')
        for s in self.score_lst:
            ml.append('  '+str(s[0])+' ~ '+str(s[1]))

        output = '\n'.join(ml)+'\n'
        self.msg.config(text=output, bg=self.mycanvas2.bg, font=('times', 15))
        self.mycanvas2.canvas.xview_moveto(0.0)
        self.mycanvas2.canvas.yview_moveto(0.0)

        return output

    def do_filter(self):
        """
        Apply filter and get results
        """
        if not self.chapter_status:
            return

        # Filter information
        output = self.show_filter()

        # Apply filter
        results = self.qd.filter(include=self.include_dict, exclude=self.exclude_dict, score=self.score_lst)

        # Display information into message box
        msg = '%d cases matched\n\n'%len(results)
        self.msg.config(text=msg+output)
        self.mycanvas2.canvas.xview_moveto(0.0)
        self.mycanvas2.canvas.yview_moveto(0.0)

        # Open a new window and output filter results
        subroot = Tk()
        rw = ResultWindow(master=subroot, results=results)
        rw.qd = self.qd
        self.subwindows.append(rw)
        subroot.mainloop()

    def output_filter(self):
        """
        Save filter results into .txt file
        """
        if not self.chapter_status:
            return
        
        # Filter information
        filter_info = self.show_filter() 
        
        # Apply filter
        results = self.qd.filter(include=self.include_dict, exclude=self.exclude_dict, score=self.score_lst)

        # Display information into message box
        msg = '%d cases matched\n\n'%len(results)
        self.msg.config(text=msg+filter_info)
        self.mycanvas2.canvas.xview_moveto(0.0)
        self.mycanvas2.canvas.yview_moveto(0.0)

        # Output format
        filter_results = '\n'.join(map(lambda v: '#'+v, sorted(results))) # add hash in front of each problem
        filter_outcome = msg + filter_info+'\n'+filter_results

        # Save result to file
        f = tkFileDialog.asksaveasfile(mode='w', defaultextension='.txt')
        if f is None:
            return
        f.write(filter_outcome)
        f.close()

    def client_exit(self):
        self.master.destroy()
        for i in range(len(self.subwindows)):
            rw = self.subwindows[i]
            try:
                rw.master.destroy()
            except:
                pass

if __name__ == "__main__":
    root = Tk()
    root.geometry("600x650")
    app = Window(master=root)
    root.mainloop()  
