from pathlib import Path
from app.celery_app import celery_app
from app.directus_client import get_one, get_all
from app import globals as woprvar
from app.logging import logger
from app.lib.safe_file import SafeFS
from app.lib.safe_file import NotFoundError, ExistsError  # ADD THIS IMPORT

# Archive
# Files in incoming
# Files in labelstudio
# Copy to labelstudio

@celery_app.task(name="archive_session")
def archive_session(session_id: str) -> dict[str, list[dict[str, str]]]:  # CHANGED RETURN TYPE
    """Archive a session by moving its files to the archive directory."""
    logger.info(f"Archiving session {session_id}")
    
    session_data = get_one("sessions", session_id)
    if not session_data:
        logger.error(f"Session {session_id} not found")
        raise ValueError(f"Session {session_id} not found")
    session_uuid = session_data.get("uuid")
    if not session_uuid:
        logger.error(f"Session {session_id} has no UUID")
        raise ValueError(f"Session {session_id} has no UUID")

    logger.info(f"Session UUID: {session_uuid}")

    try:
        base_path = Path(woprvar.WOPR_CONFIG['storage']['base_path']).resolve()
        archive_base_path = (base_path /woprvar.WOPR_CONFIG['storage']['archive_subdir']).resolve()
        archive_path = ( archive_base_path / session_uuid ).resolve()
        incoming_path = (base_path / woprvar.WOPR_CONFIG['storage']['incoming_subdir']).resolve()
    except KeyError as e:
        logger.error(f"Missing required storage config key: {e}")
        raise ValueError(f"Invalid storage configuration: {e}")

    session_plays = get_all("plays", filters={"session_id": {"_eq": session_id}})
    if not session_plays:
        logger.error(f"No plays found for session {session_id}")
        raise ValueError(f"No plays found for session {session_id}")
    
    files_to_archive = []
    for play in session_plays:
        filename = play.get("filename")
        if not filename:
            logger.warning(f"Play record missing filename, skipping: {play}")
            continue
        files_to_archive.append(filename)

    if not files_to_archive:
        logger.error(f"No valid filenames found in plays for session {session_id}")
        raise ValueError(f"No valid filenames found in plays for session {session_id}")
    logger.info(f"Files to archive: {files_to_archive}")

    filesafe = SafeFS(base_dir=str(base_path), forbid_symlinks=True)

    try:
        # Create archive directory if it doesn't exist
        logger.info(f"Creating archive directory at {archive_path}")
        filesafe.mkdir(str(archive_path.relative_to(base_path)), exist_ok=True)  # CHANGED
    except Exception as e:
        logger.error(f"Failed to create archive directory {archive_path}: {e}")
        raise

    # CHANGED: Per-file error handling for best-effort archiving
    results = []
    failures = []
    for filename in files_to_archive:
        src_path = incoming_path / filename
        dst_path = archive_path / filename
        
        try:
            logger.info(f"Archiving file {src_path} to {dst_path}")
            how = filesafe.move(
                str(src_path.relative_to(base_path)), 
                str(dst_path.relative_to(base_path))
            )
            results.append({
                "filename": filename,
                "source": str(src_path),
                "destination": str(dst_path),
                "method": str(how)
            })
        except NotFoundError:
            logger.warning(f"Source file not found, skipping: {filename}")
            failures.append({"filename": filename, "error": "source not found"})
        except ExistsError:
            logger.warning(f"Destination already exists, skipping: {filename}")
            failures.append({"filename": filename, "error": "destination exists"})
        except Exception as e:
            logger.error(f"Failed to archive {filename}: {e}")
            logger.exception(e)
            failures.append({"filename": filename, "error": str(e)})
    
    # CHANGED: Summary logging and return structure
    if failures:
        logger.warning(
            f"Session {session_id} partial archive: "
            f"{len(results)} succeeded, {len(failures)} failed"
        )
    else:
        logger.info(f"Session {session_id} archived {len(results)} files successfully.")
    
    logger.debug(f"Archive results: {results}")
    if failures:
        logger.debug(f"Archive failures: {failures}")
    
    return {"archived": results, "failed": failures}