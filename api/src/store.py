"""In-memory store for the domain API."""

store = {
    "users": {},   # Dict[str, dict]
    "items": {},   # Dict[str, dict]
}


def reset_store() -> None:
    """Reset all store collections to empty state."""
    store["users"].clear()
    store["items"].clear()
