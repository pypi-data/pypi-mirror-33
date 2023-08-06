
The EParseCIS Module
====================

Before you start, this documentation is provided in the form of an
IPython notebook. All of the code in this document can be executed if
you run the ``.ipynb`` file in a local notebook from the source code
tree.

Get Jupyter
-----------

You can download Jupyter here for free: http://jupyter.org/

The EParseCIS module is designed to allow developers to quickly and
easily parse EPCIS data.

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

Using the EParseCIS Python Package
==================================

The EParseCIS Python package contains a number of modules that make it
easy to serialize EPCIS XML structures into EPCPyYes python classes for
use in any type of python application where having an EPCIS class loaded
into a usable python class that can be serialized to any structure using
Jinja2 templates or native python mechanisms would be of value.

| Please Note: All examples below are in Python 3.5

Loading EPCIS Data From A String
--------------------------------

Before we can get into how to use the EParseCIS package and associated
modules, we’ll need to load some data into memory for use in our parsing
exercise. Here we’ll be loading it into memory using a string; however,
in the real world you may most likely be loading in from a file stream,
etc.

.. code:: ipython3

    import io
    from eparsecis import eparsecis

    test_data = io.BytesIO('''
    <epcis:EPCISDocument
        xmlns:epcis="urn:epcglobal:epcis:xsd:1"
        xmlns:cbvmd="urn:epcglobal:cbv:mda"
        schemaVersion="1.2" creationDate="2015-04-22T15:33:12.485128">
        <EPCISBody>
            <EventList>
                <ObjectEvent>
                    <eventTime>2015-04-22T15:34:31.500371+00:00</eventTime>
                    <recordTime>2015-04-22T15:34:31.500371+00:00</recordTime>
                    <eventTimeZoneOffset>+00:00</eventTimeZoneOffset>
                    <epcList>
                        <epc>urn:epc:id:sgtin:305555.0555555.1</epc>
                        <epc>urn:epc:id:sgtin:305555.0555555.2</epc>
                        <epc>urn:epc:id:sgtin:305555.0555555.3</epc>
                        <epc>urn:epc:id:sgtin:305555.0555555.4</epc>
                        <epc>urn:epc:id:sgtin:305555.0555555.5</epc>
                    </epcList>
                    <action>ADD</action>
                    <bizStep>urn:epcglobal:cbv:bizstep:commissioning</bizStep>
                    <disposition>urn:epcglobal:cbv:disp:encoded</disposition>
                    <readPoint>
                        <id>urn:epc:id:sgln:305555.123456.12</id>
                    </readPoint>
                    <bizLocation>
                        <id>urn:epc:id:sgln:305555.123456.0</id>
                    </bizLocation>
                    <extension>
                        <sourceList>
                            <source type="urn:epcglobal:cbv:sdt:possessing_party">
                                urn:epc:id:sgln:305555.123456.0
                            </source>
                            <source type="urn:epcglobal:cbv:sdt:location">
                                urn:epc:id:sgln:305555.123456.12
                            </source>
                        </sourceList>
                        <destinationList>
                            <destination
                                type="urn:epcglobal:cbv:sdt:owning_party">
                                urn:epc:id:sgln:309999.111111.0
                            </destination>
                            <destination
                                type="urn:epcglobal:cbv:sdt:location">
                                urn:epc:id:sgln:309999.111111.233
                            </destination>
                        </destinationList>
                        <ilmd>
                            <cbvmd:itemExpirationDate>2015-12-31
                            </cbvmd:itemExpirationDate>
                            <cbvmd:lotNumber>DL232</cbvmd:lotNumber>
                        </ilmd>
                    </extension>
                </ObjectEvent>
                <AggregationEvent>
                    <eventTime>2015-04-22T15:34:31.500371+00:00</eventTime>
                    <recordTime>2015-04-22T15:34:31.500371+00:00</recordTime>
                    <eventTimeZoneOffset>+00:00</eventTimeZoneOffset>
                    <parentID>urn:epc:id:sgtin:305555.3555555.1</parentID>
                    <childEPCs>
                        <epc>urn:epc:id:sgtin:305555.0555555.1</epc>
                        <epc>urn:epc:id:sgtin:305555.0555555.2</epc>
                        <epc>urn:epc:id:sgtin:305555.0555555.3</epc>
                        <epc>urn:epc:id:sgtin:305555.0555555.4</epc>
                        <epc>urn:epc:id:sgtin:305555.0555555.5</epc>
                    </childEPCs>
                    <action>ADD</action>
                    <bizStep>urn:epcglobal:cbv:bizstep:packing</bizStep>
                    <disposition>urn:epcglobal:cbv:disp:container_closed
                    </disposition>
                    <readPoint>
                        <id>urn:epc:id:sgln:305555.123456.12</id>
                    </readPoint>
                    <bizLocation>
                        <id>urn:epc:id:sgln:305555.123456.0</id>
                    </bizLocation>
                </AggregationEvent>
                <TransactionEvent>
                    <eventTime>2015-04-22T15:34:31.500371+00:00</eventTime>
                    <recordTime>2015-04-22T15:34:31.500371+00:00</recordTime>
                    <eventTimeZoneOffset>+00:00</eventTimeZoneOffset>
                    <parentID>urn:epc:id:sgtin:305555.3555555.1</parentID>
                    <action>ADD</action>
                    <bizStep>urn:epcglobal:cbv:bizstep:shipping</bizStep>
                    <disposition>urn:epcglobal:cbv:disp:in_transit</disposition>
                    <readPoint>
                        <id>urn:epc:id:sgln:305555.123456.12</id>
                    </readPoint>
                    <bizLocation>
                        <id>urn:epc:id:sgln:305555.123456.0</id>
                    </bizLocation>
                    <extension>
                        <quantityList>
                            <quantityElement>
                                <epcClass>urn:epc:idpat:sgtin:305555.0555555.*
                                </epcClass>
                                <quantity>5</quantity>
                            </quantityElement>
                            <quantityElement>
                                <epcClass>urn:epc:idpat:sgtin:305555.0555555.*
                                </epcClass>
                                <quantity>14.5</quantity>
                                <uom>LB</uom>
                            </quantityElement>
                        </quantityList>
                        <sourceList>
                            <source type="urn:epcglobal:cbv:sdt:possessing_party">
                                urn:epc:id:sgln:305555.123456.0
                            </source>
                            <source type="urn:epcglobal:cbv:sdt:location">
                                urn:epc:id:sgln:305555.123456.12
                            </source>
                        </sourceList>
                        <destinationList>
                            <destination
                                type="urn:epcglobal:cbv:sdt:owning_party">
                                urn:epc:id:sgln:309999.111111.0
                            </destination>
                            <destination
                                type="urn:epcglobal:cbv:sdt:location">
                                urn:epc:id:sgln:309999.111111.233
                            </destination>
                        </destinationList>
                    </extension>
                </TransactionEvent>
            </EventList>
        </EPCISBody>
    </epcis:EPCISDocument>
    '''.encode('utf-8'))

    #load the data into the parser
    parser = eparsecis.EPCISParser(test_data)
    parser.parse()

Loading EPCIS Data From a File
==============================

The following illustrates loading an EPCIS XML structure from a file.

.. code:: ipython3

    import os
    from eparsecis import eparsecis
    curpath = os.path.split(os.getcwd())[0]
    parser = eparsecis.EPCISParser(
        os.path.join(curpath, './tests/data/epcis.xml'))
    parser.parse()

Overriding the Base eparsecis.EPCISParser Class
==================================================

The EParseCIS package provides, essentially, a single class instance
inside the ``eparsecis`` module that is desgined to be overridin in
order to be useful in any practical sense.

The following methods are provided for use by developers:

::

    * handle_object_event
    * handle_aggregation_event
    * handle_transaction_event
    * handle_transformation_event

Examples
--------

Below we can see the power of both EParseCIS and EPCPyYes combined. As
the EParseCIS parser encounters events within an EPCIS document, it
calls each of the helper functions and passes along an EPCPyYes class
for you to use within your application. Below you can see how one might
want to inspect or iterate through various attributes of an EPCIS event.
Obviously, you’ll need to have some background in both EPCIS and the
EPCPyYes python package; but, having said that, much of the hard work
has been done for you by these two packages. The ability to quickly
serialize EPCIS messages and events into python classes that can be
intuitively manipulated lets developers focus on building applications
rather than tinkering with the protocols involved.

.. code:: ipython3

    import os
    import logging
    from eparsecis import eparsecis

    class MyParser(eparsecis.EPCISParser):
        def handle_object_event(self, epcis_event):
            # for example, access the epc list
            print("EPC List from the Object Event: %s\r\n" %
                  epcis_event.epc_list)

        def handle_aggregation_event(self, epcis_event):
            # for example, inspect the biz_location
            print("Aggregation Event Biz Location: %s\r\n" %
                  epcis_event.biz_location)

        def handle_transaction_event(self, epcis_event):
            # get the possessing party
            for source in epcis_event.source_list:
                if source.type == \
                "urn:epcglobal:cbv:sdt:possessing_party":
                    print("Transaction Event: Possessing Party: %s"
                          % source.source)


    curpath = os.path.split(os.getcwd())[0]
    parser = MyParser(
        os.path.join(curpath, './tests/data/epcis.xml'))
    parser.parse()


.. parsed-literal::

    EPC List from the Object Event: ['urn:epc:id:sgtin:305555.0555555.1', 'urn:epc:id:sgtin:305555.0555555.2', 'urn:epc:id:sgtin:305555.0555555.3', 'urn:epc:id:sgtin:305555.0555555.4', 'urn:epc:id:sgtin:305555.0555555.5']

    Aggregation Event Biz Location: urn:epc:id:sgln:305555.123456.0

    Transaction Event: Possessing Party: urn:epc:id:sgln:305555.123456.0

