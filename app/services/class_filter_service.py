def parse_class_filter(classes: str | None) -> set[str] | None:
    """Convert a comma-separated query parameter into normalized YOLO labels."""
    if not classes:
        return None

    parsed_classes = {
        class_name.strip().lower()
        for class_name in classes.split(",")
        if class_name.strip()
    }

    return parsed_classes or None
