import os
import string
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk, messagebox
import shutil
from tkinter import filedialog as fd
import regex as reg
from nltk import PorterStemmer

from nltk.corpus import stopwords
import subprocess


@dataclass
class Document:
    name: str = ""
    path: str = ""
    words_dict: dict = ()


def target_informative_words(text):
    tokens = text.split()
    tokens = [token.lower() for token in tokens]
    tokens = [reg.compile('[%s]' % reg.escape(string.punctuation)).sub('', token) for token in tokens]
    tokens = [PorterStemmer().stem(token) for token in tokens]
    tokens = [token for token in tokens if token not in STOPWORDS]
    return [token for token in tokens if token]


def open_file(event):
    item = tree.focus()
    filename = tree.item(item)["values"][0]

    try:
        subprocess.Popen(["notepad.exe", "data/texts/" + filename + ".txt"])
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Notepad не найден.")
    except subprocess.SubprocessError:
        messagebox.showerror("Ошибка", "Ошибка при открытии файла в Notepad.")


def update_table(data):
    global cur_results
    cur_results = data
    tree.delete(*tree.get_children())
    for i in range(len(data)):
        if data[i][1] != '-' and data[i][1] != 0:
            tree.insert("", 'end', values=(data[i][0], round(data[i][1], 8)))
        elif data[i][1] == '-':
            tree.insert("", 'end', values=(data[i][0], '-'))


def search():
    if entry_var.get() != "":
        search_request = target_informative_words(entry_var.get())
        results = []
        for single_doc in text_dict:
            tmp_frequency_dict = single_doc.words_dict
            score = 0
            for word in search_request:
                if tmp_frequency_dict.get(word) is not None:
                    score += tmp_frequency_dict.get(word)
            results.append((single_doc.name, score))
        update_table(sorted(results, key=lambda doc: doc[1], reverse=True))


def add_document():
    tree_frame.pack_forget()
    bottom_frame.pack_forget()
    frame_progressbar.pack(fill='x', padx=20, expand=True)
    bottom_frame.pack()

    global prog_bar_val
    global label_progress
    filetypes = (("Текстовый файл", "*.txt"),)
    filename = fd.askopenfilename(title="Открыть файл", initialdir="/",
                                  filetypes=filetypes)
    try:
        doc = Document()
        tmp = filename.split("/")
        doc.name = tmp[len(tmp) - 1].split(".")[0]
        data = open(filename, "r", encoding="utf-8")
        tmp_dict = dict()
        max_fr = 0
        lines = data.readlines()
        progressbar.configure(maximum=len(lines))
        progressbar.update()
        for line in lines:
            result = target_informative_words(line)
            for j in range(len(result)):
                if tmp_dict.get(result[j]) is None:
                    tmp_dict[result[j]] = 1
                else:
                    tmp_dict[result[j]] += 1
                if tmp_dict[result[j]] > max_fr:
                    max_fr = tmp_dict[result[j]]
            prog_bar_val += 1
            progressbar.configure(value=prog_bar_val)
            progressbar.update()
        data.close()
        for item in tmp_dict:
            tmp_dict[item] /= max_fr
        doc.words_dict = tmp_dict
        shutil.copy2(filename, "./data/texts/" + doc.name + ".txt")  # Копируем файл в директорию "./texts/"
        doc.path = "./data/texts/" + doc.name  # Устанавливаем путь к файлу
        save_docs(doc)
        text_dict.append(doc)
        label_progress["text"] = "Успех"
    except FileNotFoundError:
        label_progress["text"] = "Ошибка"
    root.after(2500, show_table)  # Примерное время ожидания - 3 секунды
    pass


def clear_search():
    global cur_results
    cur_results.clear()
    entry_var.set("")
    tree.delete(*tree.get_children())


def show_all_documents():
    results = []
    for single_doc in text_dict:
        results.append((single_doc.name, '-'))
    update_table(results)


def load_searchable_docs():
    global text_dict
    files = [f for f in os.listdir("./data/searchable_docs/") if os.path.isfile(os.path.join("./data/searchable_docs", f))]
    for i in range(len(files)):
        doc = Document()
        f_read = open("./data/searchable_docs/" + files[i], "rb+")
        read_info = f_read.readline().decode()
        doc.name = read_info[:-1]
        read_info = f_read.readline().decode()
        doc.path = read_info[:-1]
        tmp_dict = dict()
        while True:
            key_val = f_read.readline()
            key_val = key_val.decode()
            if key_val == "":
                break
            key_val = key_val[:-1]
            word_data = key_val.split(" ")
            tmp_dict[word_data[0]] = float(word_data[1])
        doc.words_dict = tmp_dict
        text_dict.append(doc)
        f_read.close()


def save_docs(doc):
    name = "data/searchable_docs/" + doc.name + ".txt"
    f = open(name, "wb+")
    to_write = doc.name + "\n"
    to_write = to_write.encode()
    f.write(to_write)
    to_write = doc.path + "\n"
    to_write = to_write.encode()
    f.write(to_write)
    for key in doc.words_dict:
        to_write = key + " " + str(doc.words_dict[key]) + "\n"
        to_write = to_write.encode()
        f.write(to_write)
    f.close()


def show_table():
    # Показываем таблицу и убираем прогрессбар
    frame_progressbar.pack_forget()
    bottom_frame.pack_forget()
    tree_frame.pack(fill='both', expand=True, padx=5)
    bottom_frame.pack()

    global label_progress
    global prog_bar_val
    label_progress["text"] = "Обработка"
    prog_bar_val = 0
    progressbar.configure(value=prog_bar_val)
    progressbar.update()


text_dict = []
prog_bar_val = 0
cur_results = []
STOPWORDS = set(stopwords.words('english'))
load_searchable_docs()

# Создание главного окна
root = tk.Tk()
root.title("Поисковая система")
root.wm_minsize(425, 350)
root.wm_maxsize(600, 450)
root.wm_geometry("500x400")

# Создание верхней строки с инпутом и кнопкой "Найти"
top_frame = ttk.Frame(root)
top_frame.pack(fill='x')

entry_var = tk.StringVar()
entry = ttk.Entry(top_frame, textvariable=entry_var)
entry.pack(side='left', padx=20, pady=5, fill='x', expand=True)

search_button = ttk.Button(top_frame, text="Найти", command=search)
search_button.pack(side='right', padx=20, pady=5)

# Создание прогрессбара
frame_progressbar = ttk.Frame(root)
label_progress = ttk.Label(frame_progressbar, text="Обработка")
progressbar = ttk.Progressbar(frame_progressbar, length=400, mode='determinate')
label_progress.pack()
progressbar.pack()

# Создание таблицы с двумя колонками "Документ" и "Релевантность"
tree_frame = ttk.Frame(root)
tree_frame.pack(fill='both', expand=True, padx=5)

tree = ttk.Treeview(tree_frame, columns=("Document", "Relevance"), show='headings')
tree.heading("Document", text="Документ")
tree.column("Document", width=350, anchor='center')
tree.heading("Relevance", text="Релевантность")
tree.column("Relevance", width=120, anchor='center')

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.bind("<Double-1>", open_file)

tree.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

# Создание строки с кнопками "Добавить документ", "Очистить" и "Показать все"
bottom_frame = tk.Frame(root)
bottom_frame.pack()

add_document_button = ttk.Button(bottom_frame, text="Добавить документ", command=add_document)
add_document_button.pack(side='left', padx=5, pady=15)

clear_search_button = ttk.Button(bottom_frame, text="Очистить", command=clear_search)
clear_search_button.pack(side='left', padx=5, pady=15)

show_all_documents_button = ttk.Button(bottom_frame, text="Показать все", command=show_all_documents)
show_all_documents_button.pack(side='left', padx=5, pady=15)

show_all_documents()

# Запуск главного цикла обработки событий
root.mainloop()
