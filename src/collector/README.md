## Capybara Collector

This collector wraps raw ACARS/VDL2 observations into capybara-v1 JSON payloads and moves processed source files to the fresh ingest directory.

### Execution Flow

1. Load YAML config.
2. Discover raw files in `rawDir` (excluding the current hour file for each feed).
3. Read line-delimited JSON observations from each source file and attach observation UUIDs.
4. Build a typed capybara payload with metadata and UTC timestamp.
5. Write one wrapper file into `freshDir`.
6. Move the original source file into `freshDir`.

### Configuration Contract

Required top-level keys in `config.yaml`:

1. `crateName`
2. `freshDir`
3. `rawDir`
4. `equipment.hostName`
5. `equipment.hostType`
6. `geoLoc.altitude`
7. `geoLoc.latitude`
8. `geoLoc.longitude`
9. `geoLoc.siteName`
10. `receiver.antenna`
11. `receiver.receiverId`
12. `receiver.task`
13. `receiver.type`

### Output Payload Contract

Each generated wrapper JSON file includes:

1. `crateName`
2. `fileName`
3. `sourceFileName`
4. `version` (2)
5. `equipment`
6. `geoLoc`
7. `job`
8. `receiver`
9. `timeStamp` (`epochSeconds`, `iso8601`)
10. `observations`

### Local Tooling

Use the in-module virtual environment:

- `source venv/bin/activate`
- `python -m pytest -q test_collector.py`
- `python -m black *.py`
- `python -m ruff check *.py`
