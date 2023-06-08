# Index_stories.py

from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader

# Loading from a directory
documents = SimpleDirectoryReader('stories').load_data()

# Construct a simple vector index
index = GPTVectorStoreIndex.from_documents(documents)

# Save your index to a .json file
index.storage_context.persist(persist_dir="storage") 
