"""Validate deployment UI flags without registering individual feature names."""


def validate_features(config):
    """The console owns flag names, defaults, and parent relationships."""
    values = config.get("features")
    if values is None:
        return
    if not isinstance(values, dict):
        raise ValueError("features must be a mapping of panel names to booleans or null")
    for name, value in values.items():
        if not isinstance(name, str):
            raise ValueError("features keys must be strings")
        if value is not None and type(value) is not bool:
            raise ValueError(f"features.{name} must be a boolean or null")
