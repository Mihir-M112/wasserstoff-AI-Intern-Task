import os
import time
import logging
from pymongo import MongoClient
from PyPDF2 import PdfReader
import concurrent.futures
import hashlib
import spacy
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

# Configure MongoDB Atlas (replace with your URI)
MONGO_URI = "mongodb+srv://mihirm1211:sHIshjSyibuFNoFf@pdf-processor.drvde.mongodb.net/?retryWrites=true&w=majority&appName=pdf-processor"
client = MongoClient(MONGO_URI)
db = client['PDFStorageDB']
collection = db['pdf_documents']

# Function to clear the MongoDB collection
def clear_mongodb_collection():
    try:
        result = collection.delete_many({})
        logging.info(f"Cleared {result.deleted_count} documents from MongoDB.")
    except Exception as e:
        logging.error(f"Error clearing MongoDB collection: {e}")
# Load spaCy's small English model for NER 
nlp = spacy.load('en_core_web_sm')

# Initialize HuggingFace's summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Logging setup
logging.basicConfig(filename="logs/pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Function to calculate file size in MB
def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    return round(size_bytes / (1024 * 1024), 2)  # Return size in MB


# Function to generate unique document ID using a hash
def generate_doc_id(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()


# Function to extract PDF metadata
def extract_pdf_metadata(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        num_pages = len(reader.pages)
        file_size = get_file_size(pdf_file)
        metadata = {
            "document_name": os.path.basename(pdf_file),
            "file_path": pdf_file,
            "file_size_MB": file_size,
            "num_pages": num_pages,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "summary": None,
            "keywords": None,
        }
        return metadata, num_pages
    except Exception as e:
        logging.error(f"Error reading PDF {pdf_file}: {e}")
        return None, 0

# Ensure NLTK's tokenizer is ready
nltk.download('punkt')

def extract_summary_from_pdf(text, keywords):
    try:
        sentences = sent_tokenize(text)
        summary_sentences = [sentence for sentence in sentences if any(keyword in sentence for keyword in keywords)]
        
        # If no sentences match keywords, fall back to first few sentences
        if not summary_sentences:
            summary_sentences = sentences[:3]
        
        summary_text = " ".join(summary_sentences)
        return summary_text if summary_text else "Summary not available."
    except Exception as e:
        logging.error(f"Error summarizing text: {e}")
        return "Summary not available."


# Function to extract keywords using NER with spaCy
def extract_keywords_from_text(text):
    try:
        doc = nlp(text)
        keywords = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "GPE", "LOC", "PRODUCT"]]
        return list(set(keywords))  # Remove duplicates
    except Exception as e:
        logging.error(f"Error extracting keywords: {e}")
        return []


# Function to extract text from PDF pages
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_file}: {e}")
        return ""


# Function to classify and process PDF based on its length

def classify_and_process_pdf(pdf_file, doc_id):
    metadata, num_pages = extract_pdf_metadata(pdf_file)
    if not metadata:
        return

    if num_pages <= 10:
        category = "Short PDF"
    elif num_pages <= 30:
        category = "Medium PDF"
    else:
        category = "Long PDF"

    logging.info(f"Processing {pdf_file} as {category} with {num_pages} pages.")

    # Extract text from PDF
    text = extract_text_from_pdf(pdf_file)
    
    if not text:
        logging.error(f"No text extracted from {pdf_file}. Skipping summarization and keyword extraction.")
        return

    # Perform keyword extraction using NER
    keywords = extract_keywords_from_text(text)

    # Perform summarization using NLP
    summary = extract_summary_from_pdf(text, keywords)  # Pass keywords here

    # Update MongoDB with summary and keywords
    update_mongo_with_summary(doc_id, summary, keywords)



# Update MongoDB document with summary and keywords
def update_mongo_with_summary(doc_id, summary, keywords):
    try:
        result = collection.update_one(
            {"_id": doc_id},
            {"$set": {"summary": summary, "keywords": keywords, "processed_at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}}
        )
        if result.matched_count > 0:
            logging.info(f"Document {doc_id} updated with summary and keywords.")
        else:
            logging.warning(f"Document {doc_id} not found for update.")
    except Exception as e:
        logging.error(f"Error updating MongoDB document {doc_id}: {e}")


# Function to process multiple PDFs concurrently
def process_pdfs_concurrently(pdf_files):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_pdf = {executor.submit(classify_and_process_pdf, pdf_file, generate_doc_id(pdf_file)): pdf_file for pdf_file in pdf_files}
        for future in concurrent.futures.as_completed(future_to_pdf):
            pdf_file = future_to_pdf[future]
            try:
                future.result()  # Check if the thread raised any exceptions
            except Exception as e:
                logging.error(f"Error processing {pdf_file}: {e}")


def ingest_pdfs_from_folder(folder_path):
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    return pdf_files


# Main pipeline function
def run_pipeline(folder_path):
    logging.info("Pipeline started.")
    
     # Step 0: Clear MongoDB collection before starting the pipeline
    clear_mongodb_collection()

    # Step 1: Ingest PDFs from folder
    pdf_files = ingest_pdfs_from_folder(folder_path)
    
    if not pdf_files:
        logging.warning("No PDFs found in the folder.")
        return

    # Step 2: Process PDFs concurrently
    process_pdfs_concurrently(pdf_files)

    logging.info("Pipeline completed.")


if __name__ == "__main__":
    folder_path = "Datasets"
    run_pipeline(folder_path)
