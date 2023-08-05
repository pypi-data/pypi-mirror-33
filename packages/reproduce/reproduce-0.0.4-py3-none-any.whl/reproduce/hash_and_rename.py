"""Script to hash and rename files."""
import os
import sys
import shutil
import logging

import reproduce

logging.basicConfig()
LOGGER = logging.getLogger(__name__)


def main():
    """Entry point."""
    base_path = sys.argv[1]
    target_dir = sys.argv[2]

    hash_algorithm = 'md5'
    LOGGER.info('hash file')
    hash_value = reproduce.hash_file(base_path, hash_algorithm)
    base, ext = os.path.splitext(base_path)
    target_path = '%s_%s_%s%s' % (base, hash_algorithm, hash_value, ext)
    LOGGER.info('copy to %s', target_path)
    shutil.copyfile(base_path, target_path)


if __name__ == '__main__':
    main()
