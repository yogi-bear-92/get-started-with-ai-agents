## Internal Project Structure (Public docs removed)

This file retained only as an internal reference. Previous public-facing documentation (deployment, setup, customization, troubleshooting, features, personalities, search, evaluation guides) was removed per privatization directive.

## 🗂️ Root Directory (Clean Structure)

The root directory contains only essential project files:

```
/
├── README.md                 # Main project documentation
├── LICENSE                   # Project license
├── azure.yaml               # Azure deployment configuration
├── pyproject.toml           # Python project configuration
├── docker-compose.yaml      # Docker composition
├── .gitignore              # Git ignore rules
├── .github/                # GitHub workflows and templates
├── .devcontainer/          # Development container configuration
└── .vscode/                # VS Code settings
```

## Remaining Internal Docs

Only project-status notes kept:

```
docs/project-status/
	MEMORY_IMPLEMENTATION_STATUS.md
	SESSION_COMPLETE_SUMMARY.md
	memory_test_results.md
	next-steps.md
```

## 🧪 Testing Structure

All test files are organized under `tests/`:

```
tests/
├── test_memory.py              # Core memory system tests
├── test_memory_integration.py  # Integration tests
├── test_vector_memory.py       # Vector memory performance tests
└── [existing tests...]         # Existing test files
```

## 🏗️ Source Code Structure

```
src/
├── requirements-dev.txt    # Development dependencies
├── api/                   # FastAPI application
├── frontend/              # React frontend
└── [other source files...]
```

## 📋 Other Organized Directories

```
tasks/          # Task management and development roadmap
scripts/        # Deployment and utility scripts
infra/          # Azure infrastructure as code
evals/          # Evaluation and testing scripts
airedteaming/   # AI red teaming tools
issues/         # Documented issues and solutions
```

## 🎯 Benefits of This Structure

1. **Clean Root**: Only essential files visible at first glance
2. **Logical Grouping**: Related files organized together
3. **Easy Navigation**: Clear hierarchy for different file types
4. **Scalable**: Structure supports project growth
5. **Developer Friendly**: Common conventions followed

## Internal Navigation

- Core overview: `README.md`
- Status notes: `docs/project-status/`
- Tests: `tests/`
- Source: `src/`
