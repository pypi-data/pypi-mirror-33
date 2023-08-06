ThermoState
===========

This package provides a wrapper around
`CoolProp <https://github.com/CoolProp/CoolProp>`__ that more naturally
allows management of a thermodynamic state.

Continuous Integration Status
=============================

TravisCI: `Build
Status <https://travis-ci.org/bryanwweber/thermostate>`__ Appveyor:
`Build
status <https://ci.appveyor.com/project/bryanwweber/thermostate/branch/master>`__
`codecov <https://codecov.io/gh/bryanwweber/thermostate>`__

Anaconda Package Version
========================

`Anaconda-Server Badge
Version <https://anaconda.org/bryanwweber/thermostate>`__
`Anaconda-Server Badge
Downloads <https://anaconda.org/bryanwweber/thermostate>`__

Change Log
==========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/>`__
and this project adheres to `Semantic
Versioning <http://semver.org/>`__.

`Unreleased <https://github.com/bryanwweber/thermostate/compare/v0.3.0...master>`__
-----------------------------------------------------------------------------------

Added
~~~~~

Changed
~~~~~~~

Fixed
~~~~~

Removed
~~~~~~~

`0.3.0 <https://github.com/bryanwweber/thermostate/compare/v0.2.4...v0.3.0>`__ - 09-JUL-2018
--------------------------------------------------------------------------------------------

.. _fixed-1:

Fixed
~~~~~

-  Added flake8 configuration to setup.cfg since linter-flake8 reads it
   and ignores built-in options
-  Only define ``_render_traceback_`` if IPython is installed

.. _jul-2018-1:

`0.2.4 <https://github.com/bryanwweber/thermostate/compare/v0.2.3...v0.2.4>`__ - 08-JUL-2018
--------------------------------------------------------------------------------------------

.. _added-1:

Added
~~~~~

-  Added ``_render_traceback_`` function to improve traceback formatting
   of ``pint.DimensionalityError``

.. _fixed-2:

Fixed
~~~~~

-  Added ``oxygen``, ``nitrogen``, and ``carbondioxide`` as available
   substances to the Tutorial

`0.2.3 <https://github.com/bryanwweber/thermostate/compare/v0.2.2...v0.2.3>`__ - 24-SEP-2017
--------------------------------------------------------------------------------------------

.. _added-2:

Added
~~~~~

-  Distributions are now uploaded to PyPI

.. _changed-1:

Changed
~~~~~~~

-  Conda packages are ``noarch`` builds
-  Appveyor tests run in a single job to speed them up
-  Minimum Python version is 3.5

`0.2.2 <https://github.com/bryanwweber/thermostate/compare/v0.2.1...v0.2.2>`__ - 13-APR-2017
--------------------------------------------------------------------------------------------

.. _added-3:

Added
~~~~~

-  Oxygen (O2) is available as a substance
-  Nitrogen (N2) is available as a substance

.. _fixed-3:

Fixed
~~~~~

-  Deploy doctr to the root directory (see
   `drdoctr/doctr#157 <https://github.com/drdoctr/doctr/issues/157>`__
   and
   `drdoctr/doctr#160 <https://github.com/drdoctr/doctr/issues/160>`__)

`0.2.1 <https://github.com/bryanwweber/thermostate/compare/v0.2.0...v0.2.1>`__
------------------------------------------------------------------------------

.. _added-4:

Added
~~~~~

-  Carbon dioxide is available as a substance
-  The software version is available as the module-level ``__version__``
   attribute

.. _section-1:

`0.2.0 <https://github.com/bryanwweber/thermostate/compare/v0.1.7...v0.2.0>`__
------------------------------------------------------------------------------

.. _added-5:

Added
~~~~~

-  Equality comparison of ``State`` instances

.. _changed-2:

Changed
~~~~~~~

-  Improve several error messages
-  Refactor property getting/setting to use less boilerplate code
-  Preface all class attributes with ``_``
-  Refactor ``_set_properties`` to use CoolProp low-level API

.. _section-2:

`0.1.7 <https://github.com/bryanwweber/thermostate/compare/v0.1.6...v0.1.7>`__
------------------------------------------------------------------------------

.. _added-6:

Added
~~~~~

-  Phase as a gettable attribute of the State
-  Isobutane is an available substance
-  Add cp and cv to Tutorial

.. _changed-3:

Changed
~~~~~~~

-  Updated Tutorial with more detail of setting properties
-  Fail Travis when a single command fails

.. _section-3:

`0.1.6 <https://github.com/bryanwweber/thermostate/compare/v0.1.5...v0.1.6>`__
------------------------------------------------------------------------------

.. _added-7:

Added
~~~~~

-  Tutorial in the docs using ``nbsphinx`` for formatting
-  Specific heat capacities at constant pressure and volume are now
   accesible via cp and cv attributes

.. _changed-4:

Changed
~~~~~~~

-  Offset units are automatically converted to base units in Pint

.. _section-4:

`0.1.5 <https://github.com/bryanwweber/thermostate/compare/v0.1.4...v0.1.5>`__
------------------------------------------------------------------------------

.. _changed-5:

Changed
~~~~~~~

-  Unknown property pairs are no longer allowed to be set

.. _section-5:

`0.1.4 <https://github.com/bryanwweber/thermostate/compare/v0.1.3...v0.1.4>`__
------------------------------------------------------------------------------

.. _fixed-4:

Fixed
~~~~~

-  Rename units module to abbreviations so it no longer shadows units
   registry in thermostate

.. _section-6:

`0.1.3 <https://github.com/bryanwweber/thermostate/compare/v0.1.2...v0.1.3>`__
------------------------------------------------------------------------------

.. _added-8:

Added
~~~~~

-  Common unit abbreviations in thermostate.EnglishEngineering and
   thermostate.SystemInternational

.. _fixed-5:

Fixed
~~~~~

-  Typo in CHANGELOG.md

.. _section-7:

`0.1.2 <https://github.com/bryanwweber/thermostate/compare/v0.1.1...v0.1.2>`__
------------------------------------------------------------------------------

.. _fixed-6:

Fixed
~~~~~

-  Fix Anaconda.org upload keys

.. _section-8:

`0.1.1 <https://github.com/bryanwweber/thermostate/compare/v0.1.0...v0.1.1>`__
------------------------------------------------------------------------------

.. _fixed-7:

Fixed
~~~~~

-  Only load pytest-runner if tests are being run

.. _section-9:

`0.1.0 <https://github.com/bryanwweber/thermostate/compare/491975d84317abdaf289c01be02567ab33bbc390...v0.1.0>`__
----------------------------------------------------------------------------------------------------------------

.. _added-9:

Added
~~~~~

-  First Release
