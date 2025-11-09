"""
Basic tests for pyhetznerdev
"""
import pytest
from pyhetznerdev.config import Config
import tempfile
import os


def test_config_default_path():
    """Test that config has a default path"""
    config = Config()
    assert config.config_path is not None
    assert "pyhetznerdev" in config.config_path


def test_config_get_set():
    """Test config get/set operations"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_path = f.name
    
    try:
        config = Config(config_path)
        
        # Test set and get
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"
        
        # Test default value
        assert config.get("nonexistent", "default") == "default"
        
        # Test save and reload
        config.save()
        config2 = Config(config_path)
        assert config2.get("test_key") == "test_value"
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_config_defaults():
    """Test config default values"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_path = f.name
    
    try:
        config = Config(config_path)
        
        # Test default values
        assert config.get_snapshot_max_age_days() == 30
        assert config.get_default_server_type() == "cx11"
        assert config.get_default_location() == "nbg1"
        assert config.get_default_image() == "ubuntu-22.04"
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_config_environment_tokens():
    """Test that environment variables are picked up for tokens"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_path = f.name
    
    try:
        # Set environment variable
        os.environ["HETZNER_API_TOKEN"] = "test-token"
        
        config = Config(config_path)
        assert config.get_api_token() == "test-token"
        
        # Clean up
        del os.environ["HETZNER_API_TOKEN"]
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_version():
    """Test that version is defined"""
    import pyhetznerdev
    assert hasattr(pyhetznerdev, '__version__')
    assert pyhetznerdev.__version__ == "0.1.0"
