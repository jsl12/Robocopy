from pathlib import Path
from subprocess import call
from datetime import datetime
import re


def Robocopy(
    source,
    destination,
    files=None,
    test=False,
    subdirs=False,
    empty=False,
    copy=None,
    dcopy=None,
    purge=False,
    mirror=False,
    move=False,
    monitor_changes=None,
    monitor_time=None,
    exclude_files=None,
    exclude_folders=None,
    exclude_changed=False,
    exclude_newer=False,
    exclude_older=False,
    exclude_extra=False,
    exclude_lonely=False,
    include_same=False,
    include_tweaked=False,
    max_size=None,
    min_size=None,
    max_age=None,
    min_age=None,
    max_lad=None,
    min_lad=None,
    exclude_junc=True,
    retries=None,
    wait=None,
    no_header=False,
    no_progress=False,
    no_filenames=False,
    full_paths=False,
    no_filesizes=False,
    no_folders=False,
    no_summary=False,
    log=None,
    log_append=None,
    console_output=True,
    execute=True,
):
    """
    Wrapper for the builtin Windows robocopy function

    Supported Keyword Arguments:
        files
        test            /l          Specifies that files are to be listed only (and not copied, deleted, or time stamped).
        subdirs         /s          Copies subdirectories, excluding empty directories.
        empty           /e          Copies subdirectories, including empty directories.
        copy            /copy:      Specifies the file properties to be copied. The following are the valid values for this option:
                                        D - Data
                                        A - Attributes
                                        T - Time Stamps
                                        S - NTFS access control list (ACL)
                                        O - Owner Information
                                        U - Auditing information
        dcopy           /dcopy:     Defines what to copy for directories.
        purge           /purge      Deletes destination files and directories that no longer exist in the source.
        mirror          /mir        Mirrors a directory tree (equivalent to /e plus /purge).
        move            /move       Moves files and directories, and deletes them from the source after they are copied.
        monitor_changes /mon:N      Monitors the source, and runs again when more than N changes are detected.
        monitor_time    /mot:M      Monitors source, and runs again in M minutes if changes are detected.
        exclude_files   /xf         Excludes files that match the specified names or paths. Note that FileName can include wildcard characters (* and ?).
        exclude_folders /xd         Excludes directories that match the specified names and paths.
        exclude_changed /xc         Excludes changed files.
        exclude_newer   /xn         Excludes newer files.
        exclude_older   /xo         Excludes older files. If destination file exists and is the same date or newer than the source - don’t bother to overwrite it.
        exclude_extra   /xx         Excludes extra files and directories (present in destination but not source). This will prevent any deletions from the destination. (this is the default)
        exclude_lonely  /xl         Excludes "lonely" files and directories (present in source but not destination). This will prevent any new files being added to the destination.
        include_same    /is         Includes the same files.
        include_tweaked /it         Includes "tweaked" files.
        max_size        /max:N      Specifies the maximum file size (to exclude files bigger than N bytes).
        min_size        /min:N      Specifies the minimum file size (to exclude files smaller than N bytes).
        max_age         /maxage:N   Specifies the maximum file age (to exclude files older than N days or date).
        min_age         /minage:N   Specifies the minimum file age (exclude files newer than N days or date).
        max_lad         /maxlad:N   Specifies the maximum last access date (excludes files used since N) If N is less than 1900, N specifies the number of days. Otherwise, N specifies a date in the format YYYYMMDD
        min_lad         /minlad:N   Specifies the minimum last access date (excludes files used since N) If N is less than 1900, N specifies the number of days. Otherwise, N specifies a date in the format YYYYMMDD
        exclude_junc    /xj         Excludes junction points (default)
        retries         /r:N        Specifies the number of retries on failed copies. The default value of N is 1,000,000 (one million retries).
        wait            /w:N        Specifies the wait time between retries, in seconds. The default value of N is 30 (wait time 30 seconds).
        no_header       /njh        Specifies that there is no job header.
        no_progress     /np         Specifies that the progress of the copying operation (the number of files or directories copied so far) will not be displayed.
        no_filenames    /nfl        Specifies that file names are not to be logged.
        full_paths      /fp         Includes the full path names of the files in the output.
        no_filesizes    /ns         Specifies that file sizes are not to be logged.
        no_folders      /ndl        Specifies that directory names are not to be logged.
        no_summary      /njs        Specifies that there is no job summary.
        log             /log:Path   Writes the status output to the log file (overwrites the existing log file).
        log_append      /log+:Path  Writes the status output to the log file (appends the output to the existing log file).
        console_output  /tee        Writes the status output to the console window, as well as to the log file.
    """
    assert isinstance(source, Path), 'source is not a Path object'
    assert isinstance(destination, Path), 'destination is not a Path object'
    assert source.exists(), 'source path does not exist:\n{}'.format(source)

    arg_vals = locals()

    cmd = ['robocopy']
    for path in [source, destination]:
        cmd.append('"{}"'.format(path))

    def opts_chars(switch, value):
        assert isinstance(value, str), 'value for {} must be a string'.format(switch)
        try:
            valid = {
                'copy': 'datso',
                'dcopy': 'dat'
            }[switch]
        except:
            print('{} not pre-defined in opts_chars'.format(switch))
        regex = re.compile('^[{}]+$'.format(valid))
        assert regex.match(value.lower()), 'invalid options for {}:{}'.format(switch, value)
        return '/{}:{}'.format(switch, value.upper())

    def opts_list(switch, value):
        base = {
            'files': '',
            'exclude_files': '/xf',
            'exclude_folders': '/xd'
        }[switch]
        if isinstance(value, list):
            res = [i.strip() for i in value if isinstance(i, str)] + ['"{}"'.format(i) for i in value if isinstance(i, Path)]
            res = ' '.join(res)
        elif isinstance(value, str):
            res = value.strip()

        return '{} {}'.format(base, res)

    def opts_num(switch, value):
        base = {
            'max_size': '/max',
            'min_size': '/min',
            'max_age': '/maxage',
            'min_age': '/minage',
            'max_lad': '/maxlad',
            'min_lad': '/minlad',
            'retries': '/r',
            'wait': '/w',
            'monitor_changes': '/mon',
            'monitor_time': '/mot'
        }[switch]
        if isinstance(value, datetime):
            assert 'age' in switch
            value = int(value.strftime('%Y%m%d'))
        return '{}:{}'.format(base, int(value))

    def opts_path(switch, value):
        base = {
            'log': '/log',
            'log_append': '/log+'
        }[switch]
        if isinstance(value, str):
            value = Path(value)
        assert value.suffix == '.txt'
        if not value.parents[0].exists():
            value.parents[0].mkdir()

        return '{}:"{}"'.format(base, value)

    switches = {
        'files': opts_list,
        'test': '/l',
        'subdirs': '/s',
        'empty': '/e',
        'copy': opts_chars,
        'dcopy': opts_chars,
        'purge': '/purge',
        'mirror': '/mir',
        'move': '/move',
        'monitor_changes': opts_num,
        'monitor_time': opts_num,
        'exclude_files': opts_list,
        'exclude_folders': opts_list,
        'exclude_changed': '/xc',
        'exclude_newer': '/xn',
        'exclude_older': '/xo',
        'exclude_extra': '/xx',
        'exclude_lonely': '/xl',
        'include_same': '/is',
        'include_tweaked': '/it',
        'max_size': opts_num,
        'min_size': opts_num,
        'max_age': opts_num,
        'min_age': opts_num,
        'max_lad': opts_num,
        'min_lad': opts_num,
        'exclude_junc': '/xj',
        'retries': opts_num,
        'wait': opts_num,
        'no_header': '/njh',
        'no_progress': '/np',
        'no_filenames': '/nfl',
        'full_paths': '/fp',
        'no_filesizes': '/ns',
        'no_folders': '/ndl',
        'no_summary': '/njs',
        'log': opts_path,
        'log_append': opts_path,
        'console_output': '/tee'
    }

    def process_switch(name):
        if name in arg_vals:
            sw = switches[name]
            val = arg_vals[name]

            if val is not None:
                if isinstance(val, bool) and isinstance(sw, str):
                    if val:
                        cmd.append(sw)
                elif callable(sw):
                        cmd.append(sw(name, val))
        else:
            print('{} is not an argument'.format(name))

    for key in switches:
        process_switch(key)

    cmd = ' '.join(cmd)

    print(cmd)

    if execute:
        call(cmd)
    return cmd