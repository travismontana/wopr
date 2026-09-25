from lib.helpers import get_config, setup_logger

logger = setup_logger()
config = get_config


def open_camera(host, port):
    logger.info(f"Opening camera at {host}:{port}")
    return MJPEGStream(host, port)


class MJPEGStream:
    # temp
    pass
