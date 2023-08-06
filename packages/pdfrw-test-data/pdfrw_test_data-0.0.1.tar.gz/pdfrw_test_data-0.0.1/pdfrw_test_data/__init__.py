import os
from os.path import abspath, dirname, join

_HERE = dirname(abspath(__file__))

files = [
    join(_HERE, pdf_file) for pdf_file in
    os.listdir(_HERE) if pdf_file.endswith('.pdf')
]
