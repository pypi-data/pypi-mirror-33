import logging
from pathlib import Path


def new_file_check(infile_path: [Path, str], outfile_path: [Path, str],
                   force: bool = False) -> bool:
    """
    Checks for existence of new source file to process.
    1. If force = True or outfile_path doesn't exist return True
    2. If outfile_path exists and infile_path is newer than outfile_path
    then return True.
    4. Else return False
    """

    try:
        infile_path = Path(infile_path)
        outfile_path = Path(outfile_path)
        if force:
            logging.debug('new_file_check set to force so returning True')
            return True
        elif infile_path.exists() and not outfile_path.exists():
            logging.debug("outfile_path doesn't exist so returning True")
            return True
        elif not infile_path.exists():
            logging.debug("infile_path doesn't exist so returning True")
            return False
        elif infile_path.stat().st_mtime_ns > outfile_path.stat().st_mtime_ns:
            logging.debug("outfile_path doesn't exist so returning True")
            return True
        else:
            logging.info('No conditions met so returning False')
            return False
    except Exception as e:
        logging.exception(e)
