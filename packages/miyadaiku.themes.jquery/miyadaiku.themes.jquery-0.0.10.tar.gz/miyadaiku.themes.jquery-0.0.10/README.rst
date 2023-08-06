
jQuery files for miyadaiku static site generator
========================================================

Provides jQuery files.


Installation
-------------------

Use pip command to install jQuery. 

::

   $ pip install miyadaiku.themes.jquery


Configuraion
----------------------


In your config.yml file of your project, add following configuration at `themes` section.

::

   themes:
     - miyadaiku.themes.jquery    # <---- add this line


Usage
----------------------

Add following code to your template files.

::

   <!-- include jquery.js -->
   {{ jquery.load_js(page) }}

