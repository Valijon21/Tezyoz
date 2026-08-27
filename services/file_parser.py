"""
Zero-dependency file parser service for TypeMaster.
Extracts sequential text from .txt, .docx, and .md files for custom typing exercises.
Converts OXML Word document paragraphs to plain text natively using standard libraries.
"""
import os
import zipfile
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger("services.file_parser")

def read_docx(file_path: str) -> str:
    """Parses Word document w:p paragraph runs from word/document.xml archive directly."""
    try:
        with zipfile.ZipFile(file_path) as docx:
            xml_content = docx.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # XML local namespace tags expansion rules
            p_tag = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'
            t_tag = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'
            
            paragraphs = []
            for p in root.iter(p_tag):
                text_runs = [t.text for t in p.iter(t_tag) if t.text]
                if text_runs:
                    paragraphs.append("".join(text_runs))
                    
            return "\n".join(paragraphs)
    except Exception as err:
        logger.error(f"Failed parsing docx file {file_path}: {err}")
        raise ValueError(f"Word (.docx) faylini ochishda xatolik yuz berdi: {err}")

def extract_typing_text(file_path: str, max_words: int = 200) -> str:
    """
    Reads the file by extension type, filters empty whitespaces, and returns 
    first max_words as a single space-separated string block.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError("Ko'rsatilgan fayl topilmadi.")
        
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in (".txt", ".md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception as err:
                raise ValueError(f"Fayl kodirovkasini aniqlab bo'lmadi: {err}")
    elif ext == ".docx":
        content = read_docx(file_path)
    else:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan fayl formati: '{ext}'. Faqat .txt, .docx, va .md fayllari mos keladi.")

    # Clean multi-spaces, newlines, and split into sequential words raw array
    words = content.split()
    if not words:
        raise ValueError("Tanlangan fayl ichida terish uchun so'zlar topilmadi.")
        
    # Extract up to max_words bounds
    selected_words = words[:max_words]
    return " ".join(selected_words)
