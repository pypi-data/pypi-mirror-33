
fullPage.js files for miyadaiku static site generator
========================================================

Provides `fullPage.js <https://alvarotrigo.com/fullPage/>`_ files.


Installation
-------------------

Use pip command to install fullPage.js

::

   $ pip install miyadaiku.themes.fullpagejs


Configuraion
----------------------


In your config.yml file of your project, add following configuration at `themes` section.

::

   themes:
     - miyadaiku.themes.fullpagejs # <---- add this line


Usage
----------------------

Add following code to your template files.

::

   <!-- include jquery.js -->
   {{ jquery.load_js(page) }}

   <!-- include fullPage.js -->
   {{ fullpagejs.load(page) }}
