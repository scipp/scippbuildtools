# scippbuildtools

Tools for building C++ libraries, python packages and documentation.

The goal of `scippbuildtools` is to reduce duplication in the CI setup between all the repositories of the [Scipp](https://github.com/scipp) organisation.

- `cpp.py` defines a `CppBuilder` used by `scipp/<repo>/tools/build_cpp.py`
- `filemover.py` is used by `scipp/<repo>/tools/build_conda.py`
- `docs.py` defines a `DocsBuilder` used by `scipp/<repo>/docs/build_docs.py`
- `sphinxconf.py` defines common variables for sphinx, which can be overridden in `scipp/<repo>/docs/conf.py`. It also writes a `_static/theme_overrides.css` file when imported.
