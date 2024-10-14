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
   git clone https://github.com/Mihir-M112/wasserstoff-AI-Intern-Task
   ```
   cd wasserstoff-AI-Intern-Task
