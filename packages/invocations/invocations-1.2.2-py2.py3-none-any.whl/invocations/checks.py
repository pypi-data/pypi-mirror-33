"""
Tasks for common project sanity-checking such as linting or type checking.

.. versionadded:: 1.2
"""

from __future__ import unicode_literals

from invoke import task


@task(name="blacken", iterable=["folders"])
def blacken(c, line_length=79, folders=None, check=False, diff=False):
    """
    Run black on the current source tree (all ``.py`` files).

    .. warning::
        ``black`` only runs on Python 3.6 or above. (However, it can be
        executed against Python 2 compatible code.)

    :param int line_length:
        Line length argument. Default: ``79``.
    :param list folders:
        List of folders (or, on the CLI, an argument that can be given N times)
        to search within for ``.py`` files. Default: ``["."]``. Honors the
        ``blacken.folders`` config option.
    :param bool check:
        Whether to run ``black --check``. Default: ``False``.
    :param bool diff:
        Whether to run ``black --diff``. Default: ``False``.

    .. versionadded:: 1.2
    """
    default_folders = ["."]
    configured_folders = c.config.get("blacken", {}).get(
        "folders", default_folders
    )
    folders = folders or configured_folders

    black_command_line = "black -l {}".format(line_length)
    if check:
        black_command_line = "{} --check".format(black_command_line)
    if diff:
        black_command_line = "{} --diff".format(black_command_line)

    cmd = "find {} -name '*.py' | xargs {}".format(
        " ".join(folders), black_command_line
    )
    c.run(cmd, pty=True)
