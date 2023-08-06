===================
Importing list data
===================

If you have the ``config.pck`` file for a version 2.1 mailing list, you can
import that into an existing mailing list in Mailman 3.0.

    >>> command = cli('mailman.commands.cli_import.import21')

You must specify the mailing list you are importing into, and it must exist.

    >>> command('mailman import21')
    Usage: ... [OPTIONS] LISTSPEC PICKLE_FILE
    <BLANKLINE>
    Error: Missing argument "listspec".

You must also specify a pickle file to import.

    >>> command('mailman import21 import@example.com')
    Usage: ... [OPTIONS] LISTSPEC PICKLE_FILE
    <BLANKLINE>
    Error: Missing argument "pickle_file".

Too bad the list doesn't exist.

    >>> from pkg_resources import resource_filename
    >>> pickle_file = resource_filename('mailman.testing', 'config.pck')
    >>> command('mailman import21 import@example.com ' + pickle_file)
    Usage: ... [OPTIONS] LISTSPEC PICKLE_FILE
    <BLANKLINE>
    Error: No such list: import@example.com

When the mailing list exists, you must specify a real pickle file to import
from.
::

    >>> mlist = create_list('import@example.com')
    >>> transaction.commit()
    >>> command('mailman import21 import@example.com ' + __file__)
    Usage: ... [OPTIONS] LISTSPEC PICKLE_FILE
    <BLANKLINE>
    Error: Not a Mailman 2.1 configuration file: .../import.rst'...

Now we can import the test pickle file.  As a simple illustration of the
import, the mailing list's "real name" will change.
::

    >>> print(mlist.display_name)
    Import

    >>> command('mailman import21 import@example.com ' + pickle_file)
    >>> print(mlist.display_name)
    Test
