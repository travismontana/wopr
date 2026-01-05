import logging
import sys

def configure_logging(logfile: str, level=logging.DEBUG):
    logging.basicConfig(
        filename=logfile,
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    root = logging.getLogger()
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(logging.StreamHandler(sys.stdout))
