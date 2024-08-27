from tkinter import Frame
import tkinter as tk


class NewWordWindow:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        self.top.title = "Добавить"
        self.frame = Frame(top)
        self.sig = 1
        self.wordLable = tk.Label(self.frame, text='Слово')
        self.wordLable.grid(column=0, row=0, padx=5, pady=5, sticky='E')
        self.wordEntry = tk.Entry(self.frame)
        self.wordEntry.grid(column=1, row=0, padx=5, pady=5, sticky='E')

        self.LGCLable = tk.Label(self.frame, text='ЛГК')
        self.LGCLable.grid(column=0, row=1, padx=5, pady=5, sticky='E')
        self.LGCEntry = tk.Entry(self.frame)
        self.LGCEntry.grid(column=1, row=1, padx=5, pady=5, sticky='E')

        self.lemmaLable = tk.Label(self.frame, text='Лемма')
        self.lemmaLable.grid(column=0, row=2, padx=5, pady=5, sticky='E')
        self.lemmaEntry = tk.Entry(self.frame)
        self.lemmaEntry.grid(column=1, row=2, padx=5, pady=5, sticky='E')

        self.lemmaLGCLable = tk.Label(self.frame, text='ЛГК леммы')
        self.lemmaLGCLable.grid(column=0, row=3, padx=5, pady=5, sticky='E')
        self.lemmaLGCEntry = tk.Entry(self.frame)
        self.lemmaLGCEntry.grid(column=1, row=3, padx=5, pady=5, sticky='E')

        self.OKButton = tk.Button(self.frame, text='ОК', command=self.send_ok)
        self.OKButton.grid(column=0, row=4, padx=5, pady=5, sticky='E')
        self.cancelButton = tk.Button(self.frame, text='отмена', command=self.send_cancel)
        self.cancelButton.grid(column=1, row=4, padx=5, pady=5, sticky='W')
        self.frame.pack()
        self.top.grab_set()
        self.top.mainloop()

    def send_ok(self):
        self.sig = 0
        self.word = self.wordEntry.get()
        self.LGC = self.LGCEntry.get()
        self.lemma = self.lemmaEntry.get()
        self.lemmaLGC = self.lemmaLGCEntry.get()
        self.top.grab_release()
        self.top.quit()
        self.top.destroy()

    def send_cancel(self):
        self.top.grab_release()
        self.top.quit()
        self.top.destroy()