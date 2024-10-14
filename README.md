# PDF Processing Pipeline

This repository contains a custom PDF processing pipeline designed to process multiple PDF documents, extract keywords, generate summaries, and store the results in a MongoDB database. The solution is designed for concurrency and high performance using Python, `ThreadPoolExecutor`, and custom logging functionality. Docker is used to containerize the application for easy deployment and environment consistency.

## Features

- **Text Extraction:** Extracts raw text from PDF documents using `PyPDF2`.
- **Keyword Extraction:** Uses Term Frequency-Inverse Document Frequency (TF-IDF) to extract relevant keywords from each PDF.
- **Summarization:** A basic TextRank-based summarizer generates concise summaries of the documents.
- **Metadata Generation:** Extracts and stores metadata such as file name, file size, and upload time for each PDF.
- **MongoDB Storage:** Stores the extracted text, keywords, summary, and metadata in a MongoDB collection.
- **Concurrency:** Efficiently processes multiple PDFs concurrently using Python's `ThreadPoolExecutor`.
- **Error Handling and Logging:** Includes detailed logging at every stage, including error tracking with stack traces.
- **Docker Integration:** Fully containerized for easy deployment, with optional Docker Compose setup for running the pipeline alongside MongoDB.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Functions](#functions)
4. [Docker Integration](#docker-integration)
5. [Project Structure](#project-structure)

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/Mihir-M112/wasserstoff-AI-Intern-Task.git
   cd wasserstoff-AI-Intern-Task
   ```


2. **Install the required packages:**  
Create a virtual environment (optional but recommended) and install the required packages:
   ```
   python3 -m venv venv
   ./venv/bin/activate # Mac OS: source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Setup MongoDB:**  

- Make sure MongoDB is running locally or in the cloud.
- Update the `MONGO_URI` in your code or use environment variables to pass the MongoDB connection string.

4. **Run the pipeline:**  
   Run the pipeline using the following command:
   ```
   python main.py
   ```

## Usage

The pipeline is designed to process multiple PDF documents concurrently.

The Pipeline will:
- Clear the MongoDB collection if already exits and create a new one.
- Extract text, keywords, and summary from each PDF file.
- Insert the processed data into the MongoDB collection.

### Folder Path
Specify the folder path containing the PDF files to be processed in the `main.py` file:
```
folder_path = "Datasets"
```

## Functions
`extract_pdf_text(pdf_path)`:
- **Purpose:** Extracts text from a PDF file using `PyPDF2`
- **Input:** pdf_path (string) – path to the PDF file.
- **Output:** Extracted text as a string.

`clean_and_tokenize(text)`:
- **Purpose:** Cleans and tokenizes the text data (removes punctuation, numbers, converts to lowercase).
- **Input:** text (string) – raw text extracted from the PDF.
- **Output:** List of cleaned and tokenized words.

`calculate_tf(word_list)`:
- **Purpose:** Calculates the Term Frequency (TF) of each word in the document.
- **Input:** word_list (list) – list of cleaned and tokenized words.
- **Output:** Dictionary containing the term frequency of each word.

`calculate_idf(documents)`:
- **Purpose:** Calculates the Inverse Document Frequency (IDF) of each word in the corpus.
- **Input:** documents (list) – list of documents, where each document is a list of words.
- **Output:** Dictionary containing the inverse document frequency of each word (A dictionary with words as keys and their IDF scores as values.)

`extract_keywords_tfidf(text, all_docs, top_n=10)`:
- **Purpose:** Extracts keywords from a document using TF-IDF.
- **Input:**
  - text (string) – raw text extracted from the PDF.
  - all_docs (list) – list of all documents in the corpus.
  - top_n (int) – number of top keywords to extract (default: 10).
- **Output:** List of top keywords extracted from the document.

`textrank_summarize(text, top_n=5)`:
- **Purpose:** Generates a summary of the text using TextRank algorithm.
- **Input:**
  - text (string) – raw text extracted from the PDF.
  - top_n (int) – number of sentences in the summary (default: 5).
- **Output:** Summary of the text as a string.

`generate_pdf_metadata(pdf_path)`:
- **Purpose:** Generates metadata for a PDF file.
- **Input:** pdf_path (string) – path to the PDF file.
- **Output:** Dictionary containing metadata such as file name, file size, and upload time.

`process_pdf(pdf_path, all_docs, top_n=10)`:
- **Purpose:** Processes a PDF file, extracts text, keywords, summary, and metadata.
- **Input:**
  - pdf_path (string) – path to the PDF file.
  - all_docs (list) – list of all documents in the corpus.
  - top_n (int) – number of top keywords to extract (default: 10).
- **Output:** Dictionary containing the processed data and result stored in MongoDB in the form of JSON.

`process_pdfs_concurrently(pdf_files, all_docs)`:
- **Purpose:** Processes multiple PDF files concurrently using ThreadPoolExecutor.
- **Input:**
  - pdf_files (list) – list of paths to the PDF files.
  - all_docs (list) – list of all documents in the corpus.
- **Output:** None (Results are stored in MongoDB).

`run_pipeline(folder_path)`:
- **Purpose:** Main function to run the PDF processing pipeline.
- **Input:** folder_path (string) – path to the folder containing the PDF files.
- **Output:** None (Results are stored in MongoDB).

## Docker Integration

The application can be containerized using Docker for easy deployment and environment consistency.

1. **Build the Docker image:**
   ```
   docker build -t pdf-pipeline .
   ```
2. **Run the Docker container:**
   ```
    docker run -e MONGO_URI="<your_mongo_uri>" pdf_processor

    ```
3. **Run the Docker container with MongoDB using Docker Compose:**
    ```
    docker-compose up
    ```
  
This will start the PDF processing pipeline and a MongoDB container. The pipeline will automatically connect to the MongoDB container to store the results.


## Project Structure

The project is structured as follows:

```
PDF-Processing-Pipeline/ 
├──   Datasets/
    ├──  sample1.pdf
    ├──   sample2.pdf
    ├──   ...
├── logs/
    ├──  pipeline.log
├──   pdf_pipeline/   
    ├──   __init__.py
    ├──   pdf_processor.py
    ├──  data_ingestion.py
├──   venv/
    ├──      ...
├──   dataset.json
├──   README.md
├──   main.py
├──  requirements.txt
├──   Dockerfile
├──  docker-compose.yml
├──   .gitignore
├──   .env
```
Video Link: https://drive.google.com/drive/folders/1Oajs4TUStoxm7m8UPckRWMTo_ZV6xZov?usp=drive_link