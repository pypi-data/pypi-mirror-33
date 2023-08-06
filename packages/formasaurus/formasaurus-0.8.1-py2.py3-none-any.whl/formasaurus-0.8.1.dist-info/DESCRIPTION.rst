===========
Formasaurus
===========

.. image:: https://img.shields.io/pypi/v/Formasaurus.svg
   :target: https://pypi.python.org/pypi/Formasaurus
   :alt: PyPI Version

.. image:: https://img.shields.io/travis/TeamHG-Memex/Formasaurus/master.svg
   :target: http://travis-ci.org/TeamHG-Memex/Formasaurus
   :alt: Build Status

.. image:: http://codecov.io/github/TeamHG-Memex/Formasaurus/coverage.svg?branch=master
   :target: http://codecov.io/github/TeamHG-Memex/Formasaurus?branch=master
   :alt: Code Coverage

.. image:: https://readthedocs.org/projects/formasaurus/badge/?version=latest
   :target: http://formasaurus.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation


Formasaurus is a Python package that tells you the type of an HTML form
and its fields using machine learning.

It can detect if a form is a login, search, registration, password recovery,
"join mailing list", contact, order form or something else, which field
is a password field and which is a search query, etc.

License is MIT.

Check `docs <http://formasaurus.readthedocs.org/>`_ for more.

----

.. image:: https://hyperiongray.s3.amazonaws.com/define-hg.svg
	:target: https://www.hyperiongray.com/?pk_campaign=github&pk_kwd=formasaurus
	:alt: define hyperiongray


Changes
=======

0.8.1 (2018-07-02)
------------------

* Support for scikit-learn < 0.18 is dropped;
* Formasaurus is no longer tested with Python 3.3;
* tests are fixed to account for upstream changes; Python 3.6 build is enabled.

0.8 (2016-05-24)
----------------

* more annotated data for captchas;
* ``formasaurus init`` command which trains & caches the model.

0.7.2 (2016-04-18)
------------------

* pip bug with ``pip install formasaurus[with-deps]`` is worked around;
  it should work now as ``pip install formasaurus[with_deps]``.

0.7.1 (2016-03-03)
------------------

* fixed API documentation at readthedocs.org

0.7 (2016-03-03)
----------------

* more annotated data;
* new ``form_classes`` and ``field_classes`` attributes of FormFieldClassifer;
* more robust web page encoding detection in ``formasaurus.utils.download``;
* bug fixes in annotation widgets;

0.6 (2016-01-27)
----------------

* ``fields=False`` argument is supported in ``formasaurus.extract_forms``,
  ``formasaurus.classify``, ``formasaurus.classify_proba`` functions and
  in related ``FormFieldClassifier`` methods. It allows to avoid predicting
  form field types if they are not needed.
* ``formasaurus.classifiers.instance()`` is renamed to
  ``formasaurus.classifiers.get_instance()``.
* Bias is no longer regularized for form type classifier.

0.5 (2015-12-19)
----------------

This is a major backwards-incompatible release.

* Formasaurus now can detect field types, not only form types;
* API is changed - check the updated documentation;
* there are more form types detected;
* evaluation setup is improved;
* annotation UI is rewritten using IPython widgets;
* more training data is added.

0.2 (2015-08-10)
----------------

* Python 3 support;
* fixed model auto-creation.

0.1 (2015-07-09)
----------------

Initial release.


