# kbb-tests — Backend Test Suite

All backend (Django) tests live here, separated from the application code.

## Structure
```
kbb-tests/
├── conftest.py              # shared pytest fixtures (api_client, factories...)
├── accounts/                # auth/user tests
│   ├── test_api.py
│   └── test_models.py
├── tasks/                   # Kanban task tests
│   ├── test_api.py
│   └── test_models.py
└── annotations/             # image/polygon tests
    ├── test_api.py
    └── test_models.py
```

## How to run

Tests are executed **from the backend project folder** (`vai-rad-kbb/`), not from
here. `vai-rad-kbb/pytest.ini` points `testpaths` at this folder.

```powershell
cd vai-rad-kbb
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: **30 passed**.

## Why the tests are separate
Keeping tests outside the Django app packages makes the production code cleaner
and gives a single, obvious place to look when reviewing test coverage.