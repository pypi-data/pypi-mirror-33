Babel extractor for vue.js
==========================

|Build Status| |Coverage Status|

Babel messages extractor for vue.js templates.

*vue.js* — Reactive Components for Modern Web Interfaces. Site:
http://vuejs.org/.

*Babel* — Internationalization library for Python. Site:
http://babel.pocoo.org/.

.. image:: https://raw.githubusercontent.com/nonamenix/babel-vue-extractor/master/babel_vuejs.png

Install
-------

.. code::

    pip install babel-vue-extractor

Usage
-----

Add to your babel config

.. code::

    [babelvueextractor.extract.extract_vue: **.vue]


Usage in .vhtml files
---------------------

.. code::

    <h1>{{ gettext('Hello') }}</h1>
    <p> {{ ngettext('Foo', 'Foos', 1) }} </p>
    <p> {{ gettext('Processed by filter')|somefilter }} </p>
    <div v-text="gettext('Sometext')"></div>
    <div :text="gettext('Sometext')"></div>


Issue Tracking
--------------

GitHub: `https://github.com/nonamenix/babel-vue-extractor/issues <https://github.com/nonamenix/babel-vue-extractor/issues>`_



.. |Build Status| image:: https://travis-ci.org/nonamenix/babel-vue-extractor.svg
   :target: https://travis-ci.org/nonamenix/babel-vue-extractor
   :alt: Build Status

.. |Coverage Status| image:: https://coveralls.io/repos/nonamenix/babel-vue-extractor/badge.svg?branch=master&service=github&v=0.1.3.1
   :target: https://coveralls.io/github/nonamenix/babel-vue-extractor?branch=master
   :alt: Coverage Status
   
