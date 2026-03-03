from lib.helpers import setup_logger, get_config

logger = setup_logger()
config = get_config

def open_camera(host,port):
    logger.info(f"Opening camera at {host}:{port}")
    return MJPEGStream(host,port)

class MJPEGStream:
    # temp
    pass