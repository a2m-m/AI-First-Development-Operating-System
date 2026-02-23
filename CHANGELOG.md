# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-23

### Added
- **AI-First OS Template Base**: Initial framework and directory structure for the development operating system.
- **Workflow / Actions**:
  - CI pipeline (`.github/workflows/ci.yml`) - Runs lint, test, format checks, and build process.
  - Test Reporting (`.github/workflows/test-report.yml`) - Automatically publishes test results as PR comments.
  - Secret Scanning (`.github/workflows/secret-scan.yml`) - Integration of Gitleaks to prevent credential leakage.
  - Dependency Scanning (`.github/workflows/dependency-scan.yml`) - Integration of Trivy for vulnerability detection.
  - Guardrail CI (`.github/workflows/guardrail.yml`) - Early stage AI-driven PR review and architecture policy enforcement (mock implementation).
  - Learning Content Generator (`.github/workflows/lcg.yml`) - Extraction of AI/human interactions and PR context into learning assets (mock implementation).
- **Scripts**:
  - `scripts/run` - Core CLI entrypoint to manage common project commands and read variables from `os-template.yml`.
  - `scripts/init` - Bootstrap script to apply OS template to an instance based on environment variables.
  - `scripts/hooks/pre-push` - Git pre-push hook to detect excessively large diffs based on `os-template.yml` policies.
- **Configuration & Policies**:
  - `os-template.yml` - Centralized configuration file for features, policies, commands, and repository metadata.
  - Commit strategy documentation (`docs/commit_strategy.md`).
  - `.ai-instructions.md` - Core system prompt rules governing AI agents' constraints and behaviors.
  - `.ai-context.md` - Maintaining current working context for consecutive AI execution.

### Changed
- Standardized Issue/PR templates to ensure strict Acceptance Criteria and Context.
