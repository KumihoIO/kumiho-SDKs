# Contributing

Thank you for your interest in contributing to the Kumiho Python SDK!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kumihoclouds/kumiho-python.git
   cd kumiho-python/python
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev,docs]"
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Add type hints to all public functions and methods
- Run `mypy` for type checking:
  ```bash
  mypy kumiho
  ```

## Documentation

Build the documentation locally:

```bash
cd docs
make html
```

View at `docs/_build/html/index.html`.

## Testing

- Write tests for all new functionality
- Use `pytest` fixtures for common setup
- Run the full test suite before submitting PRs:
  ```bash
  pytest --cov=kumiho
  ```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes with tests and documentation
4. Run linting and tests
5. Submit a pull request

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
