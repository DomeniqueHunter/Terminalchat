def merge_ordered(order:tuple[str, ...],
                  *parts:dict) -> dict:
    combined: dict = {}
    for part in parts:
        combined.update(part)
    return {key: combined[key] for key in order}
