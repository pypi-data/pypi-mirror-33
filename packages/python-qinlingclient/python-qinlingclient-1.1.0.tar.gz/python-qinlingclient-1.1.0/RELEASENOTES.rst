====================
python-qinlingclient
====================

.. _python-qinlingclient_1.1.0:

1.1.0
=====

.. _python-qinlingclient_1.1.0_Prelude:

Prelude
-------

.. releasenotes/notes/support-function-resource-limitation-f6f519999f5e23cd.yaml @ b'd8a375a8607c09e0815725817adc32298eca571d'

Support to specify the resource(memory/cpu) limitation when creating the function.


.. _python-qinlingclient_1.1.0_New Features:

New Features
------------

.. releasenotes/notes/support-function-resource-limitation-f6f519999f5e23cd.yaml @ b'd8a375a8607c09e0815725817adc32298eca571d'

- End user could restrict the resource consumption for the function execution
  by specifying ``--cpu`` and ``--memory-size`` when creating the function.
  Those resource limitation has the default value if not provided, please
  refer to Qinling documentation for more details.

.. releasenotes/notes/support-function-version-for-job-7cb12ebb9fd64456.yaml @ b'82b2cbb506d7dfe7b418eb8b2a05888d444a8e7e'

- The end user can create job by specifying function version, default value is 0 if it's not provided.

.. releasenotes/notes/support-function-version-for-webhook-67beca9f1c78eb58.yaml @ b'5a883de93788788d1aa46892d14ad40be7b76ef9'

- The user can create or update webhook by specifying the function version (``--function-version``) together with the function.

.. releasenotes/notes/support-resource-name-cd26d0edbd56bdc5.yaml @ b'c7f40f65c1d83d1230a42a3176c59637605d1c54'

- Support resource name in CLI, specifically runtime name in function operations and function name in the operations of other resources like execution, function version, job and webhook.


.. _python-qinlingclient_1.0.0:

1.0.0
=====

.. _python-qinlingclient_1.0.0_New Features:

New Features
------------

.. releasenotes/notes/function-versioning-81881bc35bc3eb64.yaml @ b'727cd89632650428c14bc7a2b5eb6a8d93584630'

- Support function versioning CLI.

