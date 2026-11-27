from cookieplone.logger import logger
from pathlib import Path

import subprocess


# lxml 6.2.0 passes an empty nsmap to the parser-target start() callback, so
# BeautifulSoup (used by zpretty) drops the xmlns declarations from ZCML.
# Keep this bound until lxml or zpretty ships a fix; then lift it.
# See https://github.com/collective/zpretty/issues/255
ZPRETTY_REQUIREMENTS = ("lxml<6.2",)


def _uvx(
    tool: str,
    args: list[str],
    base_path: Path,
    *,
    with_: list[str] | None = None,
) -> None:
    """Run a formatting tool via ``uvx``.

    :param tool: The PyPI package / tool name (e.g. ``"ruff"``).
    :param args: Extra CLI arguments passed after the tool name.
    :param base_path: Working directory for the subprocess.
    :param with_: Extra requirements, each passed as ``--with <req>``. They
        go before the tool name, because ``uvx`` reads its own flags first.
    """
    with_flags = [flag for req in with_ or [] for flag in ("--with", req)]
    cmd = ["uvx", *with_flags, tool, *args]
    logger.debug(f"Formatter {tool}: {' '.join(cmd)}")
    subprocess.run(cmd, capture_output=True, check=True, cwd=base_path)  # noqa: S603


def run_zpretty(base_path: Path):
    """Run zpretty on XML and ZCML files under ``src/``."""
    src = base_path / "src"
    if not src.exists():
        return
    extensions = ("xml", "zcml")
    files = [
        str(f.relative_to(base_path))
        for f in src.glob("**/*")
        if f.suffix.lstrip(".") in extensions
    ]
    if not files:
        return
    _uvx("zpretty", ["-i", *files], base_path, with_=list(ZPRETTY_REQUIREMENTS))


def run_isort(base_path: Path):
    """Run isort on the given path."""
    pyproject = base_path / "pyproject.toml"
    _uvx("isort", ["--quiet", "--settings", str(pyproject), str(base_path)], base_path)


def run_black(base_path: Path):
    """Run black on the given path."""
    pyproject = base_path / "pyproject.toml"
    _uvx("black", ["--quiet", "--config", str(pyproject), str(base_path)], base_path)


def run_ruff(base_path: Path):
    """Run ruff check (import sorting) and ruff format on the given path."""
    pyproject = base_path / "pyproject.toml"
    args = ["check", "--select", "I", "--fix", "--config", str(pyproject)]
    _uvx("ruff", args, base_path)
    _uvx("ruff", ["format", "--config", str(pyproject)], base_path)
