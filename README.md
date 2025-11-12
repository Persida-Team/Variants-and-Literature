# Variants-and-Literature

A comprehensive pipeline for processing PubMed Central (PMC) articles to extract variant information, parse supplementary materials, and generate W3C format documents for submission to ClinGen's Variant Interpretation and Literature (VIL) system.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Usage](#usage)
- [Module Descriptions](#module-descriptions)
- [External Services](#external-services)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Overview

This pipeline processes PMC articles through the following stages:

1. **Parsing**: Extracts structured data from PMC XML and TXT files
2. **Supplementary Material Processing**: Extracts and processes supplementary files (PDF, Excel, Word, images, etc.)
3. **Database Querying**: Retrieves related gene, disease, and variant information from a PostgreSQL database containing PubTator data
4. **Variant Search**: Searches articles for variant mentions using pattern matching
5. **W3C Document Generation**: Creates W3C format documents from the extracted data
6. **Submission**: Submits processed articles to a W3C-compatible service

## Project Structure

```
Variants-and-Literature/
├── main.py                    # Main entry point for the pipeline
├── setup.py                   # Package setup configuration
├── parser/                    # XML and TXT parsing modules
│   ├── combined_parsing.py    # Combines XML and TXT parsing
│   ├── pmc_xml_parser.py      # XML parser
│   ├── pmc_txt_parser.py      # TXT parser
│   └── table_parser.py        # Table extraction from XML
├── db/                        # Database modules
│   └── pubtator/              # PubTator database integration
│       ├── db_models.py       # SQLAlchemy models
│       ├── db_init.py         # Database initialization
│       ├── db_queries.py      # Database queries
│       └── VARIABLES.py       # Database connection configuration
├── supplementary/             # Supplementary material processing
│   ├── variants_from_supplementary.py
│   ├── readers/               # File format readers
│   ├── tests/                 # Test modules
│   └── utils/                 # Utility functions
├── variant_search/            # Variant search functionality
│   └── search.py              # Main search logic
├── w3c/                       # W3C document generation and submission
│   ├── create_w3c_document.py
│   ├── format_check.py
│   ├── prepare_for_submittion.py
│   └── utilities.py           
├── utils/                     # Utility modules
│   ├── logging/               # Logging configuration
│   ├── env_utils.py           # Environment variable utilities
│   └── ...                    # Other utilities
├── requirements.txt           # Python dependencies (includes supplementary/requirements.txt)
├── env_example                # Environment variables template
└── supplementary/requirements.txt  # Supplementary module dependencies (included in main requirements.txt)
```

## Requirements

### System Requirements

- **Python**: 3.11.3 or higher (tested with 3.11.3)
- **PostgreSQL**: Database server 
- **Operating System**: Linux/Unix

### Python Dependencies

The project uses multiple Python packages. Key dependencies include:

- `pandas` - Data manipulation
- `SQLAlchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL adapter
- `requests` - HTTP requests for API calls
- `python-docx` - Word document processing
- `openpyxl` - Excel file processing
- `PyMuPDF` - PDF processing
- `pytesseract` - OCR for images
- `python-dotenv` - Environment variable management
- `lxml` - XML parsing
- `defusedxml` - Safe XML parsing
- `beautifulsoup4` - HTML/XML parsing
- `jsonschema` - JSON schema validation

All dependencies are listed in `requirements.txt` at the root of the project. The main `requirements.txt` file includes the supplementary module requirements via `-r supplementary/requirements.txt`, ensuring all dependencies are installed when running `pip install -r requirements.txt`.



## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Variants-and-Literature
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. **Install Python packages**:
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install all required dependencies including those needed for the supplementary material processing module.

### External Tools

- **Tesseract OCR**: Required for image processing in supplementary materials
   ```bash
   sudo apt install tesseract-ocr
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root. You can use `env_example` as a template:

```bash
cp env_example .env
```

Then edit `.env` with your actual values. The following environment variables are required:

#### Logging Configuration
```bash
# Path to logging configuration JSON file
LOGGING_CONFIG_PATH="path/to/Variants-and-Literature/utils/logging/logging_config.json"

# Directory where log files will be written
LOGGING_OUTPUT_PATH="path/to/pipeline_logs/"
```

#### Directory Configuration
```bash
# Directory for downloading supplementary materials
SUPPLEMENTARY_DOWNLOAD_DIRECTORY="path/to/supplementary/download/"

# Directory containing uncompressed PMC articles (XML and TXT files)
UNCOMPRESSED_ARTICLES_DIR="path/from/where/to/read/txt_xml/article/uncompressed/data/"

# Directory where processed articles are stored
PIPELINE_OUTPUT_DIR="path/to/save/submitted/data/"

# W3C-related directories
BODY_DIRECTORY="path/to/where/to/save/previously_processed/w3c_bodies/"
EXISTING_BODIES_PATH="path/to/where/to/save/previously_processed/w3c_bodies_list.txt"
```

#### Database Configuration
```bash
# PostgreSQL Database Connection
DB_USER="db_username"
DB_PASSWORD="db_password"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="db_name"

# Path to directory containing PubTator input files
DB_INPUT_PREFIX_DIR="path/to/db/pubtator/input_samples/"
```

#### W3C Service Configuration
```bash
# W3C service credentials
W3C_LOGIN="ClinGen credentials"
W3C_PASSWORD="ClinGen credentials"
```

#### Submission Configuration
```bash
# Token generator URL for authentication
SUBMIT_TOKEN_GENERATOR="https://genboree.org/auth/usr/your_token_generator_path"

# Submission endpoint URL (provided by ClinGen)
SUBMIT_URL="submission/url/provided/by/ClinGen"  # ask ClinGen for it

# Submission event configuration (provided by ClinGen)
SUBMIT_EVENT_TYPE="submit event type"           # ask ClinGen for it
SUBMIT_EVENT_NAME="submit event name"           # ask ClinGen for it
SUBMIT_EVENT_TRIGGERED_BY_HOST="submitter host identifier"
SUBMIT_EVENT_TRIGGERED_BY_ID="ldh_excerpt_http2pulsar"
SUBMIT_EVENT_TRIGGERED_BY_IRI="https://github.com/BRL-BCM/ldh_excerpt_http2pulsar"
```

**Note**: For submission-related variables (`SUBMIT_URL`, `SUBMIT_EVENT_TYPE`, `SUBMIT_EVENT_NAME`), you will need to contact ClinGen to obtain the correct values.

### PubTator Input Files

The database module expects the following files in `DB_INPUT_PREFIX_DIR`:

- `species2pubtatorcentral` - Species mappings
- `mutation2pubtatorcentral` - Mutation/variant mappings
- `gene2pubtatorcentral` - Gene mappings
- `disease2pubtatorcentral` - Disease mappings
- `Homo_sapiens.gene_info` - Human gene information
- `human_pm_ids` - Human PubMed IDs (generated using the get_human_pm_ids function)

These files should be obtained from PubTator Central. (https://ftp.ncbi.nlm.nih.gov/pub/lu/PubTatorCentral/ and https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/)

## Database Setup

1. **Create PostgreSQL database**:
   ```bash
   createdb your_database_name
   ```

2. **Initialize database tables**:
   ```bash
   python db/pubtator/db_init.py
   ```
   
   To drop existing tables and recreate:
   ```bash
   python db/pubtator/db_init.py drop
   ```

3. **Populate database with PubTator data**:
   
   Play around with populate_pm_ids, populate_gene_ncbi_ids, populate_disease_ids, and populate_variant_ids from the *db/pubtator/test.py* by setting the batch size and commiting to database.

### Database Schema

The database contains the following main tables:

- `articles` - PMC articles with PM IDs
- `genes` - Gene information with NCBI IDs and HGNC symbols
- `diseases` - Disease information with ontology IDs
- `variants` - Variant information with exact matches
- `article_genes`, `article_diseases`, `article_variants` - Junction tables
- Status tables: `download_statuses`, `text_parse_statuses`, `supplementary_parse_statuses`, `search_statuses`, `w3c_statuses`, `submission_statuses`

## Usage

**Note**: In order to parse articles, their XML and TXT data must be present in an uncompressed form in the `UNCOMPRESSED_ARTICLES_DIR` path.

### Basic Usage

The main entry point is `main.py`. The pipeline processes articles by PMC ID:

```python
from main import do_one_article

# Process a single article
do_one_article(pmc_id="PMC1702556", submission_out_dir="/path/to/output")
```

### Running the Full Pipeline

Modify `main.py` to specify your input file containing PMC IDs:

```python
if __name__ == "__main__":
    pmc_ids_file_path = "/path/to/pmc_ids.txt"
    with open(pmc_ids_file_path, "r") as fp:
        pmc_ids = fp.read().split("\n")
    
    for pmc_id in pmc_ids:
        try:
            do_one_article(pmc_id=pmc_id, submission_out_dir=OUTPUT_DIR)
        except Exception as e:
            main_error_logger.error(f"ID: {pmc_id}\tException: {e}")
```

### Article File Structure

The pipeline expects PMC articles to be organized as follows:

```
UNCOMPRESSED_ARTICLES_DIR/
├── PMC000xxxxxx/
│   ├── PMC0000001.xml
│   ├── PMC0000001.txt
│   └── ...
├── PMC001xxxxxx/
│   └── ...
```

The grouping is based on the PMC ID pattern: `PMC` + first 3 digits + `xxxxxx`.

## Module Descriptions

### Parser Module (`parser/`)

- **Purpose**: Extracts structured data from PMC XML and TXT files
- **Key Functions**:
  - `combine_xml_and_txt_no_save()` - Combines parsed XML and TXT data
  - Extracts title, abstract, text, tables, and metadata
- **Output**: JSON structure with article content

### Database Module (`db/pubtator/`)

- **Purpose**: Manages PostgreSQL database interactions for PubTator data
- **Key Functions**:
  - `get_full_related_data()` - Retrieves genes, diseases, and variants for an article
  - Database models for articles, genes, diseases, variants
- **Dependencies**: PubTator Central data files

### Supplementary Module (`supplementary/`)

- **Purpose**: Extracts and processes supplementary materials from articles
- **Supported Formats**: PDF, Word, Excel, PowerPoint, images (PNG, JPG, TIFF), CSV, TXT, ZIP
- **Key Features**:
  - Downloads supplementary files from PMC
  - Extracts variant information from various file formats
  - Uses OCR for images
- **See**: `supplementary/README.md` for detailed documentation

### Variant Search Module (`variant_search/`)

- **Purpose**: Searches articles for variant mentions using pattern matching
- **Search Locations**:
  - Article text (title, abstract, body)
  - Tables
  - Supplementary materials
- **Pattern Types**: RSIDs, CAIDs, HGVS notation, protein changes, nucleotide changes

### W3C Module (`w3c/`)

- **Purpose**: Generates W3C format documents and submits to external service
- **Key Functions**:
  - `prepare_one_w3c()` - Creates W3C document structure
  - `format_check()` - Validates document format
  - `submit_one_article_from_w3c()` - Submits to external API
- **API Integrations**: 
  - ClinGen Allele Registry (reg.genome.network)
  - dbSNP API (api.ncbi.nlm.nih.gov)
  - MONDO ontology (www.ebi.ac.uk/ols4)

## External Services

The pipeline integrates with several external APIs:

1. **ClinGen Allele Registry** (`reg.genome.network`)
   - Resolves variant IDs (RSID, CAID, HGVS)
   - Annotates VCF files

2. **dbSNP API** (`api.ncbi.nlm.nih.gov`)
   - Retrieves variant information by RSID

3. **MONDO Ontology** (`www.ebi.ac.uk/ols4`)
   - Resolves disease ontology IDs

4. **W3C Submission Service**
   - Submits processed articles (requires authentication)

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists and tables are initialized

2. **Missing Article Files**
   - Verify `UNCOMPRESSED_ARTICLES_DIR` path is correct
   - Check article file naming convention matches expected pattern
   - Ensure files are organized in correct directory structure

3. **Environment Variable Errors**
   - Ensure all required variables are set in `.env`
   - Check for typos in variable names
   - Verify file paths exist and are accessible

4. **Logging Issues**
   - Ensure `LOGGING_OUTPUT_PATH` directory exists
   - Check file permissions for log directory
   - Verify `LOGGING_CONFIG_PATH` points to valid JSON file

## Development

### Adding New File Format Support

To add support for a new supplementary file format:

1. Create a reader class in `supplementary/readers/supported_readers/`
2. Inherit from `FormatReader` interface
3. Register in `supplementary/readers/readers.py`
4. See `supplementary/README.md` for detailed instructions

### Code Style

The code is in black formatter style

## License

MIT License

Copyright (c) 2025 Persida-Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

