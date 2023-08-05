'''
Serves annotation related files for downloads.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2011-10-03
'''
# future
from __future__ import with_statement
from __future__ import absolute_import

# standard
from os import close as os_close, remove
from os.path import join, dirname, basename, normpath
from os.path import split, exists

from tempfile import mkstemp
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

# third party
from six.moves import range

# arat
from server.document import real_directory
from server.annotation import open_textfile
from server.common import NoPrintJSONError
from subprocess import Popen


def download_file(document, collection, extension):
    """
    Send file content
    TODO: don't rely on NoPrintJSONError to encapsulate the data
          a better mechanism must be designed
    TODO: potential security hole, extensive tests must be written
    """
    directory = collection
    real_dir = real_directory(directory)
    fname = '%s.%s' % (document, extension)
    fpath = join(real_dir, fname)

    hdrs = [('Content-Type', 'text/plain; charset=utf-8'),
            ('Content-Disposition', 'inline; filename=%s' % fname)]
    with open_textfile(fpath, 'r') as txt_file:
        data = txt_file.read().encode('utf-8')
    raise NoPrintJSONError(hdrs, data)


def find_in_directory_tree(directory, filename):
    """
    TODO: DRY; partial dup of projectconfig.py:__read_first_in_directory_tree
    """
    try:
        from config import BASE_DIR
    except ImportError:
        BASE_DIR = "/"

    depth = 0
    directory, BASE_DIR = normpath(directory), normpath(BASE_DIR)
    while BASE_DIR in directory:
        if exists(join(directory, filename)):
            return (directory, depth)
        directory = split(directory)[0]
        depth += 1
    return (None, None)


def download_collection(collection, include_conf=False):
    directory = collection
    real_dir = real_directory(directory)
    dir_name = basename(dirname(real_dir))
    fname = '%s.%s' % (dir_name, 'tar.gz')

    confs = ['annotation.conf', 'visual.conf', 'tools.conf',
             'kb_shortcuts.conf']

    try:
        include_conf = int(include_conf)
    except ValueError:
        pass

    tmp_file_path = None
    try:
        tmp_file_fh, tmp_file_path = mkstemp()
        os_close(tmp_file_fh)

        tar_cmd_split = ['tar', '--exclude=.stats_cache']
        conf_names = []
        if not include_conf:
            tar_cmd_split.extend(['--exclude=%s' % c for c in confs])
        else:
            # also include configs from parent directories.
            for cname in confs:
                _, depth = find_in_directory_tree(real_dir, cname)
                if depth is not None and depth > 0:
                    relpath = join(
                        dir_name, *['..' for _ in range(depth)])
                    conf_names.append(join(relpath, cname))
            if conf_names:
                # replace pathname components ending in ".." with target
                # directory name so that .confs in parent directories appear
                # in the target directory in the tar.
                tar_cmd_split.extend(['--absolute-names', '--transform',
                                      's|.*\\.\\.|%s|' % dir_name])

        tar_cmd_split.extend(['-c', '-z', '-f', tmp_file_path, dir_name])
        tar_cmd_split.extend(conf_names)
        tar_p = Popen(tar_cmd_split, cwd=join(real_dir, '..'))
        tar_p.wait()

        hdrs = [('Content-Type', 'application/octet-stream'),  # 'application/x-tgz'),
                ('Content-Disposition', 'inline; filename=%s' % fname)]
        with open(tmp_file_path, 'rb') as tmp_file:
            tar_data = tmp_file.read()

        raise NoPrintJSONError(hdrs, tar_data)
    finally:
        if tmp_file_path is not None:
            remove(tmp_file_path)
