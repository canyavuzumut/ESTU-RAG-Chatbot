# 🎓 ESTÜ Ders Öneri RAG Chatbotu (Gemini & LlamaIndex)

> 🤖 Eskişehir Teknik Üniversitesi (ESTÜ) ders içeriklerini analiz ederek öğrencilere yapay zeka destekli, kişiselleştirilmiş ders önerileri sunan Retrieval-Augmented Generation (RAG) sistemi.

## ✨ Proje Amacı ve Özeti

Bu proje, öğrencilerin kariyer hedeflerine ve ilgi alanlarına uygun dersleri bulmalarına yardımcı olmak için geliştirilmiştir. Sistem, ESTÜ ders katalog verilerini kullanarak, standart anahtar kelime aramalarının ötesine geçen **anlamsal (semantik) arama** yeteneği sunar.

Kullanıcılar "Yazılımla ilgileniyorum, bana yapay zeka dersleri önerir misin?" gibi doğal dilde sorular sorabilir ve sistem, ders içeriklerini anlayarak doğru önerileri sunar.

### 🧠 RAG Mimarisi

Sistem, iki ana aşamada çalışır:

1.  **Retrieval (Geri Çağırma):** Kullanıcının sorgusu, ders içeriklerinin vektör veritabanında saklanan anlamlarına göre eşleştirilir.
2.  **Generation (Üretim):** Çekilen en alakalı ders metinleri, Google **Gemini 2.5 Flash** modeline sunularak, bağlama uygun ve akıcı bir öneri cevabı oluşturulur.

## 🛠️ Kullanılan Teknolojiler

| Kategori | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| **Büyük Dil Modeli (LLM)** | Google Gemini 2.5 Flash | Sorguları yanıtlamak ve RAG çıktısını düzenlemek için kullanılır. |
| **RAG Çatısı** | LlamaIndex | Veri yönetimi, vektörleştirme ve sorgu motoru oluşturma. |
| **Vektörleştirme (Embedding)** | `intfloat/multilingual-e5-large` | Türkçe ve teknik metinler için optimize edilmiş güçlü çok dilli gömme modeli. **(Performans için kritik)** |
| **Vektör Veritabanı** | ChromaDB (Lokal) | Yüksek boyutlu vektörleri depolamak ve hızlı arama yapmak için kullanılır. |
| **Backend/API** | FastAPI & Uvicorn | RAG motorunu bir HTTP API olarak sunar (`/query` endpoint). |
| **Frontend** | HTML, CSS, JavaScript | Kullanıcı dostu ve responsive sohbet arayüzü. |

---

## ⚙️ Kurulum ve Çalıştırma Rehberi

Bu projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları sırasıyla uygulayın.

### 1. Projeyi Klonlama ve Sanal Ortam

```bash
# Projeyi klonla
git clone [https://github.com/canyavuzumut/ESTU-RAG-Chatbot.git](https://github.com/canyavuzumut/ESTU-RAG-Chatbot.git)
cd ESTU-RAG-Chatbot

# Sanal ortam oluşturma ve etkinleştirme
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate # Windows


pip install -r requirements.txt