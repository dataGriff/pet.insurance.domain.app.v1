"""In-memory store for the pet insurance domain API."""

store = {
    "users": {},   # Dict[str, dict]
    "pets": {},    # Dict[str, dict]
    "claims": {},  # Dict[str, dict]
}


def reset_store() -> None:
    """Reset all store collections to empty state."""
    store["users"].clear()
    store["pets"].clear()
    store["claims"].clear()
