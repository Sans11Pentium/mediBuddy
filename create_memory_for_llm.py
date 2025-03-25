import os
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# Load env var
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Step 1: Load raw PDF(s)
DATA_PATH = "data/"

def load_pdf_files(data_path):
    documents = []
    for file_name in os.listdir(data_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(data_path, file_name)
            print(f"Loading: {file_name}")
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            documents.append(Document(page_content=text))
                    print(f"Loaded {len(pdf.pages)} pages from {file_name}")
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
    
    return documents

# Load PDF files
documents = load_pdf_files(DATA_PATH)
print("Total pages loaded:", len(documents))



# Step 2: Create Chunks
def create_chunks(extracted_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,
                                                 chunk_overlap=50)
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks

text_chunks=create_chunks(extracted_data=documents)
#print("Length of Text Chunks: ", len(text_chunks))

# Step 3: Create Vector Embeddings 

def get_embedding_model():
    embedding_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embedding_model

embedding_model=get_embedding_model()

# Step 4: Store embeddings in FAISS
DB_FAISS_PATH="vectorstore/db_faiss"
db=FAISS.from_documents(text_chunks, embedding_model)
db.save_local(DB_FAISS_PATH)