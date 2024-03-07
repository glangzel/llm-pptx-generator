import os

from langchain.schema.embeddings import Embeddings
from langchain.vectorstores.chroma import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def upload_text(emb: Embeddings, filename: str, src_folder: str, dst_folder: str)->bool:
    """ Converts pdf documents into text and saves the embeddings in a vector store. """
    file_ext = filename.rsplit('.', 1)[1].lower()
    file_name_wo_ext = filename.rsplit('.', 1)[0].lower()
    dst_file_path = os.path.join(dst_folder, file_name_wo_ext + ".txt")
    src_file_path = os.path.join(src_folder, filename)
    db_name = f"{os.path.join(dst_folder, file_name_wo_ext)}_doc.db"

    if os.path.exists(db_name):  #Only embed if no embeddings db exists
        return True
    try:
        print(f"file source {src_file_path} - destination: {dst_file_path}")
        if file_ext == "pdf": #PDF File
            print(f"Running conversion of PDF file '{file_name_wo_ext}'")
            loader = PyPDFLoader(src_file_path)
            pages = loader.load_and_split()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs_chunks = text_splitter.split_documents(pages)
            db = Chroma.from_documents(documents=docs_chunks, embedding=emb, persist_directory=db_name)
            print(f"Converted filename {filename} into text.")
    except Exception as e:
        print(f"Exception: {e}")
        return False
    return True