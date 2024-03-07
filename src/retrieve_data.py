from operator import itemgetter

from langchain.prompts.chat import (
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
        )
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

from langchain.schema.language_model import BaseLanguageModel
from langchain.vectorstores.chroma import Chroma

SYS_TEMPLATE_1 = f"""
    Make theme and sections and body texts of each pages of a presentation. You only answer with finished presentation.
    You must follow these:
    - The presentation has a table of contents which maches the slide/content count.
    - You are not allowed to insert contents and links/images.
    - Start with Introduction Page, and End with Summary Page.
    - In "section_context", please enter 2~3 body sentence texts.
        - Body sentence texts are related to "section_name".
        - Body sentence texts should be related on the content of the uploaded document.
        - The length of each body should be about 100 words.
    - Make them into json format.

    Example:
    1. INTRODUCTION OF PAGE 1 OF THIS POWERPOINT
    2. SECTION NAME OF PAGE 2 OF THIS POWERPOINT
    3. SECTION NAME OF PAGE 3 OF THIS POWERPOINT
    ...
    X. SUMMARY OF THIS POWERPOINT

    Please move It Into a JSON format :
    ```
    "title_name": "TITLE NAME OF THIS POWERPOINT",
    "section_content": [
        "section_name": "INTRODUCTION OF PAGE 1 OF THIS POWERPOINT",
        "section_content": [
                    "",
                    "",
                    ...
                    ""
                ],
        "section_name": "SECTION NAME OF PAGE 2 OF THIS POWERPOINT",
        "section_content": [
                    "",
                    "",
                    ...
                    ""
                ],
        "section_name": "SECTION NAME OF PAGE 3 OF THIS POWERPOINT",
        "section_content": [
                    "",
                    "",
                    ...
                    ""
                ],
        ...
        "section_name": "SUMMARY OF LAST PAGE OF THIS POWERPOINT
        "section_content": [
                    "",
                    "",
                    ...
                    ""
                ]
    ]
"""
HUMAN_TEMPLATE_1 = """
    Make theme and sections of each pages of a presentation about {topic}. 
    You only answer with finished presentation.     
"""



def retrieve_data(vector_db: Chroma, llm: BaseLanguageModel, topic: str, language: str)->str:
    """ Retrieves data from store and passes back result """
    retriever = vector_db.as_retriever(k=4)
    response_schemas = [
        ResponseSchema(name="answer", type="json", description="Answer with finished presentation as JSON format.")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    my_prompt_1 = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(SYS_TEMPLATE_1),
            HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE_1)  
        ],
        input_variables=['topic', 'language'],
        partial_variables={"format_instructions": format_instructions}
    )

    rag_chain_1 = (
            {
                "topic": itemgetter("topic"),
                "language": itemgetter("language") | retriever
            } 
            | my_prompt_1
            | llm
        )
    output_1 = rag_chain_1.invoke({"topic": topic, "language": language})
    print(output_1.content)

    return output_1.content