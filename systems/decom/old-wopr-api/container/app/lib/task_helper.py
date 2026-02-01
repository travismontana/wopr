from typing import Any, Optional, Dict
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.logging import configure_logging
logger = configure_logging("wopr-api")

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

def get_all_tasks(filter_state: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all tasks from Celery workers across different states.
    
    Args:
        filter_state: Optional filter (active, scheduled, reserved, registered)
    
    Returns:
        Dict with tasks grouped by worker and state
        
    Note:
        Only sees tasks known to currently running workers.
        Completed tasks may not appear unless result backend stores them.
        
    Limitations:
        The inspect API queries all workers synchronously.
        Performance degrades with many workers.
    """
    try:
        from celery import current_app
        
        inspect = current_app.control.inspect()
        
        # Gather different task states
        tasks = {
            "active": inspect.active() or {},       # Currently executing
            "scheduled": inspect.scheduled() or {}, # Waiting for ETA
            "reserved": inspect.reserved() or {},   # Claimed by worker, not started
            "registered": inspect.registered() or {} # All known task types
        }
        
        # If filter requested, return only that state
        if filter_state and filter_state in tasks:
            logger.info(f"Retrieved {filter_state} tasks from Celery workers")
            return {filter_state: tasks[filter_state]}
        
        # Otherwise return everything
        total_count = sum(len(worker_tasks) if isinstance(worker_tasks, dict) 
                         else 0 for worker_tasks in tasks.values())
        logger.info(f"Retrieved all task states from Celery workers (total workers: {total_count})")
        return tasks
        
    except Exception as e:
        logger.error(f"Failed to retrieve tasks from Celery workers: {e}")
        raise


def get_all_active_tasks() -> list:
    """
    Flatten all active/scheduled/reserved tasks into a simple list.
    
    Returns:
        List of dicts with task_id, name, state, worker, args, kwargs
        
    States included:
        - ACTIVE: Currently executing
        - SCHEDULED: Queued with future ETA
        - RESERVED: Acknowledged by worker, not yet started
        
    Note:
        Does not include PENDING tasks (not yet sent to broker)
        or completed tasks (SUCCESS/FAILURE/REVOKED).
    """
    try:
        from celery import current_app
        
        inspect = current_app.control.inspect()
        all_tasks = []
        
        # Get active tasks (currently executing)
        active = inspect.active() or {}
        for worker, tasks in active.items():
            for task in tasks:
                all_tasks.append({
                    "task_id": task.get("id"),
                    "name": task.get("name"),
                    "state": "ACTIVE",
                    "worker": worker,
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {})
                })
        
        # Get scheduled tasks (waiting for ETA)
        scheduled = inspect.scheduled() or {}
        for worker, tasks in scheduled.items():
            for task in tasks:
                all_tasks.append({
                    "task_id": task.get("id"),
                    "name": task.get("name"),
                    "state": "SCHEDULED",
                    "worker": worker,
                    "eta": task.get("eta"),
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {})
                })
        
        # Get reserved tasks (acknowledged but not started)
        reserved = inspect.reserved() or {}
        for worker, tasks in reserved.items():
            for task in tasks:
                all_tasks.append({
                    "task_id": task.get("id"),
                    "name": task.get("name"),
                    "state": "RESERVED",
                    "worker": worker,
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {})
                })
        
        logger.info(f"Retrieved {len(all_tasks)} active tasks from Celery workers")
        return all_tasks
        
    except Exception as e:
        logger.error(f"Failed to retrieve active tasks from Celery workers: {e}")
        raise