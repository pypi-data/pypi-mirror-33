Run the tests
=============

We use pytest, but unittest is still the used style. I plan on linking this codecov or similar.

Tox is used by Travis CI to run tests on python 2.7, 3.4 and 3.5


Full test on your machine
-------------------------
.. sourcecode:: shell

    cd test
    py.test --cov=debinterface test

To have it work with breakpoints
--------------------------------
.. sourcecode:: shell

    cd test
    py.test --cov=debinterface test -s
