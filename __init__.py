"""
Shim: when this repo directory is imported as ``saddle`` (e.g. parent folder is on
``sys.path``), delegate to ``src/saddle`` and run the real ``__init__.py`` in this
module namespace so ``__version__`` and submodules match the installed layout.
"""

from pathlib import Path

_pkg_dir = Path(__file__).resolve().parent / "src" / "saddle"
__path__ = [str(_pkg_dir)]

_real_init = _pkg_dir / "__init__.py"
if _real_init.is_file():
    _src = _real_init.read_text(encoding="utf-8")
    exec(compile(_src, str(_real_init), "exec"), globals())
