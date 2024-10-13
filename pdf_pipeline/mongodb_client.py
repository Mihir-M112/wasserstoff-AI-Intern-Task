from pymongo import MongoClient
import logging
import time

# Configure MongoDB Atlas (replace with your URI)
MONGO_URI = "mongodb+srv://mihirm1211:sHIshjSyibuFNoFf@pdf-processor.drvde.mongodb.net/?retryWrites=true&w=majority&appName=pdf-processor"
client = MongoClient(MONGO_URI)
db = client['PDFStorageDB']
collection = db['pdf_documents']

# Function to insert metadata into MongoDB
def insert_metadata(doc_id, metadata):
    try:
        collection.insert_one({"_id": doc_id, **metadata})
    except Exception as e:
        logging.error(f"Error inserting metadata into MongoDB: {e}")

# Function to update MongoDB document with summary and keywords
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
