Overview
========

This is a rendering server that will wrap an OpenOffice/LibreOffice server and provide
a pythonic API which is remotely callable.

The main advantage is that your client code does not need to import pyuno... This
is a main plus because pyuno is a pain to get working on Windows and some flavors of
Linux, don't even think of Mac :)

Once you deploy a py3o.renderserver all you need in your python code is to use the
`py3o.renderclient`_ which is really straightforward...

Deployment
==========

We recommend you use the dockerized versions from the `dockerhub`_

Using this way you'll get the latest tested version of LibreOffice and
py3o.renderserver without the hassle of building all the dependencies...

If you want to have templating fusion & document convertion in one
single web service usable from any language with just HTTP/POST you can install
`py3o.fusion`_ server. Which also exists as a `docker image`_

Manual Installation
===================

Requirements
~~~~~~~~~~~~

Install the latest JDK for your plateform. Here is an example for
Ubuntu (13.04 or 14.04)::

  apt-get install default-jdk

This will give you the necessary tools to compile the juno driver.

You will need to install (and compile) the `py3o.renderers.juno`_ driver.


Follow the instructions from the driver's documentation to install it and
then you're ready to start your own RenderServer

Running the server
~~~~~~~~~~~~~~~~~~

Here is how we start the server on a Linux host (Ubuntu 16.04)::

  $ start-py3o-renderserver --java=/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/amd64/server/libjvm.so --ure=/usr/lib/libreoffice --office=/usr/share --driver=juno --sofficeport=8997

You MUST have a  running LibreOffice (OpenOffice) server somewhere. In our example it is running on localhost with port 8997. Here is how you can start such a server on Linux (Ubuntu 13.04 / LibreOffice 4.0.4)::

  $ libreoffice --nologo --norestore --invisible --headless --nocrashreport --nofirststartwizard --nodefault --accept="socket,host=localhost,port=8997;urp;"

As you can see it works with OpenJDK, LibreOffice and even on 64bit systems :)

.. _dockerhub: https://registry.hub.docker.com/u/xcgd/py3oserver-docker/
.. _py3o.renderers.juno: http://bitbucket.org/faide/py3o.renderers.juno
.. _py3o.renderclient: http://bitbucket.org/faide/py3o.renderclient
.. _py3o.fusion: http://bitbucket.org/faide/py3o.fusion
.. _docker image: https://registry.hub.docker.com/u/xcgd/py3o.fusion


