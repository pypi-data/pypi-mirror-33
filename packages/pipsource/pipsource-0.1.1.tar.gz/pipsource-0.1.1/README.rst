pipsource
---------

manage source of pipenv projects

Use
---

.. code-block:: shell

    $ pipsource list
    Pypi                https://pypi.org/simple

    Douban              https://pypi.douban.com/simple

    Tencent             https://mirrors.cloud.tencent.com/pypi/simple

    Aliyun              https://mirrors.aliyun.com/pypi/simple/
    $ pipsource show

    Tencent             https://mirrors.cloud.tencent.com/pypi/simple
    $ pipsource use pypi
    # It may take a long time in a project with many dependencies.
    Changed Pipfile's source to Pypi
    $ pipsource show

    Pypi                https://pypi.org/simple
    $ pipsource --help

    Usage: pipsource [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      list  List trusted sources
      show  Show the current source
      use   Change the source with the name specificed



Install
-------

.. code-block:: shell
    
    pip install pipsource


Author
------
Yixian Du
