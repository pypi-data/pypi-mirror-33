Gitlab-stats
------------

`Github <https://github.com/Sylhare/gitlab_stats>`__ |Gitlab| |Python|
`Build Status <https://travis-ci.org/Sylhare/gitlab_stats>`__
`codecov <https://codecov.io/gh/Sylhare/gitlab_stats>`__ `Codacy
Badge <https://www.codacy.com/app/Sylhare/gitlab_stats?utm_source=github.com&utm_medium=referral&utm_content=Sylhare/gitlab_stats&utm_campaign=Badge_Grade>`__

Get to the gitlab API and generates a report based on the pipeline
builds. Creates a report for the pipelines of the last two weeks. (On
the assumption that there are less than 100 push per 2 weeks)

Installation
~~~~~~~~~~~~

Install via pip using:

.. code:: bash

   pip install gitlab_stats

Local install with pip3:

.. code:: bash

   pip3 install -e .   

In order to make it work:

-  Create a ``GITLAB_TOKEN`` env variable with your access token.

Get the project ID
~~~~~~~~~~~~~~~~~~

For the script to work, you will need to get the project ID of your
gitlab project. It is a unique ID that is used by the gitlab REST API to
store your project information.

Get it in
``[your project] > Settings > General > General project settings``

|image2|

How to use
~~~~~~~~~~

When installed you should be able to run it like that:

.. code:: bash

   gitlab_stats <id> -u <your gitlab url> -p <your proxy>

Here is the help when ``gitlab_stats -h``:

.. code:: bash

   usage: gitlab_stats [-h] [-r] [-u URL] [-p PROXY] id

   gitlab_stats: Generate a report from gitlab's pipeline metrics

   positional arguments:
     id                    Put the id of the gitlab project

   optional arguments:
     -h, --help                show this help message and exit
     -r, --report              Generate a csv report
     -u URL, --url URL         Put the url of your gitlab instance if different from
                               https://gitlab.com
     -p PROXY, --proxy PROXY   Add the url of your proxy like
                               'http://my.proxy.url:8083'

.. |Gitlab| image:: https://img.shields.io/badge/gitlab_api-v4-orange.svg
.. |Python| image:: https://img.shields.io/badge/python-3.6.x-yellow.svg
.. |image2| image:: ../screenshot.png

