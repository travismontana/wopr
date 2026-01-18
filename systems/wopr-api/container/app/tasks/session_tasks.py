"""
Session file archiving and status checking tasks.

Provides Celery tasks for managing WOPR session image files across different
storage locations (incoming, archive, label studio).
"""

from pathlib import Path

from app import globals as woprvar
from app.celery_app import celery_app
from app.directus_client import get_all, get_one
from app.lib.safe_file import ExistsError, NotFoundError, SafeFS
from app.logging import configure_logging


logger = configure_logging(woprvar.LOGFILE)


def _get_session_data(session_id: str) -> tuple[dict, str]:
    """
    Fetch and validate session data from Directus.

    Args:
        session_id: The session ID to fetch

    Returns:
        Tuple of (session_data dict, session_uuid string)

    Raises:
        ValueError: If session not found or has no UUID
    """
    logger.info(f"=== _get_session_data START === session_id={session_id}")
    
    session_data = get_one("sessiontracker", session_id)
    if not session_data:
        logger.error(f"Session {session_id} not found")
        raise ValueError(f"Session {session_id} not found")

    session_uuid = session_data.get("uuid")
    if not session_uuid:
        logger.error(f"Session {session_id} has no UUID")
        raise ValueError(f"Session {session_id} has no UUID")

    logger.info(f"Session data retrieved: session_id={session_id}, session_uuid={session_uuid}")
    logger.info(f"=== _get_session_data END === session_uuid={session_uuid}")
    return session_data, session_uuid


def _get_session_filenames(session_id: str) -> list[str]:
    """
    Extract filenames from all plays associated with a session.

    Args:
        session_id: The session ID to fetch plays for

    Returns:
        List of filenames from the session's plays

    Raises:
        ValueError: If no plays found or no valid filenames exist
    """
    logger.info(f"=== _get_session_filenames START === session_id={session_id}")
    
    session_plays = get_all("playtracker", filters={"sessionid": {"_eq": session_id}})
    logger.info(f"Retrieved {len(session_plays) if session_plays else 0} play records from playtracker")
    
    if not session_plays:
        logger.error(f"No plays found for session {session_id}")
        raise ValueError(f"No plays found for session {session_id}")

    # Extract filenames, filtering out plays with missing filename field
    filenames = [
        play.get("filename")
        for play in session_plays
        if play.get("filename")
    ]

    # Log warning for any plays missing filenames
    missing_count = len(session_plays) - len(filenames)
    if missing_count > 0:
        logger.warning(
            f"Found {missing_count} play records without filenames for session {session_id}"
        )

    if not filenames:
        logger.error(f"No valid filenames found in plays for session {session_id}")
        raise ValueError(f"No valid filenames found in plays for session {session_id}")

    logger.info(f"=== _get_session_filenames END === session_id={session_id}, filename_count={len(filenames)}, filenames={filenames}")
    return filenames


@celery_app.task(name="archive_session_images")
def archive_session_images(session_id: str) -> dict[str, list[dict[str, str]]]:
    """
    Archive a session by moving its files from incoming to archive directory.

    Files are moved on a best-effort basis - individual file failures don't
    stop the overall archiving process. Results include both successful and
    failed file operations.

    Args:
        session_id: The session ID to archive

    Returns:
        Dict with keys:
            - "archived": List of successfully archived files with metadata
            - "failed": List of files that failed to archive with error info

    Raises:
        ValueError: If session not found, has no UUID, or has no valid files
    """
    logger.info(f"=== archive_session_images START === session_id={session_id}")

    # Fetch and validate session
    session_data, session_uuid = _get_session_data(session_id)

    # Get storage paths from globals
    base_path = woprvar.storage_paths["base_path"]
    archive_base_path = woprvar.storage_paths["archive_base_path"]
    incoming_path = woprvar.storage_paths["incoming_path"]
    archive_path = (archive_base_path / session_uuid).resolve()

    logger.info(f"Paths: base_path={base_path}, archive_base_path={archive_base_path}, incoming_path={incoming_path}, archive_path={archive_path}")

    # Get list of files to archive
    files_to_archive = _get_session_filenames(session_id)
    logger.info(f"Files to archive: count={len(files_to_archive)}, files={files_to_archive}")

    # Initialize SafeFS wrapper
    filesafe = SafeFS(base_dir=base_path, forbid_symlinks=True)
    logger.info(f"SafeFS initialized with base_dir={base_path}, forbid_symlinks=True")

    # Create archive directory for this session
    try:
        logger.info(f"Creating archive directory at {archive_path}")
        filesafe.mkdir(str(archive_path.relative_to(base_path)), exist_ok=True)
        logger.info(f"Archive directory created/verified at {archive_path}")
    except (OSError, ValueError, RuntimeError) as e:
        # OSError: permission/disk issues, ValueError: path validation,
        # RuntimeError: SafeFS constraint violations
        logger.error(f"Failed to create archive directory {archive_path}: {e}")
        raise

    # Archive files with per-file error handling for best-effort completion
    results = []
    failures = []
    logger.info(f"Beginning file archiving operations for {len(files_to_archive)} files")

    for filename in files_to_archive:
        src_path = incoming_path / filename
        dst_path = archive_path / filename

        try:
            logger.info(f"Archiving file: src={src_path}, dst={dst_path}")
            how = filesafe.move(
                str(src_path.relative_to(base_path)),
                str(dst_path.relative_to(base_path))
            )
            logger.info(f"File archived successfully: {filename}, method={how}")
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
        except (OSError, ValueError, RuntimeError) as e:
            # Catch specific exceptions that SafeFS.move() might raise
            logger.error(f"Failed to archive {filename}: {e}")
            logger.exception(e)
            failures.append({"filename": filename, "error": str(e)})

    # Log summary of archiving operation
    if failures:
        logger.warning(
            f"Session {session_id} partial archive: "
            f"{len(results)} succeeded, {len(failures)} failed"
        )
        logger.debug(f"Archive failures: {failures}")
    else:
        logger.info(f"Session {session_id} archived {len(results)} files successfully")

    logger.debug(f"Archive results: {results}")
    logger.info(f"=== archive_session_images END === session_id={session_id}, archived_count={len(results)}, failed_count={len(failures)}")

    return {"archived": results, "failed": failures}


@celery_app.task(name="check_session_file_status_task")
def check_session_file_status_task(session_id: str) -> dict[str, list[str]]:
    """
    Check which files for a session are present in various storage locations.

    Checks for file presence in:
        - incoming: Files awaiting processing
        - archive: Files that have been archived
        - label_source: Files staged for labeling (if configured)
        - label_target: Labeled files (if configured)

    Args:
        session_id: The session ID to check

    Returns:
        Dict mapping location names to lists of filenames present there

    Raises:
        ValueError: If session not found, has no UUID, or has no valid files
    """
    logger.info(f"=== check_session_file_status_task START === session_id={session_id}")

    # Fetch and validate session
    session_data, session_uuid = _get_session_data(session_id)

    # Get storage paths from globals
    base_path = woprvar.storage_paths["base_path"]
    archive_base_path = woprvar.storage_paths["archive_base_path"]
    incoming_path = woprvar.storage_paths["incoming_path"]
    archive_path = (archive_base_path / session_uuid).resolve()

    # Build label studio paths if configured
    # These are optional paths that may not be configured yet
    label_subdir = woprvar.storage_paths.get("label_subdir")
    label_source_subdir = woprvar.storage_paths.get("label_source_subdir")
    label_target_subdir = woprvar.storage_paths.get("label_target_subdir")

    # Only construct label paths if all required config exists
    if label_subdir and label_source_subdir and label_target_subdir:
        label_base_path = (archive_base_path / label_subdir).resolve()
        label_source_path = (label_base_path / label_source_subdir).resolve()
        label_target_path = (label_base_path / label_target_subdir).resolve()
        logger.info(f"Paths: base_path={base_path}, archive_base_path={archive_base_path}, incoming_path={incoming_path}, archive_path={archive_path}, label_subdir={label_subdir}, label_source_subdir={label_source_subdir}, label_target_subdir={label_target_subdir}, label_base_path={label_base_path}, label_source_path={label_source_path}, label_target_path={label_target_path}")
        logger.debug("Label studio paths configured and available")
    else:
        # Use None to indicate unconfigured paths
        label_source_path = None
        label_target_path = None
        logger.info(f"Paths: base_path={base_path}, archive_base_path={archive_base_path}, incoming_path={incoming_path}, archive_path={archive_path}, label_subdir={label_subdir}, label_source_subdir={label_source_subdir}, label_target_subdir={label_target_subdir}")
        logger.debug("Label studio paths not fully configured, skipping those checks")

    # Get list of files to check
    files_to_check = _get_session_filenames(session_id)
    logger.info(f"Checking {len(files_to_check)} files across storage locations")

    # Initialize SafeFS wrapper
    filesafe = SafeFS(base_dir=base_path, forbid_symlinks=True)
    logger.info(f"SafeFS initialized with base_dir={base_path}, forbid_symlinks=True")

    # Build location map for iteration
    # Note: Using SafeFS._resolve_rel() internal method as public API doesn't
    # provide a "check if exists" without raising exceptions
    locations = {
        "incoming": incoming_path,
        "archive": archive_path,
        "label_source": label_source_path,
        "label_target": label_target_path
    }

    # Initialize result structure
    presence = {key: [] for key in locations.keys()}
    logger.info(f"Beginning file presence check across {len([k for k, v in locations.items() if v is not None])} configured locations")

    # Check each file's presence in each location
    for filename in files_to_check:
        logger.info(f"Checking presence of file: {filename}")
        for location_key, location_path in locations.items():
            # Skip unconfigured locations
            if location_path is None:
                continue

            file_path = location_path / filename
            logger.debug(f" - Checking in {location_key} at {file_path}")

            try:
                # Check if file exists using SafeFS internal resolution
                # must_exist=False prevents exception on missing files
                resolved = filesafe._resolve_rel(
                    str(file_path.relative_to(base_path)),
                    must_exist=False
                )
                if resolved.exists():
                    presence[location_key].append(filename)
                    logger.info(f"   -> Found in {location_key}")
                else:
                    logger.debug(f"   -> Not found in {location_key}")
            except (ValueError, RuntimeError) as e:
                # Path validation errors from SafeFS
                logger.warning(
                    f"Error checking {filename} in {location_key}: {e}"
                )
                continue

    # Log summary
    summary_parts = [
        f"{key}={len(files)}"
        for key, files in presence.items()
        if files  # Only show locations with files
    ]
    logger.info(
        f"File status for session {session_id}: {', '.join(summary_parts) if summary_parts else 'no files found'}"
    )
    logger.info(f"=== check_session_file_status_task END === session_id={session_id}, presence={presence}")

    return presence

@celery_app.task(name="copy_files_to_label_source")
def copy_files_to_label_source(session_id: str) -> dict[str, list[dict[str, str]]]:
    """
    Copy session files from archive to label studio source directory.

    Files are copied on a best-effort basis - individual file failures don't
    stop the overall copying process. Results include both successful and
    failed file operations.

    files are copied from the incoming directory to the label studio source 
    directory and archive (for backup).

    Args:
        session_id: The session ID to copy files for
    Returns:
        Dict with keys:
            - "success": List of successfully copied files with metadata
            - "failed": List of files that failed to copy with error info
    """
    logger.info(f"=== copy_files_to_label_source START === session_id={session_id}")
    
    # Fetch and validate session
    session_data, session_uuid = _get_session_data(session_id)

    # Get storage paths from globals
    base_path = woprvar.storage_paths["base_path"] 
    incoming_base_path = woprvar.storage_paths["incoming_path"]
    incoming_path = (incoming_base_path ).resolve()
    archive_base_path = woprvar.storage_paths["archive_base_path"]
    archive_path = (archive_base_path / session_uuid).resolve()

    label_base_path = base_path / woprvar.storage_paths.get("label_subdir")
    label_source_subdir = (label_base_path / woprvar.storage_paths.get("label_source_subdir")).resolve()

    logger.info(f"Paths: base_path={base_path}, incoming_base_path={incoming_base_path}, incoming_path={incoming_path}, archive_base_path={archive_base_path}, archive_path={archive_path}, label_subdir={label_subdir}, label_source_subdir={label_source_subdir}")
    
    if not label_subdir or not label_source_subdir:
        logger.error("Label studio paths not fully configured")
        raise ValueError("Label studio paths not fully configured")

    label_base_path = (archive_base_path / label_subdir).resolve()
    label_source_path = (label_base_path / label_source_subdir).resolve()
    logger.info(f"Computed label paths: label_base_path={label_base_path}, label_source_path={label_source_path}")

    # Get list of files to copy
    files_to_copy = _get_session_filenames(session_id)
    logger.info(f"Files to copy: count={len(files_to_copy)}, files={files_to_copy}")

    # Initialize SafeFS wrapper
    filesafe = SafeFS(base_dir=base_path, forbid_symlinks=True)
    logger.info(f"SafeFS initialized with base_dir={base_path}, forbid_symlinks=True")

    # Create label source directory for this session
    try:
        logger.info(f"Creating label source directory at {label_source_path}")
        filesafe.mkdir(str(label_source_path.relative_to(base_path)), exist_ok=True)
        logger.info(f"Label source directory created/verified at {label_source_path}")
    except (OSError, ValueError, RuntimeError) as e:
        logger.error(f"Failed to create label source directory {label_source_path}: {e}")
        raise

    # Copy files with per-file error handling for best-effort completion
    results = []
    failures = []
    logger.info(f"Beginning file copy operations for {len(files_to_copy)} files")

    for filename in files_to_copy:
        src_path = incoming_base_path / filename
        arch_path = archive_path / filename
        dst_path = label_source_path / filename

        try:
            logger.info(f"Copying file to label source: src={src_path}, dst={dst_path}")
            how = filesafe.copy(
                str(src_path.relative_to(base_path)),
                str(dst_path.relative_to(base_path))
            )
            logger.info(f"File copied to label source successfully: {filename}, method={how}")
            results.append({
                "filename": filename,
                "source": str(src_path),
                "destination": str(dst_path),
                "method": str(how)
            })
            
            logger.info(f"Copying file to archive: src={src_path}, dst={arch_path}")
            how = filesafe.copy(
                str(src_path.relative_to(base_path)),
                str(arch_path.relative_to(base_path))
            )
            logger.info(f"File copied to archive successfully: {filename}, method={how}")
            results.append({
                "filename": filename,
                "source": str(src_path),
                "destination": str(arch_path),
                "method": str(how)
            })
        except NotFoundError:
            logger.warning(f"Source file not found, skipping: {filename}")
            failures.append({"filename": filename, "error": "source not found"})
        except ExistsError:
            logger.warning(f"Destination already exists, skipping: {filename}")
            failures.append({"filename": filename, "error": "destination exists"})
        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Failed to copy {filename}: {e}")
            logger.exception(e)
            failures.append({"filename": filename, "error": str(e)})
    
    # Log summary of copying operation
    if failures:
        logger.warning(
            f"Session {session_id} partial copy: "
            f"{len(results)} succeeded, {len(failures)} failed"
        )
        logger.debug(f"Copy failures: {failures}")
    else:
        logger.info(f"Session {session_id} copied {len(results)} files successfully")
    
    logger.debug(f"Copy results: {results}")
    logger.info(f"=== copy_files_to_label_source END === session_id={session_id}, success_count={len(results)}, failed_count={len(failures)}")
    
    return {"success": results, "failed": failures}