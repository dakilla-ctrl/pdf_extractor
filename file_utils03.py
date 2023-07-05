# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 05:25:51 2023

@author: Admin
"""

import os
from tkinter.filedialog import askopenfilename
import PyPDF2

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