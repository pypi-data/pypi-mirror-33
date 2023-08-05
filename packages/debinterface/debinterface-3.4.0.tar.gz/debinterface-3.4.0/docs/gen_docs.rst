Generate Documentation
======================

Read the Docs builds it, but you need to prepare the doc source files

Extract and commit
-------------------------
.. sourcecode:: shell

    cd docs
    # Extract docstrings
    sphinx-apidoc -f -o . ../debinterface

    # Remove uneeded keywords
    ls *.rst | xargs -n 1 sed -i 's/\(module\|package\)$//g'

    # Clean
    make clean

    # If needed, update version in conf.py

    # Commit
    git add docs && git commit -m "Docs"


If you want to build the doc
----------------------------
.. sourcecode:: shell

    cd docs
    make html
    firefox _build/html/index.html
