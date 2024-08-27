import os
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk, simpledialog, messagebox
import tkinter.messagebox
import tkinter.filedialog as fd

import nltk
from nltk import word_tokenize, WordNetLemmatizer, pos_tag
from nltk.corpus import wordnet
from regex import regex

from new_word_window import NewWordWindow


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


def add_text():
    text = text_entry.get("1.0", "end-1c")
    text_entry.delete("1.0", "end-1c")
    start_processing(text)
    tab_control.select(0)


def open_file():
    filetypes = (("Текстовый файл", "*.txt"),)
    filename = fd.askopenfilename(title="Открыть файл", initialdir="/", filetypes=filetypes)
    if len(filename) == 0:
        return
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
        start_processing(text)
        tab_control.select(0)


def text_processing(original_text, progress_bar, progress_window):
    # Заблокировать окно приложения
    root.attributes("-disabled", True)

    global text_idx
    global total_words
    global unique_words
    global total_pairs
    global unique_pairs
    global unique_lgc

    file = open("data/texts/text_" + str(text_idx) + ".txt", "w")
    text_idx += 1
    file.write(original_text)
    file.close()

    lemmatizer = WordNetLemmatizer()
    text = word_tokenize(original_text)
    tmp = pos_tag(text)

    # Заполнение 1 и 2 таблиц
    # lemma_tmp = [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in word_tokenize(original_text)]
    tokenized_text = word_tokenize(original_text)
    bar_size = 2 * len(tmp) + len(tokenized_text) + 10
    lemma_tmp = []
    idx = 1
    for word in tokenized_text:
        pos = get_wordnet_pos(word)
        lemma = lemmatizer.lemmatize(word, pos)
        lemma_tmp.append(lemma)
        progress_bar["value"] = idx / bar_size * 100
        idx += 1
        progress_bar.update()

    for j in range(0, len(tmp)):
        word = tmp[j][0]
        word = word.capitalize()
        if lgc_dict.get(tmp[j][1]) is None:
            lgc_dict[tmp[j][1]] = 1
            unique_lgc += 1
        else:
            lgc_dict[tmp[j][1]] += 1
        if pattern_en.match(word):
            if main_dict.get(word + "-" + tmp[j][1]) is None:
                tagged = word_tokenize(lemma_tmp[j])
                main_dict[word + "-" + tmp[j][1]] = (1, lemma_tmp[j].capitalize(), pos_tag(tagged)[0][1])
                unique_words += 1
            else:
                tmp_word = main_dict.pop(word + "-" + tmp[j][1])
                main_dict[word + "-" + tmp[j][1]] = (tmp_word[0] + 1, tmp_word[1], tmp_word[2])
            total_words = total_words + 1
        progress_bar["value"] = (j + len(tokenized_text)) / bar_size * 100
        progress_bar.update()

    # Заполнение 3 таблицы
    for j in range(0, len(tmp) - 1):
        LGC_1 = tmp[j][1]
        LGC_2 = tmp[j + 1][1]
        key = LGC_1 + " " + LGC_2
        if pairs_dict.get(key) is None:
            pairs_dict[key] = 1
            unique_pairs += 1
        else:
            pairs_dict[key] += 1
        total_pairs += 1
        progress_bar["value"] = (j + len(tmp) + len(tokenized_text)) / bar_size * 100
        progress_bar.update()
    update_tables()
    progress_bar["value"] = 100
    progress_bar.update()
    # Заблокировать окно приложения
    root.attributes("-disabled", False)
    progress_window.destroy()


def start_processing(original_text):
    # Создание нового окна для Progress Bar
    progress_window = tk.Toplevel(root)
    progress_window.title("Обработка")
    progress_window.minsize(275, 45)
    progress_window.maxsize(400, 45)

    def on_closing():
        pass

    # Установка функции on_closing для предотвращения закрытия окна
    progress_window.protocol("WM_DELETE_WINDOW", on_closing)

    # Создание Progress Bar в новом окне
    progress = ttk.Progressbar(progress_window, orient="horizontal", length=200, mode="determinate")
    progress.pack(side='left', fill='both', pady=10, expand=True)
    # Запуск обработки текста в отдельном потоке, чтобы избежать блокировки GUI
    import threading
    processing_thread = threading.Thread(target=lambda: text_processing(original_text,
                                                                        progress,
                                                                        progress_window))
    processing_thread.start()


def add_word():
    result = NewWordWindow(root)
    if result.sig == 0:

        f = open("data/lgc_meaning", "r")
        lgc_count = 0
        txt = f.readline()
        list_of_lgc = [result.LGC.upper(), result.lemmaLGC.upper()]
        while txt != "":
            tmp = txt.split(":")
            if tmp[0] == list_of_lgc[0]:
                lgc_count += 1
            if len(list_of_lgc) == 2 and tmp[0] == list_of_lgc[1]:
                lgc_count += 1
            txt = f.readline()
        if lgc_count != 2:
            messagebox.showerror("Ошибка", "Введен несуществующий ЛГК")
            return

        global unique_words
        if main_dict.get(result.word.capitalize() + "-" + result.LGC.upper()) is None:
            main_dict[result.word.capitalize() + "-" + result.LGC.upper()] = \
                (0, result.lemma.capitalize(), result.lemmaLGC.upper())
            unique_words += 1
        if lgc_dict.get(result.LGC.upper()) is None:
            lgc_dict[result.LGC.upper()] = 0
        update_tables()


def edit_word():
    global unique_words
    cur_item = tree.item(tree.focus())
    if cur_item['values'] != "":
        new_word = simpledialog.askstring("Изменить", "Измените слово:",
                                          parent=root,
                                          initialvalue=cur_item["values"][0])
        if new_word != "" and new_word != cur_item['values'][0]:
            if pattern_en.match(new_word.lower()):
                if main_dict.get(new_word.capitalize() + "-" + cur_item['values'][2]) is not None:
                    deleted = main_dict.pop(cur_item['values'][0] + "-" + cur_item['values'][2])
                    tmp = main_dict.pop(new_word.capitalize() + "-" + cur_item['values'][2])
                    main_dict[new_word.capitalize() + "-" + cur_item['values'][2]] = \
                        (deleted[0] + tmp[0], tmp[1], tmp[2])
                    unique_words -= 1
                else:
                    tmp = main_dict.pop(cur_item['values'][0] + "-" + cur_item['values'][2])
                    main_dict[new_word.capitalize() + "-" + cur_item['values'][2]] = \
                        (tmp[0], tmp[1], tmp[2])
                update_tables()
        else:
            messagebox.showwarning("Ошибка", "Слово не было изменено")
    else:
        messagebox.showinfo("Информация", "Выберите слово для изменения")


def delete_word():
    cur_item = tree.item(tree.focus())
    global total_words
    global unique_words
    if cur_item['values'] != "":
        answer = tkinter.messagebox.askyesno(title="Удаление",
                                             message="Вы уверенны, что хотите удалить слово '" + cur_item['values'][
                                                 0] + "'?")
        if answer:
            unique_words -= 1
            total_words -= cur_item['values'][1]
            lgc_dict[cur_item['values'][2]] -= cur_item['values'][1]
            if lgc_dict[cur_item['values'][2]] <= 0:
                del lgc_dict[cur_item['values'][2]]
            del main_dict[cur_item['values'][0] + "-" + cur_item['values'][2]]
            update_tables()
    else:
        messagebox.showinfo("Информация", "Выберите слово для удаления")


def clear_table():
    global text_idx
    global unique_words
    global unique_pairs
    global total_words
    global total_pairs
    global unique_lgc
    main_dict.clear()
    pairs_dict.clear()
    lgc_dict.clear()
    text_idx = 0
    unique_words = 0
    unique_pairs = 0
    total_words = 0
    total_pairs = 0
    unique_lgc = 0
    # Получаем список файлов в директории
    file_list = os.listdir('data/texts')

    # Проходимся по списку файлов и удаляем каждый файл
    for file_name in file_list:
        file_path = os.path.join('data/texts', file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    update_tables()


def show_statistic_table():
    selected_option = statistic_var.get()

    label_unique_symbols.pack_forget()
    label_total_symbols.pack_forget()

    if selected_option == "Код":
        frame_table1.pack(fill='both', pady=10, expand=True)
        frame_table3.pack_forget()
    elif selected_option == "Код-Код":
        frame_table1.pack_forget()
        frame_table3.pack(fill='both', pady=10, expand=True)
    label_unique_symbols.pack()
    label_total_symbols.pack(pady=10)
    update_labels()


def find_view(*args):
    tab = tab_control.tab(tab_control.select(), "text")
    if tab == 'Словарь' and entry_var.get().lower() != "":
        tree.delete(*tree.get_children())
        find_pattern = regex.compile(entry_var.get().lower())
        list_1 = [(k, v) for k, v in main_dict.items()]
        for i in range(0, len(list_1)):
            if find_pattern.match(list_1[i][0].split("-")[0].lower()):
                tree.insert("", 'end', i, values=(list_1[i][0].split("-")[0], list_1[i][1][0],
                                                  list_1[i][0].split("-")[1], list_1[i][1][1],
                                                  list_1[i][1][2]))
    elif tab == 'Словарь' and entry_var.get().lower() == "":
        tree.delete(*tree.get_children())
        list_1 = [(k, v) for k, v in main_dict.items()]
        for i in range(0, len(list_1)):
            tree.insert("", 'end', i, values=(list_1[i][0].split("-")[0], list_1[i][1][0],
                                              list_1[i][0].split("-")[1], list_1[i][1][1],
                                              list_1[i][1][2]))


def update_main_table():
    tree.delete(*tree.get_children())
    list_1 = [(k, v) for k, v in main_dict.items()]
    for i in range(0, len(list_1)):
        tree.insert("", 'end', i, values=(list_1[i][0].split("-")[0], list_1[i][1][0],
                                          list_1[i][0].split("-")[1], list_1[i][1][1],
                                          list_1[i][1][2]))


def update_table_1():
    table1.delete(*table1.get_children())
    list_1 = [(k, v) for k, v in lgc_dict.items()]
    for i in range(0, len(list_1)):
        table1.insert("", 'end', i, values=list_1[i])


def update_table_3():
    table3.delete(*table3.get_children())
    list_3 = [(k, v) for k, v in pairs_dict.items()]
    for i in range(0, len(list_3)):
        key = list_3[i][0].split(" ")
        table3.insert("", 'end', i, values=(key[0], key[1], list_3[i][1]))


def update_tables():
    update_main_table()
    update_table_1()
    update_table_3()
    update_labels()


def update_labels():
    tab = tab_control.tab(tab_control.select(), "text")
    if tab == 'Словарь':
        label_total["text"] = "Всего слов: " + str(total_words)
        label_unique["text"] = "Уникальных слов: " + str(unique_words)
    elif statistic_var.get() == "Код":
        label_total_symbols["text"] = "Всего кодов: " + str(total_words)
        label_unique_symbols["text"] = "Уникальных кодов: " + str(unique_lgc)
    else:
        label_total_symbols["text"] = "Всего пар: " + str(total_pairs)
        label_unique_symbols["text"] = "Уникальных пар: " + str(unique_pairs)


def show_popup(event):
    tab = tab_control.tab(tab_control.select(), "text")
    if tab == 'Словарь':
        menu_1.post(event.x_root, event.y_root)
    else:
        if statistic_var.get() == "Код":
            menu_2.post(event.x_root, event.y_root)
        else:
            menu_3.post(event.x_root, event.y_root)


def about_lgc():
    cur_item = None
    tab = tab_control.tab(tab_control.select(), "text")
    if tab == 'Словарь':
        cur_item = tree.item(tree.focus())
    else:
        if statistic_var.get() == "Код":
            cur_item = table1.item(table1.focus())
        else:
            cur_item = table3.item(table3.focus())

    if cur_item['values'] != "":
        f = open("data/lgc_meaning", "r")
        meaning = []
        txt = f.readline()
        list_of_lgc = []
        if tab == 'Словарь':
            list_of_lgc.append(cur_item['values'][2])
            if cur_item['values'][2] != cur_item['values'][4]:
                list_of_lgc.append(cur_item['values'][4])
        else:
            if statistic_var.get() == "Код":
                list_of_lgc.append(cur_item['values'][0])
            else:
                list_of_lgc.append(cur_item['values'][0])
                if cur_item['values'][0] != cur_item['values'][1]:
                    list_of_lgc.append(cur_item['values'][1])

        while txt != "":
            tmp = txt.split(":")
            if tmp[0] == list_of_lgc[0]:
                meaning.append(txt)
            if len(list_of_lgc) == 2 and tmp[0] == list_of_lgc[1]:
                meaning.append(txt)
            txt = f.readline()
        mes = ""
        for i in range(len(meaning), 0, -1):
            mes += meaning[i - 1]
        tkinter.messagebox.showinfo("About LGC", mes)
        f.close()


def load_dicts():
    global text_idx
    global unique_words
    global total_words
    global unique_pairs
    global total_pairs
    global unique_lgc

    # чтение номера текста
    f = open("data/text_idx", "rb+")
    idx = f.readline().decode()
    if len(idx) != 0:
        text_idx = int(idx)
    else:
        text_idx = 1
    # Чтение английских слов и их кодов
    f_read_en = open("data/dict_main", "rb+")
    count_en = f_read_en.readline()
    count_en = count_en.replace(b'\n', b'').replace(b'\t', b'').replace(b'\r', b'')
    if len(count_en) == 0:
        return
    count_en = count_en.decode()
    # count_en = count_en[:-1]
    count_vals_en = count_en.split("-")
    unique_words = int(count_vals_en[0])
    total_words = int(count_vals_en[1])
    while True:
        key_val = f_read_en.readline()
        key_val = key_val.decode()
        if key_val == "":
            break
        key_val = key_val[:-1]
        word_data = key_val.split(" ")
        main_dict[word_data[0] + "-" + word_data[1]] = (int(word_data[2]), word_data[3], word_data[4])
    f_read_en.close()

    # Чтение пар кодов
    f_read_pairs = open("data/dict_pairs", "rb+")
    count_pairs = f_read_pairs.readline()
    count_pairs = count_pairs.decode()
    count_pairs = count_pairs[:-1]
    count_vals_pairs = count_pairs.split("-")
    unique_pairs = int(count_vals_pairs[0])
    total_pairs = int(count_vals_pairs[1])
    while True:
        key_val_pair = f_read_pairs.readline()
        key_val_pair = key_val_pair.decode()
        if key_val_pair == "":
            break
        key_val_pair = key_val_pair[:-1]
        pair_data = key_val_pair.split(" ")
        pairs_dict[pair_data[0] + " " + pair_data[1]] = int(pair_data[2])
    f_read_pairs.close()

    # Чтение ЛГК
    f_read_pairs = open("data/dict_lgc", "rb+")
    count_lgc_f = f_read_pairs.readline()
    count_lgc_f = count_lgc_f.decode()
    count_lgc_f = count_lgc_f[:-1]
    unique_lgc = int(count_lgc_f)
    while True:
        key_val_lgc = f_read_pairs.readline()
        key_val_lgc = key_val_lgc.decode()
        if key_val_lgc == "":
            break
        key_val_lgc = key_val_lgc[:-1]
        lgc_data = key_val_lgc.split(" ")
        lgc_dict[lgc_data[0]] = int(lgc_data[1])
    f_read_pairs.close()


def save_dicts():
    # сохранение номера текста
    f = open("data/text_idx", "wb+")
    f.write(str(text_idx).encode())

    # сохранение слов с кодами
    f = open("data/dict_main", "wb+")
    count = str(unique_words) + '-' + str(total_words) + '\n'
    count = count.encode()
    f.write(count)
    n = len(main_dict)
    for i in range(0, n):
        word_info = main_dict.popitem()
        key = str(word_info[0].split("-")[0])
        lgc = str(word_info[0].split("-")[1])
        freq = str(word_info[1][0])
        lemma = str(word_info[1][1])
        lemma_lgc = str(word_info[1][2])
        bt_key = (key + ' ').encode()
        bt_lgc = (lgc + ' ').encode()
        bt_freq = (freq + ' ').encode()
        bt_lemma = (lemma + ' ').encode()
        bt_lemma_lgc = (lemma_lgc + '\n').encode()
        f.write(bt_key + bt_lgc + bt_freq + bt_lemma + bt_lemma_lgc)
    f.close()

    # сохранение пар
    f = open("data/dict_pairs", "wb+")
    count_p = str(unique_pairs) + '-' + str(total_pairs) + '\n'
    count_p = count_p.encode()
    f.write(count_p)
    n = len(pairs_dict)
    for i in range(0, n):
        data = pairs_dict.popitem()
        key = str(data[0])
        val = str(data[1])
        bt_key = (key + ' ').encode()
        bt_val = (val + '\n').encode()
        f.write(bt_key + bt_val)
    f.close()

    # сохрание частот кодов
    f = open("data/dict_lgc", "wb+")
    count_lgc = str(unique_lgc) + '\n'
    count_lgc = count_lgc.encode()
    f.write(count_lgc)
    n = len(lgc_dict)
    for i in range(0, n):
        data = lgc_dict.popitem()
        key = str(data[0])
        val = str(data[1])
        bt_key = (key + ' ').encode()
        bt_val = (val + '\n').encode()
        f.write(bt_key + bt_val)
    f.close()
    root.destroy()


def switch_tab(event):
    update_labels()


def sort_main_table(col, reverse):
    if col == 0:
        sorted_dict = OrderedDict(sorted(main_dict.items(), key=lambda x: x[0].split("-")[0], reverse=reverse))
        main_dict.clear()
        main_dict.update(sorted_dict)
    elif col == 1:
        sorted_dict = OrderedDict(sorted(main_dict.items(), key=lambda x: x[1][0], reverse=reverse))
        main_dict.clear()
        main_dict.update(sorted_dict)
    elif col == 2:
        sorted_dict = OrderedDict(sorted(main_dict.items(), key=lambda x: x[0].split("-")[1], reverse=reverse))
        main_dict.clear()
        main_dict.update(sorted_dict)
    elif col == 3:
        sorted_dict = OrderedDict(sorted(main_dict.items(), key=lambda x: x[1][1], reverse=reverse))
        main_dict.clear()
        main_dict.update(sorted_dict)
    elif col == 4:
        sorted_dict = OrderedDict(sorted(main_dict.items(), key=lambda x: x[1][2], reverse=reverse))
        main_dict.clear()
        main_dict.update(sorted_dict)
    update_main_table()
    tree.heading(col, command=lambda: sort_main_table(col, not reverse))


def sort_table_1(col, reverse):
    if col == 0:
        sorted_dict = dict(sorted(lgc_dict.items(), reverse=reverse))
        lgc_dict.clear()
        lgc_dict.update(sorted_dict)
    else:
        sorted_keys = sorted(lgc_dict, key=lgc_dict.get, reverse=reverse)
        sorted_dict2 = {}
        for w in sorted_keys:
            sorted_dict2[w] = lgc_dict[w]
        lgc_dict.clear()
        lgc_dict.update(sorted_dict2)
    update_table_1()
    table1.heading(col, command=lambda: sort_table_1(col, not reverse))


def sort_table_3(col, reverse):
    if col == 0:
        sorted_dict = OrderedDict(sorted(pairs_dict.items(), key=lambda x: x[0].split(" ")[0], reverse=reverse))
        pairs_dict.clear()
        pairs_dict.update(sorted_dict)
    elif col == 1:
        sorted_dict = OrderedDict(sorted(pairs_dict.items(), key=lambda x: x[0].split(" ")[1], reverse=reverse))
        pairs_dict.clear()
        pairs_dict.update(sorted_dict)
    elif col == 2:
        sorted_dict = OrderedDict(sorted(pairs_dict.items(), key=lambda x: x[1], reverse=reverse))
        pairs_dict.clear()
        pairs_dict.update(sorted_dict)
    update_table_3()
    table3.heading(col, command=lambda: sort_table_3(col, not reverse))


# регулярные выражения для определения языка
pattern_en = regex.compile(r'[\u0041-\u005A\u0061-\u007A]', regex.UNICODE)

# Словари
main_dict = {}
pairs_dict = {}
lgc_dict = {}

# Количества
text_idx = 1
total_words = 0
unique_words = 0
total_pairs = 0
unique_pairs = 0
unique_lgc = 0
load_dicts()

# Создание главного окна
root = tk.Tk()
root.title("Аннотированный словарь")

root.minsize(675, 550)
root.maxsize(800, 600)

# Создание вкладок
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Словарь')
tab_control.add(tab2, text='Добавление')
tab_control.add(tab3, text='Статистика')
tab_control.pack(expand=1, fill='both')
tab_control.bind("<<NotebookTabChanged>>", switch_tab)

# Вкладка "Словарь"

# Надпись "Найти:" и поле для ввода слова
frame_search = ttk.Frame(tab1)
frame_search.pack(pady=10)

label_find = ttk.Label(frame_search, text="Найти:")
label_find.pack(side='left')

entry_var = tk.StringVar()
entry_var.trace("w", find_view)
entry_word = ttk.Entry(frame_search, textvariable=entry_var)
entry_word.pack(side='left', padx=5)

# Таблица
frame_table = ttk.Frame(tab1)
frame_table.pack(fill='both', pady=10, expand=True)

columns = ('Слово', 'Частота', 'ЛГК', 'Лемма', 'ЛГК Леммы')
tree = ttk.Treeview(frame_table, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor='center')
tree.heading('Слово', command=lambda: sort_main_table(0, False))
tree.heading('Частота', command=lambda: sort_main_table(1, False))
tree.heading('ЛГК', command=lambda: sort_main_table(2, False))
tree.heading('Лемма', command=lambda: sort_main_table(3, False))
tree.heading('ЛГК Леммы', command=lambda: sort_main_table(4, False))
tree.pack(side='left', fill='both', pady=10, expand=True)

# Создание скроллбара
scrollbar = ttk.Scrollbar(frame_table, orient='vertical', command=tree.yview)
scrollbar.pack(side='right', fill='both', pady=10)
# Связывание скроллбара с Treeview
tree.configure(yscrollcommand=scrollbar.set)

# Кнопки
frame_buttons = ttk.Frame(tab1)
frame_buttons.pack()

button_add = ttk.Button(frame_buttons, text="Добавить", command=add_word)
button_add.pack(side='left', padx=5)

button_edit = ttk.Button(frame_buttons, text="Изменить", command=edit_word)
button_edit.pack(side='left', padx=5)

button_delete = ttk.Button(frame_buttons, text="Удалить", command=delete_word)
button_delete.pack(side='left', padx=5)

button_clear = ttk.Button(frame_buttons, text="Очистить", command=clear_table)
button_clear.pack(side='left', padx=5)

# Надписи с числами
label_unique = ttk.Label(tab1)
label_unique.pack(pady=10)

label_total = ttk.Label(tab1)
label_total.pack()

# Вкладка "Добавление"

label_text = ttk.Label(tab2, text="Введите текст", font=1)
label_text.pack(pady=10)

# Форма для ввода текста
text_form = ttk.Frame(tab2)
text_form.pack(fill='both', pady=10, expand=True)

text_entry = tk.Text(text_form)
text_entry.pack(side='left', fill='both', expand=True)

scrollbar_text = tk.Scrollbar(text_form, orient='vertical', command=text_entry.yview)
scrollbar_text.pack(side='right', fill='both')
text_entry.config(yscrollcommand=scrollbar_text.set)

# Кнопки
button_add_text = ttk.Button(tab2, text="Добавить Текст", command=add_text)
button_add_text.pack(pady=5)

button_select_file = ttk.Button(tab2, text="Выбрать файл", command=open_file)
button_select_file.pack(pady=5)

# Вкладка "Статистика"

statistic_var = tk.StringVar()
statistic_var.set("Код")

# Ряд из 2 кнопок radiobutton
radio_frame = ttk.Frame(tab3)
radio_frame.pack(pady=10)

radio_button1 = ttk.Radiobutton(radio_frame, text="Код", variable=statistic_var,
                                value="Код", command=show_statistic_table)
radio_button1.pack(side='left', padx=5)

radio_button3 = ttk.Radiobutton(radio_frame, text="Код-Код", variable=statistic_var,
                                value="Код-Код", command=show_statistic_table)
radio_button3.pack(side='left', padx=5)

# Таблица 1
frame_table1 = ttk.Frame(tab3)
columns_table1 = ('Код', 'Частота')
table1 = ttk.Treeview(frame_table1, columns=columns_table1, show='headings')
for col in columns_table1:
    table1.heading(col, text=col)
    table1.column(col, anchor='center')
table1.heading('Код', command=lambda: sort_table_1(0, False))
table1.heading('Частота', command=lambda: sort_table_1(1, False))

table1.pack(side='left', fill='both', pady=10, expand=True)
scrollbar1 = ttk.Scrollbar(frame_table1, orient='vertical', command=table1.yview)
scrollbar1.pack(side='right', fill='y', pady=10)
table1.configure(yscrollcommand=scrollbar1.set)

# Таблица 3
frame_table3 = ttk.Frame(tab3)
columns_table3 = ('Код 1', 'Код 2', 'Частота')
table3 = ttk.Treeview(frame_table3, columns=columns_table3, show='headings')
for col in columns_table3:
    table3.heading(col, text=col)
    table3.column(col, anchor='center')
table3.heading('Код 1', command=lambda: sort_table_3(0, False))
table3.heading('Код 2', command=lambda: sort_table_3(1, False))
table3.heading('Частота', command=lambda: sort_table_3(2, False))

table3.pack(side='left', fill='both', pady=10, expand=True)
scrollbar3 = ttk.Scrollbar(frame_table3, orient='vertical', command=table3.yview)
scrollbar3.pack(side='right', fill='y', pady=10)
table3.configure(yscrollcommand=scrollbar3.set)

# Надписи с числами
label_unique_symbols = ttk.Label(tab3)
label_total_symbols = ttk.Label(tab3)

update_tables()
show_statistic_table()

# Контектсное меню
menu_1 = tk.Menu(tree, tearoff=0)
menu_1.add_command(label="Справка об ЛГК", command=about_lgc)
tree.bind("<Button-3>", show_popup)
menu_2 = tk.Menu(table1, tearoff=0)
menu_2.add_command(label="Справка об ЛГК", command=about_lgc)
table1.bind("<Button-3>", show_popup)
menu_3 = tk.Menu(table3, tearoff=0)
menu_3.add_command(label="Справка об ЛГК", command=about_lgc)
table3.bind("<Button-3>", show_popup)

root.protocol("WM_DELETE_WINDOW", save_dicts)

# Запуск приложения
root.mainloop()
