from elasticsearch import Elasticsearch
from config import ELASTIC_HOST
import math
class ElasticsearchDB:
    # def __init__(self, base_dir,index_name='data_training', host='http://localhost:9200',username=None, password=None):
    def __init__(self, base_dir,index_name='data_training', host=ELASTIC_HOST,username=None, password=None):

        if username and password:
            self.client = Elasticsearch(
                [host],
                # basic_auth=(username, password),
                request_timeout=30,
                verify_certs=False
            )
        else:
            self.client = Elasticsearch(
                [host],
                request_timeout=30,
                verify_certs=False
            )
        self.index = index_name
        self.base_dir = base_dir
        try:
            index_exists = self.client.indices.exists(index=self.index)
            print(f"Index {self.index} exists: {index_exists}")

            if not index_exists:
                print(f"Creating new index: {self.index}")
                self.client.indices.create(
                    index=self.index,
                    body={
                        "mappings": {
                            "properties": {
                                "embedding": {
                                    "type": "dense_vector",
                                    "dims": 768,
                                    "index": True,
                                    "similarity": "cosine"
                                },
                                "metadata": {
                                    "type": "object"
                                },
                                "document": {
                                    "type": "text"
                                }
                            }
                        }
                    }
                )
        except Exception as e:
            print(f"Error checking/creating index: {e}")

    def add(self, embeddings, metadatas, ids, documents):
        for i in range(len(documents)):
            try:
                if not self.is_valid_vector(embeddings[i]):
                    print(f"Embedding không hợp lệ tại ID {ids[i]} — bỏ qua.")
                    continue
                doc = {
                    "embedding": embeddings[i],
                    "metadata": metadatas[i],
                    "document": documents[i]
                }
                self.client.index(index=self.index, id=ids[i], document=doc)
            except Exception as e:
                print(f"Lỗi khi thêm document {ids[i]}: {str(e)}")

    def get(self):
        res = self.client.search(index=self.index, body={"query": {"match_all": {}}}, size=1000)
        results = {
            "ids": [],
            "documents": [],
            "metadatas": [],
            "embeddings": []
        }
        for hit in res['hits']['hits']:
            source = hit['_source']
            results["ids"].append(hit["_id"])
            results["documents"].append(source["document"])
            results["metadatas"].append(source["metadata"])
            results["embeddings"].append(source["embedding"])
        return results

    def delete_collection(self):
        if self.client.indices.exists(index=self.index):
            self.client.indices.delete(index=self.index)

    def count(self):
        return self.client.count(index=self.index)["count"]

    def query(self, query_embedding, n_results=5):
        if not self.is_valid_vector(query_embedding):
            raise ValueError("Query embedding không hợp lệ hoặc không đúng chiều")
        # script_query = {
        #     "script_score": {
        #         "query": {
        #             "match_all": {}
        #         },
        #         "script": {
        #             "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
        #             "params": {
        #                 "query_vector": query_embedding
        #             }
        #         }
        #     }
        # }
        script_query = {
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": n_results,
                "num_candidates": 100
            }
        }
        try:
            res = self.client.search(
                index=self.index,
                body={
                    "query": script_query,
                    "_source": ["document", "metadata"]
                }
            )
        except Exception as e:
            print(f"KNN search failed: {str(e)}")
            raise

        documents = []
        metadatas = []
        distances = []

        for hit in res["hits"]["hits"]:
            score = hit["_score"]
            source = hit["_source"]
            documents.append(source["document"])
            metadatas.append(source["metadata"])
            distances.append(1.0 - (score - 1.0))  # Reverse cosine score to "distance"

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances]
        }

    def is_valid_vector(self, vec):
        return isinstance(vec, list) and all(
            isinstance(v, (float, int)) and not math.isnan(v) and not math.isinf(v) for v in vec)
