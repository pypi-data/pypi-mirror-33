Developers documentation
========================

Development process
-------------------

silx follows a peer-review development process based on the `github flow<https://guides.github.com/introduction/flow/>`_
(See `scikit-image contribution documentation<http://scikit-image.org/docs/stable/contribute.html#development-process>`_).

General guidelines
------------------

See `scikit-image guidelines<http://scikit-image.org/docs/stable/contribute.html#guidelines>`_.

Coding convention
-----------------

silx follows `PEP 8<https://www.python.org/dev/peps/pep-0008/>`_ keeping in mind its recommendation:

.. container::

  A style guide is about consistency.
  Consistency with this style guide is important.
  Consistency within a project is more important.
  Consistency within one module or function is the most important.

  However, know when to be inconsistent -- sometimes style guide recommendations just aren't applicable.
  When in doubt, use your best judgment.
  Look at other examples and decide what looks best.
  And don't hesitate to ask!

  In particular: do not break backwards compatibility just to comply with this PEP!

Therefore in GUI with inheritance from Qt, camelCase will be the preferred coding style.
External modules integrated in the library will follow the coding style of the external module.

- Whenever possible refer to array as row, column not x, y
  (See `scikit-image coordinate conventions<http://scikit-image.org/docs/stable/user_guide/numpy_images.html#numpy-images-coordinate-conventions>`_)
  This might not be possible in the GUI part where coordinate convention is x, y.

``silx.gui`` coding convention
------------------------------

This package mostly contains objects inherited from Qt, thus it follows Qt style.
But the way to describe a ``QObject`` in Python (with getter, setter, properties) does not allow to respect it.
Here are some recommendations:

- Follow the Qt style as much as possible

  - That is particularly important for the public API
  - CamelCase for all the package
  - For widget constructor

    - ``parent=None`` as first argument, and no other mandatory arguments
      (it is needed to promote widget with Qt designer).
    - Avoid as much as possible other arguments

  - Avoid Python properties or attributes, use ``value()`` instead of ``value``
  - Prefer prefixing getter and setter with ``get``, ``is``, ``set``...
    (it avoid hiding getter when we also define a Qt property).
  - Lower case or camel case but no ``_`` for arguments
    (lower case is inherited from matplotlib conventions)
  - Signals can be prefixed by ``sig``
    (``sig`` allows to identify and list signals easily)
  - Manipulate as much as possible Qt style objects

- Do not use right-click for interaction purpose, keep it for context menu.


How-to add icons
================

silx icons are stored in ``silx/resources/gui/icons/``.
Icons should be provided as both a SVG file and a 32x32 PNG file.

Animated icons should be provided as both a MNG file and a folder with the same name containing a serie of PNG files with number as filename: 00.png, 01.png, ...

For maximum compatibility, here are a few recommendation to produce SVG icons:

- It should be SVG 1.1.
- It should not contain raster images (even embedded).
  This makes files smaller and does not rely on a decompression library (it occured that libjpeg was not available)
- The text should use a free font.
- The text should be converted to paths.
  As its font might not be available everywhere.

Steps to create an icon:

- Create an icon with `inkscape <https://inkscape.org/fr/>`_ (or another authoring tool), save it as SVG and export it as a 32x32 PNG file.
- Then, optimize the SVG file with `scour <https://github.com/scour-project/scour>`_::

    scour -i input.svg -o output.svg --enable-viewboxing --enable-id-stripping --enable-comment-stripping --shorten-ids --indent=none --remove-metadata

  .. warning:: By default all icons are copyrighted ESRF and available under the MIT license.
  If an icon has a different copyright/license, then provide the copyright/license in the SVG file and optimize it without the ``--remove-metadata`` option.
  Also update the ``copyright`` file at the root of the project.
- Update the icons gallery in the documentation by running the ``doc/source/modules/gui/update_icons_rst.py`` script.

