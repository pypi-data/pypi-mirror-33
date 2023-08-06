robobrowserquery
~~~~~~~~~~~~~~~~

.. image:: https://secure.travis-ci.org/ytyng/robobrowserquery.svg?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/ytyng/robobrowserquery

.. image:: https://img.shields.io/pypi/v/robobrowserquery.svg
    :target: https://pypi.python.org/pypi/robobrowserquery/
    :alt: Latest PyPI version

PyQuery on RoboBrowser

RoboBrowser: https://github.com/jmcarp/robobrowser

recommend: pip install git+https://github.com/M157q/robobrowser/


PyQuery: https://pythonhosted.org/pyquery/


install
=======

pip install robobrowserquery



How to use
==========

::

    from robobrowserquery import RoboBrowserQuery

    browser = RoboBrowserQuery()

    browser.open('https://www.mangazenkan.com/')

    f = browser.get_form()
    f['name'].value = 'Tokyo'
    browser.submit_form(f)

    print(browser.query('title').text())
    for a in browser.query('a').items():
        print(a.attr('href'))
