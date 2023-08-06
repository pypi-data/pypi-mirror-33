=======
History
=======

0.1.0
------------------

* First beta release on GitLab.

1.0.0
------------------

PyPI release candidate.

1.0.1
------------------

Fix to CBV enumeration issues with ILMD.

1.0.11
-------------------
Updated docs and CI build working out to PyPI.  All patches
between 1.0.1 and this were mods to both fix PyPI restructured
text issues in the readme and to tweak the documentation
to include files in the root that were being ignored.

1.1.0
--------------------
Added JSON serialization support to the EPCPyYes core
template event classes and the standard business document header
template classes.

1.1.2
--------------------
Fixes to allow datetimes and strings to be used more flexibly in
EPCIS events and a fix to the bizTransactionList label in the
JSON encoder.

1.2.0
--------------------
Added a dict render function to the JSON plugin for API view support
in Django projects, etc.

Added in a new template and template_events EPCISEventListDocument class
to support a generic list of EPCIS template_event instances in any order.

Updated documentation for EPCISEventListDocument and JSON rendering
options.

1.2.1
---------------------
Updates to the setup and stated python compatibility.

1.2.7
---------------------
Added the new `EventType` enumeration to the events module.  Can be used
to compare event types and settings while keeping string literals consistent
across applications.