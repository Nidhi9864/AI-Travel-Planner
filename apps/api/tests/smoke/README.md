Smoke tests run against a deployed base URL (make smoke URL=<base url>).

- `make smoke URL=http://localhost:8000` checks the local container (`docker compose --profile api up api`).
- `make smoke URL=<API URL> ARGS='--web-origin <web origin>'` also checks that the web origin is allowed by CORS.

The normal test targets never collect this directory; without `--base-url` the tests skip.
