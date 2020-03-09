import logging

# Create a custom logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s')
log = logging.getLogger()
