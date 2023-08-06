
Using the EPCPyYes Module
=========================

Before you start, this documentation is provided in the form of an
IPython notebook. All of the code in this document can be executed if
you run the ``.ipynb`` file in a local notebook from the source code
tree.

Get Jupyter
-----------

You can download Jupyter here for free: http://jupyter.org/

Additional and more detailed examples can be found in the EPCPyYes unit
tests.

The EPCPyYes module is designed to allow developers to quickly and
easily generate EPCIS data. There are four fundamental areas of
developer tools covered by the module:

::

    * EPCIS Documents
    * EPCIS Events
    * Core Business Vocabulary (CBV) Enumberations
    * Helper functions for creating various URN values

Before You Try To Run This Code in Jupyter
==========================================

If you are running the jupyter notebook from the EPCPyYes source tree
execute the cell below to append the EPCPyYes module to the python path.
Also, each of the EPCIS event and document rendering examples here rely
on the prior examples being run for context.

.. code:: ipython3

    import os
    import sys
    nb_dir = os.path.split(os.getcwd())[0]
    if nb_dir not in sys.path:
        sys.path.append(nb_dir)

Creating SGTIN URN Values
-------------------------

The ``EPCPyYes.core.v1_2.helpers`` module contains some helpful
functions for creating common URN values.

In the example below, we create a python generator with ten SGTIN URN
values by supplying the following (For notebook users: if you get an
import error, run the code section above first):

-  Company Prefix
-  Indicator Digit
-  Item Reference Number
-  A list of serial numbers (in this case sequential)

``gtin_urn_generator`` helper function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    from EPCPyYes.core.v1_2.CBV import business_steps
    from EPCPyYes.core.v1_2 import helpers
    
    def create_epcs(start=1000, end=1002):
        # create a range for the number generation (we can use SerialBox as well)
        nums = range(start, end)
        # generate some URNS by passing in the company prefix, indicator, item refernce
        # number and a range of sequetial serial numbers.
        epcs = helpers.gtin_urn_generator('305555', '1', '555555', nums)
        return epcs
    
    for epc in create_epcs(1000,1010):
        print(epc)

``gtin_to_urn`` helper function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to the example above but instead of passing in a list of serial
numbers pass in a single serial number.

.. code:: ipython3

    from EPCPyYes.core.v1_2 import helpers
    print(helpers.gtin_to_urn('305555', '1', '555551', 1000))

Getting Time Values for Events with the ``get_current_utc_time_and_offset`` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``get_current_utc_time_and_offset`` returns a two-tuple value with
the current UTC time and the timezone offset. Usefull for generating
time values in EPCIS events (this is covered later).

.. code:: ipython3

    from EPCPyYes.core.v1_2 import helpers
    print(helpers.get_current_utc_time_and_offset())

Converting a GLN to an SGLN URN Value with the gln13\_data\_to\_sgln\_urn function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below you can see we are creating a generic GLN by specifying a company
prefix and location reference as well as creating a SGLN by specifying
the aformentioned values along with an extension.

.. code:: ipython3

    from EPCPyYes.core.v1_2 import helpers
    destination_party = helpers.gln13_data_to_sgln_urn(company_prefix='0614141',
                                               location_reference='00001')
    destination_location = helpers.gln13_data_to_sgln_urn(company_prefix='0614141',
                                                  location_reference='00001',
                                                  extension='23')
    print(destination_party)
    print(destination_location)

Generating EPCIS Events
=======================

Events can be generated in EPCPyYes by using the ``template_events``
module classes. These classes rely on the Jinja2 templates defined in
the root level ``templates`` directory of the project.

Create Sample EPCs Using the Helpers
------------------------------------

Since we don't have any real EPCs to use for our examples, we will
create some using the
\`EPCPyYes.core.v1\_2.helpers.gtin\_urn\_generator' which will create a
python generator based on a list of inbound serial numbers, company
prefix and indicator digit. Since we'll be using the EPCs in various
examples below we'll convert the python generator to a list.

.. code:: ipython3

    from EPCPyYes.core.v1_2 import helpers
    
    # we will use the same company prefix across many functions
    company_prefix = '305555'
    # we will need to create some dummy EPC values for our event...
    def create_epcs(start, end):
        # create a range for the number generation (we can use SerialBox as well)
        nums = range(start, end+1)
        # generate some URNS by passing in the company prefix, indicator, item refernce
        # number and a range of sequetial serial numbers.
        epcs = helpers.gtin_urn_generator(company_prefix, '0', '555555', nums)
        return epcs
    
    # create 5 epcs
    epcs = create_epcs(1,5)
    # this function returns a python generator so we will
    # convert it to a list for re-use in these examples
    epcs = [epc for epc in epcs]
    
    print('{0} epcs were created.'.format(len(epcs)))

Creating a Basic Object Event
-----------------------------

Here we will define an Object event in python and render it to XML. By
the time we complete all the other examples below, this event would be
very much like a commissioning event one might see from a pharmaceutical
packaging operation complete with lot and exipration date.

Using the CVB ``BusinessSteps`` and ``Disposition`` enumerations.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will notice below that we are adding a ``biz_step`` (commissioning)
and a ``disposition`` (encoded) to the event. This is done safely using
the ``EPCPyYes.core.v1_2.CBV`` modulewhich contains enumeration for all
compliant CBV data-types. Using the ``.value`` property of each enum
value will convert that value to a string for use in EPCIS events, etc.

.. code:: ipython3

    from EPCPyYes.core.v1_2.events import Action
    from EPCPyYes.core.v1_2.template_events import ObjectEvent
    from EPCPyYes.core.v1_2.CBV.business_steps import BusinessSteps
    from EPCPyYes.core.v1_2.CBV.dispositions import Disposition
    
    # we will use the helper function to get the event time
    now, tzoffset = helpers.get_current_utc_time_and_offset()
    
    # now we create an object event...
    oe = ObjectEvent(now, tzoffset,
                     record_time=now,
                     action=Action.add.value,
                     epc_list=epcs,
                     biz_step=BusinessSteps.commissioning.value,
                     disposition=Disposition.encoded.value)
    
    print(oe.render())

Adding a *Business Location* and *Read Point*
---------------------------------------------

Adding some business context by putting information relative to where
the event took place and what device originated the event is done via
the ``biz_location`` and ``read_point`` properties of EPCIS event
objects in EPCPyYes. In the example below we are using the GLN helpers
in the ``EPCPyYes.core.v1_2.helpers`` module.

.. code:: ipython3

    # the helper used below is designed to create the right GLN URN values based on input
    from EPCPyYes.core.v1_2 import helpers
    # next we will create a biz location and a read point
    biz_location = helpers.gln13_data_to_sgln_urn(company_prefix=company_prefix,
                                          location_reference='123456')
    read_point = helpers.gln13_data_to_sgln_urn(company_prefix=company_prefix,
                                        location_reference='123456',
                                        extension='12')
    
    # these could also be supplied in the class constructor...
    oe.biz_location = biz_location
    oe.read_point = read_point
    
    print(oe.render())

Adding Instance Lot Master Data (ILMD) to an Event
--------------------------------------------------

This is covered in section 7.3.6 of the EPCIS 1.2 standard. Having said
that, the simple explanation of ILMD is that it is a way to associate a
lot or batch number to the serial numbers (or EPCs) in the event. For a
more complicated description, see the standard.

.. code:: ipython3

    from EPCPyYes.core.v1_2.CBV.instance_lot_master_data import InstanceLotMasterDataAttribute,\
        LotLevelAttributeName, ItemLevelAttributeName
    
    # lets create some lot and expiration data for event
    ilmd = [
        InstanceLotMasterDataAttribute(
            name=LotLevelAttributeName.itemExpirationDate.value,
            value='2015-12-31'),
        InstanceLotMasterDataAttribute(
            name=ItemLevelAttributeName.lotNumber.value,
            value='DL232')
    ]
    
    # assign the property and that's it
    oe.ilmd = ilmd
    
    print(oe.render())

Adding Source and Destination Data to an Event
----------------------------------------------

Here we are adding source and destination data to an event using the CVB
values created for this task. The source and destination lists can be
added to any EPCIS event. *Source/Destination types* are covered in
section 7.4 of the *CBV 1.2* standard.

.. code:: ipython3

    from EPCPyYes.core.v1_2.CBV.source_destination import SourceDestinationTypes
    from EPCPyYes.core.v1_2.events import Source, Destination
    
    dest_company_prefix = '309999'
    # next we will create a biz location and a read point using the helpers...
    # you can do this manually if you want...
    owner_gln = helpers.gln13_data_to_sgln_urn(company_prefix=dest_company_prefix,
                                          location_reference='111111')
    owner_location_gln = helpers.gln13_data_to_sgln_urn(company_prefix=dest_company_prefix,
                                        location_reference='111111',
                                        extension='233')
    
    
    # let's create a source list using the biz_location and read_point values just as an example
    # any GLN could be used here to signify who owns the product and where it is located. 
    source_list = [
        Source(SourceDestinationTypes.possessing_party.value,
               biz_location),
        Source(SourceDestinationTypes.location.value, read_point)
    ]
    
    destination_list = [
        Destination(SourceDestinationTypes.owning_party.value, owner_gln),
        Destination(SourceDestinationTypes.location.value, owner_location_gln)
    ]
    
    oe.source_list = source_list
    oe.destination_list = destination_list
    
    print(oe.render())

Creating an Aggregation Event
-----------------------------

.. code:: ipython3

    from EPCPyYes.core.v1_2 import helpers
    from EPCPyYes.core.v1_2.events import Source, Action
    from EPCPyYes.core.v1_2.template_events import AggregationEvent
    from EPCPyYes.core.v1_2.CBV import business_steps
    from EPCPyYes.core.v1_2.CBV.business_steps import BusinessSteps
    from EPCPyYes.core.v1_2.CBV.source_destination import SourceDestinationTypes
    from EPCPyYes.core.v1_2.CBV.dispositions import Disposition
    from EPCPyYes.core.v1_2.CBV.instance_lot_master_data import InstanceLotMasterDataAttribute,\
        LotLevelAttributeName, ItemLevelAttributeName
    
    # we will use the same company prefix across many functions
    company_prefix = '305555'
    
    # create a parent EPC to pack our child EPC values into
    # (note the different indicator)
    parent_epc = helpers.gtin_to_urn(company_prefix, indicator=3,
                                     item_reference='555555',
                                     serial_number='1')
    
    # now we create an object event...
    ae = AggregationEvent(
        event_time=now, event_timezone_offset=tzoffset,
        record_time=now, action=Action.add.value, parent_id=parent_epc,
        child_epcs=epcs,
        biz_step=BusinessSteps.packing,
        disposition=Disposition.container_closed,
        read_point=read_point,biz_location=biz_location
    )
    
    print(ae.render())

Adding a Transaction Event
--------------------------

Below we will add a transaction event that mimics a *shipping* event in
EPCIS. The end result of the combined examples in this notebook will be
a full EPCIS lot notification that would be typical in a pharmaceutical
manufacturing environment with the following data (to review):

::

    * Object Event with Commissioning of Prodcut IDs
    * Aggregation Event of type ADD showing how goods were packaged together
    * Transaction Event of type ADD showing that the goods were shipped from one location to another

.. code:: ipython3

    from EPCPyYes.core.v1_2.CBV.helpers import make_trade_item_master_data_urn
    from EPCPyYes.core.v1_2.template_events import TransactionEvent
    
    disposition = Disposition.in_transit.value
    biz_step = BusinessSteps.shipping.value
    
    # We will use the other biz location and read point data, etc. from the 
    # examples above.
    te = TransactionEvent(now, tzoffset, now, 
                          action=Action.add.value,
                          parent_id=parent_epc, 
                          biz_location=biz_location, 
                          read_point=read_point,
                          source_list=source_list,
                          destination_list=destination_list,
                          biz_step=biz_step, 
                          disposition=disposition)
    print(te.render())

Creating a Quantity List
------------------------

EPCIS events allow you to specify a quantity list to express the
presence of items in an event that are not identified via a unique id.
We will add a ``quantity_list`` to our event to express that there were
5 identifiable trade items shipped of a certain weight.

.. code:: ipython3

    from EPCPyYes.core.v1_2.events import QuantityElement
    from EPCPyYes.core.v1_2.CBV.helpers import make_trade_item_master_data_urn
    
    # This helper function will create the proper trade
    # item master date URN value for us using the company
    # prefix, indicator and item reference.
    trade_item = make_trade_item_master_data_urn('305555', '0',
                                                '555555')
    
    quantity_list = [
        QuantityElement(epc_class=trade_item, quantity=5),
        QuantityElement(epc_class=trade_item, quantity=14.5,
                       uom='LB')]
    
    te.quantity_list = quantity_list
    print(te.render())

Adding The Events to an EPCIS Document
======================================

To execute this code in Jupyter, make sure you have run the code in the
prior example.

Creating and EPCIS Document and adding events to it in EPCPyYes if
fairly simple:

.. code:: ipython3

    from EPCPyYes.core.v1_2.template_events import EPCISDocument
    
    epc_doc = EPCISDocument(object_events=[oe], aggregation_events=[ae],
                            transaction_events=[te])
    print(epc_doc.render())
