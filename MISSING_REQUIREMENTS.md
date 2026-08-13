# Part 2 – Missing Requirements & Clarification Questions

This document fulfils **Part 2, Task 3**: listing the gaps in the given requirements and
the questions a senior QA engineer would ask before committing to a framework design.

---

## 1. Test Data Management

| # | Question | Why it matters |
|---|---|---|
| 1 | Is there a dedicated test database / sandbox per environment, or do tests share production data? | Determines whether we can freely create/delete records or need strict isolation. |
| 2 | Who owns test data setup — the QA team, a shared DevOps script, or the app's seed API? | Affects whether data fixtures are in this repo or an external service. |
| 3 | Do tenants persist between test runs, or are they spun up fresh each run? | A fresh tenant per run is safer but slower; shared tenants risk cross-test pollution. |
| 4 | Is there a data-masking / anonymisation requirement for staging data? | Regulatory constraint (GDPR, SOC 2) that changes how we handle PII in fixture files. |
| 5 | Are there read-only "golden" records that tests must not mutate? | Requires guard assertions or separate read-only test accounts. |

---

## 2. Parallel Execution

| # | Question | Why it matters |
|---|---|---|
| 6 | What is the target total test-suite runtime? | Drives how many parallel workers (`pytest-xdist -n N`) and BrowserStack sessions to provision. |
| 7 | Are tests allowed to share a browser context, or must each test get an isolated context? | Shared contexts break storage-state isolation between roles; isolated contexts cost more RAM. |
| 8 | Is there a tenant-level rate limit on the API that parallel tests could hit? | May require per-worker tenant namespacing (e.g., `company1-worker3`). |
| 9 | Does the CI runner have enough CPU/RAM for N headless Chromium processes simultaneously? | A 2-core GitHub-hosted runner saturates quickly; self-hosted or larger runners may be needed. |

---

## 3. Reporting & Alerting

| # | Question | Why it matters |
|---|---|---|
| 10 | Where should test results be published — Allure, TestRail, Jira, Teams/Slack webhook? | Determines which reporter plugin to install and whether a test-management integration is required. |
| 11 | Should failures trigger an immediate Slack/Teams notification, or is the CI log sufficient? | Affects whether we add a notification step to `ci/pipeline.yml`. |
| 12 | Are screenshots and video on failure required? | Playwright supports both; they add storage and upload cost. |
| 13 | Is there a flakiness-tracking requirement (e.g., quarantine flaky tests automatically)? | Needs a retry plugin (`pytest-rerunfailures`) and a flakiness dashboard. |

---

## 4. Authentication & 2FA

| # | Question | Why it matters |
|---|---|---|
| 14 | Which user roles have 2FA enforced? | Tests must handle TOTP (`pyotp`) or SMS-OTP for those accounts; affects fixture design. |
| 15 | Can we create bot/service accounts with 2FA disabled for automation? | The safest approach — avoids time-sync issues with TOTP in CI. |
| 16 | Are SSO / SAML providers involved for any tenant? | SSO login flows require a completely different fixture (cookie injection vs form fill). |

---

## 5. Mobile & Cross-Platform

| # | Question | Why it matters |
|---|---|---|
| 17 | Is the mobile target a responsive web app or a native app? | Native (iOS `.ipa` / Android `.apk`) requires Appium + BrowserStack App Automate, not Playwright. |
| 18 | Which specific iOS and Android versions must be green? | BrowserStack device matrix grows quickly; need an agreed minimum support matrix. |
| 19 | Are there mobile-specific features (push notifications, camera, biometrics) to test? | These cannot be reliably tested in a browser context. |

---

## 6. CI/CD Pipeline

| # | Question | Why it matters |
|---|---|---|
| 20 | Which CI platform is used — GitHub Actions, GitLab CI, Jenkins, Azure DevOps? | Current `ci/pipeline.yml` targets GitHub Actions; other platforms need different syntax. |
| 21 | Should the full suite run on every PR, or only a smoke subset? | Smoke-first gates speed up developer feedback; full suite runs nightly. |
| 22 | How are secrets (API tokens, BrowserStack credentials) managed — Vault, CI secrets, AWS SSM? | Determines how `os.getenv()` calls are populated without committing credentials. |
| 23 | Is there a required code coverage minimum for the API tests? | Affects whether we add `pytest-cov` and a coverage gate to the pipeline. |

---

## 7. Accessibility & Performance (not mentioned)

| # | Question | Why it matters |
|---|---|---|
| 24 | Is WCAG 2.1 / accessibility compliance required? | Adds `axe-playwright` to the suite. |
| 25 | Are there page-load SLAs (e.g., dashboard must load in < 3 s)? | Adds Playwright performance assertion steps or a dedicated Lighthouse job. |

---

## Summary of highest-priority gaps

```
Priority  Gap                               Impact if ignored
HIGH      2FA robot accounts                Tests fail for 2FA-enabled roles
HIGH      Parallel isolation strategy        Tests pollute each other's data
HIGH      Real device vs responsive web      Wrong tool chosen for mobile
MEDIUM    Reporting destination              Failures invisible to stakeholders
MEDIUM    CI secret management              Credentials committed or tests skipped
LOW       Accessibility / performance SLAs  Missed non-functional requirements
```
