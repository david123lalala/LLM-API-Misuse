import json
import os
import time
import csv
import sys
from langchain_openai import ChatOpenAI, OpenAI
from langchain_community.document_loaders import TextLoader
from langchain.memory import ConversationBufferMemory
import openai

from langchain.text_splitter import CharacterTextSplitter

from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from langchain.retrievers.multi_query import MultiQueryRetriever

from langchain.prompts import PromptTemplate

from langchain.chains import LLMChain, SimpleSequentialChain

from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser


import logging

from openai import OpenAI


import copy


os.environ["OPENAI_BASE_URL"] = "********"

os.environ["OPENAI_API_KEY"] = "******"


llm_model = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key="*****",
)


generate_template = '''
# Role: 
# You will be considered an assistant to detect if the input slice_A_snippets has security API misuse. 

# slice_A_snippets: {slice_A_snippets},

# static_variables: {static_variables}

# function_calls: {function_calls}

# crypto_API_knowledge: {crypto_API_knowledge}


# Requirments:
1.You should analyze the snippets step by step, and you can refer to the function_calls, static_variables, and crypto_API_knowledge to judge API misuse.
2.You can judge the data-call relationships between static_variables and slice_A_snippets to detect if the input slice_A_snippets has constant key API misuse.
3.You can refer to the crypto_API_knowledge to detect slice_A_snippets has crypto API misuse.
4.You can refer to the previous_generation of LLMs to self-reflect and self-summarize crypto API misuse.
5.This is reflection round {reflection_round}. You should critically review the previous_generation, identify any errors or omissions, and produce an improved and more accurate judgement.

            
#Question: 
1. Does this input slice_A_snippets have security API misuse? Output yes or no, give me the type, location (code line), and reasoning of API misuse, and please to repair the API misuse.
2. You should carefully check each line of snippets and output the specific code line of API misuse.

#Response
The reply format will be JSON format, you should follow the following format:
['answer':'yes/no','type':''****','location':'*****',"reason":'****','repair approach':'****']                       
'''



refine_template = '''
#Role: You should re-check the first_response of LLMs, and output the final judgement to crypto API misuse.

#first_response:{first_response}

#Response
The final format will be JSON format, you should follow the following format:
['answer':'yes/no','type':''****','location':'*****',"reason":'****','repair approach':'****']                              
'''


class CryptoAPI_Agent:
    DEFAULT_REFLECTION_ROUNDS = 5

    def __init__(self, llm, reflection_rounds=None):
        self.llm = llm
        self.reflection_rounds = reflection_rounds or self.DEFAULT_REFLECTION_ROUNDS
        self.generate_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(template=generate_template),
        )
        self.reflect_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(template=refine_template),
        )

    def _build_input(self, data):
        return {
            'slice_A_snippets': data.get('slice_A_snippets', ''),
            'static_variables': data.get('static_variables', ''),
            'function_calls': data.get('function_calls', ''),
            'crypto_API_knowledge': data.get('crypto_API', data.get('crypto_API_knowledge', '')),
        }

    def generate(self, data):
        input_data = self._build_input(data)
        return self.generate_chain.run(input_data)

    def reflect(self, data, previous_generation, round_num):
        input_data = self._build_input(data)
        input_data['previous_generation'] = previous_generation
        input_data['reflection_round'] = str(round_num)
        return self.reflect_chain.run(input_data)

    def run(self, data):
        initial_response = self.generate(data)
        reflection_history = [initial_response]

        current_response = initial_response
        for i in range(self.reflection_rounds):
            print(f"Reflection round {i + 1}/{self.reflection_rounds}")
            current_response = self.reflect(data, current_response, i + 1)
            reflection_history.append(current_response)

        return {
            'final_result': current_response,
            'reflection_history': reflection_history,
            'initial_generation': initial_response,
            'reflection_rounds': self.reflection_rounds,
        }


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def detect_and_enrich_with_results(enriched_data_path, output_json_path, reflection_rounds=None):
    enriched_data = load_json(enriched_data_path)
    agent = CryptoAPI_Agent(llm=llm_model, reflection_rounds=reflection_rounds)
    results = []

    for entry in enriched_data:
        file_path = entry['file_path']
        slice_A_snippets = entry['slice_A_snippets']
        static_variables = entry['static_variables']
        function_calls = entry['function_calls']
        crypto_API = entry['crypto_API']

        model_input = {
            'slice_A_snippets': slice_A_snippets,
            'static_variables': static_variables,
            'function_calls': function_calls,
            'crypto_API': crypto_API,
        }

        print(f"Processing: {file_path}")
        agent_result = agent.run(model_input)

        detection_entry = {
            'file_path': file_path,
            'detection_result': agent_result['final_result'],
            'initial_generation': agent_result['initial_generation'],
            'reflection_history': agent_result['reflection_history'],
            'reflection_rounds': agent_result['reflection_rounds'],
        }

        results.append(detection_entry)

    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Detection results saved to {output_json_path}")


input_path_list = [
    '******',
]

save_path = '*****'
output_path_list = [
    save_path + '*****',
]

for input_path, output_path in zip(input_path_list, output_path_list):
    detect_and_enrich_with_results(input_path, output_path)