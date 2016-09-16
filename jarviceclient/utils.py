#!/usr/bin/env python
#
# Copyright (c) 2016, Nimbix, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nimbix, Inc.
#
# Author: Stephen Fox (stephen.fox@nimbix.net)

import os
import logging
import sys
import stat
import time
from . import exceptions
from . import JarviceAPI

logging.basicConfig()

try:
    import paramiko
except ImportError:
    sys.write.stderr("Please install paramiko. Upload and download will not "
                     "function without this dependency.")


def _format_status(filename, current, total):
    """Wrapper to print progress while uploading.
    """
    progress = 0
    if total > 0:
        progress = float(current)/float(total)*100
        sys.stdout.write("\r%(filename)s %(percent)d %% "
                         "(%(current)s B of %(total)s B)" % {
                             'filename': filename,
                             'percent': int(progress),
                             'current': str(current),
                             'total': str(total)})
        sys.stdout.flush()


def _remote_path_exists(sftp, remote_path):
    exists = False
    try:
        sftp.normalize(remote_path)
        exists = True
    except IOError:
        exists = False
    return exists


def _remote_path_isdir(sftp, remote_path):
    if _remote_path_exists(sftp, remote_path):
        mode = sftp.stat(remote_path).st_mode
        if stat.S_ISDIR(mode) and not stat.S_ISLNK(mode):
            return True
    return False


def _remote_path_isfile(sftp, remote_path):
    if _remote_path_exists(sftp, remote_path):
        mode = sftp.stat(remote_path).st_mode
        if stat.S_ISREG(mode) and not stat.S_ISLNK(mode):
            return True
    return False


def _download_file(sftp, remote_path, local_path=None):
    """Wrapper to download a single file
    """
    remote_filename = os.path.basename(remote_path)
    if not local_path:
        local_path = remote_filename
    else:
        local_directory = os.path.dirname(os.path.abspath(local_path))
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)

    sftp.get(remote_path, local_path)


def _upload_file(sftp, local_path, remote_path):
    """Wrapper to upload a single file.

    Raises:
       paramiko.sftp.SFTPError: Internal paramiko error due to SSH connection
         or other issues.
       IOError: Local file does not exist or cannot be read; post-transfer file
         sanity checks (size, etc...) fail
       Exception: Unknown failures
    """
    # local_path_stat = os.stat(local_path)
    # if not os.path.exists(local_path):
    #     logging.error("Skipping %s. Path does not exist.")

    #     or \
    #    not stat.S_ISREG(local_path_stat.st_mode):
    #     logging.error('%s is not a regular file.' % (local_path))

    # Create remote directories if necessary
    try:
        logging.info("Uploading %s to %s" % (
            local_path,
            remote_path))
        sftp.put(local_path, remote_path)
    except paramiko.sftp.SFTPError as e:
        logging.error("SFTP Error %s" % e.message)
        raise
    except IOError as e:
        logging.error("IOError %s" % e.message)
        raise
    except Exception:
        logging.error("Failure to upload %s %s" % (local_path,
                                                   remote_path))
        raise


def _filter_valid(filename):
    """Simple filter for ignoring hidden files
    """
    # TODO: this filter function is currently unused
    # TODO: Add glob-style filtering
    if len(filename) > 0 and os.path.basename(filename)[0] != '.':
        return True
    else:
        return False


def _create_remote_path(sftp, remote_path):
    current = '.'
    for d in remote_path.split('/'):
        current = current + '/' + d
        try:
            sftp.normalize(current)
        except IOError:
            sftp.mkdir(current)


def _put_dir(sftp, local_path, remote_path, overwrite=False):
    """Put local_path tree onto drop.jarvice.com. This method
    is not meant to be called directly by a user.

    If remote path is none, creates a path with the same basename as
    local_path.

    Args:
      sftp(paramiko.SFTPClient): Active paramiko sftp client
      local_path(str): Root of local destination. Defaults to
         current local_path retrieved by os.getcwd()
      remote_path(str): Root of remote path to recursively copy. If not
         provided, then will mirror the absolute path of local_path with
         /data/ prepended.
      overwrite(bool): Overwrite file if it exists in remote path. Default
         is false. Writes paths to stderr if error occurs.
    """
    try:
        _create_remote_path(sftp, remote_path)
    except IOError:
        logging.critical("Failure to create remote directory: %(remote_path)s"
                         % {'remote_path': remote_path})
        raise

    try:
        for item in os.listdir(local_path):
            full_path = os.path.join(local_path, item)
            if not os.access(full_path, os.R_OK):
                logging.error("Skipping %s. Path is not readable." % full_path)
                continue
            mode = os.stat(full_path).st_mode
            destination = os.path.join(remote_path, item)
            if stat.S_ISREG(mode):
                try:
                    _upload_file(sftp, full_path, destination)
                except paramiko.sftp.SFTPError as e:
                    message = "Skipping %(local)s. Failure uploading %(local)s"
                    " to %(remote)s with error %(message)s." %\
                        {'local': full_path,
                         'remote': destination,
                         'message': e.message}
                    logging.warning(message)
                    continue
                except Exception as e:
                    logging.critical("Failure uploading %s to %s" %
                                     (full_path,
                                      os.path.join(remote_path, item)))
                    raise
            elif stat.S_ISDIR(mode):
                _put_dir(sftp, full_path,
                         os.path.join(remote_path, item))
            else:
                logging.warning("Skipping %s. Path is invalid type." %
                                full_path)
                continue
    except Exception:
        logging.critical("Failure uploading %s to %s" %
                         (local_path, remote_path))
        raise


def _get_dir(sftp, remote_path, local_path, overwrite=False):
    """Recusrively walk remote_path and transfer to local_path mirroring
    the directory structure.

    Args:
      sftp(paramiko.SFTPClient): Active paramiko sftp client
      remote_path(str): Root of remote path to recursively copy.
      local_path(str): Root of local destination. Defaults to current directory
         retrieved by os.getcwd()
      overwrite(bool): Overwrite file if exists in local path. Default False.
         writes path to stderr if error occurs.
    """
    try:
        sftp.normalize(remote_path)
    except IOError:
        logging.critical("Remote directory %s does not exist" % (remote_path))
        raise

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    for item in sftp.listdir_attr(remote_path):
        # If directory, copy it to current local directory recusrively
        if stat.S_ISDIR(item.st_mode) and not stat.S_ISLNK(item.st_mode):
            next_remote_directory = os.path.join(remote_path, item.filename)
            next_local_directory = os.path.join(local_path, item.filename)
            logging.info("Copying %s to %s" % (next_remote_directory,
                                               local_path))
            _get_dir(sftp, remote_path=next_remote_directory,
                     local_path=next_local_directory)
        # If a file, cocpy the file to current local directory
        elif stat.S_ISREG(item.st_mode) or stat.S_ISLNK(item.st_mode):
            remote_file_path = os.path.join(remote_path, item.filename)
            local_file_path = os.path.join(local_path, item.filename)
            try:
                sftp.get(remote_file_path, local_file_path)
            except IOError as e:
                message = "IOError %s - %s" % (e.errno, e.strerror)
                logging.critical("IOError transferring %(remote)s to %(local)s"
                                 % {'remote': remote_file_path,
                                    'local': local_file_path})
                raise exceptions.DownloadException(message)
        else:
            message = "Unknown error downloading directory %s to %s" %\
                      (remote_path, local_path)
            logging.critical(message)
            raise exceptions.DownloadException(message)


def _download_dir(sftp, remote_path, local_path=None):
    if not local_path:
        basename = os.path.basename(remote_path)
        local_path = basename
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    _get_dir(sftp, remote_path, local_path)


def _upload_dir(sftp, local_path, remote_path=None):
    if not remote_path:
        remote_path = os.path.basename(local_path)
    _put_dir(sftp, local_path, remote_path)


def _get_sftp_client(username, apikey):
    """Construct a paramiko SFTP client connected to drop.jarvice.com
    using the user's Nimbix credentials.

    Args:
      username(str): Nimbix username for platform.jarvice.com
      apikey(str): Nimbix apikey for platform.jarvice.com
    """
    transport = paramiko.Transport(('drop.jarvice.com', 22))
    transport.connect(username=username, password=apikey)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp


def ls(username, apikey, remote_path):
    sftp = _get_sftp_client(username, apikey)
    try:
        result = sftp.listdir(remote_path)
    except Exception:
        logging.error("%(remote_path)s does not exist" %
                      {'remote_path': remote_path})
        raise
    return result


def upload(username, apikey, local_path, remote_path=None, overwrite=False):
    """Upload files to username@drop.jarvice.com

    Args:
      username(str): Jarvice username
      apikey(str): Jarvice API key available at platform.jarvice.com
      local_path(str): relative or absolute path to local file or directory
      remote_path(str): file destination or directory
      recursive(bool): Like -r in cp; recursively uploads entire directory
    Raises:
      jarviceclient.exceptions.UploadException if:
         - local path does not exist
         - remote path exists but overwrite is false
         - remote path exists but is an unrecognized type (not a regular file
           or directory)
    """
    sftp = _get_sftp_client(username, apikey)

    if os.path.exists(local_path):
        is_dir = os.path.isdir(local_path)
    else:
        message = 'Local path %(local_path)s does not exist!' % {
            'local_path': local_path
        }
        raise exceptions.UploadException(message)

    if is_dir:
        if remote_path is None:
            remote_path = os.path.dirname(local_path)
        if _remote_path_exists(sftp, remote_path) and not overwrite:
            message = "Remote path exists"
            logging.error(message)
            raise exceptions.UploadException(message)
        _create_remote_path(sftp, remote_path)
        _put_dir(sftp, local_path, remote_path)
    else:
        # This is a file. Construct the remote path as
        # remote_directory + basename(local_file).
        if remote_path is None:
            remote_directory = './'
            remote_filename = os.path.basename(local_path)
            destination_path = os.path.join(remote_directory, remote_filename)
        else:
            # If remote path is specified, check if it exists
            if _remote_path_exists(sftp, remote_path):
                if _remote_path_isdir(sftp, remote_path):
                    remote_directory = remote_path
                    remote_filename = os.path.basename(local_path)
                    destination_path = os.path.join(remote_directory,
                                                    remote_filename)
                elif _remote_path_isfile(sftp, remote_path):
                    if not overwrite:
                        # Do not overwrite if it is a file
                        message = "Remote path exists."
                        logging.error(message)
                        raise exceptions.UploadException(message)
                    else:
                        destination_path = remote_path
                else:
                    message = 'Remote path unknown'
                    logging.critical("%s :Remote path %s exists but is not"
                                     " a recognized type." % (message,
                                                              remote_path))
                    raise exceptions.UploadException(message)
            else:
                destination_path = remote_path
                # remote_path is defined, but does not exist on the remote
                remote_directory = os.path.dirname(destination_path)
                if remote_directory != '' and remote_directory != '.':
                    _create_remote_path(sftp, remote_directory)
        sftp.put(local_path, destination_path)


def download(username, apikey, remote_path, local_path, overwrite=False):
    """Download files from username@drop.jarvice.com

    Args:
      username(str): Jarvice username
      apikey(str): Jarvice API key available at platform.jarvice.com
      local_path(str): relative or absolute path to local file or directory
      remote_path(str): file destination or directory
      recursive(bool): Like -r in cp; recursively uploads entire directory
    """
    sftp = _get_sftp_client(username, apikey)

    if _remote_path_exists(sftp, remote_path):
        if _remote_path_isfile(sftp, remote_path):
            _download_file(sftp, remote_path, local_path)
        else:
            _download_dir(sftp, remote_path, local_path)


def wait_for(username, apikey, number=None, name=None):
    """Polls /jarvice/status endpoint until job completes.

    Args:
      username(str): Jarvice username
      apikey(str): Jarvice API key available at platform.jarvice.com
      job_number(str): Jarvice job number
      job_name(str): Jarvice job name
    """
    if not number and not name:
        raise Exception("number or name is required")

    first_iteration = True

    while True:
        result, error = JarviceAPI.Client.status(username, apikey,
                                                 number=number, name=name)

        if error:
            raise Exception("Could not query job status %s" % error)
        else:
            status = result.get(result.keys()[0])['job_status']
            if status.lower() not in JarviceAPI.Client.COMPLETED_STATUSES:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(5)
                first_iteration = False
                continue
            else:
                if not first_iteration:
                    # Add a linebreak after the .....
                    sys.stdout.write('\n')
                job_id = number if number else name
                sys.stdout.write('Job %s ended with Status: %s\n' %
                                 (job_id, status))
                return
