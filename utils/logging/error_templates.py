import datetime
import traceback


# ERROR
def supplementary_file_error(source, error_message=""):
    # PMCid = source.split("_")[0]
    return f"{source} | {error_message}\n {traceback.format_exc()} \n"


# ERROR
def run_error(source):
    return f"{source} | RUN ERROR | \n {traceback.format_exc()} \n"

def pptx_slide_error(source, error_message=""):
    return f"{source} | {error_message}\n {traceback.format_exc()} \n"

# INFO
def saved_vs_not_saved_info(pmc_id, saved_files, not_saved_files):
    saved_files_str = ", ".join(saved_files)
    not_saved_files_str = ", ".join(not_saved_files)
    return f"{pmc_id} | \nSaved files: {saved_files_str}\nNot saved files: {not_saved_files_str}\n"

# INFO
def started_info(pmc_id):
    return f"{pmc_id} | STARTED | {datetime.datetime.now(datetime.timezone.utc).isoformat()}Z"

# INFO
def ended_info(pmc_id):
    return f"{pmc_id} | ENDED | {datetime.datetime.now(datetime.timezone.utc).isoformat()}Z"

def libreoffice_conversion_error(source):
    return f"{source} | LibreOffice conversion failed | {datetime.datetime.now(datetime.timezone.utc).isoformat()}Z"

def libreoffice_conversion_timeout(source):
    return f"{source} | LibreOffice conversion timed out | {datetime.datetime.now(datetime.timezone.utc).isoformat()}Z"