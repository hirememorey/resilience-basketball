"""
Configuration management for NBA Playoff Resilience Engine.
Loads and merges configuration from YAML files with environment overrides.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


def get_config(environment: str = None) -> Dict[str, Any]:
    """
    Get configuration for the specified environment.

    Loads default config and merges environment-specific overrides.
    Also loads secrets if available.

    Args:
        environment: Environment name ('development', 'production', etc.)
                    If None, uses NBA_ENV environment variable or 'development'

    Returns:
        Merged configuration dictionary
    """
    if environment is None:
        environment = os.getenv('NBA_ENV', 'development')

    config_dir = Path(__file__).parent.parent / 'config'

    # Load default configuration
    default_config = _load_yaml_file(config_dir / 'default.yaml')
    if not default_config:
        raise RuntimeError("Could not load default configuration")

    # Load environment-specific configuration
    env_config_file = config_dir / f'{environment}.yaml'
    env_config = _load_yaml_file(env_config_file) if env_config_file.exists() else {}

    # Load secrets (optional)
    secrets_file = config_dir / 'secrets.yaml'
    secrets_config = _load_yaml_file(secrets_file) if secrets_file.exists() else {}

    # Merge configurations (secrets override env, env overrides default)
    config = _deep_merge(default_config, env_config)
    config = _deep_merge(config, secrets_config)

    # Override with environment variables (highest priority)
    config = _apply_env_overrides(config)

    logger.info(f"Loaded configuration for environment: {environment}")
    return config


def _load_yaml_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load a YAML configuration file."""
    if yaml is None:
        logger.warning("PyYAML not installed. Configuration files must be loaded manually.")
        return None

    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config file {file_path}: {e}")
        return None


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    Override values replace base values, but nested dicts are merged recursively.
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides.
    Environment variables should be prefixed with NBA_ and use double underscores for nesting.

    Examples:
        NBA_APP__DEBUG=true → config['app']['debug'] = True
        NBA_MODEL__XGBOOST__N_ESTIMATORS=200 → config['model']['xgboost']['n_estimators'] = 200
    """
    prefix = 'NBA_'

    for env_key, env_value in os.environ.items():
        if not env_key.startswith(prefix):
            continue

        # Remove prefix and split by double underscore
        config_path = env_key[len(prefix):].lower().split('__')

        # Navigate to the config location
        current = config
        for path_part in config_path[:-1]:
            if path_part not in current:
                current[path_part] = {}
            current = current[path_part]

        # Set the value (try to parse as appropriate type)
        final_key = config_path[-1]
        parsed_value = _parse_env_value(env_value)
        current[final_key] = parsed_value

        logger.debug(f"Applied env override: {env_key} = {parsed_value}")

    return config


def _parse_env_value(value: str) -> Any:
    """Parse environment variable value to appropriate type."""
    # Boolean
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'

    # Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Float
    try:
        return float(value)
    except ValueError:
        pass

    # String (default)
    return value


# Global config instance
_config = None


def get_global_config() -> Dict[str, Any]:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = get_config()
    return _config


def reload_config() -> Dict[str, Any]:
    """Reload configuration from files."""
    global _config
    _config = get_config()
    return _config
