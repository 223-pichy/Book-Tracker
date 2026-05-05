import json
from tkinter import *
from tkinter import ttk, messagebox

DATA_FILE = "books.json"


books = []
tree = None
entries = {}
genre_filter_var = None
pages_filter_var = None
genre_combo = None
root = None



def load_data():
    global books
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            books = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        
        books = [
            {"title": "Преступление и наказание", "author": "Достоевский", "genre": "Роман", "pages": 672},
            {"title": "1984", "author": "Оруэлл", "genre": "Антиутопия", "pages": 328},
            {"title": "Мастер и Маргарита", "author": "Булгаков", "genre": "Роман", "pages": 480}
        ]
        save_to_json()



def save_to_json():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", str(e))



def update_genre_filter_list():
    global genre_combo, genre_filter_var
    genres = sorted(set(book['genre'] for book in books))
    genres_list = ["Все жанры"] + genres
    genre_combo['values'] = genres_list
    if not genre_filter_var.get() or genre_filter_var.get() not in genres_list:
        genre_filter_var.set("Все жанры")



def refresh_table():
    global tree, books, genre_filter_var, pages_filter_var

    
    for row in tree.get_children():
        tree.delete(row)

    
    filtered_books = books[:]

    
    genre_filter = genre_filter_var.get().strip()
    if genre_filter and genre_filter != "Все жанры":
        filtered_books = [b for b in filtered_books if b['genre'] == genre_filter]

    
    pages_filter = pages_filter_var.get().strip()
    if pages_filter and pages_filter.isdigit():
        min_pages = int(pages_filter)
        filtered_books = [b for b in filtered_books if b['pages'] > min_pages]

    
    for book in filtered_books:
        tree.insert("", END, values=(book['title'], book['author'], book['genre'], book['pages']))



def reset_filter():
    global genre_filter_var, pages_filter_var
    genre_filter_var.set("Все жанры")
    pages_filter_var.set("")
    refresh_table()



def add_book():
    global books, entries

    title = entries["Название книги:"].get().strip()
    author = entries["Автор:"].get().strip()
    genre = entries["Жанр:"].get().strip()
    pages_str = entries["Количество страниц:"].get().strip()

    
    if not title or not author or not genre or not pages_str:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return

    if not pages_str.isdigit():
        messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
        return

    pages = int(pages_str)

    
    books.append({
        "title": title,
        "author": author,
        "genre": genre,
        "pages": pages
    })

    
    for entry in entries.values():
        entry.delete(0, END)

    
    update_genre_filter_list()
    save_to_json()
    refresh_table()
    messagebox.showinfo("Успех", f"Книга «{title}» добавлена!")



def delete_book():
    global tree, books

    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Внимание", "Выберите книгу для удаления!")
        return

    
    item = tree.item(selected[0])
    title = item['values'][0]

    
    books = [book for book in books if book['title'] != title]

    
    save_to_json()
    update_genre_filter_list()
    refresh_table()
    messagebox.showinfo("Успех", f"Книга «{title}» удалена!")



def load_from_json():
    load_data()
    update_genre_filter_list()
    refresh_table()
    messagebox.showinfo("Загрузка", "Данные загружены из JSON!")



def create_interface():
    global root, tree, entries, genre_filter_var, pages_filter_var, genre_combo

    root = Tk()
    root.title("Book Tracker - Трекер прочитанных книг")
    root.geometry("900x600")
    root.resizable(True, True)

    
    input_frame = LabelFrame(root, text="Добавить новую книгу", padx=10, pady=10)
    input_frame.pack(fill="x", padx=10, pady=5)

    labels = ["Название книги:", "Автор:", "Жанр:", "Количество страниц:"]

    for i, label in enumerate(labels):
        lbl = Label(input_frame, text=label)
        lbl.grid(row=i, column=0, sticky="w", padx=5, pady=5)
        entry = Entry(input_frame, width=40)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[label] = entry

    btn_add = Button(input_frame, text="Добавить книгу", command=add_book, bg="#4CAF50", fg="white")
    btn_add.grid(row=len(labels), column=0, columnspan=2, pady=10)

    
    filter_frame = LabelFrame(root, text="Фильтрация", padx=10, pady=10)
    filter_frame.pack(fill="x", padx=10, pady=5)

    Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5, pady=5)
    genre_filter_var = StringVar()
    genre_combo = ttk.Combobox(filter_frame, textvariable=genre_filter_var, width=30)
    genre_combo.grid(row=0, column=1, padx=5, pady=5)

    Label(filter_frame, text="Страниц > ").grid(row=0, column=2, padx=5, pady=5)
    pages_filter_var = StringVar()
    pages_entry = Entry(filter_frame, textvariable=pages_filter_var, width=10)
    pages_entry.grid(row=0, column=3, padx=5, pady=5)

    btn_filter = Button(filter_frame, text="Применить фильтр", command=refresh_table, bg="#2196F3", fg="white")
    btn_filter.grid(row=0, column=4, padx=10, pady=5)

    btn_reset = Button(filter_frame, text="Сбросить фильтр", command=reset_filter, bg="#FF9800", fg="white")
    btn_reset.grid(row=0, column=5, padx=5, pady=5)

    
    tree_frame = Frame(root)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("Название", "Автор", "Жанр", "Страницы")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=200)

    scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=LEFT, fill="both", expand=True)
    scrollbar.pack(side=RIGHT, fill="y")

    
    button_frame = Frame(root)
    button_frame.pack(fill="x", padx=10, pady=10)

    Button(button_frame, text="Сохранить в JSON", command=save_to_json, bg="#4CAF50", fg="white").pack(side=LEFT,
                                                                                                       padx=5)
    Button(button_frame, text="Загрузить из JSON", command=load_from_json, bg="#FFC107", fg="black").pack(side=LEFT,
                                                                                                          padx=5)
    Button(button_frame, text="Удалить выбранную книгу", command=delete_book, bg="#F44336", fg="white").pack(side=LEFT,
                                                                                                             padx=5)



def main():
    global books
    create_interface()
    load_data()
    update_genre_filter_list()
    refresh_table()
    root.mainloop()


if __name__ == "__main__":
    main()