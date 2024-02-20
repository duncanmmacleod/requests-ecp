##############
 requests-ecp
##############

`requests-ecp` provides a SAML/ECP authentication handler for
`Requests <http://requests.readthedocs.io/>`__ that implements the
`SAML 2.0 ECP Profile <https://docs.oasis-open.org/security/saml/Post2.0/saml-ecp/v2.0/cs01/saml-ecp-v2.0-cs01.html>`__.

.. image:: https://img.shields.io/pypi/v/requests-ecp
    :target: https://pypi.org/project/requests-ecp/
    :alt: requests-ecp PyPI version badge
.. image:: https://img.shields.io/conda/vn/conda-forge/requests-ecp
    :target: https://anaconda.org/conda-forge/requests-ecp/
    :alt: requests-ecp Conda-forge version badge

.. image:: https://zenodo.org/badge/238942798.svg
    :target: https://zenodo.org/badge/latestdoi/238942798
    :alt: requests-ecp DOI badge
.. image:: https://img.shields.io/pypi/l/requests-ecp.svg
    :target: https://choosealicense.com/licenses/gpl-3.0/
    :alt: requests-ecp license badge
.. image:: https://img.shields.io/pypi/pyversions/requests-ecp.svg
    :alt: Supported Python versions badge

============
Installation
============

.. tab-set::
    .. tab-item:: Conda

        .. code-block:: bash

            conda install -c conda-forge requests-ecp

        The conda package includes the optional Kerberos Auth plugin
        from ``requests-gssapi``, which in turn ensures that a working
        GSSAPI implementation is installed.

        Installing with Conda (or Mamba) is the recommended installation
        method for `requests-ecp`.

    .. tab-item:: Debian Linux

        .. code-block:: bash

            apt-get install python3-requests-ecp

        See the IGWN Computing Guide software repositories entry for
        `Debian <https://computing.docs.ligo.org/guide/software/debian/>`__
        for instructions on how to configure the required
        IGWN Debian repositories.

    .. tab-item:: Pip

        .. code-block:: bash

            python -m pip install requests-ecp

        .. admonition:: Default ``pip install`` doesn't include Kerberos Auth support

           By default ``pip install requests-ecp`` does not bundle
           Kerberos auth support.
           This is provided by the
           `requests-gssapi <https://github.com/pythongssapi/requests-gssapi>`__
           package, which in turn relies on a working installation of GSSAPI
           (such as MIT Kerberos).

           The ``requests-ecp[kerberos]`` extra can be used to automatically
           include ``requests-gssapi``:

           .. code-block:: shell

               python -m pip install requests-ecp[kerberos]

           If you need Kerberos auth, and need to install GSSAPI itself on your
           system, it is recommended that you
           **use Conda to install `requests-ecp`**.

    .. tab-item:: Scientific Linux

       .. code-block:: bash

           yum install python3-requests-ecp

       See the IGWN Computing Guide software repositories entries for
       `Scientific Linux 7
       <https://computing.docs.ligo.org/guide/software/sl7/>`__
       or
       `Rocky Linux 8 <https://computing.docs.ligo.org/guide/software/rl8/>`__
       for instructions on how to configure the required IGWN Yum repositories.

==============================
``requests-ecp`` documentation
==============================

.. automodapi:: requests_ecp
   :no-inheritance-diagram:
   :no-heading:
   :headings: =-
