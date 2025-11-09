# main.py
import os
import chromadb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# FastAPI uygulaması başlatılıyor
app = FastAPI(
    title="RAG Ders Asistanı API",
    description="Gemini ve ChromaDB kullanarak ders içerikleri üzerinde çalışan Retrieval-Augmented Generation (RAG) sistemi."
)

# --- Sabitler (ingest.py ile aynı olmalı) ---
CHROMA_PATH = "./chroma_db"
# main.py dosyasında bu satırı değiştir:
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
PERSIST_DIR = "./chroma_db" 

# --- Model ve İndeks Yükleme ---

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_chat_interface():
    with open("static/index.html", "r") as f:
        return f.read()

def initialize_query_engine():
    """
    Kayıtlı ChromaDB indeksini yükler ve Gemini LLM ile sorgu motoru oluşturur.
    """
    # 1. Gemini API Anahtarı Kontrolü
    if 'GEMINI_API_KEY' not in os.environ:
        raise EnvironmentError(
            "GEMINI_API_KEY ortam değişkeni ayarlanmadı. Lütfen API anahtarınızı giriniz."
        )

    # 2. Embedding Modelini Yükle (ingest.py ile aynı)
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)

    # 3. ChromaDB İstemcisini ve Koleksiyonunu Yükle
    print("RAG QueryEngine yükleniyor...")
    
    # Chroma istemcisi ve koleksiyonu
    db = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = db.get_collection("ders_metinleri") # ingest.py'deki koleksiyon adı

    # LlamaIndex için depolama bağlamını oluştur
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4. İndeksi Yükle
    # 'storage_context' sadece vektör depoyu belirtmek için kullanılır
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, 
        storage_context=storage_context, 
        embed_model=embed_model
    )

    # 5. Gemini LLM'i Tanımla

    system_instruction = (
    "Sen, Eskişehir Teknik Üniversitesi (ESTÜ) derslerini analiz eden bir RAG asistanısın. "
    "Senin tek görevin ve uzmanlığın, kullanıcının sorduğu soruları sadece sana sunulan "
    "ders içerikleri ve meta verileri üzerinden cevaplamaktır. "
    "Eğer kullanıcı ders içerikleriyle İLGİLİ OLMAYAN (örn: 'nasılsın', 'hava nasıl', 'şaka yap') bir soru sorarsa, "
    "şu cevabı ver: 'Ben sadece Estü dersleri ve içerikleri hakkında yardımcı olabilirim. Lütfen derslerle ilgili sorular sorun.'"
    )
    llm = Gemini(
        model="gemini-2.5-flash", 
        temperature=0.1
    )

    # 6. Sorgu Motorunu Oluştur
    # LLM ve RAG Retriever (veri çekici) birleştirilir
    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=7  # Sorguya en alakalı 3 dokümanı çek
    )
    
    print("RAG QueryEngine başarıyla yüklendi ve Gemini ile hazır.")
    return query_engine

# Global değişken olarak sorgu motorunu tanımla
try:
    rag_query_engine = initialize_query_engine()
except EnvironmentError as e:
    rag_query_engine = None # Anahtar yoksa boş bırak
    print(f"Hata: {e}")
except Exception as e:
    rag_query_engine = None
    print(f"Veritabanı yüklenirken bir hata oluştu: {e}")

# --- API Şemaları ---
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

# --- API Endpoint'leri ---

@app.get("/")
async def root():
    if rag_query_engine is None:
        return {"status": "Error", "message": "API anahtarı eksik veya veritabanı yüklenemedi. Detaylar için konsolu kontrol edin."}
    return {"status": "Ready", "message": "RAG Ders Asistanı çalışıyor. /docs adresinden sorgu yapabilirsiniz."}

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    RAG Asistanına bir soru sorar ve cevabı döndürür.
    """
    if rag_query_engine is None:
        raise HTTPException(
            status_code=503, 
            detail="Servis kullanılamıyor. Lütfen GEMINI_API_KEY'i kontrol edin veya ingest.py'yi çalıştırdığınızdan emin olun."
        )

    try:
        # Sorguyu çalıştır
        response = rag_query_engine.query(request.query)
        return QueryResponse(response=str(response))
    except Exception as e:
        print(f"Sorgu sırasında hata: {e}")
        raise HTTPException(status_code=500, detail=f"Sorgu işlenirken bir hata oluştu: {str(e)}")

# ---