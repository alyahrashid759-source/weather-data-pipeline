"""Run extract -> validate -> load. Then run `dbt build` for transformations."""
import logging

from extract import extract_all
from load import load_raw
from quality import validate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("pipeline")


def run() -> int:
    rows = extract_all()
    log.info("Extracted %d rows", len(rows))
    validate(rows)
    log.info("Quality checks passed")
    n = load_raw(rows)
    log.info("Loaded %d rows into raw.weather", n)
    return n


if __name__ == "__main__":
    run()
