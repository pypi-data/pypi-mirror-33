
Using the EPCPyYes Module
=========================

Before you start, this documentation is provided in the form of an
IPython notebook. All of the code in this document can be executed if
you run the ``.ipynb`` file in a local notebook from the source code
tree.

Python Classes That Generate Compliant XML and JSON
---------------------------------------------------

The EPCPyYes module allows you to work with Python objects that
represent the constructs defined in the GS1 EPCIS and CBV standards and
then serialize those class instances to EPCSI compliant XML or JSON-
which has value in web interface development and also document database
use cases.

Each class that can render XML or JSON has three functions it exposes:

::

    render() # renders XML
    render_json() # renders compressed json
    render_pretty_json() # renders pretty printed json

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
        epcs = helpers.gtin_urn_generator('305555', '0', '555551', nums)
        return epcs
    
    for epc in create_epcs(1000,1010):
        print(epc)

``gtin_to_urn`` helper function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to the example above but instead of passing in a list of serial
numbers pass in a single serial number.

.. code:: ipython3

    from EPCPyYes.core.v1_2 import helpers
    print(helpers.gtin_to_urn('305555', '10', '555551', 1000))

Getting Time Values for Events with the ``get_current_utc_time_and_offset`` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``get_current_utc_time_and_offset`` returns a two-tuple value with
the current UTC time and the timezone offset. Usefull for generating
time values in EPCIS events (this is covered later).

.. code:: ipython3

    from EPCPyYes.core.v1_2 import helpers
    print(helpers.get_current_utc_time_and_offset())

Converting a GLN to an SGLN URN Value with the gln13_data_to_sgln_urn function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Since we don’t have any real EPCs to use for our examples, we will
create some using the \`EPCPyYes.core.v1_2.helpers.gtin_urn_generator’
which will create a python generator based on a list of inbound serial
numbers, company prefix and indicator digit. Since we’ll be using the
EPCs in various examples below we’ll convert the python generator to a
list.

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
            name=LotLevelAttributeName.itemExpirationDate,
            value='2015-12-31'),
        InstanceLotMasterDataAttribute(
            name=ItemLevelAttributeName.lotNumber.value,
            value='DL232')
    ]
    
    # assign the property and that's it
    oe.ilmd = ilmd
    
    print(oe.render())
    # try pretty json
    print(oe.render_pretty_json())

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
    print(oe.render_json())

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
        biz_step=BusinessSteps.packing.value,
        disposition=Disposition.container_closed.value,
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

    from EPCPyYes.core.v1_2.CBV.business_transactions import BusinessTransactionType
    from EPCPyYes.core.v1_2.CBV.helpers import make_trade_item_master_data_urn
    from EPCPyYes.core.v1_2.template_events import TransactionEvent
    from EPCPyYes.core.v1_2.events import BusinessTransaction
    
    disposition = Disposition.in_transit.value
    biz_step = BusinessSteps.shipping.value
    
    #here we create a business transaction to add to the events business transaction list.
    biz_transaction_list = [
        BusinessTransaction(
            'urn:epc:id:gdti:0614141.06012.1234', 
            type=BusinessTransactionType.Purchase_Order
        )
    ]
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
                          disposition=disposition,
                          business_transaction_list=biz_transaction_list
                         )
    print(te.render())
    print(oe.render_json())

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
    print(oe.render_json())

Using the New EventID and ErrorDeclaration
==========================================

Before we create our TransformationEvent (see below) we’ll use the new
features of EPCIS 1.2 to create a unique identifier for our event and
also add an ErrorDeclaration that contains info with regards to the
(albeit fictional) EPCIS events that the ErrorDeclaration claims to have
the error fixed by.

.. code:: ipython3

    import uuid
    from datetime import datetime
    from EPCPyYes.core.v1_2.events import ErrorDeclaration
    from EPCPyYes.core.v1_2.CBV import error_reasons
    
    # here we create a new error declaration using the CBV error reasons
    # along with the current time and some fake corrective event ids 
    # to use as an example
    error_declaration = ErrorDeclaration(
        declaration_time = datetime.utcnow().isoformat(),
        reason=error_reasons.ErrorReason.incorrect_data.value,
        corrective_event_ids=[str(uuid.uuid4()), str(uuid.uuid4())]
    )
    # here we create a new event id by using a UUID 4
    event_id = str(uuid.uuid4())


Add a Transformation Event
==========================

Next we will add a transformation event that shows how some EPC values
were repacked into new EPC values.

.. code:: ipython3

    import uuid
    from EPCPyYes.core.v1_2.template_events import TransformationEvent
    
    #lets create a custom ilmd for the transformation event
    ilmd = [
        InstanceLotMasterDataAttribute(
            name=LotLevelAttributeName.itemExpirationDate,
            value='2015-12-31'),
        InstanceLotMasterDataAttribute(
            name=ItemLevelAttributeName.lotNumber.value,
            value='DL232')
    ]
    
    #next we will create an input and ouput quantity list that
    #shows a different count but the same weight
    input_quantity_list = [
                QuantityElement(epc_class=trade_item, quantity=100, uom='EA'),
                QuantityElement(epc_class=trade_item, quantity=94.3,
                                uom='LB')]
    output_quantity_list = [
        QuantityElement(epc_class=trade_item, quantity=10, uom='EA'),
        QuantityElement(epc_class=trade_item, quantity=94.3,
                        uom='LB')]
    
    # we will create a list of 100 for input
    epcs = create_epcs(2000,2099)
    # this function returns a python generator so we will
    # convert it to a list for re-use in this example since
    # the event will be rendered twice
    input_epcs = [epc for epc in epcs]
    # and a list of 10 for the output
    epcs = create_epcs(2100,2109)
    # this function returns a python generator so we will
    # convert it to a list for re-use in this example since
    # the event will be rendered twice
    output_epcs = [epc for epc in epcs]
    
    #while it's not realistic, we can use the rest of the business transaction, source,
    #destination lists, etc to keep the code to a minimum...
    
    tx_event = TransformationEvent(
        now, tzoffset, record_time=now,
        input_epc_list=input_epcs,
        input_quantity_list=input_quantity_list,
        output_epc_list=output_epcs,
        output_quantity_list=output_quantity_list,
        transformation_id=str(uuid.uuid4()),
        biz_step=BusinessSteps.repackaging.value,
        disposition=Disposition.returned.value,
        read_point=read_point,
        biz_location=biz_location,
        business_transaction_list=biz_transaction_list,
        source_list=source_list,
        destination_list=destination_list,
        ilmd=ilmd,
        event_id=event_id,
        error_declaration=error_declaration
    )
    
    print(tx_event.render())

Create a Standard Business Document Header
==========================================

If you’d like to include a SBDH header in your document to denote who
the document is from and where it is going, you’ll add a document
header.

Create sender and receiver partner ids
--------------------------------------

First we will create the partner ids for sender and receiver. For most
EPCIS event documents, it is common to just use the SGLN of each party.
The examples below will do more than this, but they are only examples
intended to show how to use each field/element/value in the header.

.. code:: ipython3

    from EPCPyYes.core.SBDH import template_sbdh
    from EPCPyYes.core.SBDH import sbdh
    
    sender_partner_id = sbdh.PartnerIdentification(
        authority='SGLN',
        value='urn:epc:id:sgln:039999.999999.0'
    )
    receiver_partner_id = sbdh.PartnerIdentification(
        authority='SGLN',
        value='urn:epc:id:sgln:039999.111111.0'
    )


Create the Partner Instances for Sender and Reciever
----------------------------------------------------

So below we will create two partners and set one to have a
``partner_type`` of *Sender* and the other to have one of *Receiver*. In
addition, we use the **optional** contact info properties of the
``Partner`` class to specify things like email, phone number, contact
name, etc.

.. code:: ipython3

    sender = sbdh.Partner(
        partner_type=sbdh.PartnerType.SENDER,
        partner_id=sender_partner_id,
        contact='John Smith',
        telephone_number='555-555-5555',
        email_address='john.smith@pharma.local',
        contact_type_identifier='Seller'
    )
    receiver = sbdh.Partner(
        partner_type=sbdh.PartnerType.RECEIVER,
        partner_id=receiver_partner_id,
        contact='Joe Blow',
        telephone_number='555-555-2222',
        email_address='joe.blow@distributor.local',
        contact_type_identifier='Buyer'
    )


Create the Document Identification and Header Class Instances
-------------------------------------------------------------

So the SBDH requires a specific ``DocumentIdentification`` element with
required values. Some optional values that you can supply are the
``instance_identifier`` which is a unique value that identifies the
document- the default value for this is a UUID4. Another optional value
you can supply is the created date and time in ISO format- the default
for this is the current date and time in ISO using UTC timezone info.

.. code:: ipython3

    document_identification = sbdh.DocumentIdentification(
        creation_date_and_time=datetime.now().isoformat(),
        document_type=sbdh.DocumentType.EVENTS
    )
    header = template_sbdh.StandardBusinessDocumentHeader(
        document_identification=document_identification,
        partners=[sender, receiver]
    )
    print(header.render())
    print(header.render_json())

Adding The Header and Events to an EPCIS Document
=================================================

To execute this code in Jupyter, make sure you have run the code in the
prior example.

EPCISDocument Class
-------------------

The first type of document class is the ``EPCISDocument`` and, as you
can see below, it has a 4 lists you intialize the object with that
contain object, aggregation, transaction and transformation event lists.
Each of those event types will always be rendered in that order if you
use this class…which is usually fine.

EPCISEventListDocument
----------------------

If you need to directly control the order of events in a document, use
the ``EPCISEventListDocument`` which allows you to pass in a list of any
type event in any order. Each event will be rendered in the order in
which it sits in the list.

Creating and EPCIS Document and adding events to it in EPCPyYes if
fairly simple:

.. code:: ipython3

    from EPCPyYes.core.v1_2.template_events import EPCISDocument, EPCISEventListDocument
    
    #event types strictly ordered
    epc_doc = EPCISDocument(header=header, object_events=[oe], aggregation_events=[ae],
                            transaction_events=[te], transformation_events=[tx_event])
    
    #events ordered as they appear in the list
    epc_doc_2 = EPCISEventListDocument(template_events=[te, oe, ae, tx_event], header=header)
    
    print(epc_doc.render())
    print('\n'*5)
    print(epc_doc_2.render())
    
    # as with all the template_event classes, you can render to JSON as well...
    print(epc_doc_2.render_json())

