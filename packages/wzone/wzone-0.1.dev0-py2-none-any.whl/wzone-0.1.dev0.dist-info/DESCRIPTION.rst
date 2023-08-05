Copyright (c) 2018 Kyosuke Kikuta

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
Description-Content-Type: UNKNOWN
Description: Wzone
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
Platform: UNKNOWN
Classifier: Development Status :: 3 - Alpha
Classifier: Environment :: Console
Classifier: Intended Audience :: End Users/Desktop
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: Microsoft :: Windows :: Windows 10
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Programming Language :: Python :: 2.7
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Requires-Python: >=2.7
