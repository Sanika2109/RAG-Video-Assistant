# RAG Video Assistant

An AI-powered video assistant that transforms video/audio content into searchable knowledge using speech-to-text, LLM-based summarization, and Retrieval-Augmented Generation (RAG).

## ✨ Features

- 🎥 Process YouTube videos and local audio/video files
- 🎙️ Transcribe content using OpenAI Whisper and Sarvam AI
- 📝 Generate concise titles and summaries
- 📌 Extract action items, key decisions, and open questions
- 🧠 Build a transcript-based RAG pipeline using vector embeddings and ChromaDB
- 💬 Ask context-aware questions about processed video content
- 🖥️ Interactive Streamlit interface

## 🏗️ Architecture

```text
Video / Audio
     │
     ▼
Audio Extraction & Chunking
     │
     ▼
Speech-to-Text
Whisper / Sarvam AI
     │
     ▼
Transcript
     │
     ├──────────────► Summarization & Insights
     │
     ▼
Text Chunking
     │
     ▼
Hugging Face Embeddings
     │
     ▼
ChromaDB
     │
     ▼
Similarity Retrieval
     │
     ▼
Mistral LLM
     │
     ▼
Context-Aware Q&A
````

## 🛠️ Tech Stack

**Languages & Frameworks**

* Python
* Streamlit
* LangChain

**AI/ML**

* OpenAI Whisper
* Mistral AI
* Sarvam AI
* Hugging Face Sentence Transformers

**RAG & Data**

* ChromaDB
* Vector Embeddings
* Similarity Search

**Media Processing**

* yt-dlp
* FFmpeg
* pydub

## 📁 Project Structure

```text
RAG-Video-Assistant/
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── app.py
├── main.py
├── requirements.txt
└── test.py
```

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sanika2109/RAG-Video-Assistant.git
cd RAG-Video-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v3
```

### 5. Run the application

```bash
streamlit run app.py
```

## 💡 Example Use Cases

* **Meetings:** Extract decisions, action items, and unresolved questions
* **Lectures:** Summarize educational videos and query specific concepts
* **Interviews:** Retrieve key discussion points and insights
* **YouTube content:** Convert long-form videos into searchable knowledge
