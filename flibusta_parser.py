import time
import requests
from bs4 import BeautifulSoup
import zipfile
import tkinter as tk
from tkinter import *
from tkinter.scrolledtext import ScrolledText

main_win = tk.Tk()
main_win.resizable(False, False)
main_win.geometry('640x480+200+10')
main_win.title('Flibusta parser')


def find_books():
    book_name = entry_book_name.get()
    url = f'https://flibusta.club'
    search_url = f'https://flibusta.club/booksearch?ask={book_name}'

    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    response = requests.get(search_url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    body = soup.find('h3', string=' Найденные книги:')
    all_next = body.find_all_next('li')
    del all_next[-11:-1]
    book_dict = {}
    book_list = []
    count = 1

    for i in all_next:
        url_book = i.find_next('a').get('href')
        name = i.find_next('a').text
        pre_author = i.find_all_next('a')
        author = pre_author[1].text
        if name == 'Фильтр-список':
            break
        else:
            book_dict[f'{count}. {name} - {author}'] = url + url_book
            count += 1
            book_list.append(url + url_book)

    for key, value in book_dict.items():
        books_list_text.insert(END, f'{key}\n')

    def download_book():
        number_of_book = int(entry_num.get())

        download_page = '/download/?format=fb2.zip'
        response_download_page = requests.get(book_list[number_of_book-1]+download_page, headers=headers).text
        soup_download_page = BeautifulSoup(response_download_page, 'lxml')
        time.sleep(4)
        download_link_block = soup_download_page.find('div', class_='p_load_progress_txt')
        download_link = download_link_block.find_next('a').get('href')
        if download_link[0] == '/':
            download_book = requests.get(url+download_link, headers=headers).content
        else:
            download_book = requests.get(download_link, headers=headers).content
        time.sleep(5)

        with open('content/book.zip', 'wb') as f:
            f.write(download_book)

        try:
            with zipfile.ZipFile('content/book.zip', 'r') as zip_book:
                zip_book.extractall('content/')

            for widget in main_win.winfo_children():
                widget.destroy()

        except Exception as ex:
            for widget in main_win.winfo_children():
                widget.destroy()

            main_win.geometry('400x200+200+10')
            Label(text='Произошла ошибка.\n Скорее всего файла этой\n книги не существует :(', font=('calibri', 20),
                  fg='red').pack(pady=20, side='top')
            Label(text=f'({ex})', font=('calibri', 16)).pack()

        main_win.geometry('400x200+200+10')
        Label(text='ГОТОВО', font=('calibri', 48)).pack(pady=50, side='top')

    lbl = Label(text='Какую книжку скачать? введите номер: ', font=('calibri', 20))
    entry_num = Entry(font=('calibri', 20), width=3)
    download_btn = Button(text='скачать', font=('calibri', 20), command=download_book)

    lbl.pack(side='left', pady=5, padx=5)
    download_btn.pack(side='right', pady=5, padx=5)
    entry_num.pack(side='right', pady=5, padx=5)


label1 = Label(text='Введите название книги', font=('calibri', 20))
entry_book_name = Entry(font=('calibri', 20), width=80)
btn_ok = Button(text='Искать', font=('calibri', 20), command=find_books)
books_list_text = ScrolledText(bd=2, font=('calibri', 14), height=11, width=80, padx=3, pady=3, wrap='word')

label1.pack(pady=5, padx=5)
entry_book_name.pack(pady=5, padx=5)
btn_ok.pack(pady=5, padx=5)
books_list_text.pack(pady=5, padx=5)

main_win.mainloop()