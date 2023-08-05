===========================
Color schemes for Astrality
===========================

This is a simple module which defines several sets of color schemes to be used in `Astrality <https://astrality.readthedocs.io/en/latest/readme.html>`_ templates. 

At the moment, the module contains the following color schemes:

* `gruvbox_light <https://github.com/morhetz/gruvbox>`_
* `gruvbox_dark <https://github.com/morhetz/gruvbox>`_
* `solarized_light <http://ethanschoonover.com/solarized>`_
* `solarized_dark <http://ethanschoonover.com/solarized>`_

Pull requests with new color schemes are welcome.


How to install
==============

Install the module by adding the following to ``astrality.yml``:

.. code-block:: yaml

    config/modules:
        enabled_modules:
            - name: github::jakobgm/color-schemes.astrality


How to configure
================

You can configure which color scheme that is imported into Astrality's context, and what you want to name that context section. The default values are as following:

.. code-block:: yaml

    context/color_schemes_config:
        enabled: gruvbox_dark
        context_section: colors


How to use
==========

Each color scheme defines the following color groups:

``background``
    Integer indexed colors, starting from 1, the primary background color, with additional colors 2, 3, and so on for contrast. Most often the same color but with different shades.

``foreground``
    Same as ``background``, only for colors meant for foreground elements, such as letters, etc..

``primary``
    The primary colors used by the specific color scheme. Also integer indexed. These colors are often more colorful. You can use these values to set colors when you don't care exactly which colors you want to use, but you want colors from the color scheme.

``normal``
    For when you need a *specific* color from your color scheme. Each color scheme includes the following colors (although some of these may be duplicates of each other): black, red, green, yellow, blue, purple, aqua, gray, magenta, cyan, orange, white.

``bright``
    Same as ``normal`` but with a brighter shade.


Examples
========

Here are two examples of Astrality modules using these color scheme context values:

* `Setting the color scheme of the kitty terminal emulator <https://github.com/JakobGM/astrality/blob/master/astrality/config/modules/terminals/kitty.conf.template>`_.
* `Setting the color scheme of the polybar status bar utility <https://github.com/JakobGM/astrality/blob/master/astrality/config/modules/polybar/config.template>`_.
