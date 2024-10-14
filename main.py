# For data ingestion run this command

# from pdf_pipeline.data_ingestions import run_pipeline
# run_pipeline()

from pdf_pipeline.pdf_processor import run_pipeline

run_pipeline("Datasets")