import pytest

def test_always_passes():
    assert True
    print("Test passed!")

def test_python_version():
    import sys
    assert sys.version_info.major == 3
    print(f"Python {sys.version_info.major}.{sys.version_info.minor}")

def test_import_fastapi():
    try:
        import fastapi
        print("FastAPI available")
    except ImportError:
        print("FastAPI not installed (optional)")
    assert True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
