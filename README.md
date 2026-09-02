# reff-extractor-racer-team

A Python CLI tool for extracting and processing references from racing team data.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Prerequisites
- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv)

### Installation

Clone the repository and install the project with development dependencies:

```bash
git clone <repository-url>
cd reff-extractor-racer-team
uv sync --all-extras
```

Or, to install without development dependencies:

```bash
uv sync
```

## Usage

### Run the application

```bash
uv run reff-extractor-racer-team
```

Or, if you've activated the virtual environment:

```bash
reff-extractor-racer-team
```

## Development

### Run tests

```bash
uv run pytest
```

### Run linting and formatting

Check code with ruff:

```bash
uv run ruff check .
```

Format code with ruff:

```bash
uv run ruff format .
```

Check and format in one command:

```bash
uv run ruff check . --fix
uv run ruff format .
```

## License

Add your license information here.
