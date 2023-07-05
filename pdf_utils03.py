# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 05:24:43 2023

@author: Admin
"""

import PyPDF2

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
