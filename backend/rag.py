"""Adaptación literal del esquema E5 + ChromaDB del notebook V11, sin Google Drive."""
from pathlib import Path
from config import SETTINGS

class CorpusUnavailable(RuntimeError):
    pass

class V11Retriever:
    def __init__(self, db_path=None):
        from sentence_transformers import SentenceTransformer
        import chromadb
        path = Path(db_path or SETTINGS.chroma_path)
        if not (path / "chroma.sqlite3").is_file():
            raise CorpusUnavailable("No está instalada una base documental autorizada.")
        self.model = SentenceTransformer(SETTINGS.embedding_model, device="cpu")
        if self.model.get_sentence_embedding_dimension() != 384:
            raise CorpusUnavailable("Dimensión E5 no coincide con V11.")
        client = chromadb.PersistentClient(path=str(path))
        collections = client.list_collections()
        if SETTINGS.collection_name:
            collection_name = SETTINGS.collection_name
        elif len(collections) == 1:
            collection_name = collections[0].name
        else:
            raise CorpusUnavailable("No puede determinarse una colección única.")
        self.collection = client.get_collection(name=collection_name)
        if self.collection.count() != 173:
            raise CorpusUnavailable("La base no coincide con los 173 fragmentos V11.")

    def retrieve(self, question: str, k: int = 4, article8: bool = False):
        if not isinstance(question,str) or not question.strip():
            raise ValueError("Consulta vacía")
        vec = self.model.encode(["query: " + question], convert_to_numpy=True,
            normalize_embeddings=True, show_progress_bar=False)
        kwargs = {"query_embeddings":vec.tolist(), "n_results":4 if article8 else k,
                  "include":["documents","metadatas","distances"]}
        if article8:
            kwargs["where"] = {"$and":[{"documento":{"$eq":"Ley_1257_de_2008.pdf"}},
                                           {"articulo":{"$eq":"8"}}]}
        result = self.collection.query(**kwargs)
        fragments = []
        for ident,body,meta,dist in zip(result["ids"][0],result["documents"][0],
                                         result["metadatas"][0],result["distances"][0]):
            fragments.append({"id": ident,"texto":body,"documento":meta.get("documento",""),
                              "pagina_pdf":meta.get("pagina_pdf",""),"categoria":meta.get("categoria",""),
                              "distancia":float(dist)})
        if article8:
            expected={f"Ley_1257_de_2008_p3_art8_f{i}" for i in range(1,5)}
            if {f['id'] for f in fragments} != expected:
                raise CorpusUnavailable("Artículo 8 incompleto: se bloquea la respuesta.")
            fragments.sort(key=lambda f: int(f['id'].rsplit('_f',1)[1]))
        return fragments
