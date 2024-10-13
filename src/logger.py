import logging

# Logging setup
def setup_logging():
    logging.basicConfig(filename="logs/pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
