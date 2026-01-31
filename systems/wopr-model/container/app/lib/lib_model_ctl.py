import ultralytics
from pathlib import Path
import lib.globals as globals
from lib.helpers import logit, setup_logger, check_for_file_in_dir

from lib.safe_file import SafeFS

def initialize_model(model: dict) -> dict:
    """Initialize Model
    Check if the model file exists in distfiles_path.
    If not, check downloads_path.
    If not there, download using ultralytics.

    Args:
        model_name (str): Name of the model to initialize.
    """
    
    paths = globals.storage_paths
    
    protected_path = SafeFS(Path(paths["models_path"]))
    
    filename = f"{model['name']}.pt"

    distfile_results = check_for_file_in_dir(filename, paths["models_distfiles_path"], protected_path)
    
    if ! distfile_results:
        
        downloadfile_results = check_for_file_in_dir(filename, paths["downloads_path"], protected_path)
        
        if ! downloadfile_results:
            results = download_model_file(model)
