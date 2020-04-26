"""Create an autocomplete listbox based on a given matching function and list"""
#adapted code from https://gist.github.com/ricardj/ec64dd3171caba3e3818a269f6b57ab2

import tkinter as tk
import re


class AutocompleteEntry(tk.Entry):
    """Creates an autocomplete tkinter Entry box"""
    def __init__(self, autocomplete_list, *args, **kwargs):

        self.listbox_length = 0

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matches_function = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(field_value, ac_list_entry):
                pattern = re.compile(
                    '.*' + re.escape(field_value) + '.*', re.IGNORECASE)
                return re.match(pattern, ac_list_entry)

            self.matches_function = matches

        # Custom return function
        if 'returnFunction' in kwargs:
            self.return_function = kwargs['returnFunction']
            del kwargs['returnFunction']
        else:
            def selected_value(value):
                print(value)
            self.return_function = selected_value

        tk.Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.autocomplete_list = autocomplete_list

        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)
        #self.bind("<Return>", self.select)
        self.bind("<Return>", self.selection)
        self.bind("<Button-1>", self.selectclick)
        self.bind("<Escape>", self.delete_listbox)

        self.listbox_up = False

    def delete_listbox(self, event=None):
        """Deletes the listbox is it exists"""
        if self.listbox_up:
            self.listbox.destroy()
            self.listbox_up = False

    def selectclick(self, event):
        """Called when item in listbox is clicked with mouse button"""
        if self.listbox_up:
            if self.listbox.curselection() != ():
                index = self.listbox.curselection()
                value = self.listbox.get(index)
                self.var.set(self.listbox.get(index))
                self.listbox.destroy()
                self.listbox_up = False
                self.return_function(value)
                self.icursor(tk.END)

    def changed(self, name, index, mode):
        """Keeps track of cursor change position"""
        if self.var.get() == '':
            self.delete_listbox()
        else:
            words = self.comparison()
            if words:
                if not self.listbox_up:
                    self.listbox_length = len(words)
                    self.listbox = tk.Listbox(
                        width=self["width"], font=self["font"],
                        height=self.listbox_length)
                    self.listbox.bind("<Button-1>", self.selectclick)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.bind("<Return>", self.selection)
                    self.listbox.place(
                        x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.listbox_up = True
                else:
                    self.listbox_length = len(words)
                    self.listbox.config(height=self.listbox_length)

                self.listbox.delete(0, tk.END)
                for word in words:
                    self.listbox.insert(tk.END, word)
            else:
                self.delete_listbox()

    def selection(self, event):
        """Called when right arrow or Return key selected"""
        if self.listbox_up:
            self.var.set(self.listbox.get(tk.ACTIVE))
            self.listbox.destroy()
            self.listbox_up = False
            self.icursor(tk.END)

    def move_up(self, event):
        """Moves cursor up in listbox"""
        if self.listbox_up:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            self.listbox.selection_clear(first=index)
            index = str(int(index) - 1)
            if int(index) == -1:
                index = str(self.listbox_length-1)

            self.listbox.see(index)  # Scroll!
            self.listbox.selection_set(first=index)
            self.listbox.activate(index)

    def move_down(self, event):
        """Moves the cursor in listbox down"""
        if self.listbox_up:
            if self.listbox.curselection() == ():
                index = '-1'
            else:
                index = self.listbox.curselection()[0]

            if index != tk.END:
                self.listbox.selection_clear(first=index)
                if int(index) == self.listbox_length-1:
                    index = "0"
                else:
                    index = str(int(index)+1)

                self.listbox.see(index)  # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def comparison(self):
        """Uses given regex to find matching list for autocomplete box"""
        return [w for w in self.autocomplete_list if self.matches_function(self.var.get(), w)]
