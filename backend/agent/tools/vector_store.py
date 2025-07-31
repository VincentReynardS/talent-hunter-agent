import json
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer
from ...config import Settings, settings

CANDIDATES_COLLECTION = "candidates"
COMPANIES_COLLECTION = "companies"
EMBEDDING_MODEL = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

class VectorStore:
    def __init__(self, settings: Settings):
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_endpoint,
            api_key=settings.qdrant_api_key,
        )
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self._create_collection(CANDIDATES_COLLECTION)
        self._create_collection(COMPANIES_COLLECTION)
        
    def _create_collection(self, name, vector_size=768, distance=Distance.COSINE):
        """
        Create a collection if it does not exist

        Args:
            name: str
            vector_size: int
            distance: Distance
        """
        if not self.qdrant_client.collection_exists(name):
            self.qdrant_client.recreate_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )
            
    def _create_candidate_point_struct(self, candidate_name: str, email: str, resume: str) -> PointStruct:
        """
        Create a point struct for a candidate

        Args:
            candidate_name: str
            email: str
            resume: str

        Returns:
            PointStruct
        """
        payload = {
            "metadata": {
                "name": candidate_name,
                "email": email,
            },
            "content": json.dumps(
                {
                    "resume": resume,
                    "email": email,
                    "name": candidate_name
                }
            )
        }

        vector = self._embed_document(resume)

        unique_id = int(hashlib.md5(f"{candidate_name}__{email}".encode()).hexdigest(), 16) % (10 ** 10)

        return PointStruct(
            id=unique_id,
            vector=vector,
            payload=payload
        )
    
    def _create_company_point_struct(self, company_name: str, job_title: str, company_query: str) -> PointStruct:
        """
        Create a point struct for a company

        Args:
            company_name: str
            job_title: str
            company_query: str

        Returns:
            PointStruct
        """
        payload = {
            "metadata": {
                "name": company_name,
                "job_title": job_title
            },
            "content": company_query
        }

        vector = self._embed_document(company_query)

        unique_id = int(hashlib.md5(f"{company_name}_{job_title}".encode()).hexdigest(), 16) % (10 ** 10)

        return PointStruct(
            id=unique_id,
            vector=vector,
            payload=payload
        )

    def _embed_document(self, document: str) -> list[list[float]]:
        """
        Embed a document

        Args:
            document: str

        Returns:
            list[list[float]]
        """
        return self.embedding_model.encode(document).tolist()

    def upsert_candidate(self, candidate_name: str, email: str,resume: str):
        """
        Upsert a candidate into the vector database

        Args:
            candidate_name: str
            email: str
            resume: str
        """
        point_struct = self._create_candidate_point_struct(candidate_name, email,resume)

        self.qdrant_client.upsert(
            collection_name=CANDIDATES_COLLECTION,
            points=[point_struct],
        )

    def upsert_company(self, company_name: str, job_title: str, company_query: str):
        """
        Upsert a company into the vector database

        Args:
            company_name: str
            job_title: str
            company_query: str
        """
        point_struct = self._create_company_point_struct(company_name, job_title, company_query)

        self.qdrant_client.upsert(
            collection_name=COMPANIES_COLLECTION,
            points=[point_struct],
        )

    def search_candidate(self, query: str):
        """
        Search for a candidate in the vector database
        """
        query_embedding = self.embedding_model.encode(query).tolist()
        results = self.qdrant_client.search(
            collection_name=CANDIDATES_COLLECTION,
            query_vector=query_embedding,
            limit=10
        )
        return results
    
    def search_company(self, query: str):
        """
        Search for a company in the vector database
        """
        query_embedding = self.embedding_model.encode(query).tolist()
        results = self.qdrant_client.search(
            collection_name=COMPANIES_COLLECTION,
            query_vector=query_embedding,
            limit=10
        )
        return results

vector_store = VectorStore(settings)
