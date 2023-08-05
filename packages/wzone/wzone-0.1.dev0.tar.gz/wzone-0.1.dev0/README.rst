Wzone
=====

Wzone is a package for generating zones of armed conflicts. The package contains functionalities 
for querying and creating conflict zones in the ESRI ASCII raster format. The methodological details 
can be found `here`_. The package greatly relies on the UCDPGED (version 17.1) compiled by
`the Uppsala Conflict Data Program`_.


Installing
----------

Install and update using `pip`_:

.. code-block:: text

    pip install --index-url https://test.pypi.org/simple/ wzone


An Example
----------------

.. code-block:: python

    import wzone
    
    # list of UCDPGED conflict IDs relevant to Somalia
    somalia_ids = wzone.find_ids(country = 'Somalia')
    
    # Yearly sequence of dates from the first to the last events
    somalia_dates = wzone.find_dates(ids = somalia_ids, interval = 'year')
    
    # create war zones for the first conflict ID (only the first 5 years for the purpose of test)
    somalia_paths = wzone.gen_wzones(dates=somalia_dates[0][0:4], ids=somalia_ids[0], out_dir='')
    
    # print the output file locations
    print somalia_paths


Links
-----

* Website: https://github.com/kyosuke-kkt/wzone/
* License: `MIT <https://github.com/kyosuke_kkt/wzone/LICENSE>`_
* Releases: https://pypi.org/project/wzone/

.. _here: aa//
.. _the Uppsala Conflict Data Program: http://ucdp.uu.se/
.. _pip: https://pip.pypa.io/en/stable/quickstart/