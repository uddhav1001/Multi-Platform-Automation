# WorkFlow Pro QA Automation — Practical Demo

This repository is a runnable learning/demo implementation of the three parts in the submitted case study.

## 1. Setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

## 2. Start the local demo application

```bash
python app/app.py
```

It runs at http://127.0.0.1:5000.

Demo accounts:
- admin@company1.com / AdminPass123
- tenant@company2.com / TenantPass123

## 3. Run Part 1

In another terminal:

```bash
pytest tests/ui/test_login.py --browser chromium -v
```

Then demonstrate cross-browser execution:

```bash
pytest tests/ui/test_login.py --browser chromium --browser firefox --browser webkit -v
```

Explain: Playwright's `expect()` retries assertions; `wait_for_url()` removes the navigation race; credentials come from environment variables; pytest-playwright owns browser lifecycle.

## 4. Run Part 2

Part 2 is the framework design layer. The important files are:
- `src/pages/` — Page Object Model
- `src/api/` — API client abstraction and retries
- `src/fixtures/` — reusable data/auth fixtures
- `config/` — environments, tenants and BrowserStack capabilities
- `ci/pipeline.yml` — CI example

You can demonstrate the architecture by running all tests:

```bash
pytest -v
```

## 5. Run Part 3

```bash
pytest tests/api tests/integration -v
```

The integration test creates data through the API, opens the UI, searches for the created project and verifies it is rendered. Cleanup is done after the test through the fixture `yield` teardown.

## 6. Environment variables

For real/staging execution, do not commit credentials:

Windows PowerShell:
```powershell
$env:TEST_ADMIN_EMAIL='...'
$env:TEST_ADMIN_PASSWORD='...'
$env:WORKFLOWPRO_API_TOKEN='...'
$env:TEST_ENV='staging'
```

macOS/Linux:
```bash
export TEST_ADMIN_EMAIL='...'
export TEST_ADMIN_PASSWORD='...'
export WORKFLOWPRO_API_TOKEN='...'
export TEST_ENV='staging'
```

## 7. BrowserStack

The case study describes BrowserStack real-device testing. The local repository keeps that configuration in `config/browserstack.yaml`. A real run requires a BrowserStack account, credentials, and a Playwright BrowserStack fixture. Do not claim this part was executed locally unless you actually configure and run it.

## 8. Interview demo order

1. Show the original flaky problems in Part 1.
2. Open `tests/ui/test_login.py` and explain `wait_for_url`, `expect`, fixtures and environment credentials.
3. Run the UI test.
4. Run Chromium + Firefox + WebKit.
5. Show `src/pages`, `src/api`, `src/fixtures` and `config` as the Part 2 framework.
6. Run API + integration tests.
7. Open `created_project` and explain `yield` cleanup.
8. Explain BrowserStack and CI as the next production integrations.

## Important honesty rule

This is a practical local demo matching the case-study architecture. The original case study assumes a real WorkFlow Pro application and APIs. If the company gives you their actual application during the interview, replace the local demo URLs/selectors with the real ones and configure real credentials through environment/CI secrets.
