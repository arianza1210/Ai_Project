from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import faiss
import numpy as np
import os
import pandas as pd
import time

class KnowledgeBaseManager:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.data_path = os.path.join(self.base_path, "res", "LayananeService_new.xlsx")
        self.index_path = os.path.join(self.base_path, "res", "faiss_new.index")
        self.timestamp_path = os.path.join(self.base_path, "res", "index.timestamp")
        self.embedding_model = None
        self.knowledge_base = self._load_knowledge_base()
        self.index = self._load_or_create_index()

    def load_embedding_model(self):
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(
                "distiluse-base-multilingual-cased-v2"
            )

    def _load_knowledge_base(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found at: {self.data_path}")

        df = pd.read_excel(self.data_path, usecols=[
            "nama_layanan", "nama_kategori", "nama_layanan_unit",
            "produk_layanan", "persyaratan", "sm_prosedur",
            "waktu_penyelesaian", "biaya", "nama_unit", "link_url"
        ])
        df = df.fillna("")
        df["content"] = (
            df["nama_layanan"] + " | " + df["nama_kategori"] + " | " +
            df["nama_layanan_unit"] + " | " + df["produk_layanan"] + " | " +
            df["persyaratan"] + " | " + df["sm_prosedur"] + " | " +
            df["waktu_penyelesaian"] + " | " + df["biaya"] + " | " + df["nama_unit"] +
            " | " + df["link_url"]
        )
        return df

    def _create_new_index(self) -> faiss.IndexFlatL2:
        print("Creating new FAISS index...")
        self.load_embedding_model()

        texts = self.knowledge_base["content"].tolist()
        batch_size = 32
        embeddings_list = []

        total_batches = len(texts) // batch_size + (1 if len(texts) % batch_size > 0 else 0)
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i: i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts)
            embeddings_list.append(batch_embeddings)
            print(f"Processing batch {(i//batch_size)+1}/{total_batches}")

        embeddings = np.vstack(embeddings_list).astype("float32")
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        faiss.write_index(index, self.index_path)
        # simpan timestamp modifikasi dataset
        with open(self.timestamp_path, "w") as f:
            f.write(str(os.path.getmtime(self.data_path)))

        return index

    def _load_or_create_index(self) -> faiss.IndexFlatL2:
        need_rebuild = True
        if os.path.exists(self.index_path) and os.path.exists(self.timestamp_path):
            try:
                # cek apakah dataset berubah
                with open(self.timestamp_path, "r") as f:
                    last_mtime = float(f.read().strip())
                current_mtime = os.path.getmtime(self.data_path)
                if abs(current_mtime - last_mtime) < 0.001:
                    need_rebuild = False
                    print("Loading existing FAISS index...")
                    return faiss.read_index(self.index_path)
            except Exception as e:
                print(f"Index load check failed: {e}. Rebuilding index.")

        if need_rebuild:
            return self._create_new_index()

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Cari data paling relevan, default hanya ambil 2 hasil."""
        self.load_embedding_model()
        query_embedding = self.embedding_model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                results.append({
                    "text": self.knowledge_base.iloc[idx]["content"],
                    "distance": float(distances[0][i]),
                    "index": int(idx)
                })
        return results

    def get_relevant_context(self, query: str) -> List[Dict[str, Any]]:
        """Shortcut untuk ambil 2 data teratas."""
        return self.search(query, top_k=2)



if __name__ == "__main__":
    kb = KnowledgeBaseManager()
    hasil = kb.get_relevant_context("saya mau pengajuan zoom unit apa yg harus sy lakukan? syaratnya apa aja?")
    print(hasil)
