from pathlib import Path

from black import main as black_main
from click.testing import CliRunner
from isort.main import main as isort_main
from zpretty.xml import XMLPrettifier
from zpretty.zcml import ZCMLPrettifier

from cookieplone.logger import logger

ZPRETTY_MAPPING = {
    "xml": XMLPrettifier,
    "zcml": ZCMLPrettifier,
}


def run_zpretty(base_path: Path):
    """Run zpretty on the given path."""
    files = (base_path / "src").glob("**/*")
    for filepath in files:
        ext = filepath.name.split(".")[-1]
        klass = ZPRETTY_MAPPING.get(ext)
        if not klass:
            continue
        prettifier = klass(filepath, encoding="utf-8")
        result = prettifier()
        filepath.write_text(result)
        logger.debug(f"Formatter zpretty: {filepath}")


def run_isort(base_path: Path):
    """Run isort on the given path."""
    pyproject = base_path / "pyproject.toml"
    isort_main([
        "--quiet",
        "--settings",
        f"{pyproject}",
        f"{base_path}",
    ])


def run_black(base_path: Path):
    """Run black on the given path."""
    pyproject = base_path / "pyproject.toml"
    args = ["--config", f"{pyproject}", f"{base_path}"]
    _ = CliRunner().invoke(black_main, args)
