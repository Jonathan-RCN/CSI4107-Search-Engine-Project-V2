"""
Title: GUI for Search Engine

Project: CSI4107 Project
Version: Vanilla System
Component: Module 1

Created: 23 Jan 2020
Last modified: 13 Feb 2020

Author: Tiffany Maynard
Status: Complete

Description: Allow a user to access search engine capabilities

"""
import tkinter
from tkinter import messagebox
import tkinter.scrolledtext as tkscrolled
from tkinter import PhotoImage
import config
import corpus_access
import vsm_retrieval
import boolean_search
import spelling

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
        self.spelling_frame = tkinter.Frame(self.root)
        self.spelling_list = list()
        search_frame = tkinter.Frame(self.root)
        collection_frame = tkinter.Frame(self.root)
        button_frame = tkinter.Frame(self.root)
        bottom_frame = tkinter.Frame(self.root)
        results_frame = tkinter.Frame(bottom_frame)
        # Create labels
        tkinter.Label(top_frame, font=(self.font_to_use, 24),
                      fg='#5016b5', text='Jindalee  ').pack(side='left')


        self.search_entry = tkinter.Entry(top_frame, width=50, textvariable="Type here",
                                          font=(self.font_to_use, 18))

        self.search_entry.pack(side='left')
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
        # root.destroy exits/destroys the main window
        # self.quit_button = tkinter.Button(
        #     top_frame,
        #     text='Quit',
        #     command=self.root.destroy,
        #     font=(self.font_to_use, 18))
        # # Pack the buttons
        # self.quit_button.pack(side='right')
        self.search_button.pack(side='left')
        tkinter.Label(bottom_frame, font=(self.font_to_use, 18),
                      text='Search results').pack()
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
        self.reuters_radio.configure(state=tkinter.DISABLED)
        self.search_results = tkscrolled.ScrolledText(results_frame,
                                                      state="normal", wrap='word',
                                                      font=(self.font_to_use, 12))
        self.search_results.pack(side='bottom')
        # Now pack the frames also

        top_frame.pack(padx=50, pady=50, side='top', fill='both')
        self.spelling_frame.pack()
        search_frame.pack()
        collection_frame.pack()
        button_frame.pack()
        results_frame.pack()
        bottom_frame.pack()
        self.root.mainloop()

    def run_search(self):
        """Start search (callback function for search button)."""
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
                                                    corpus)
        else:
        #do boolean search
            docs_retrieved = boolean_search.boolean_search_module(
                self.search_entry.get().strip(), corpus)
        # Clear previous search results
        self.search_results.delete('1.0', "end")
        # Clear previous suggestions
        self.spelling_label.config(text="")
        for lab in self.spelling_list:
            lab.destroy()
        #account for times a word is returned instead of a doc_id
        if docs_retrieved and isinstance(docs_retrieved, str):
            docs_retrieved = []
        docs = corpus_access.get_documents(corpus, docs_retrieved)
        hyperlink = HyperlinkManager(self.search_results)

        suggestions = spelling.suggest_words(self.search_entry.get().strip(), corpus)

        if suggestions:
            self.show_spelling_options(config.TOP_N_SPELLING, suggestions)
            self.spelling_label.config(text="Did you mean? ")
        if docs is None or docs == []:
            self.search_results.insert("insert", 'No documents found')
        else:
            for doc in docs:
                score_str = ''
                if search == 'VSM':
                    score_str = '{:0.3f}'.format(doc.score) + ' '
                self.search_results.insert("insert",
                                           score_str + doc.title,
                                           hyperlink.add
                                           (self.click_link, doc.doc_id, corpus))
                self.search_results.insert("insert", doc.doctext[:100] + '\n')

    def click_link(self, click_id, corpus):
        """Click link function."""
        # add score of 1.0 for consistency of arguments
        doc = corpus_access.get_documents(corpus, [(click_id, 1.0)])[0]
        messagebox.showinfo(
            doc.title,
            doc.doctext)

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
                self.links[tag][0](self.links[tag][1], self.links[tag][2])
                return
