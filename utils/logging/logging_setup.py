import json
import logging
import logging.config
import os
from pathlib import Path
from typing import Iterable
from ..env_utils import get_env_or_fail

def _ensure_dirs(paths: Iterable[str]) -> None:
    for p in paths:
        if p:
            Path(p).parent.mkdir(parents=True, exist_ok=True)

def setup_logging(
    config_path = Path(get_env_or_fail("LOGGING_CONFIG_PATH")),
    output_dir = Path(get_env_or_fail("LOGGING_OUTPUT_PATH")),
    default_level=logging.INFO,
    fallback_format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    reset=False,
):
    """
    Load dictConfig from JSON if present; otherwise basicConfig.
    Ensures directories for FileHandlers exist. Returns the logging module.
    """
    if reset:
        for h in list(logging.root.handlers):
            logging.root.removeHandler(h)

    if os.path.exists(config_path):
        print("Setup logging")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            file_targets = []
            for h_name, h in (cfg.get("handlers") or {}).items():
                if h.get("class", "").endswith("FileHandler"):
                    filename = str(output_dir) + "/" + h_name + ".log"
                    file_targets.append(filename)
                    cfg.get("handlers").get(h_name)["filename"] = filename                    
                    h.setdefault("encoding", "utf-8")
            _ensure_dirs(file_targets)
            

            logging.config.dictConfig(cfg)
        except Exception as e:
            logging.basicConfig(level=default_level, format=fallback_format)
            logging.getLogger(__name__).warning(
                "Failed to load logging config %r (%s). Falling back to basicConfig.",
                config_path, e, exc_info=True,
            )
    else:
        logging.basicConfig(level=default_level, format=fallback_format)

    logging.captureWarnings(True)  # route warnings.warn(...) into logging
    return logging

# Get your named loggers
log = setup_logging()
supplementary_error_logger = log.getLogger("supplementary_error_logger")
supplementary_info_logger  = log.getLogger("supplementary_info_logger")
parsing_error_logger       = log.getLogger("parsing_error_logger")
parsing_info_logger        = log.getLogger("parsing_info_logger")
variant_search_error_logger= log.getLogger("variant_search_error_logger")
variant_search_info_logger = log.getLogger("variant_search_info_logger")
w3c_error_logger           = log.getLogger("w3c_error_logger")
w3c_info_logger            = log.getLogger("w3c_info_logger")
