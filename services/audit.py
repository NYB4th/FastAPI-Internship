from logger import logger


def log_task_event(task_id: int, user_id: int, event_type: str) -> None:
    """
    In-process background audit logging function.
    Safely captures task events without blocking HTTP responses or crashing the app on error.
    """
    try:
        logger.info(
            f"[AUDIT] Event: {event_type} | Task ID: {task_id} | User ID: {user_id}"
        )
    except Exception as exc:
        logger.error(
            f"[AUDIT ERROR] Failed to record audit log for event '{event_type}' (Task ID: {task_id}): {exc}"
        )
