import chromadb

chroma_client = chromadb.PersistentClient('db/')
collection = chroma_client.get_or_create_collection(name='image_vectors', metadata={"hnsw:space": "cosine"})
print(chroma_client.delete_collection('image_vectors'))