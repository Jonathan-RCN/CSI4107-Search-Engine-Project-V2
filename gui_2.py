"""
Title: GUI for Search Engine

Project: CSI4107 Project
Version: Vanilla System + Final System
Component: Module 1 + Module 7

Created: 23 Jan 2020
Last modified: 13 Apr 2020

Author: Tiffany Maynard
Status: Completed

Description: Allow a user to access search engine capabilities

"""
import tkinter
from tkinter import messagebox
import tkinter.scrolledtext as tkscrolled
from tkinter import PhotoImage
import tkinter.ttk
import re
import config
import corpus_access
import vsm_retrieval
import boolean_search
import spelling
from tkinter_autocomplete_listbox import AutocompleteEntry
import Reteurs.global_query_expansion as qem
import Reteurs.relevance_feeback as rf
import Reteurs.Querry_Completion as qcm

class SearchEngineGUI:
    """Start the search engine GUI."""

    def __init__(self):
        """Initialize search GUI."""
        self.font_to_use = "courier 10 pitch"
        # GUI Code adapted from
        # https://codinginfinite.com/gui-application-in-python-tkinter-tutorial/
        # Create a root window
        self.root = tkinter.Tk()
        self.root.title("Jindalee - a search engine")
        self.root.geometry("1200x1200")
        # Create frames

        top_frame = tkinter.Frame(self.root)
        self.expanded_frame = tkinter.Frame(self.root)
        self.expanded_list = list()
        self.tailor_frame = tkinter.Frame(self.root)
        self.tailor_list = list()
        self.spelling_frame = tkinter.Frame(self.root)
        self.spelling_list = list()
        topic_frame = tkinter.Frame(self.root)
        search_frame = tkinter.Frame(self.root)
        collection_frame = tkinter.Frame(self.root)
        button_frame = tkinter.Frame(self.root)
        bottom_frame = tkinter.Frame(self.root)
        results_frame = tkinter.Frame(bottom_frame)
        # Create labels
        tkinter.Label(top_frame, font=(self.font_to_use, 24),
                      fg='#5016b5', text='Jindalee  ').pack(side='left')


        #self.search_entry = tkinter.Entry(top_frame, width=50, textvariable="Type here",
#                                          font=(self.font_to_use, 18))

        #self.search_entry.pack(side='left')
        auto_complete_list = qcm.qcm_completion_list_access()
        #auto_complete_list = ["stock broker", "wine box", "wine maker", "stocks life"]
        def matches(field_value, ac_list_entry):
            pattern = re.compile(re.escape(field_value) + '.*', re.IGNORECASE)
            return re.match(pattern, ac_list_entry)

        self.search_entry = AutocompleteEntry(
            auto_complete_list, top_frame, width=50, font=(self.font_to_use, 18),
            matchesFunction=matches)
        self.search_entry.pack(side='left')
        self.expanded_label = tkinter.Label(
            self.expanded_frame,
            text=" ", font=(self.font_to_use, 14))
        self.expanded_label.pack(side='left')
        self.tailor_label = tkinter.Label(
            self.tailor_frame,
            text=" ", font=(self.font_to_use, 14))
        self.tailor_label.pack(side='left')

        self.spelling_label = tkinter.Label(
            self.spelling_frame,
            text=" ", font=(self.font_to_use, 18))
        self.spelling_label.pack(side='left')
        mag_glass = PhotoImage(file='magglass2.png')
        mag_glass = mag_glass.subsample(8)
        # Create the button widgets
        #height=25, width=25,
        self.search_button = tkinter.Button(
            top_frame,
            image=mag_glass,
            command=self.run_search,
            font=(self.font_to_use, 18))
        #bind Return key to search
        self.root.bind('<Return>', lambda event=None: self.run_search())

        self.search_button.pack(side='left')
        tkinter.Label(bottom_frame, font=(self.font_to_use, 18),
                      text='Search results (right-click a result to toggle relevance)').pack()
        self.search_topic = tkinter.StringVar()
        #// topics = config.TOPICS
        # self.search_topic.set(topics[0])
        tkinter.Label(topic_frame,
                      text="Choose a topic:",
                      justify=tkinter.LEFT,
                      font=(self.font_to_use, 18)).pack(side='left')
        #dropdown = tkinter.OptionMenu(topic_frame, self.search_topic, *topics)
        #// dropdown = tkinter.ttk.Combobox(topic_frame, textvariable=self.search_topic, values=topics)
        #menu = dropdown.nametowidget(dropdown.menuname)
        #// dropdown.pack()
        #menu.configure(font=(self.font_to_use, 18))
        #// dropdown.configure(width=25, font=(self.font_to_use, 18))
        self.search_model = tkinter.IntVar()
        # Initialize search model to 1 - Boolean
        self.search_model.set(1)
        tkinter.Label(search_frame,
                      text="Choose a search model:",
                      justify=tkinter.LEFT,
                      font=(self.font_to_use, 18)).pack(side='left')

        tkinter.Radiobutton(search_frame,
                            text="Boolean",
                            font=(self.font_to_use, 18),
                            variable=self.search_model,
                            value=1).pack(side='left')
        tkinter.Radiobutton(search_frame,
                            text="VSM",
                            font=(self.font_to_use, 18),
                            variable=self.search_model,
                            value=2).pack(side='left')
        # Initialize collection to 1 - uO course_html_div_element catalogue
        self.search_collection = tkinter.IntVar()
        self.search_collection.set(1)
        tkinter.Label(collection_frame,
                      text="Choose a collection:",
                      justify=tkinter.LEFT,
                      font=(self.font_to_use, 18)).pack(side='left')
        tkinter.Radiobutton(collection_frame,
                            text="uO Course Catalogue",
                            font=(self.font_to_use, 18),
                            variable=self.search_collection,
                            value=1).pack(side='left')
        self.reuters_radio = tkinter.Radiobutton(collection_frame,
                                                 text="Reuters",
                                                 font=(self.font_to_use, 18),
                                                 variable=self.search_collection,
                                                 value=2)
        self.reuters_radio.pack(side='left')
        #self.reuters_radio.configure(state=tkinter.DISABLED)
        self.search_results = tkscrolled.ScrolledText(results_frame,
                                                      state="normal", wrap='word',
                                                      font=(self.font_to_use, 12))
        self.search_results.pack(side='bottom')
        # Now pack the frames also

        top_frame.pack(padx=50, pady=40, side='top', fill='both')
        self.expanded_frame.pack()
        self.tailor_frame.pack()
        self.spelling_frame.pack()
        topic_frame.pack()
        search_frame.pack()
        collection_frame.pack()
        button_frame.pack()
        results_frame.pack()
        bottom_frame.pack()
        self.root.mainloop()

    def run_search(self):
        """Start search (callback function for search button)."""
        if not self.search_entry.get().strip():
            return
        # Clear previous search results
        # Clear previous suggestions
        self.expanded_label.config(text="")
        self.tailor_label.config(text="")
        self.spelling_label.config(text="")
        for lab in self.tailor_list:
            lab.destroy()
        for lab in self.spelling_list:
            lab.destroy()
        for lab in self.expanded_list:
            lab.destroy()
        self.search_results.delete('1.0', "end")
        self.search_results.insert("insert", 'Searching, please wait...')
        self.root.update()
        # Set corpus to be used for search
        if self.search_collection.get() == 1:
            corpus = config.UOTTAWA
        else:
            corpus = config.REUTERS

        # Set search type
        if self.search_model.get() == 1:
            if boolean_search.check_for_operators(self.search_entry.get().strip()):
                search = 'Boolean'
            else:
                messagebox.showinfo(
                    "Change query to VSM",
                    "No Boolean operators (AND, OR, AND_NOT) found in query, changing query to VSM")
                self.search_model.set(2)
                search = 'VSM'
        else:
            search = 'VSM'

        if search == 'VSM':
        #do VSM search
            docs_retrieved = vsm_retrieval.retrieve(self.search_entry.get().strip(),
                                                    corpus)#// , self.search_topic.get())
        else:
        #do boolean search
            docs_retrieved = boolean_search.boolean_search_module(
                self.search_entry.get().strip(), corpus)
        self.search_results.delete('1.0', "end")
        # Clear previous suggestions
        self.expanded_label.config(text="")
        self.tailor_label.config(text="")
        self.spelling_label.config(text="")
        for lab in self.tailor_list:
            lab.destroy()
        for lab in self.spelling_list:
            lab.destroy()
        for lab in self.expanded_list:
            lab.destroy()
        #account for times a word is returned instead of a doc_id
        if docs_retrieved and isinstance(docs_retrieved, str):
            docs_retrieved = []
        docs = corpus_access.get_documents(corpus, docs_retrieved)
        hyperlink = HyperlinkManager(self.search_results)

        suggestions = spelling.suggest_words(self.search_entry.get().strip(), corpus)

        exp_obj = qem.create_global_expanded_query(self.search_entry.get().strip(), search)
        expanded = exp_obj.expanded_query
        tailored_items = exp_obj.suggestions

        if expanded and (exp_obj.initial_query != expanded):
            self.show_suggested_items(1, [expanded], self.expanded_list,
                                      self.expanded_label, self.expanded_frame)
            self.expanded_label.config(text="Expanded query: ")
        if tailored_items and len(tailored_items) > 1:
            self.show_suggested_items(config.QEM_MAX_QUERY_WORD_LEN_FOR_EXP, tailored_items, self.tailor_list,
                                      self.tailor_label, self.tailor_frame)
            self.tailor_label.config(text="Refine search: ")
        if suggestions:
            self.show_spelling_options(config.TOP_N_SPELLING, suggestions)
            self.spelling_label.config(text="Did you mean? ")
        if docs is None or docs == []:
            self.search_results.insert("insert", 'No documents found')
        else:
            input_query = self.search_entry.get().strip().replace('( ', '(').replace(' )', ')')
            for doc in docs:
                score_str = ''
                #placeholder to add relevant indicator
                relevant_str = ' '
                if search == 'VSM':
                    score_str = '{:0.3f}'.format(doc.score) + ' '
                self.search_results.insert("insert",
                                           score_str + doc.title + relevant_str,
                                           hyperlink.add
                                           (self.click_link, doc.doc_id, corpus))
                self.search_results.insert("insert", doc.doctext[:100] + '\n')

    def click_link(self, click_id, corpus, btn):
        """Click link function."""
        # add score of 1.0 for consistency of arguments
        input_query = self.search_entry.get().strip().replace('( ', '(').replace(' )', ')')
        if btn == 'left':
            doc = corpus_access.get_documents(corpus, [(click_id, 1.0)])[0]
            messagebox.showinfo(
                doc.title,
                rf.get_relevance(input_query, doc.doc_id, corpus) \
                + ' ' + str(doc.doc_id) + ' \n' + doc.doctext)
        if btn == 'right':
            rf.update_relevance(input_query, click_id, corpus)

    def show_spelling_options(self, max_count, suggestions):
        """Show spelling suggestions."""
        for i in range(min(max_count, len(suggestions))):
            if suggestions[i]:
                self.spelling_list.append(tkinter.Label(self.spelling_frame, fg="blue",
                                                        font=(self.font_to_use, 14),
                                                        text=suggestions[i]))
                def update_search_term(event, word=suggestions[i]):
                    self.spelling_label.config(text="Did you mean? ")
                    self.search_entry.delete(0, tkinter.END)
                    self.search_entry.insert(0, word)
                    self.run_search()
                self.spelling_list[-1].bind("<Button-1>", update_search_term)
                self.spelling_list[-1].pack(side='left', padx=10, pady=10)
    def show_suggested_items(self, max_count, suggestions, displaylist, displaylabel, displayframe):
        """Show suggested items in list"""
        for i in range(min(max_count, len(suggestions))):
            if suggestions[i]:
                displaylist.append(tkinter.Label(displayframe, fg="blue",
                                                 font=(self.font_to_use, 14),
                                                 text=suggestions[i]))
                def update_search_term(event, word=suggestions[i]):

                    self.search_entry.delete(0, tkinter.END)
                    self.search_entry.insert(0, word)
                    self.run_search()
                displaylist[-1].bind("<Button-1>", update_search_term)
                displaylist[-1].pack(side='left', padx=10, pady=10)
# Code for hyperlink manager modified from
# http://effbot.org/zone/tkinter-text-hyperlink.htm
class HyperlinkManager:
    """HyperlinkManager allows for hyperlinks in tkinter textbox."""

    def __init__(self, text):
        """Initialize HyperlinkManager."""
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.text.tag_bind("hyper", "<Button-3>", self._clickright)
        #self.text.tag_bind("hyper", "<Button-2>", self._clickmid)

        self.reset()

    def reset(self):
        """Reset HyperlinkManager links."""
        self.links = {}

    def add(self, action, doc_id, corpus):
        """Add an action to the manager."""
        # returns tags to use in associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = [action, doc_id, corpus]
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names("current"):
            if tag[:6] == "hyper-":
                self.links[tag][0](self.links[tag][1], self.links[tag][2], 'left')
                return

    def _clickright(self, event):
        for tag in self.text.tag_names("current"):
            if tag[:6] == "hyper-":
                self.links[tag][0](self.links[tag][1], self.links[tag][2], 'right')
                return

    def _clickmid(self, event):
        for tag in self.text.tag_names("current"):
            if tag[:6] == "hyper-":
                self.links[tag][0](self.links[tag][1], self.links[tag][2], 'mid')
                return
