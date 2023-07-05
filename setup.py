# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:20:36 2023

@author: Admin
"""

import sys
from cx_Freeze import setup, Executable

# Add your main script here
target = Executable("main03.py")

setup(
    name="pdf_extractor",
    version="3.0",
    description="Extracts PDF contents",
    executables=[target]
)
