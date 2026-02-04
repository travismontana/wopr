from lib.helpers import setup_logger, get_config

logger = setup_logger()
config = get_config()

def get_images_ondisk(image_dir: str) -> list:
    """
    list out the files on disk
    select from the available directories:
    - images/incoming
    - images/processed
    """
    
    results = []
    debug_vars = []
    logger.info("Starting get_images_ondisk()")
    logger.debug(f"Debug vars: {debug_vars}")
    
    
