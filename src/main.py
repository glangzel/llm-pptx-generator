import sys, os, json

from langchain.vectorstores.chroma import Chroma

import get_llm
import retrieve_data
import upload_text
import gen_pptx



FOLDER_NAME = "./tmp"
SRC_FOLDER = "./src/src"
FILENAME = "20210603008-4_meti.pdf"
design_number = "6"
DESIGN_TEMPLATE = f"./src/Designs/Design-{design_number}.pptx"



def main()->None:
    input_topic = input("Enter a topic (type 'exit' to stop): ")
    # input_page = input("Enter page number (type 'exit' to stop): ")
    
    """ Main routine of program. """
    if not os.path.exists(FOLDER_NAME):
        print(f"Folder {FOLDER_NAME} for temporary file storage missing. Create.")
        os.makedirs(FOLDER_NAME)

    print("Analyzing Documents ...")
    if (upload_text.upload_text(emb=get_llm.get_embed(), filename=FILENAME, src_folder=SRC_FOLDER, dst_folder=FOLDER_NAME)):
        # Open connection to DB (normally you would not do that twice but here is just for testing)
        db = Chroma(embedding_function=get_llm.get_embed(), persist_directory=f"{os.path.join(FOLDER_NAME, FILENAME.rsplit('.', 1)[0].lower())}_doc.db")

        # JSON -> Python Object
        data = json.loads(retrieve_data.retrieve_data(vector_db=db, llm=get_llm.get_llm(), topic=input_topic, language="en"))
        print("parsing done!")
        gen_pptx.gen_pptx(data, DESIGN_TEMPLATE)
        print("gen pptx done!")  
            

if __name__ == '__main__':
    sys.exit(main())