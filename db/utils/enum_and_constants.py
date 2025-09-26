import enum
import os
from dotenv import load_dotenv()

load_dotenv()

class ProcessingStageEnum(enum.Enum):
    pending_download = "pending_download"
    pending_parse_text = "pending_parse_text"
    pending_parse_supplementary = "pending_parse_supplementary"
    pending_search = "pending_search"
    pending_w3c = "pending_w3c"
    pending_submission = "pending_submission"
    complete = "complete"


class ArticleProcessingStatusEnum(enum.Enum):
    # pending = "pending"
    # in_progress = "in_progress"
    # complete = "complete"
    success = "success"
    error = "error"
    skipped = "skipped"


POSTGRESQL_FALSE = "false"
FALSE_SERVER_DEFAULT = POSTGRESQL_FALSE

generate_uri = (
    lambda user, password, host, port, dbname: f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
)
_user = os.getenv("DB_USER", None)
_password = os.getenv("DB_PASSWORD", None)
_host = os.getenv("DB_HOST", None)
_port = os.getenv("DB_PORT", None)
_dbname = os.getenv("DB_NAME", None)
INPUT_PREFIX_DIR = os.getenv("DB_INPUT_PREFIX_DIR", None)
if not _user:
    raise Exception("DB_USER is not set in env file")
if not _password:
    raise Exception("DB_PASSWORD is not set in env file")
if not _host:
    raise Exception("DB_HOST is not set in env file")
if not _port:
    raise Exception("DB_PORT is not set in env file")
if not _dbname:
    raise Exception("DB_NAME is not set in env file")
if not INPUT_PREFIX_DIR:
    raise Exception("DB_INPUT_PREFIX_DIR is not set in env file")

DATABASE_URI = generate_uri(_user, _password, _host, _port, _dbname)

SPECIES = os.path.join(INPUT_PREFIX_DIR, "species2pubtatorcentral")
VARIANTS = os.path.join(INPUT_PREFIX_DIR, "mutation2pubtatorcentral")
GENES = os.path.join(INPUT_PREFIX_DIR, "gene2pubtatorcentral")
HUMAN_GENES = os.path.join(INPUT_PREFIX_DIR, "Homo_sapiens.gene_info")
DISEASE = os.path.join(INPUT_PREFIX_DIR, "disease2pubtatorcentral")
INFO = os.path.join(INPUT_PREFIX_DIR, "Homo_sapiens.gene_info")

HUMAN_PM_IDS = os.path.join(INPUT_PREFIX_DIR, "human_pm_ids")
