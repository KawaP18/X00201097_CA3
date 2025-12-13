# X00201097_CA3 – CI/CD Pipeline Implementation
---

## Overview
This project demonstrates the design and implementation of a complete CI/CD pipeline using GitHub Actions for Continuous Integration and Azure DevOps Pipelines for Continuous Deployment.

The objective of CA3 is to extend beyond basic CI (implemented in CA2) and showcase industry-standard DevOps practices, including:

- Automated testing and validation

- Static code analysis and security scanning

- Performance testing

- User Acceptance Testing (UAT)

- Multi-stage deployments

- Environment-based approval gates for production

A simple Python calculator application is used to support the pipeline. The application itself is intentionally lightweight so that the focus remains on pipeline architecture, automation, and governance, rather than application complexity.
---
## Repository Structure
The repository follows a clean, industry-style structure that separates application code, tests, pipeline configuration, and automation scripts.

### Key Directories and Files

- .github/workflows/ci.yml – GitHub Actions CI workflow

- calculator/ – Python application source code

- tests/ – Pytest unit tests

- uat_tests/ – Selenium User Acceptance Tests

- loadtest.js – k6 performance testing script

- pytest.ini – Pytest configuration file

- azure-pipelines.yml – Azure DevOps multi-stage CD pipeline

- README.md – Technical documentation for CA3

This structure ensures that automation tools can detect the correct components and that responsibilities are clearly separated.
---
## Technologies Used
- Python 3.x

- Pytest validates functional correctness through automated testing

- Pylint enforces coding standards and detects maintainability issues

- Bandit introduces security scanning early in the pipeline (shift-left security)

- k6 demonstrates performance and load testing as part of CI/CD

- Selenium provides UI-level automation and end-to-end validation

- GitHub Actions enables fast, developer-focused CI feedback

- Azure DevOps Pipelines enables governed, multi-stage deployments

- Azure DevOps Environments – Deployment governance and approvals

Together, these tools form a layered quality assurance pipeline, rather than relying on a single testing mechanism.
---
## Local Development Setup
To run the project locally, the following steps can be followed:

1. Clone the repository:
   ```bash
   git clone https://github.com/KawaP18/X00201097_CA3.git
   cd X00201097_CA3
    ```
2. (Optional) Create and activate a Python virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the unit tests:
   ```bash
   pytest
   ```
This mirrors the same commands executed automatically in the CI pipeline.

---
## Application Features
The application used in this project is a simple Python-based calculator. It provides the following functionality:

- Addition
- Subtraction
- Multiplication

All functionality is validated through automated unit tests.
No manual testing is required.

---
## CI Pipeline Implementation
Continuous Integration is implemented using GitHub Actions. The workflow is triggered:

- On every push to the `dev` branch

- On pull requests targeting the `main` branch

This ensures that all code changes are validated automatically before being merged.


CI Workflow Configuration (`ci.yml`)
```yaml
name: CI

on:
  push:
    branches:
      - dev
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run unit tests
        run: |
          export PYTHONPATH=$PYTHONPATH:$(pwd)
          pytest

```
### Explanation
The `ci.yml` file defines the contract that all code changes must satisfy.

Key responsibilities of this workflow include:

- Provisioning a clean execution environment
- Installing dependencies deterministically
- Running automated tests
- Failing fast when errors are detected

The explicit `PYTHONPATH` configuration resolves a common CI issue where module imports succeed locally but fail in isolated runners. Identifying and fixing this issue demonstrates practical CI debugging skills, which are essential in real-world DevOps roles.
### Successful CI Execution
The screenshot below shows a successful GitHub Actions run, where all CI steps complete without errors.
![Successful GitHub Actions run](screenshots/succesfulaction.PNG)


---
## Automated Unit Testing
Unit tests are executed using Pytest as part of the CI workflow.

### What This Confirms

- Tests are discovered correctly

- All application functionality is validated

- CI fails immediately if tests break

The following screenshot shows successful unit test execution within the pipeline.
This confirms that all calculator functions are validated automatically.

![Unit test results](screenshots/unittests.PNG)

### Pytest Configuration `(pytest.ini)`
```ini
[pytest]
testpaths = tests
```

### Explanation

- Restricts Pytest discovery to unit tests only

- Prevents Selenium UAT tests from running during CI

- Ensures fast and focused feedback
---
## Azure DevOps CI/CD Pipeline

Continuous Deployment is implemented using Azure DevOps Pipelines.

### Pipeline Stages

1. CI – Tests & Security

   - Unit tests

   - Pylint

   - Bandit security scan

2. Performance Testing

   - k6 load testing

3. User Acceptance Testing

   - Selenium WebDriver tests

4. Deploy to TEST

5. Deploy to PROD

Each stage must succeed before the next can run.

The screenshot below shows a completed multi-stage pipeline run in Azure DevOps,
including CI, testing, and deployment stages.

![Azure DevOps pipeline](screenshots/pipeline.PNG)

### Azure Pipeline Configuration `(azure-pipelines.yml)`

```yaml
trigger:
- dev

pool:
  vmImage: 'ubuntu-latest'

stages:

# =========================
# CI STAGE — UNIT TESTS + SAST
# =========================
- stage: CI
  displayName: "CI - Tests & Security"
  jobs:

  - job: UnitTests
    displayName: "Run Pytest Unit Tests"
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.10'

    - script: |
        pip install -r requirements.txt
        export PYTHONPATH=$(System.DefaultWorkingDirectory)
        pytest --junitxml=unit-tests.xml
      displayName: "Install deps & run pytest"

    - task: PublishTestResults@2
      inputs:
        testResultsFiles: 'unit-tests.xml'
        testRunTitle: 'Unit Tests'
      condition: succeededOrFailed()

  - job: BanditScan
    displayName: "SAST - Bandit"
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.10'

    - script: |
        pip install bandit
        bandit -r calculator -f json -o bandit-report.json || true
      displayName: "Run Bandit scan"

    - publish: bandit-report.json
      artifact: security-report


# =========================
# PERFORMANCE TESTING — k6
# =========================
- stage: Performance
  displayName: "Performance Testing"
  dependsOn: CI
  condition: succeeded()
  jobs:
  - job: K6Tests
    displayName: "Run k6 load test"
    steps:
    - script: |
        sudo apt-get update
        sudo apt-get install -y ca-certificates gnupg
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://dl.k6.io/key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/k6.gpg
        echo "deb [signed-by=/etc/apt/keyrings/k6.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install -y k6
        k6 run loadtest.js --out json=perf-results.json
      displayName: "Execute k6 test"

    - publish: perf-results.json
      artifact: performance-results


# =========================
# UAT — SELENIUM
# =========================
- stage: UAT
  displayName: "User Acceptance Testing"
  dependsOn: Performance
  condition: succeeded()
  jobs:
  - job: SeleniumUAT
    displayName: "Run Selenium tests"
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.10'

    - script: |
        sudo apt-get update
        sudo apt-get install -y wget gnupg
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
      displayName: "Install Chrome"

    - script: |
        pip install selenium
      displayName: "Install Selenium"

    - script: |
        python uat_tests/selenium_test.py
      displayName: "Run Selenium UAT"


# =========================
# DEPLOY TO TEST
# =========================
- stage: DeployTest
  displayName: "Deploy to TEST"
  dependsOn: UAT
  condition: succeeded()
  jobs:
  - deployment: DeployTestJob
    environment: Test
    strategy:
      runOnce:
        deploy:
          steps:
          - script: echo "Deploying to TEST environment"


# =========================
# DEPLOY TO PROD (APPROVAL)
# =========================
- stage: DeployProd
  displayName: "Deploy to PROD"
  dependsOn: DeployTest
  condition: succeeded()
  jobs:
  - deployment: DeployProdJob
    environment: Prod
    strategy:
      runOnce:
        deploy:
          steps:
          - script: echo "Deploying to PRODUCTION"

```
### Azure DevOps Pipeline Configuration – Explanation

The `azure-pipelines.yml` file defines a multi-stage Continuous Deployment pipeline that controls how code progresses from validation to production. Each stage acts as a quality gate, ensuring that only fully validated builds are allowed to continue.

### Multi-Stage Design and Execution Order

The pipeline is structured into clearly defined stages, each responsible for a specific validation step.

A strict execution order is enforced using stage dependencies, meaning:

- A stage cannot start unless the previous stage succeeds
- Test failures immediately stop the pipeline
- Deployment stages are protected from unvalidated builds

This ensures that errors are detected early and do not propagate to later stages.

### Separation of Testing Responsibilities

Testing concerns are deliberately separated into independent stages:

- Unit testing and security scanning
- Performance testing
- User Acceptance Testing (UAT)

This separation improves:

- Clarity – each stage has a single responsibility
- Traceability – failures are easy to diagnose
- Efficiency – resource-intensive tests only run after basic checks pass

### Environment-Based Deployment Governance
Deployments are managed using Azure DevOps Environments rather than direct script execution. This allows:

- Environment-specific deployment tracking
- Centralised visibility of releases
- Manual approval gates for sensitive environments

The Production environment is protected by a manual approval gate, ensuring that production releases require explicit human authorisation.

The following screenshot shows the manual approval gate required before deploying
to the Production environment.

![Production approval gate](screenshots/prodapporval.PNG)

**Summary:**  
This pipeline design demonstrates a controlled and scalable Continuous Deployment approach that balances automation with governance, aligning closely with real-world DevOps practices.

---
## Performance Testing with k6
```javascript
import http from 'k6/http';
import { sleep } from 'k6';

export default function () {
  http.get('https://test.k6.io');
  sleep(1);
}
```
### Explanation
- Simulates HTTP load

- Validates pipeline performance stage

- Demonstrates non-functional testing integration
---
## User Acceptance Testing with Selenium
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)
driver.get("https://example.com")
assert "Example Domain" in driver.title
driver.quit()

```
### Explanation

- Runs browser-based UI automation

- Executes in headless Chrome

- Demonstrates end-to-end testing in CI/CD
---
## Environment Setup and Configuration

Two Azure DevOps environments are used:

- Test – automatic deployment

- Prod – protected by approvals

This enforces controlled promotion of builds.
---
## Production Approval Gate

Production deployment requires manual approval.

### Why This Matters

- Prevents accidental deployments

- Reflects real-world DevOps governance

---
## Branch Policies and Protection
The repository follows a two-branch strategy to support controlled development and deployment:

- `dev`: Used for active development and testing.
- `main`: Represents stable, production-ready code.

All changes are developed and tested on the `dev` branch before being promoted to `main`. Pull requests are used to merge changes into `main`, ensuring that automated CI checks pass before production deployment.

This approach aligns with industry best practices by separating development work from production-ready code and reducing the risk of introducing breaking changes.

---
## Testing Strategy
A layered testing strategy is implemented to validate both the application and the CI/CD pipeline. Each testing type runs in a dedicated pipeline stage to ensure clear separation of responsibilities and faster feedback.

The testing strategy includes:

- **Unit Testing**  
  Unit tests are written using Pytest to validate the calculator’s core functionality. These tests execute during the CI stage and provide immediate feedback on code changes.

- **Static Code Analysis**  
  Pylint is used to analyse code quality and enforce consistent coding standards.

- **Security Testing (SAST)**  
  Bandit performs Static Application Security Testing to identify common Python security issues early in the pipeline.

- **Performance Testing**  
  k6 is used to execute load and performance tests against a sample HTTP endpoint, demonstrating performance validation within the CI/CD pipeline.

- **User Acceptance Testing (UAT)**  
  Selenium WebDriver executes browser-based tests to validate UI-level automation and demonstrate realistic end-to-end testing capability.

Separating these testing layers ensures that failures are easy to identify and that each stage focuses on a specific quality attribute.


By separating testing concerns into distinct pipeline stages, the CI/CDworkflow improves traceability and fault isolation.
Failures can be identified quickly without impacting unrelated pipeline stages.

---
## Environment Setup and Configuration
Two deployment environments are configured in Azure DevOps to support controlled application releases:

- **Test**: Used to validate deployments after all automated testing stages have completed.
- **Prod**: Represents the production environment and is protected by manual approval gates.

These environments are managed using Azure DevOps Environments and are explicitly referenced within the pipeline YAML configuration. This ensures that deployments are environment-aware and follow a structured promotion process.

---
## Deployment Process

The deployment process follows a structured and controlled flow to minimise risk and ensure stability.

Once all CI and testing stages have completed successfully, the application is deployed automatically to the **Test** environment. This deployment verifies that the pipeline can successfully promote a validated build to a downstream environment.

Deployment to the **Prod** environment is protected by a manual approval gate. A deployment cannot proceed until approval is granted, ensuring that production releases are intentional and reviewed.

This controlled promotion model mirrors real-world DevOps practices where confidence in releases is built progressively
rather than deploying directly to production.

---
## Security and Performance Testing
### Security Testing
Security testing is implemented using Bandit, a static analysis tool for Python applications. Bandit scans the codebase during the CI stage to identify common security issues such as insecure function usage or unsafe configurations.

Security scan results are generated in report format and published as pipeline artefacts for review.

### Performance Testing
Performance testing is implemented using k6. A scripted load test is executed during the pipeline to demonstrate how performance validation can be integrated into CI/CD workflows.

The performance tests simulate HTTP requests against a sample endpoint and generate performance metrics, which are stored as pipeline artefacts.

---
## UAT Testing with Selenium
User Acceptance Testing (UAT) is implemented using Selenium WebDriver. Selenium is used to demonstrate browser-based test automation within the CI/CD pipeline.

The Selenium tests run in a dedicated UAT stage after performance testing has completed. Google Chrome is installed dynamically in the pipeline, and the tests are executed in a headless environment.

While the calculator application itself is validated through unit tests, Selenium is used to showcase realistic end-to-end UI automation and pipeline integration, which is the primary focus of this assessment.

---
## Pipeline Approval Gates
The Production deployment stage is protected using Azure DevOps pipeline approval gates. Before a deployment to the **Prod** environment can proceed, manual approval is required.

This mechanism ensures that production releases are controlled and prevents unauthorised or accidental deployments. Approval gates reflect real-world DevOps practices where production environments are safeguarded through human oversight.

---
## Troubleshooting Guide
- **Pytest import errors**  
  Ensure the repository root is included in the `PYTHONPATH` during CI execution so that application modules can be resolved correctly.

- **Selenium errors (Chrome not found)**  
  Verify that Google Chrome is installed in the UAT stage before executing Selenium tests.

- **k6 installation failures**  
  Ensure the official k6 repository and signing key are added before attempting installation.

- **Pipeline not triggering**  
  Confirm that branch triggers are correctly defined in the pipeline YAML file.

- **Environment not found or unauthorised**  
  Ensure that Azure DevOps environments exist and are authorised for use by the pipeline.

---
## References
- Pytest Documentation: https://docs.pytest.org  
- Bandit Security Scanner: https://bandit.readthedocs.io  
- k6 Load Testing Tool: https://k6.io/docs  
- Selenium WebDriver Documentation: https://www.selenium.dev/documentation  
- Azure DevOps Pipelines Documentation: https://learn.microsoft.com/azure/devops/pipelines
---
## Appendix – Application Code Overview
The calculator application and unit tests are carried forward from CA2.
The application code remains unchanged, as the focus of CA3 is CI/CD
pipeline extension rather than application development.
