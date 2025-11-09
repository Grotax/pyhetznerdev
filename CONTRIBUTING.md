# Contributing to pyhetznerdev

Thank you for your interest in contributing to pyhetznerdev!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/Grotax/pyhetznerdev.git
cd pyhetznerdev
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

## Code Style

- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow PEP 8 guidelines
- Add type hints where appropriate
- Write docstrings for public functions and classes

## Testing

- Add tests for new features
- Ensure all tests pass before submitting a PR
- Run `pytest -v` to run the test suite

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -am 'Add my feature'`)
6. Push to the branch (`git push origin feature/my-feature`)
7. Create a Pull Request

## Reporting Issues

Please use the GitHub issue tracker to report bugs or request features.
Include as much detail as possible:
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
