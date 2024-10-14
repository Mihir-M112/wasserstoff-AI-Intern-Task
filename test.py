import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import PyPDF2
import string
import re
from pymongo import MongoClient
from datetime import datetime
from math import log
import traceback
import multiprocessing


# Configure MongoDB Atlas (replace with your URI)
MONGO_URI = "mongodb+srv://mihirm1211:sHIshjSyibuFNoFf@pdf-processor.drvde.mongodb.net/?retryWrites=true&w=majority&appName=pdf-processor"
client = MongoClient(MONGO_URI)
db = client['PDFStorageDB']
collection = db['pdf_documents']


# Set up logging: both console and file handlers
def setup_logging(log_file='logs/pipeline.log'):
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),      # Log to file
            logging.StreamHandler()             # Log to console (terminal)
        ]
    )

# Call setup_logging() to initialize logging in both file and console
setup_logging()


# Function to clear the MongoDB collection before starting the pipeline
def clear_mongo_collection():
    try:
        collection.drop()  # Drop the collection to clear it
        logging.info("MongoDB collection cleared.")
    except Exception as e:
        logging.error(f"Failed to clear MongoDB collection: {e}")
        logging.error(traceback.format_exc())


# Function to extract text from a PDF
def extract_pdf_text(pdf_path):
    logging.info(f"Extracting text from {pdf_path}")
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return None


# Function to clean and tokenize text
def clean_and_tokenize(text):
    text = text.lower()  # convert to lowercase
    text = re.sub(r'\d+', '', text)  # remove numbers
    text = text.translate(str.maketrans('', '', string.punctuation))  # remove punctuation
    words = text.split()
    return words

# Function to calculate Term Frequency (TF)
def calculate_tf(word_list):
    word_freq = Counter(word_list)
    total_words = len(word_list)
    tf_scores = {word: freq / total_words for word, freq in word_freq.items()}
    return tf_scores

# Function to calculate Inverse Document Frequency (IDF)
def calculate_idf(documents):
    num_documents = len(documents)
    idf_scores = {}
    all_tokens_set = set([word for doc in documents for word in set(doc)])
    
    for word in all_tokens_set:
        containing_docs = sum(1 for doc in documents if word in doc)
        idf_scores[word] = log(num_documents / (1 + containing_docs))  # Adding 1 to avoid division by zero
    return idf_scores

# Function to calculate TF-IDF and extract keywords
def extract_keywords_tfidf(text, all_docs, top_n=10):
    logging.info("Extracting keywords using TF-IDF")
    
    # Clean and tokenize the text
    words = clean_and_tokenize(text)
    
    # Step 1: Calculate TF (Term Frequency)
    tf_scores = calculate_tf(words)
    
    # Step 2: Calculate IDF (Inverse Document Frequency) across all documents
    all_docs_cleaned = [clean_and_tokenize(doc) for doc in all_docs]
    idf_scores = calculate_idf(all_docs_cleaned)
    
    # Step 3: Calculate TF-IDF
    tf_idf_scores = {word: tf_scores[word] * idf_scores.get(word, 0) for word in words}
    
    # Step 4: Sort words by TF-IDF score
    sorted_keywords = sorted(tf_idf_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top N keywords
    return [word for word, score in sorted_keywords[:top_n] if len(word) > 2 and word.isalpha()]  # Filter out short/common words


# Custom sentence tokenizer
def sentence_tokenize(text):
    # Splitting text into sentences based on punctuation marks
    return re.split(r'(?<=[.!?]) +', text)

# TextRank-based summarizer (simple version)
def textrank_summarize(text, top_n=5):
    logging.info("Summarizing text using TextRank")
    sentences = sentence_tokenize(text)
    clean_sentences = [' '.join(clean_and_tokenize(s)) for s in sentences]

    # Simple ranking by sentence length (for demo purposes)
    ranked_sentences = sorted(clean_sentences, key=len, reverse=True)
    summary = ' '.join(ranked_sentences[:top_n])
    return summary

# Function to generate PDF metadata
def generate_pdf_metadata(pdf_path):
    logging.info(f"Generating metadata for {pdf_path}")
    metadata = {
        'file_name': os.path.basename(pdf_path),
        'file_size': os.path.getsize(pdf_path),
        'upload_time': datetime.utcnow()
    }
    return metadata


# Function to process a single PDF and store results in MongoDB
def process_pdf(pdf_path, all_docs, top_n=10):
    try:
        logging.info(f"Processing {pdf_path}")
        
        # Extract the text from the PDF
        text = extract_pdf_text(pdf_path)
        
        if text:
            # Extract keywords using the improved TF-IDF method
            keywords = extract_keywords_tfidf(text, all_docs, top_n)
            
            # Summarize the document using the TextRank method
            summary = textrank_summarize(text, top_n)
            
            # Generate metadata for the PDF
            metadata = generate_pdf_metadata(pdf_path)
            
            # Prepare the document for MongoDB insertion
            document = {
                'metadata': metadata,
                'summary': summary,
                'keywords': keywords,
                'content': text
            }
            
            # Insert the document into MongoDB
            collection.insert_one(document)
            logging.info(f"Inserted data for {pdf_path} into MongoDB")
        
        else:
            logging.warning(f"Failed to extract text from {pdf_path}")
    
    except Exception as e:
        # Log the exception with a detailed traceback
        logging.error(f"Error processing {pdf_path}: {e}")
        logging.error(traceback.format_exc())  # Logs the detailed stack trace



# Function to process PDFs concurrently
def process_pdfs_concurrently(pdf_files, all_docs):
    logging.info("Starting concurrent processing of PDFs.")
    
    try:
        # Calculate max_workers based on the number of PDFs or CPU cores
        max_workers = min(len(pdf_files), multiprocessing.cpu_count())
        logging.info(f"Using {max_workers} workers for PDF processing.")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda pdf_file: process_pdf(pdf_file, all_docs), pdf_files)
    
    except Exception as e:
        logging.error(f"Error during concurrent processing: {e}")
        logging.error(traceback.format_exc())


# Function to ingest PDFs from a folder
def ingest_pdfs_from_folder(folder_path):
    logging.info(f"Ingesting PDFs from {folder_path}")
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    if not pdf_files:
        logging.warning("No PDF files found in the folder")
    return pdf_files

# Main pipeline function
def run_pipeline(folder_path):
    logging.info("Pipeline started.")
    
    # Clear MongoDB collection
    clear_mongo_collection()
    
    # Ingest PDFs from folder
    pdf_files = ingest_pdfs_from_folder(folder_path)
    
    if not pdf_files:
        logging.warning("No PDFs found in the folder.")
        return

    # Extract text from all PDFs for keyword extraction
    all_docs = [extract_pdf_text(pdf_file) for pdf_file in pdf_files]

    # Process PDFs concurrently
    try:
        process_pdfs_concurrently(pdf_files, all_docs)
    except Exception as e:
        logging.error(f"Error during PDF processing: {e}")
        logging.error(traceback.format_exc())
    
    logging.info("Pipeline completed.")




if __name__ == "__main__":
    folder_path = "Datasets"
    run_pipeline(folder_path)
