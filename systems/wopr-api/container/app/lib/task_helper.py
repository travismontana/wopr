from typing import Any, Optional, Dict
from celery.result import AsyncResult
from app.celery_app import celery_app

def queue_task(task_func, *args, **kwargs) -> Dict[str, Any]:
    """
    Queue a Celery task for async execution.
    
    Args:
        task_func: The Celery task function to execute
        *args: Positional arguments for the task
        **kwargs: Keyword arguments for the task
    
    Returns:
        Dict with task_id and status
    """
    try:
        task = task_func.delay(*args, **kwargs)
        logger.info(f"Queued task {task_func.name} with ID {task.id}")
        
        return {
            "task_id": task.id,
            "task_name": task_func.name,
            "status": "queued"
        }
    except Exception as e:
        logger.error(f"Failed to queue task {task_func.name}: {e}")
        raise


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Check the status of a queued task.
    
    Returns:
        Dict with status, result/error, and metadata
    """
    task = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "state": task.state,
        "status": task.state.lower()
    }
    
    if task.state == "PENDING":
        # Task hasn't started or doesn't exist
        response["info"] = "Task not found or not yet started"
        
    elif task.state == "FAILURE":
        # Task failed
        response["error"] = str(task.info)
        response["traceback"] = task.traceback if hasattr(task, 'traceback') else None
        
    elif task.state == "SUCCESS":
        # Task completed
        response["result"] = task.result
        response["completed_at"] = task.date_done
        
    else:
        # STARTED, RETRY, etc.
        response["info"] = task.info if task.info else f"Task is {task.state}"
    
    return response


def revoke_task(task_id: str, terminate: bool = False) -> Dict[str, Any]:
    """
    Cancel a running or queued task.
    
    Args:
        task_id: The task ID to revoke
        terminate: If True, send SIGTERM to worker process (use with caution)
    
    Returns:
        Dict with revocation status
    """
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        logger.info(f"Revoked task {task_id} (terminate={terminate})")
        
        return {
            "task_id": task_id,
            "status": "revoked",
            "terminated": terminate
        }
    except Exception as e:
        logger.error(f"Failed to revoke task {task_id}: {e}")
        raise


def wait_for_task(task_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
    """
    Block until task completes (or timeout).
    
    Args:
        task_id: The task ID to wait for
        timeout: Max seconds to wait (None = infinite)
    
    Returns:
        Dict with final status and result
        
    Note: Defeats async purpose. Use sparingly.
    """
    task = AsyncResult(task_id, app=celery_app)
    
    try:
        result = task.get(timeout=timeout)
        return {
            "task_id": task_id,
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e)
        }


def get_task_info(task_id: str) -> Dict[str, Any]:
    """
    Get detailed task metadata.
    
    Returns:
        Dict with task name, args, kwargs, etc.
    """
    task = AsyncResult(task_id, app=celery_app)
    
    info = {
        "task_id": task_id,
        "state": task.state,
        "name": task.name,
    }
    
    # Some backends provide more detail
    if hasattr(task, 'args'):
        info["args"] = task.args
    if hasattr(task, 'kwargs'):
        info["kwargs"] = task.kwargs
    if task.date_done:
        info["completed_at"] = task.date_done
        
    return info