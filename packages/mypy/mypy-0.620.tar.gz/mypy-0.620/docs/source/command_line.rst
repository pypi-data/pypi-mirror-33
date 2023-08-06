.. _command-line:

The mypy command line
=====================

This section documents many of mypy's command line flags.  A quick
summary of command line flags can always be printed using the ``-h``
flag (or its long form ``--help``)::

  $ mypy -h
  usage: mypy [-h] [-v] [-V] [--python-version x.y] [--platform PLATFORM] [-2]
              [--ignore-missing-imports]
              [--follow-imports {normal,silent,skip,error}]
              [--disallow-any-unimported] [--disallow-any-expr]
              [--disallow-any-decorated] [--disallow-any-explicit]
              [--disallow-any-generics] [--disallow-untyped-calls]
              [--disallow-untyped-defs] [--disallow-incomplete-defs]
              [--check-untyped-defs] [--disallow-subclassing-any]
              [--warn-incomplete-stub] [--disallow-untyped-decorators]
              [--warn-redundant-casts] [--no-warn-no-return] [--warn-return-any]
              [--warn-unused-ignores] [--warn-unused-configs]
              [--show-error-context] [--no-implicit-optional] [--no-incremental]
              [--quick-and-dirty] [--cache-dir DIR] [--cache-fine-grained]
              [--skip-version-check] [--no-strict-optional]
              [--strict-optional-whitelist [GLOB [GLOB ...]]]
              [--always-true NAME] [--always-false NAME] [--junit-xml JUNIT_XML]
              [--pdb] [--show-traceback] [--stats] [--inferstats]
              [--custom-typing MODULE] [--custom-typeshed-dir DIR]
              [--scripts-are-modules] [--config-file CONFIG_FILE]
              [--show-column-numbers] [--find-occurrences CLASS.MEMBER]
              [--strict] [--shadow-file SOURCE_FILE SHADOW_FILE]
              [--any-exprs-report DIR] [--cobertura-xml-report DIR]
              [--html-report DIR] [--linecount-report DIR]
              [--linecoverage-report DIR] [--memory-xml-report DIR]
              [--txt-report DIR] [--xml-report DIR] [--xslt-html-report DIR]
              [--xslt-txt-report DIR] [-m MODULE] [-p PACKAGE] [-c PROGRAM_TEXT]
              [files [files ...]]

  (etc., too long to show everything here)

Specifying files and directories to be checked
**********************************************

You've already seen ``mypy program.py`` as a way to type check the
file ``program.py``.  More generally you can pass any number of files
and directories on the command line and they will all be type checked
together.

- Files ending in ``.py`` (and stub files ending in ``.pyi``) are
  checked as Python modules.

- Files not ending in ``.py`` or ``.pyi`` are assumed to be Python
  scripts and checked as such.

- Directories representing Python packages (i.e. containing a
  ``__init__.py[i]`` file) are checked as Python packages; all
  submodules and subpackages will be checked (subpackages must
  themselves have a ``__init__.py[i]`` file).

- Directories that don't represent Python packages (i.e. not directly
  containing an ``__init__.py[i]`` file) are checked as follows:

  - All ``*.py[i]`` files contained directly therein are checked as
    toplevel Python modules;

  - All packages contained directly therein (i.e. immediate
    subdirectories with an ``__init__.py[i]`` file) are checked as
    toplevel Python packages.

One more thing about checking modules and packages: if the directory
*containing* a module or package specified on the command line has an
``__init__.py[i]`` file, mypy assigns these an absolute module name by
crawling up the path until no ``__init__.py[i]`` file is found.  For
example, suppose we run the command ``mypy foo/bar/baz.py`` where
``foo/bar/__init__.py`` exists but ``foo/__init__.py`` does not.  Then
the module name assumed is ``bar.baz`` and the directory ``foo`` is
added to mypy's module search path.  On the other hand, if
``foo/bar/__init__.py`` did not exist, ``foo/bar`` would be added to
the module search path instead, and the module name assumed is just
``baz``.

If a script (a file not ending in ``.py[i]``) is processed, the module
name assumed is always ``__main__`` (matching the behavior of the
Python interpreter).

Other ways of specifying code to be checked
*******************************************

The flag ``-m`` (long form: ``--module``) lets you specify a module
name to be found using the default module search path.  The module
name may contain dots.  For example::

  $ mypy -m html.parser

will type check the module ``html.parser`` (this happens to be a
library stub).

The flag ``-p`` (long form: ``--package``) is similar to ``-m`` but
you give it a package name and it will type check all submodules and
subpackages (recursively) of that package.  (If you pass a package
name to ``-m`` it will just type check the package's ``__init__.py``
and anything imported from there.)  For example::

  $ mypy -p html

will type check the entire ``html`` package (of library stubs). One can
specify multiple packages and modules on the command line, for example::

  $ mypy --package p.a --package p.b --module c

Finally the flag ``-c`` (long form: ``--command``) will take a string
from the command line and type check it as a small program.  For
example::

  $ mypy -c 'x = [1, 2]; print(x())'

will type check that little program (and complain that ``List[int]``
is not callable).

Reading a list of files from a file
***********************************

Finally, any command-line argument starting with ``@`` reads additional
command-line arguments from the file following the ``@`` character.
This is primarily useful if you have a file containing a list of files
that you want to be type-checked: instead of using shell syntax like::

  mypy $(cat file_of_files)

you can use this instead::

  mypy @file_of_files

Such a file can also contain other flags, but a preferred way of
reading flags (not files) from a file is to use a
:ref:`configuration file <config-file>`.


.. _finding-imports:

How imports are found
*********************

When mypy encounters an `import` statement it tries to find the module
on the file system, similar to the way Python finds it.
However, there are some differences.

First, mypy has its own search path.
This is computed from the following items:

- The ``MYPYPATH`` environment variable
  (a colon-separated list of directories).
- The directories containing the sources given on the command line
  (see below).
- The installed packages marked as safe for type checking (see
  :ref:`PEP 561 support <installed-packages>`)
- The relevant directories of the
  `typeshed <https://github.com/python/typeshed>`_ repo.

For sources given on the command line, the path is adjusted by crawling
up from the given file or package to the nearest directory that does not
contain an ``__init__.py`` or ``__init__.pyi`` file.

Second, mypy searches for stub files in addition to regular Python files
and packages.
The rules for searching for a module ``foo`` are as follows:

- The search looks in each of the directories in the search path
  (see above) until a match is found.
- If a package named ``foo`` is found (i.e. a directory
  ``foo`` containing an ``__init__.py`` or ``__init__.pyi`` file)
  that's a match.
- If a stub file named ``foo.pyi`` is found, that's a match.
- If a Python module named ``foo.py`` is found, that's a match.

These matches are tried in order, so that if multiple matches are found
in the same directory on the search path
(e.g. a package and a Python file, or a stub file and a Python file)
the first one in the above list wins.

In particular, if a Python file and a stub file are both present in the
same directory on the search path, only the stub file is used.
(However, if the files are in different directories, the one found
in the earlier directory is used.)

NOTE: These rules are relevant to the following section too:
the ``--follow-imports`` flag described below is applied *after* the
above algorithm has determined which package, stub or module to use.

.. _follow-imports:

Following imports or not?
*************************

When you're first attacking a large existing codebase with mypy, you
may only want to check selected files.  For example, you may only want
to check those files to which you have already added annotations.
This is easily accomplished using a shell pipeline like this::

  mypy $(find . -name \*.py | xargs grep -l '# type:')

(While there are many improvements possible to make this example more
robust, this is not the place for a tutorial in shell programming.)

However, by default mypy doggedly tries to :ref:`follow imports
<finding-imports>`.  This may cause several types of problems that you
may want to silence during your initial conquest:

- Your code may import library modules for which no stub files exist
  yet.  This can cause a lot of errors like the following::

    main.py:1: error: No library stub file for standard library module 'antigravity'
    main.py:2: error: No library stub file for module 'flask'
    main.py:3: error: Cannot find module named 'sir_not_appearing_in_this_film'

  If you see only a few of these you may be able to silence them by
  putting ``# type: ignore`` on the respective ``import`` statements,
  but it's usually easier to silence all such errors by using
  :ref:`--ignore-missing-imports <ignore-missing-imports>`.

- Your project's directory structure may hinder mypy in finding
  certain modules that are part of your project, e.g. modules hidden
  away in a subdirectory that's not a package.  You can usually deal
  with this by setting the ``MYPYPATH`` variable (see
  :ref:`finding-imports`).

- When following imports mypy may find a module that's part of your
  project but which you haven't annotated yet, mypy may report errors
  for the top level code in that module (where the top level includes
  class bodies and function/method default values).  Here the
  ``--follow-imports`` flag comes in handy.

The ``--follow-imports`` flag takes a mandatory string value that can
take one of four values.  It only applies to modules for which a
``.py`` file is found (but no corresponding ``.pyi`` stub file) and
that are not given on the command line.  Passing a package or
directory on the command line implies all modules in that package or
directory.  The four possible values are:

- ``normal`` (the default) follow imports normally and type check all
  top level code (as well as the bodies of all functions and methods
  with at least one type annotation in the signature).

- ``silent`` follow imports normally and even "type check" them
  normally, but *suppress any error messages*. This is typically the
  best option for a new codebase.

- ``skip`` *don't* follow imports, silently replacing the module (and
  everything imported *from* it) with an object of type ``Any``.
  (This option used to be known as ``--silent-imports`` and while it
  is very powerful it can also cause hard-to-debug errors, hence the
  recommendation of using ``silent`` instead.)

- ``error`` the same behavior as ``skip`` but not quite as silent --
  it flags the import as an error, like this::

    main.py:1: note: Import of 'submodule' ignored
    main.py:1: note: (Using --follow-imports=error, module not passed on command line)

.. _disallow-any:

Disallow Any Flags
******************

The ``--disallow-any`` family of flags disallows various types of ``Any`` in a module.
The following options are available:

- ``--disallow-any-unimported`` disallows usage of types that come from unfollowed imports
  (such types become aliases for ``Any``). Unfollowed imports occur either
  when the imported module does not exist or when ``--follow-imports=skip``
  is set.

- ``--disallow-any-expr`` disallows all expressions in the module that have type ``Any``.
  If an expression of type ``Any`` appears anywhere in the module
  mypy will output an error unless the expression is immediately
  used as an argument to ``cast`` or assigned to a variable with an
  explicit type annotation. In addition, declaring a variable of type ``Any``
  or casting to type ``Any`` is not allowed. Note that calling functions
  that take parameters of type ``Any`` is still allowed.

- ``--disallow-any-decorated`` disallows functions that have ``Any`` in their signature
  after decorator transformation.

- ``--disallow-any-explicit`` disallows explicit ``Any`` in type positions such as type
  annotations and generic type parameters.

- ``--disallow-any-generics`` disallows usage of generic types that do not specify explicit
  type parameters. Moreover, built-in collections (such as ``list`` and
  ``dict``) become disallowed as you should use their aliases from the typing
  module (such as ``List[int]`` and ``Dict[str, str]``).


.. _additional-command-line-flags:

Additional command line flags
*****************************

Here are some more useful flags:

.. _ignore-missing-imports:

- ``--ignore-missing-imports`` suppresses error messages about imports
  that cannot be resolved (see :ref:`follow-imports` for some examples).
  This doesn't suppress errors about missing names in successfully resolved
  modules. For example, if one has the following files::

    package/__init__.py
    package/mod.py

  Then mypy will generate the following errors with ``--ignore-missing-imports``:

  .. code-block:: python

     import package.unknown  # No error, ignored
     x = package.unknown.func()  # OK

     from package import unknown  # No error, ignored
     from package.mod import NonExisting  # Error: Module has no attribute 'NonExisting'

- ``--no-strict-optional`` disables strict checking of ``Optional[...]``
  types and ``None`` values. With this option, mypy doesn't
  generally check the use of ``None`` values -- they are valid
  everywhere. See :ref:`no_strict_optional` for more about this feature.

  **Note:** Strict optional checking was enabled by default starting in
  mypy 0.600, and in previous versions it had to be explicitly enabled
  using ``--strict-optional`` (which is still accepted).

- ``--disallow-untyped-defs`` reports an error whenever it encounters
  a function definition without type annotations.

- ``--check-untyped-defs`` is less severe than the previous option --
  it type checks the body of every function, regardless of whether it
  has type annotations.  (By default the bodies of functions without
  annotations are not type checked.)  It will assume all arguments
  have type ``Any`` and always infer ``Any`` as the return type.

- ``--disallow-incomplete-defs`` reports an error whenever it
  encounters a partly annotated function definition.

- ``--disallow-untyped-calls`` reports an error whenever a function
  with type annotations calls a function defined without annotations.

- ``--disallow-untyped-decorators`` reports an error whenever a function
  with type annotations is decorated with a decorator without annotations.

.. _disallow-subclassing-any:

- ``--disallow-subclassing-any`` reports an error whenever a class
  subclasses a value of type ``Any``.  This may occur when the base
  class is imported from a module that doesn't exist (when using
  :ref:`--ignore-missing-imports <ignore-missing-imports>`) or is
  ignored due to :ref:`--follow-imports=skip <follow-imports>` or a
  ``# type: ignore`` comment on the ``import`` statement.  Since the
  module is silenced, the imported class is given a type of ``Any``.
  By default mypy will assume that the subclass correctly inherited
  the base class even though that may not actually be the case.  This
  flag makes mypy raise an error instead.

.. _incremental:

- Incremental mode enables a module cache, using results from
  previous runs to speed up type checking. Incremental mode can help
  when most parts of your program haven't changed since the previous
  mypy run.

  Incremental mode is the default and may be disabled with
  ``--no-incremental``.

- ``--cache-dir DIR`` is a companion flag to incremental mode, which
  specifies where the cache files are written.  By default this is
  ``.mypy_cache`` in the current directory.  While the cache is only
  read in incremental mode, it is written even in non-incremental
  mode, in order to "warm" the cache.  To disable writing the cache,
  use ``--cache-dir=/dev/null`` (UNIX) or ``--cache-dir=nul``
  (Windows).  Cache files belonging to a different mypy version are
  ignored.  This flag can be useful for controlling cache use when using
  :ref:`remote caching <remote-cache>`.

.. _quick-mode:

- ``--quick-and-dirty`` is an experimental, unsafe variant of
  :ref:`incremental mode <incremental>`.  Quick mode is faster than
  regular incremental mode, because it only re-checks modules that
  were modified since their cache file was last written (regular
  incremental mode also re-checks all modules that depend on one or
  more modules that were re-checked).  Quick mode is unsafe because it
  may miss problems caused by a change in a dependency.  Quick mode
  updates the cache, but regular incremental mode ignores cache files
  written by quick mode.

- ``--python-executable EXECUTABLE`` will have mypy collect type information
  from `PEP 561`_ compliant packages installed for the Python executable
  ``EXECUTABLE``. If not provided, mypy will use PEP 561 compliant packages
  installed for the Python executable running mypy. See
  :ref:`installed-packages` for more on making PEP 561 compliant packages.
  This flag will attempt to set ``--python-version`` if not already set.

- ``--python-version X.Y`` will make mypy typecheck your code as if it were
  run under Python version X.Y. Without this option, mypy will default to using
  whatever version of Python is running mypy. Note that the ``-2`` and
  ``--py2`` flags are aliases for ``--python-version 2.7``. See
  :ref:`version_and_platform_checks` for more about this feature. This flag
  will attempt to find a Python executable of the corresponding version to
  search for `PEP 561`_ compliant packages. If you'd like to disable this,
  see ``--no-site-packages`` below.

- ``--no-site-packages`` will disable searching for `PEP 561`_ compliant
  packages. This will also disable searching for a usable Python executable.
  Use this  flag if mypy cannot find a Python executable for the version of
  Python being checked, and you don't need to use PEP 561 typed packages.
  Otherwise, use ``--python-executable``.

- ``--platform PLATFORM`` will make mypy typecheck your code as if it were
  run under the given operating system. Without this option, mypy will
  default to using whatever operating system you are currently using. See
  :ref:`version_and_platform_checks` for more about this feature.

.. _always-true:

- ``--always-true NAME`` will treat all variables named ``NAME`` as
  compile-time constants that are always true.  May be repeated.

- ``--always-false NAME`` will treat all variables named ``NAME`` as
  compile-time constants that are always false.  May be repeated.

- ``--show-column-numbers`` will add column offsets to error messages,
  for example, the following indicates an error in line 12, column 9
  (note that column offsets are 0-based):

  .. code-block:: python

     main.py:12:9: error: Unsupported operand types for / ("int" and "str")

- ``--scripts-are-modules`` will give command line arguments that
  appear to be scripts (i.e. files whose name does not end in ``.py``)
  a module name derived from the script name rather than the fixed
  name ``__main__``.  This allows checking more than one script in a
  single mypy invocation.  (The default ``__main__`` is technically
  more correct, but if you have many scripts that import a large
  package, the behavior enabled by this flag is often more
  convenient.)

- ``--custom-typeshed-dir DIR`` specifies the directory where mypy looks for
  typeshed stubs, instead of the typeshed that ships with mypy.  This is
  primarily intended to make it easier to test typeshed changes before
  submitting them upstream, but also allows you to use a forked version of
  typeshed.

.. _config-file-flag:

- ``--config-file CONFIG_FILE`` causes configuration settings to be
  read from the given file.  By default settings are read from ``mypy.ini``
  or ``setup.cfg`` in the current directory, or ``.mypy.ini`` in the user home
  directory.  Settings override mypy's built-in defaults and command line flags
  can override settings. See :ref:`config-file` for the syntax of configuration
  files.

- ``--junit-xml JUNIT_XML`` will make mypy generate a JUnit XML test
  result document with type checking results. This can make it easier
  to integrate mypy with continuous integration (CI) tools.

- ``--find-occurrences CLASS.MEMBER`` will make mypy print out all
  usages of a class member based on static type information. This
  feature is experimental.

- ``--cobertura-xml-report DIR`` causes mypy to generate a Cobertura
  XML type checking coverage report.

- ``--warn-no-return`` causes mypy to generate errors for missing return
  statements on some execution paths. Mypy doesn't generate these errors
  for functions with ``None`` or ``Any`` return types. Mypy
  also currently ignores functions with an empty body or a body that is
  just ellipsis (``...``), since these can be valid as abstract methods.
  This option is on by default.

- ``--warn-return-any`` causes mypy to generate a warning when returning a value
  with type ``Any`` from a function declared with a non- ``Any`` return type.

- ``--strict`` mode enables all optional error checking flags.  You can see the
  list of flags enabled by strict mode in the full ``mypy -h`` output.

.. _shadow-file:

- ``--shadow-file SOURCE_FILE SHADOW_FILE``: when mypy is asked to typecheck
  ``SOURCE_FILE``, this makes it read from and typecheck the contents of
  ``SHADOW_FILE`` instead. However, diagnostics will continue to refer to
  ``SOURCE_FILE``. Specifying this argument multiple times
  (``--shadow-file X1 Y1 --shadow-file X2 Y2``)
  will allow mypy to perform multiple substitutions.

  This allows tooling to create temporary files with helpful modifications
  without having to change the source file in place. For example, suppose we
  have a pipeline that adds ``reveal_type`` for certain variables.
  This pipeline is run on ``original.py`` to produce ``temp.py``.
  Running ``mypy --shadow-file original.py temp.py original.py`` will then
  cause mypy to typecheck the contents of ``temp.py`` instead of  ``original.py``,
  but error messages will still reference ``original.py``.

.. _no-implicit-optional:

- ``--no-implicit-optional`` causes mypy to stop treating arguments
  with a ``None`` default value as having an implicit ``Optional[...]``
  type.

For the remaining flags you can read the full ``mypy -h`` output.

.. note::

   Command line flags are liable to change between releases.

.. _PEP 561: https://www.python.org/dev/peps/pep-0561/

.. _integrating-mypy:

Integrating mypy into another Python application
************************************************

It is possible to integrate mypy into another Python 3 application by
importing ``mypy.api`` and calling the ``run`` function with a parameter of type ``List[str]``, containing
what normally would have been the command line arguments to mypy.

Function ``run`` returns a ``Tuple[str, str, int]``, namely
``(<normal_report>, <error_report>, <exit_status>)``, in which ``<normal_report>``
is what mypy normally writes to ``sys.stdout``, ``<error_report>`` is what mypy
normally writes to ``sys.stderr`` and ``exit_status`` is the exit status mypy normally
returns to the operating system.

A trivial example of using the api is the following::

    import sys
    from mypy import api

    result = api.run(sys.argv[1:])

    if result[0]:
        print('\nType checking report:\n')
        print(result[0])  # stdout

    if result[1]:
        print('\nError report:\n')
        print(result[1])  # stderr

    print ('\nExit status:', result[2])
