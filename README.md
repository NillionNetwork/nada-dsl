# nada-dsl

nada-dsl is a Python DSL for building MPC programs on the Nillion Network.

See the official Nillion documentation site for more about the [Nada-Lang
Framework][framework] and [Nada Program Examples][examples].

[examples]: https://github.com/NillionNetwork/nillion-python-starter/tree/main/programs
[framework]: https://docs.nillion.com/nada-lang-framework

## Auto-Generated Documentation

Documentation for this package can be generated automatically via the commands below (using a variant of `python` appropriate for the environment):

```console
python -m pip install '.[docs]'
cd docs
sphinx-build . _build
```

Alternatively, you can use the `just` target (from the root of nillion): `just nada-dsl-doc`
