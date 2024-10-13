import os
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
import concurrent.futures
from PyPDF2 import PdfReader
import threading

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Create 'Datasets' folder if it doesn't exist
folder_path = "Datasets"
os.makedirs(folder_path, exist_ok=True)

# Step 1: Download PDFs from URLs if needed, and process them as soon as they are downloaded
def download_and_process_pdfs_from_json():
    with open("dataset.json", "r") as data:
        pdf_dict = json.load(data)

    # Function to download a PDF and immediately start processing it
    def download_and_process_pdf(key, url):
        file_name = os.path.join(folder_path, f"{key}.pdf")
        try:
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {file_name}")
                
                # Once the file is downloaded, immediately start processing
                process_pdf(file_name)
            else:
                print(f"Failed to download {file_name}. HTTP Status Code: {response.status_code}")
        except requests.exceptions.SSLError as e:
            print(f"SSL error while downloading {file_name}: {e}")
        except Exception as e:
            print(f"Error occurred while downloading {file_name}: {e}")

    # Use ThreadPoolExecutor to download PDFs concurrently and process them immediately
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_and_process_pdf, key, url) for key, url in pdf_dict.items()]
        concurrent.futures.wait(futures)

    print("All PDFs have been downloaded and processed.")

# Step 2: Ingest PDFs from a Folder
def ingest_pdfs_from_folder(folder_path):
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    return pdf_files

# Step 3: Process Each PDF (Short, Medium, Long PDFs)
def process_pdf(pdf_file):
    try:
        # Read the PDF
        reader = PdfReader(pdf_file)
        num_pages = len(reader.pages)

        # Classify PDF size based on number of pages
        if num_pages <= 10:
            category = "Short PDF"
        elif num_pages <= 30:
            category = "Medium PDF"
        else:
            category = "Long PDF"

        print(f"Processing '{os.path.basename(pdf_file)}' as {category} with {num_pages} pages.")
        # Implement further PDF processing logic here as needed.
    
    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

# Main function to run the pipeline
def run_pipeline():
    # Download PDFs and process them concurrently as they are downloaded
    if os.path.exists("dataset.json"):
        download_and_process_pdfs_from_json()

    # Ingest any remaining PDFs in the folder (if there are any already existing)
    print("\nIngesting any remaining PDFs from the folder...")
    pdf_files = ingest_pdfs_from_folder(folder_path)
    
    if pdf_files:
        print("\nProcessing remaining PDFs concurrently...")
        # Process any unprocessed PDFs concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_pdf, pdf_file) for pdf_file in pdf_files]
            concurrent.futures.wait(futures)
    else:
        print("No PDFs found in the folder.")

if __name__ == "__main__":
    run_pipeline()
