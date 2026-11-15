"""Corpus ORIGINAL de demostración. No contiene fragmentos de CONALDEM ni material V11."""
import json, re, unicodedata
from pathlib import Path
from config import SETTINGS

TEMAS = {
 "rag": ("rag", "recuperacion aumentada", "retrieval"),
 "embedding": ("embedding", "vectores semanticos", "representacion vectorial"),
 "chroma": ("chroma", "chromadb", "base vectorial", "almacenamiento vectorial"),
 "chunk": ("chunk", "fragmentacion", "segmentacion documental"),
 "memoria": ("memoria", "contexto conversacional", "historial"),
 "seguridad": ("seguridad", "abstencion", "alucinacion"),
 "evaluacion": ("evaluacion", "evalua", "evaluar", "evaluado", "pruebas", "metricas"),
 "streamlit": ("streamlit", "despliegue", "interfaz"),
}

def normalize(s):
    s=unicodedata.normalize('NFD',s.lower())
    return ''.join(c for c in s if unicodedata.category(c)!='Mn')

def demo_topic(question):
    q=normalize(question)
    for topic,terms in TEMAS.items():
        if any(re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',q) for term in terms):
            return topic
    return None

class DemoRetriever:
    def __init__(self):
        import chromadb
        from sentence_transformers import SentenceTransformer
        source=Path(__file__).resolve().parents[1]/'data'/'demo'/'documentos_academicos_originales.json'
        self.items=json.loads(source.read_text(encoding='utf-8'))
        self.model=SentenceTransformer(SETTINGS.embedding_model, device='cpu')
        if self.model.get_sentence_embedding_dimension()!=384:
            raise RuntimeError('El embedding no corresponde a E5 V11')
        self.client=chromadb.EphemeralClient()
        # self.col=self.client.get_or_create_collection('demo_academica_original_v1',metadata={'hnsw:space':'cosine'})
        self.col=self.client.get_or_create_collection(name=SETTINGS.demo_collection_name,metadata={'hnsw:space':'cosine'}        )
        vectors=self.model.encode(['passage: '+x['texto'] for x in self.items],normalize_embeddings=True,show_progress_bar=False)
        self.col.upsert(ids=[x['id'] for x in self.items],documents=[x['texto'] for x in self.items],
                        metadatas=[{'tema':x['tema'],'titulo':x['titulo'],'origen':'contenido educativo original'} for x in self.items],
                        embeddings=vectors.tolist())
    def retrieve(self,question,k=2):
        topic=demo_topic(question)
        if not topic: return []
        vec=self.model.encode(['query: '+question],normalize_embeddings=True,show_progress_bar=False)
        r=self.col.query(query_embeddings=vec.tolist(),n_results=1,
                         where={'tema':topic},include=['documents','metadatas','distances'])
        return [{'id':i,'texto':t,'titulo':m['titulo'],'distancia':round(float(d),3)}
                for i,t,m,d in zip(r['ids'][0],r['documents'][0],r['metadatas'][0],r['distances'][0])]
