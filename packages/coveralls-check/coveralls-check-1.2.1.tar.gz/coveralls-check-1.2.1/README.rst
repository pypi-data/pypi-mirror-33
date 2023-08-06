|Travis|_ |Coveralls|_

.. |Travis| image:: https://api.travis-ci.org/cjw296/coveralls-check.svg?branch=master
.. _Travis: https://travis-ci.org/cjw296/coveralls-check

.. |Coveralls| image:: https://coveralls.io/repos/cjw296/coveralls-check/badge.svg?branch=master
.. _Coveralls: https://coveralls.io/r/cjw296/coveralls-check?branch=master

coveralls-check
================

A small helper to check https://coveralls.io for a given commit hash.

Development takes place here:
https://github.com/cjw296/coveralls-check/

Usage
-----

This was designed for use with Travis CI `Build Stages`__ where you want
to check code coverage before doing a deployment or release.

__ https://docs.travis-ci.com/user/build-stages/

A sample ``.travis.yml`` using it is as follows::

    language: python

    sudo: false

    env:
      secure: "..."

    python:
      - "2.7"
      - "3.6"

    install:
      - "pip install --upgrade pip setuptools"
      - "pip install -Ue .[test]"

    script: coverage run --source ... -m py.test

    after_success:
      - "COVERALLS_PARALLEL=true coveralls"

    jobs:
      include:

        - stage: coverage
          python: 3.6
          after_success: skip

          install: "pip install -U coveralls-check"
          script: "coveralls-check $TRAVIS_COMMIT --parallel-build-number $TRAVIS_BUILD_NUMBER --repo-token $COVERALLS_REPO_TOKEN"

The ``COVERALLS_REPO_TOKEN`` is set in the ``secure`` section, which can be obtained using::

    travis encrypt COVERALLS_REPO_TOKEN=(your coveralls repo token)

Changes
-------

1.2.1 (11 Jul 2018)
-------------------

- Fix packaging and copyright.

1.2.0 (11 Jul 2018)
-------------------

- Add support for Coveralls parallel build stuff.

1.1.0 (14 Sep 2017)
~~~~~~~~~~~~~~~~~~~

- Add retrying logic to wait up to 5 minutes, by default, for coveralls
  coverage data to be ready.

1.0.1 (17 Aug 2017)
~~~~~~~~~~~~~~~~~~~

- Fix packaging.

1.0.0 (17 Aug 2017)
~~~~~~~~~~~~~~~~~~~

- Initial release
