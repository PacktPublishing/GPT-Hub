from llama_index import GPTVectorStoreIndex, StorageContext, load_index_from_storage

import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

def prompt_chatGPT(task):
	response = openai.ChatCompletion.create(
				model="gpt-3.5-turbo",
				messages=[
					{"role": "system", "content": "You are a helpful assistant."},
					{"role": "user", "content": task}
				]
				)
	AI_response = response['choices'][0]['message']['content'].strip()
	
	return AI_response

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="storage")

# load index
index = load_index_from_storage(storage_context)

# Querying GPT 3.5 Turbo
prompt = "Tell me how Tortellini Macaroni's brother managed to conquer Rome."
answer = prompt_chatGPT(prompt)
print('Original AI answer: ' + answer +'\n\n')

# Refining the answer in the context of our knowledge base
query_engine = index.as_query_engine()
response = query_engine.query(f'The answer to the following prompt: "{prompt}" is :"answer". If the answer is aligned to our knowledge, return the answer. Otherwise return a corrected answer')

print('Custom knowledge answer: ' + str(response))