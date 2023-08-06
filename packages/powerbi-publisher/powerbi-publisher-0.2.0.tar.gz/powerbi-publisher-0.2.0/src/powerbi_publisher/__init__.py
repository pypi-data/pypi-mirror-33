from pkg_resources import get_distribution, DistributionNotFound, Distribution


__project__ = 'powerbi_publisher'
__version__ = '0.2.0'
__dist__ = Distribution(project_name=str(__project__),
                        version=str(__version__))

try:
    __dist__ = get_distribution(__project__)  # type: Distribution
    __version__ = __dist__.version
except DistributionNotFound:
    # This will happen if the package is not installed.
    # For more informations about development installation, read about
    # the 'develop' setup.py command or the '--editable' pip option.
    # Note that development installations may break other packages from
    # the same implicit namespace
    # (see https://github.com/pypa/packaging-problems/issues/12)
    pass
else:
    pass


class SetuppyError(Exception):
    pass
