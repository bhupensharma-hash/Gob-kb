# Changelog

All notable changes to `gobiq-knowledge` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repo scaffolding
- Schema definition (`knowledge/_schema.yaml`) covering atom types: `global`, `category`, `template`, `domain`, `topic`, `procedure`, `concept`, `detection`, `threshold`, `output_spec`, `recipe`
- Loader (`src/gobiq_knowledge/loader.py`) ported from GoBIQ
- Chat assembler (`src/gobiq_knowledge/assemblers/chat.py`)
- Report assembler skeleton (`src/gobiq_knowledge/assemblers/report.py`)
- Example atoms: `concepts.osa`, `concepts.psl`, `detections.transfer_issue`, `thresholds.osa_health`, `procedures.availability_diagnosis`, `output_specs.availability_section`
- Schema, reference, and traversal validators in `tests/`
- CI workflow (`.github/workflows/validate.yml`)

## [0.1.0] - TBD

First internal release. Both GoBIQ chat and GoBIQ report import from this package.
