# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 05:23:01 2023

@author: Admin
"""

import os
from pdf_utils03 import extract_pages_with_text
from file_utils03 import get_file_info
import PyPDF2

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