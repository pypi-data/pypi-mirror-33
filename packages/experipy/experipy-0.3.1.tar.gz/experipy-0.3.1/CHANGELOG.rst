====================
 Experipy Changelog
====================

Version 0.3.1
-------------

- Added support for `-h` and `-n` PBS options

Version 0.3.0
-------------

- More bugfixes
- Added dest argument to :func:`exp.Experiment.queue` to allow targeting a
  specific resource queue
- Added :class:`~metrics.Metric` for automatically extracting values from 
  results files.
- Renamed :module:`utils` to :module:`config`
- Added :func:`~dump_config` shortcut for 
  :func:`~config.Namespace.dump_full_config`.

Version 0.2.0
-------------

- Various bugfixes
- Added support for configuration of namespaces via an ``~/.experipyrc`` file
  using ConfigParser.
- Added :func:`~utils.Namespace.dump_full_config` helper for generating the 
  config file.

Version 0.1.0
-------------

First public release.
