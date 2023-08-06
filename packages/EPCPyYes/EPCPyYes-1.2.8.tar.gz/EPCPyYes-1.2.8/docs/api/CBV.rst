Core Business Vocabulary Modules
--------
The *Core Business Vocabulary* (CBV) module is mostly a collection of
enumerated values that, as such, make the development of CVB/EPCIS applications
considerably easier and much less prone to error.  For most Python development
environments, this module will enable code-completion for the various
enumerations within this module.  To represent any of the enumeration values
in your code as a python string, reference the `.value` property of the enum
value in question.  For example:

   >>> from EPCPyYes.core.v1_2.CBV.dispositions import Disposition
   >>> print(Disposition.encoded.value)
   urn:epcglobal:cbv:disp:encoded

CBV Helper Functions
=========
The helper functions assist in the creation of properly formed URN values
for use in EPCIS events.

.. automodule:: EPCPyYes.core.v1_2.CBV.helpers
   :members:

Business Steps (BizSteps)
===================
The Business Steps enumerations make it easy for developers to programatically include
the proper CBV compliant business step data in their events.

Click on the source link to see the enumeration values for business steps.

.. automodule:: EPCPyYes.core.v1_2.CBV.business_steps
   :members:

Business Transactions (BizTransactions)
==========
.. automodule:: EPCPyYes.core.v1_2.CBV.business_transactions
   :members:

Dispositions
======

.. automodule:: EPCPyYes.core.v1_2.CBV.dispositions
   :members:

Error Reasons
=======
.. automodule:: EPCPyYes.core.v1_2.CBV.error_reasons
   :members:

Trade Item Master Data
========
.. automodule:: EPCPyYes.core.v1_2.CBV.instance_lot_master_data
   :members:

Location Party Master Data
=======
.. automodule:: EPCPyYes.core.v1_2.CBV.location_party_master_data
   :members:

.. automodule:: EPCPyYes.core.v1_2.CBV.source_destination
   :members: