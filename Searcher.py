from io import BytesIO
import chromadb
from PIL import Image
from joblib import load

chroma_client = chromadb.PersistentClient('db/')
images = chroma_client.get_or_create_collection(name='image_vectors', metadata={"hnsw:space": "cosine"})


class ImageSearcher:
    def __init__(self, db_connection):
        """
        This takes the db connection of the postgres url
        :param db_connection:
        """
        url: str = "https://togwawzkgfhfhfbuozib.supabase.co"
        key: str = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
                    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZ3dhd3prZ2ZoZmhmYnVvemliIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA2MzI4NzAsImV4cCI6MjAyNjIwODg3MH0.k6C_rgs6i1MD2irsVq__xNJ5YhjkV1R7r4tu8CpSN_Q")
        self.key = key
        self.url = url
        self.DB_CONNECTION = db_connection
        self.images_searched = False
        self.model = load('image-text-searcher.joblib')

    def seed_one_image(self, image_uri, image_data, image_format, uuid, image_date):
        model = self.model
        try:
            with Image.open(BytesIO(image_data)) as img:
                try:
                    embedding = model.encode((img))
                    embedding_list = embedding.tolist()  # Convert embedding to list
                    metadatas = {
                        "user_id": uuid,
                        "image_date": image_date,
                        "type": image_format,
                    }
                    ids = image_uri
                    images.upsert(
                        embeddings=embedding_list,
                        ids=ids,
                        metadatas=metadatas
                    )

                    print('Embeddings Created')
                    return 1
                except Exception as embed_error:
                    print(f"Embedding failed for {image_uri}: {embed_error}")
                    return 0
        except Exception as img_open_error:
            print(f"Failed to open image {image_uri}: {img_open_error}")
            return 0



    def search_one_image(self, query, uuid):
        model = self.model
        text_emb = model.encode(query).tolist()
        results = images.query(
            query_embeddings=text_emb,
            n_results=3,
        )
        return results

    def get_inserted_images(self):
        return images.get()
