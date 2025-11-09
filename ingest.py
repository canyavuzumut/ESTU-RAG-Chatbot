# ingest.py

import pandas as pd
from llama_index.core import Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

# 1. PARAMETRELER
INPUT_FILE = "llm_hazir_ders_verisi_FINAL_TEMIZ.csv" # TEMİZLEDİĞİN SON DOSYA ADI
CHROMA_PATH = "./chroma_db"
# ingest.py dosyasında bu satırı değiştir:
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"

def ingest_data():
    """Veriyi yükler, vektörleştirir ve ChromaDB'ye kaydeder."""
    
    # Veriyi Oku (UTF-8 ile okuduğundan emin ol)
    print(f"1/4: {INPUT_FILE} dosyası okunuyor...")
    try:
        df = pd.read_csv(INPUT_FILE, encoding='utf-8')
    except Exception as e:
        print(f"Hata: {e}. Kodlama hatası nedeniyle latin1 ile okunuyor.")
        df = pd.read_csv(INPUT_FILE, encoding='latin1')

    # LLM_METIN sütunundaki her satırı bir LlamaIndex Document'a çevir
    documents = []
    for index, row in df.iterrows():
        # Her bir ders kaydını (LLM_METIN) bir belge (Document) olarak al
        # Bu, RAG'in arayacağı ana metin olacak
        doc = Document(
            text=row['LLM_METIN'],
            # Metadata eklemek, daha sonra filtreleme için kullanışlıdır (opsiyonel)
            metadata={
                "ders_kodu": row['ders_kodu'],
                "donem": row['donem'],
                "dersinadi": row['dersinadi']
            }
        )
        documents.append(doc)
    
    print(f"2/4: Toplam {len(documents)} adet belge (ders) oluşturuldu.")

    # ChromaDB (Vektör Veritabanı) kurulumu
    # Lokal bir Chroma istemcisi oluştur
    db = chromadb.PersistentClient(path=CHROMA_PATH)
    # Varsayılan "collection" (veritabanındaki tabloya benzer) adını kullan
    chroma_collection = db.get_or_create_collection("ders_metinleri")
    
    # Embedding Modelini Yükle
    # all-MiniLM-L6-v2 hızlı ve küçük boyutlu, başlangıç için harika bir modeldir.
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
    
    # Vektör ve Depolama Bağlamını Tanımla
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    print(f"3/4: Embedding modeli ({EMBEDDING_MODEL_NAME}) yüklendi ve vektörler oluşturuluyor...")

    # İndeksleme (Vektörleştirme) İşlemini Başlat
    # Tüm belgeler okunur, vektörleştirilir ve ChromaDB'ye kaydedilir.
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model
    )
    
    print(f"4/4: İndeksleme tamamlandı. Vektör Veritabanı {CHROMA_PATH} klasörüne kaydedildi.")

if __name__ == "__main__":
    ingest_data()