##############
 requests-ecp
##############

`requests-ecp` provides a SAML/ECP authentication handler for
`Requests <http://requests.readthedocs.io/>`__ that implements the
`SAML 2.0 ECP Profile <https://docs.oasis-open.org/security/saml/Post2.0/saml-ecp/v2.0/cs01/saml-ecp-v2.0-cs01.html>`__.

============
Installation
============

.. tabs::

   .. tab:: Conda

      .. code-block:: bash

          $ conda install -c conda-forge requests-ecp

   .. tab:: Debian Linux

      .. code-block:: bash

          $ apt-get install python3-requests-ecp

      See the IGWN Computing Guide software repositories entry for
      `Debian <https://computing.docs.ligo.org/guide/software/debian/>`__
      for instructions on how to configure the required
      IGWN Debian repositories.

   .. tab:: Pip

      .. code-block:: bash

          $ python -m pip install requests-ecp

   .. tab:: Scientific Linux

      .. code-block:: bash

          $ yum install python3-requests-ecp

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
