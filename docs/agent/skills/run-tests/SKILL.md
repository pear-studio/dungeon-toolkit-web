---
name: openspec-run-tests
description: Run tests for the project. Executes backend pytest and frontend lint to validate implementation correctness.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.1.1"
---

Run tests for the Dungeon Toolkit project to validate implementation correctness.

**Input**: Optionally specify which tests to run. If omitted, run all tests.

**Prerequisites**

- Docker must be running
- Development environment must be started: `docker-compose -f docker-compose.dev.yml up -d`

**Steps**

1. **Check Docker environment**

   Verify Docker daemon is running:
   ```bash
   docker info
   ```

   If Docker is not running:
   - Add CRITICAL issue: "Docker daemon not running"
   - Recommendation: "Start Docker and run: docker-compose -f docker-compose.dev.yml up -d"

2. **Check containers are running**

   Verify backend and frontend containers are up:
   ```bash
   docker compose -f docker-compose.dev.yml ps
   ```

   If containers are not running:
   - Add CRITICAL issue: "Development containers not running"
   - Recommendation: "Run: docker-compose -f docker-compose.dev.yml up -d"

3. **Run Backend Tests**

   Execute pytest in backend container:
   ```bash
   docker compose exec -T backend pytest -v --tb=short
   ```

   Parse the output:
   - Count passed tests
   - Count failed tests
   - Note any errors or warnings

   **Test Results**:
   - If tests pass: Add to report "✓ Backend tests: X passed"
   - If tests fail:
     - Add CRITICAL issue: "Backend tests failed: <test name>"
     - List failing tests
     - Recommendation: "Fix failing tests before continuing"

4. **Run Frontend Lint**

   Execute ESLint in frontend container:
   ```bash
   docker compose exec -T frontend npm run lint
   ```

   Parse the output:
   - Count lint errors
   - Count lint warnings

   **Lint Results**:
   - If no issues: Add to report "✓ Frontend lint: passed"
   - If issues found:
     - Add WARNING: "Frontend lint issues: N errors, M warnings"
     - List critical issues
     - Recommendation: "Fix lint issues or update .eslintrc if false positives"

5. **Generate Test Report**

   Create a summary report:

   ```
   ## Test Report

   ### Backend Tests
   | Status   | Passed | Failed | Duration |
   |----------|--------|--------|----------|
   | Pass/Fail| X      | Y      | ~Zs      |

   ### Frontend Lint
   | Status | Errors | Warnings |
   |--------|--------|----------|
   | Pass   | 0      | 0        |

   ### Final Assessment
   - If backend tests fail: "X test(s) failed. Fix before proceeding."
   - If only lint warnings: "Lint warnings found, but tests pass."
   - If all pass: "All tests and checks passed! ✓"
   ```

**Options**

- `--backend, -b`: Run only backend tests (pytest)
- `--frontend, -f`: Run only frontend lint
- `--all, -a`: Run all tests (default)

**Usage Examples**

```bash
# Run all tests
openspec-run-tests

# Run only backend tests
openspec-run-tests --backend

# Run only frontend lint
openspec-run-tests --frontend
```

**Exit Criteria**

- Backend tests must pass (exit code 0)
- Frontend lint should pass (warnings are acceptable but will be noted)

If tests fail, report specific failing tests and suggest fixes.
