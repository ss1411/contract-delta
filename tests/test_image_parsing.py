import pytest
from pathlib import Path

from src.image_parser import validate_image_path


def test_validate_image_path_not_found(tmp_path: Path):
    missing = tmp_path / "missing.png"
    with pytest.raises(FileNotFoundError):
        validate_image_path(str(missing))


def test_validate_image_path_bad_extension(tmp_path: Path):
    bad = tmp_path / "file.txt"
    bad.write_text("dummy")
    with pytest.raises(ValueError):
        validate_image_path(str(bad))
