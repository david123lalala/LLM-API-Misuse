import os 
import time
import csv
import sys
import json

from langchain_openai import ChatOpenAI,OpenAI
from langchain_community.document_loaders import TextLoader

from langchain.text_splitter import CharacterTextSplitter

from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from langchain.retrievers.multi_query import MultiQueryRetriever

from langchain.prompts import PromptTemplate

from langchain.chains import LLMChain,SimpleSequentialChain

from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser


import logging

from openai import OpenAI



my_template=''''
#Role: You will be considered an assistant to detect if the input source code has crypto API misuse.

#Input source code:{target_file}
                                
#Question: 
1. Does this source code have crypto API misuse? Output yes or no, give me the type of misuse and the reasoning process. 

#Response
The reply format will be JSON format, you should follow the following format:
[answer:'yes/no',
location:'***'
reason:'**']                                 
'''


os.environ["OPENAI_BASE_URL"] = ""

os.environ["OPENAI_API_KEY"] = "" 



llm_model = ChatOpenAI(
    model_name="",
    openai_api_key="",
)



def llms_detection(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()

    prompt_question=PromptTemplate.from_template(
        template=my_template,
        )
    my_chain = LLMChain(llm=llm_model, prompt=prompt_question)

    llm_first_response=my_chain.run({'target_file':str(file_content)})
    print('type(llm_first_response)',type(llm_first_response))

    return llm_first_response



def detect_in_folder(folder_path):
    print('folder_path的路径',folder_path)
    results = []
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            detection_result = llms_detection(file_path)

            time.sleep(5)
            
            result_entry = {
                'file_path': file_path,
                'detection_result': detection_result
            }
            results.append(result_entry)
    
    return results


input_path_list = []

save_tmp_path=''

output_path_list = []

for input_path,output_path in zip(input_path_list,output_path_list):
    detection_results = detect_in_folder(input_path)

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(detection_results, json_file, ensure_ascii=False, indent=4)