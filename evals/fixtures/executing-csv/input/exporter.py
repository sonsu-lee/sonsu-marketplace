def export_csv(rows):
    """Serialize rows as comma-separated fields, one row per line."""
    return "".join(",".join(str(field) for field in row) + "\n" for row in rows)
