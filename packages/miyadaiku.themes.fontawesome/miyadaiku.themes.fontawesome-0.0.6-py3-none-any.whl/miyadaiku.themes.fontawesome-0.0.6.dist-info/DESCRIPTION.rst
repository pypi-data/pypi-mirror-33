
Font Awesome files for miyadaiku static site generator
========================================================

Provides Font Awesome files.


Installation
-------------------

Use pip command to install Font Awesome. 

::

   $ pip install miyadaiku.themes.fontawesome


Configuraion
----------------------


In your config.yml file of your project, add following configuration at `themes` section.

::

   themes:
     - miyadaiku.themes.fontawesome    # <---- add this line


Usage
----------------------

Add following code to your template files.

::

  <!-- include fontawesome -->
  {{ fontawesome.load_css(page) }}



