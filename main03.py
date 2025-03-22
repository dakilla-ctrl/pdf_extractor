# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 05:23:01 2023

@author: Admin
"""

import os
import PyPDF2
from tkinter.filedialog import askopenfilename

# to get file info


def get_file_info():
    file_path = askopenfilename(filetypes=[("PDF files", "*.pdf")])

    if not file_path:
        print("No file selected.")
        return None, None, None, None

    file_title = os.path.splitext(os.path.basename(file_path))[0]
    num_pages = len(PyPDF2.PdfReader(file_path).pages)
    size_bytes = os.path.getsize(file_path)
    size_mb = round(size_bytes / (1024 * 1024), 2)

    return file_path, file_title, num_pages, size_mb

# to extract file


def extract_pages_with_text(file_path, search_phrase):
    pdf_reader = PyPDF2.PdfReader(file_path)
    num_pages = len(pdf_reader.pages)
    extracted_pages = []
    found_pages = []

    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()

        if search_phrase.lower() in text.lower():
            extracted_pages.append(page)
            found_pages.append(page_num + 1)

    return extracted_pages, found_pages


def main():
    file_path, file_title, num_pages, size_mb = get_file_info()

    if file_path is None:
        return

    print("File Title is:", file_title, ".pdf")
    print("This file contains:", num_pages, "pages")
    print("The File size is:", size_mb, "MB")

    search_phrase = input("Enter search phrase: ")
    print()

    extracted_pages, found_pages = extract_pages_with_text(file_path, search_phrase)

    if len(extracted_pages) == 0:
        print("No pages found containing the search phrase", search_phrase)
    else:
        output_file_name = f"{file_title}-{search_phrase[:10].capitalize()}.pdf"
        pdf_writer = PyPDF2.PdfWriter()

        for page in extracted_pages:
            pdf_writer.add_page(page)

        with open(output_file_name, "wb") as output_file:
            pdf_writer.write(output_file)

        print(f"{search_phrase.capitalize()} was found in {len(extracted_pages)} out of {num_pages} pages.")

        print(search_phrase.capitalize(), "found in the page(s)", end=' ')
        for i, page_num in enumerate(found_pages):
            if i == len(found_pages) - 1:
                print("and", end=' ')
            print(f"{page_num}", end=', ')
        print()


if __name__ == "__main__":
    main()
