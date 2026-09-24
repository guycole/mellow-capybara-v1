# mellow-capybara-v1

Capybara v1 is an ACARS and VDL2 data pipeline for collecting raw receiver output,
wrapping observations into a common JSON envelope, validating payloads, and loading
scored frequency/activity data into PostgreSQL.

## Repository Contents

### Top-level docs

- `README.md`: this repository overview.
- `DISCOVERY.md`: notes about ACARS frequency discovery motivation.
- `ACARS_FREQUENCY.md`: curated frequency lists for legacy ACARS and VDL2.

### Runtime scripts

- `bin/`: operational shell scripts.
	- ACARS/VDL2 capture and driver scripts.
	- Collector/validator orchestration scripts.
	- Archival and S3 transfer helpers.

### Infrastructure

- `infra/psql/`: schema and SQL jobs.
	- schema create/drop scripts.
	- load-log, frequency, geo-location, observation, and daily-score SQL.
- `infra/systemd/`: service unit files for station-specific ACARS/VDL2 jobs.

### Source code

- `src/collector/`: wrapper generator for raw ACARS/VDL2 files.
	- Reads line-delimited JSON from raw feeds.
	- Emits capybara-v1 wrapper payloads with metadata and timestamps.
- `src/helper/`: shared utilities (JSON/schema helper, PostgreSQL helper).
- `src/wombat_docker/`: validator application.
	- Validates payloads.
	- Updates load-log, daily-score, and frequency tables.
	- Moves files into success/failure directories.
- `src/peccary_docker/`: loader-oriented application variant.
- `src/utility/`: supporting utility code.
- `src/config.yaml`: base runtime configuration.
- `src/wombat.sh`, `src/peccary.sh`: local execution wrappers.

### Samples and tests

- `samples/`: real and representative payload examples.
	- Includes ACARS and dumpvdl2 source snapshots plus wrapped payload examples.
- `tests/`: unit tests for schema, loader, collector behavior, and frequency logic.

## Data Flow At A Glance

1. Raw ACARS and VDL2 files are captured by receiver jobs.
2. Collector wraps observations into capybara-v1 JSON files.
3. Validator/loader processes wrapper files from fresh directories.
4. PostgreSQL tables are updated with load-log and frequency scoring results.
5. Files are moved to success/failure and optionally archived.

## See Also

- `src/collector/README.md` for collector-specific behavior and payload contract.
- `src/wombat_docker/README.md` for validator runtime and Docker usage.
