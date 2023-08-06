"""
    experipy.config
    ~~~~~~~~~~~~~~~

    This module provides the Namespace class, which provides a mechanism 
    for defining collections of configurable constants.
"""
import os
import sys

if sys.version_info[0] == 2:
    import ConfigParser as configparser
else:
    import configparser


class Namespace(object):
    """Namespace objects are intended to act as collections of constants.

    All arguments passed to the Namespace when it is instantiated are 
    bound to attributes of the instance, allowing attribute reference as 
    opposed to dictionary access syntax. For example: 
    ``n = Namespace("N", foo="bar")`` would generate a namespace with an 
    attribute ``n.foo`` whose value is ``"bar"``. 

    Namespaces also support configuration using configparser INI files. 
    By default, configuration is stored and read from ``~/.experipyrc``, 
    unless the environment variable ``EXPERIPY_CONFIG_PATH`` is set, in 
    which case that value is used as the filename.

    Parameters
    ----------
    name : str
        The name to assign to the namespace. If not provided, the 
        resulting Namespace instance will be anonymous and not 
        configurable via the configuration file. 
    **kwargs :
        The remaining keyword arguments will be added the Namespace's
        dictionary, allowing for attribute access. If a name was 
        provided, and the namespace had a section in the configuration 
        file, conflicting arguments will have their values ignored in 
        favor of the value in the configuration file.
    """
    
    _config_file = os.getenv("EXPERIPY_CONFIG_PATH",
        os.path.expanduser("~/.experipyrc")
    )
    _config = configparser.RawConfigParser(allow_no_value=True)
    _config.read(_config_file)
    
    _registry = {}

    def __init__(self, name=None, **kwargs):
        self.attrs = dict(kwargs)
        self.name = name

        if name != None:
            self._register(name, self)

            # Override the defaults if they are specified in the config file
            if self._config.has_section(name):
                self.attrs.update(self._config.items(name))
    

    def __getattr__(self, name):
        try:
            return self.attrs[name]
        except KeyError:
            raise AttributeError("Namespace {} has no attribute: {}".format(
                self.name if self.name else "<unnamed>", name
            ))


    @classmethod
    def _register(cls, name, inst):
        """Record all named Namespaces who have been instantiated"""
        cls._registry[name] = inst


    @classmethod
    def dump_full_config(cls, fname=_config_file):
        """Write a config of all instantiated and preconfigured Namespaces.
        
        All instantiated and named Namespaces will be dumped to the 
        given file, along with any Namespace configurations which have 
        been loaded from the config, but whose corresponding Namespace 
        has not yet been instantiated.

        Parameters
        ----------
        fname : str
            Name of the file to write the config to. If not provided, it 
            will default to the current config file ("~/.experipyrc" or 
            the value of the EXPERIPY_CONFIG_PATH environment variable).
        """
        for name in cls._registry:
            if not cls._config.has_section(name):
                cls._config.add_section(name)

            ns = cls._registry[name]
            for attr in ns.attrs:
                cls._config.set(name, attr, ns.attrs[attr])

        with open(cls._config_file, 'w') as f:
            cls._config.write(f)


__all__ = [
    "Namespace",
]
