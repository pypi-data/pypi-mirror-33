from .version import __version__, version_info
from .utils import (
    eprint,
    join_cmd,
    check_dns,
    try_quit_xquartz,
    get_xquartz_open_windows,
    xquartz_is_open,
    quit_xquartz
)
from .pysectools import (
    zero,
    cmd_exists,
    Pinentry,
    PinentryException,
    PinentryUnavailableException,
    PinentryClosedException,
    PinentryErrorException
)
from .jupyter_remote import (
    main,
    JupyterRemote,
    CustomSSH,
    FilteredOut
)
from .config_manager import (
    JRMT_DEFAULTS,
    CFG_FILENAME,
    CFG_DIR,
    CFG_SEARCH_LOCATIONS,
    DNS_SERVER_GROUPS,
    ConfigManager,
    generate_config_file,
    get_base_arg_parser
)

__author__ = "Aaron Kollasch"
__date__ = "2018-03-18"
__copyright__ = "Copyright 2017-2018, Aaron Kollasch"
__email__ = "awkollasch@gmail.com"
__status__ = "Beta"
