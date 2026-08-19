def has_blank_choice(choices):
    """Is there a blank choice in choices?"""
    return any(value == "" for value, _ in choices)
