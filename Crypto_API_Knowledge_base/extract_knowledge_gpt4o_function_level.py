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


llm_model = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key="*****",
    temperature='**',
)

extraction_template=''''
#Role: You will be considered an assistant in extracting API function knowledge from the input segments.

#Input segment:{segment}
                                
#Question: 
You should analyze the input segment step by step and judge whether it has the API function.
If the segment has the related API function knowledge, please just output the related function knowledge.

#Output
The output format will be JSON. You should follow the following format: If the segment has more than one API knowledge, please output more API knowledge.
{API_function_name:'****',
 definition:'*****',
 Parameters:'*****',
 Returns::'*****',
 Throws:'*****',
 Secure_use:'*****',
 Insecure_use:'*******'}    

Notes:
1.If the segment has the function with same function name and different parameter, please output all functions knowledge.
2.If you can not find some knowledge from input segment, you can output 'N/A'.

'''

def single_extraction_llm(segment_file):
    prompt_question=PromptTemplate.from_template(template=extraction_template)
    rag_chain = LLMChain(llm=llm_model, prompt=prompt_question)
    llm_first_response=rag_chain.run({'segment':str(segment_file)})
    return llm_first_response


def load_file_segments(filename):
    lines_per_segment=20
    with open(filename, 'r') as file:
        lines = file.readlines()
    segments = []
    for i in range(0, len(lines), lines_per_segment):
        segment = lines[i:i + lines_per_segment]
        segments.append("".join(segment)) 
    return segments
    

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def LLM_knowledge_extraction():

    API_list=['****','****','****','****','****','****','****','****','****','****','****','****']
    file_path='******'
    save_path='******'

    with open(file_path, 'r') as file:
        file = file.readlines()

    file_segments=load_file_segments(file_path)
    save_API_knowledge=[]
    
    for i in range(len(file_segments)):
        tmp_segment=file_segments[i]
        tmp_knowledge=single_extraction_llm(tmp_segment)
        save_API_knowledge.append(tmp_knowledge)

    save_to_json(save_API_knowledge,save_path)


if __name__ == "__main__":
    print('begin')
    LLM_knowledge_extraction()