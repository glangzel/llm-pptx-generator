# from dotenv import load_dotenv
# load_dotenv()

import settings
import sys, os, datetime, json

from operator import itemgetter

from langchain.schema import SystemMessage, HumanMessage

from langchain.prompts.chat import (
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
        )
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema.embeddings import Embeddings
from langchain.schema.language_model import BaseLanguageModel
from langchain.vectorstores.chroma import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


from llm_commons.proxy.base import set_proxy_version
from llm_commons.proxy.identity import AICoreProxyClient
from llm_commons.langchain.proxy import init_llm, init_embedding_model


AICORE_LLM_CLIENT_ID = settings.AICORE_LLM_CLIENT_ID
AICORE_LLM_CLIENT_SECRET = settings.AICORE_LLM_CLIENT_SECRET
AICORE_LLM_AUTH_URL = settings.AICORE_LLM_AUTH_URL
AICORE_LLM_API_BASE = settings.AICORE_LLM_API_BASE
AICORE_LLM_RESOURCE_GROUP = settings.AICORE_LLM_RESOURCE_GROUP


FOLDER_NAME = "./tmp"
SRC_FOLDER = "../doc"
LANGUAGE_MODEL = "gpt-35-turbo-16k"
LANGUAGE_MODEL = "gpt-4"
FILENAME = "g72023hiroshimaleaderscommunique.pdf"

SYS_TEMPLATE = f"""
    You are a journalist that replies to a question always with the truth you get from a document and also with a comment that can be funny. Don't make up answers.
    Pass back only JSON data as so: 
    "answer": "the answer from the document", "comment": "A comment from your perspective."
"""
HUMAN_TEMPLATE = """
    The question is: {query}. Reply using below document information with JSON for "answer" and "comment".
    Answer in the language of the iso language code '{language}'. Also comment in the same language.
    ===========================
    {context}        
"""

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

def retrieve_data(vector_db: Chroma, llm: BaseLanguageModel, query: str, language = "en")->str:
    """ Retrieves data from store and passes back result """
    retriever = vector_db.as_retriever(k=4)
    response_schemas = [
        ResponseSchema(name="answer", type = "string", description="Answer based on the document data."),
        ResponseSchema(name="comment", type = "string", description="Comment on the answer as a journalist.")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    my_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(SYS_TEMPLATE),
            HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)  
        ],
        input_variables=['query', 'context', 'language'],
        partial_variables={"format_instructions": format_instructions}
    )
    rag_chain = (
            {
                "query": itemgetter("query"), 
                "language": itemgetter("language"),
                "context": itemgetter("query") | retriever
            } 
            | my_prompt 
            | llm
        )
    try:
        output = rag_chain.invoke({"query": query, "language": language})
        result = output_parser.parse(output.content)
        return result
    except Exception as e:
        return f"Exception: {e}"

def main()->None:
    """ Main routine of program. """
    set_proxy_version('aicore') # for an AI Core proxy
    proxy_client = AICoreProxyClient()
    proxy_client.get_deployments() # to cache the deployment data

    embed = init_embedding_model(model_name="text-embedding-ada-002")
    llm = init_llm(model_name=LANGUAGE_MODEL, 
                proxy_client=proxy_client,
                temperature=0.3
                    )
    if not os.path.exists(FOLDER_NAME):
        print(f"Folder {FOLDER_NAME} for temporary file storage missing. Create.")
        os.makedirs(FOLDER_NAME)

    if (upload_text(emb=embed, filename=FILENAME, src_folder=SRC_FOLDER, dst_folder=FOLDER_NAME)):
        # Open connection to DB (normally you would not do that twice but here is just for testing)
        db = Chroma(embedding_function=embed, persist_directory=f"{os.path.join(FOLDER_NAME, FILENAME.rsplit('.', 1)[0].lower())}_doc.db")
        
        # Run RAG sequence on query
        user_input = "What was said about Russia and at which event was it said?"
        while True:
            print(json.dumps(retrieve_data(vector_db=db, llm=llm, query=user_input, language="en"), indent=4))
            user_input = input("Enter a query (type 'exit' to stop): ")
            
            if user_input.lower() == 'exit':
                print("Exiting.")
                break
            

if __name__ == '__main__':
    sys.exit(main())