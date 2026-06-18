#!/usr/bin/env python3
import sys
import os
from docx import Document

def count_words_in_docx(path):
    doc = Document(path)
    text = " ".join(para.text for para in doc.paragraphs)
    return len(text.split())

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    total = 0
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".docx"):
            filepath = os.path.join(directory, filename)
            count = count_words_in_docx(filepath)
            print(f"{count:>8,}  {filename}")
            total += count
    print(f"{'':->30}")
    print(f"{total:>8,}  total")

if __name__ == "__main__":
    main()
