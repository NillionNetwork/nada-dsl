# Contributing to `nada-dsl`

Thank you for considering contributing to `nada-dsl`! There are two ways to contribute to `nada-dsl`:

1. [Open issues](#open-issues) to report bugs and typos, or to suggest new ideas.
2. [Submit a PR](#submit-a-pull-request) with a new feature or improvement.

To ensure a consistent development process, please follow the guidelines outlined below.

## Code quality and type checking

- All contributions must adhere to the project's coding standards. We enforce these standards using `pylint` for code quality and `mypy` for type checking. 
- Before submitting your contributions, ensure that your code passes both `pylint` and `mypy` checks.
- These tools are also integrated into our CI/CD pipeline, and any PR will be automatically validated against these checks.

## Development 

We recommend continuously running your code through `pylint` and `mypy` during the development process. These tools help identify potential issues early, enforce coding standards, and maintain type safety.

### Installation

1. Install [black](https://pypi.org/project/black/) and [isort](https://pycqa.github.io/isort/) for code formating
```bash
pip3 install black && isort
```
2. Fork the [repo](https://github.com/NillionNetwork/nada-dsl.git)
3. Install from source the `nada-dsl` library:
```bash
cd nada-dsl
pip3 install -e .
```


## Submit a Pull Request

We actively welcome your pull requests. Please follow these steps to successfully submit a PR:

1. Fork the [repo](https://github.com/NillionNetwork/nada-dsl.git) and create your branch from `main`.
2. If you've added code that should be tested, add tests as explained [above](#adding-tests). 
3. Ensure that the test suite passes.
```bash
make test 
```
4. Run from the root directory both 
```bash
black . && isort .
```
5. Ensure that your code passes both `pylint` and `mypy` checks:
```bash
poetry run pylint
poetry run mypy
```

## Open Issues

We use [GitHub issues](https://github.com/NillionNetwork/nada-dsl/issues/new/choose) to report bugs and typos, or to suggest new ideas. Please ensure your description is clear and has sufficient instructions to be able to reproduce the issue.

## License
By contributing to `nada-dsl`, you agree that your contributions will be licensed under the [LICENSE](./LICENSE) file in the root directory of this source tree.