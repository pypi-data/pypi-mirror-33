Server environment for Magento Connector
========================================

This module is based on the `server_environment` module to use files for
configuration.  Thus we can have a different configutation for each
environment (dev, test, staging, prod).  This module define the config
variables for the `magentoerpconnect` module.

In the configuration file, you can configure the url, login and
password of the Magento Backends.

Exemple of the section to put in the configuration file::

    [magento_backend.name_of_the_backend]
    location = http://localhost/magento/
    username = my_api_login
    password = my_api_password



