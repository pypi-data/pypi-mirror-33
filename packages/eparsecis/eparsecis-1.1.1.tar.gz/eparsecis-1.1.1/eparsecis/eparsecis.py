# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

from lxml import etree
import logging

from EPCPyYes.core.v1_2 import template_events
from EPCPyYes.core.v1_2.events import Action, BusinessTransaction
from EPCPyYes.core.v1_2.events import Source, Destination, QuantityElement, \
    ErrorDeclaration
from EPCPyYes.core.v1_2.CBV.instance_lot_master_data import \
    InstanceLotMasterDataAttribute
from EPCPyYes.core.SBDH import sbdh, template_sbdh
from eparsecis.namespace_helpers import SBDHNamespaceHelper
from eparsecis.elements import EPCPyYesElement

logger = logging.getLogger()


class EPCISParser(object):
    '''
    Parses EPCIS XML from a stream and serializes each EPCIS Event
    in a given document into a serialized EPCPyYes event object.
    '''

    def __init__(
        self,
        stream,
        header_namespace='http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader'
    ):
        '''
        Initialize a new EPCISParser with a stream to be
        parsed.
        :param stream: The stream containing the EPCIS XML to be parsed.
        :param header_namespace: The namespace prefix for the standard
        business document header elements (if any).
        '''
        self._stream = stream
        self._header_namespace = header_namespace
        self._sbdh_helper = SBDHNamespaceHelper(header_namespace)

    @property
    def header_namespace(self):
        return self._header_namespace

    @header_namespace.setter
    def header_namespace(self, value):
        self._header_namespace = value

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        self._stream = value

    def parse(self, huge_tree=False):
        parser_lookup = etree.ElementDefaultClassLookup(
            element=EPCPyYesElement)
        epcis = etree.iterparse(self.stream, events=('end',),
                                remove_comments=True, huge_tree=huge_tree)
        epcis.set_element_class_lookup(parser_lookup)
        for event, element in epcis:
            if element.tag == 'EPCISHeader':
                self.parse_epcis_header(event, element)
                self.clear_element(element)
            elif element.tag == 'ObjectEvent':
                self.parse_object_event_element(event, element)
                self.clear_element(element)
            elif element.tag == 'AggregationEvent':
                self.parse_aggregation_event_element(event, element)
                self.clear_element(element)
            elif element.tag == 'TransactionEvent':
                self.parse_transaction_event_element(event, element)
                self.clear_element(element)
            elif element.tag == 'TransformationEvent':
                self.parse_transformation_event_element(event, element)
                self.clear_element(element)
            else:
                self.handle_unexpected_element(event, element)

    def clear_element(self, element):
        '''
        Clears out an element and any previous (skipped over) elements.
        :param element: The element to clear.
        '''
        element.clear()
        # this will clean up any nodes that were skipped
        while element.getprevious() is not None:
            del element.getparent()[0]

    def parse_epcis_header(self, event, header_element):
        '''
        Parses the EPCIS header if one is found.
        :param event: The lxml/etree event.
        :param header_element: The XML etree/lxml element.
        :return: None
        '''
        logger.debug('handling the header')
        for child in header_element:
            if child.tag == self._sbdh_helper.sbdh:
                self.parse_sbdh(child)
        else:
            self.parse_header_info(event, child)
        logger.debug('Clearing out the header element.')
        header_element.clear()

    def parse_sbdh(self, sbdh_element):
        '''
        Parses out the Standard Business Document Header element.
        :param sbdh_element: The element.
        :return: None
        '''
        header = template_sbdh.StandardBusinessDocumentHeader()
        header.partners = []
        logger.debug('Found an SBDH element...parsing...')
        for child in sbdh_element:
            if child.tag == self._sbdh_helper.header_version:
                header.header_version = child.text.strip()
            elif child.tag == self._sbdh_helper.sender:
                header.partners.append(
                    self.parse_partner(sbdh.PartnerType.SENDER, child)
                )
            elif child.tag == self._sbdh_helper.receiver:
                header.partners.append(
                    self.parse_partner(sbdh.PartnerType.RECEIVER, child)
                )
            elif child.tag == self._sbdh_helper.document_identification:
                header.document_identification = \
                    self.parse_document_identification(child)
        self.handle_sbdh(header)

    def parse_partner(self, partner_type: sbdh.PartnerType, partner_element):
        '''
        Parses any partner elements into a sbdh.Partner class instance.
        :param partner_type: The type of partner (Sender or Receiver)
        :return: A sbdh.Partner class instance.
        '''
        partner = sbdh.Partner(partner_type=partner_type)
        for child in partner_element:
            if child.tag == self._sbdh_helper.identifier:
                partner.partner_id = self.create_partner_identification(child)
            elif child.tag == self._sbdh_helper.contact_information:
                self.parse_contact_information(child, partner)
        return partner

    def parse_contact_information(self, contact_info_element, partner):
        '''
        Adds any contact info to a partner class instance.
        '''
        for child in contact_info_element:
            if child.tag == self._sbdh_helper.contact:
                partner.contact = child.text.strip()
            elif child.tag == self._sbdh_helper.email_address:
                partner.email_address = child.text.strip()
            elif child.tag == self._sbdh_helper.fax_number:
                partner.fax_number = child.text.strip()
            elif child.tag == self._sbdh_helper.telephone_number:
                partner.telephone_number = child.text.strip()
            elif child.tag == self._sbdh_helper.contact_type_identifier:
                partner.contact_type_identifier = child.text.strip()

    def create_partner_identification(self, partner_id_element):
        '''
        Creates and returns an EPCPyYes sbdh.PartnerIdentification
        class instance.
        :param partner_id_element: The element to parse.
        :return: an EPCPyYes PartnerIdentification instance.
        '''

        authority = partner_id_element.attrib.get('Authority', None)
        value = partner_id_element.text.strip()
        return sbdh.PartnerIdentification(authority, value)

    def parse_document_identification(self, element):
        '''
        Parses the document identification node of the SBDH
        :param element: The document identification element
        :return: A sbdh.DocumentIdentification class instance (EPCPyYes).
        '''
        logger.debug('parsing the document identification element')
        did = sbdh.DocumentIdentification()
        for child in element:
            if child.tag == self._sbdh_helper.standard:
                did.standard = child.text.strip()
            elif child.tag == self._sbdh_helper.type_version:
                did.type_version = child.text.strip()
            elif child.tag == self._sbdh_helper.instance_identifier:
                did.instance_identifier = child.text.strip()
            elif child.tag == self._sbdh_helper.document_type:
                did.document_type = child.text.strip()
            elif child.tag == self._sbdh_helper.multiple_type:
                did.multiple_type = child.text.strip()
            elif child.tag == self._sbdh_helper._creation_date_and_time:
                did.creation_date_and_time = child.text.strip()
        return did

    def parse_header_info(self, event, header_element):
        '''
        Override this method to handle any extra header info.
        :param header_element: The header element that falls outside
        the standard SBDH.
        :return: None
        '''
        logger.debug('parse_header_info. element: %s', header_element.tag)
        pass

    def parse_object_event_element(self, event, object_element):
        logger.debug('handling object event')
        oevent = template_events.ObjectEvent(epc_list=[], quantity_list=[])
        for child in object_element:
            logger.debug('%s,%s', child.tag, child.text.strip())
            if child.tag == 'eventTime':
                oevent.event_time = child.text.strip()
            elif child.tag == 'bizTransactionList':
                self.parse_biz_transaction_list(oevent, child)
            elif child.tag == 'eventTimeZoneOffset':
                oevent.event_timezone_offset = child.text.strip()
            elif child.tag == 'recordTime':
                oevent.record_time = child.text.strip()
            elif child.tag == 'epcList':
                self.parse_epc_list(oevent, child)
            elif child.tag == 'action':
                oevent.action = child.text.strip()
            elif child.tag == 'bizStep':
                oevent.biz_step = child.text.strip()
            elif child.tag == 'disposition':
                oevent.disposition = child.text.strip()
            elif child.tag == 'readPoint':
                self.parse_readpoint(oevent, child)
            elif child.tag == 'bizLocation':
                self.parse_biz_location(oevent, child)
            elif child.tag == 'extension':
                self.parse_extension(oevent, child)
            elif child.tag == 'baseExtension':
                self.parse_base_extension(oevent, child)
        logger.debug('clearing out the Element')
        object_element.clear()
        if oevent:
            self.handle_object_event(oevent)

    def parse_aggregation_event_element(self, event, aggregation_element):
        logger.debug('handling aggregation event')
        aevent = template_events.AggregationEvent()
        for child in aggregation_element:
            logger.debug('%s,%s', child.tag, child.text.strip())
            if child.tag == 'eventTime':
                aevent.event_time = child.text.strip().strip()
            elif child.tag == 'eventTimeZoneOffset':
                aevent.event_timezone_offset = child.text.strip()
            elif child.tag == 'bizTransactionList':
                self.parse_biz_transaction_list(aevent, child)
            elif child.tag == 'recordTime':
                aevent.record_time = child.text.strip().strip()
            elif child.tag == 'parentID':
                aevent.parent_id = child.text.strip().strip()
            elif child.tag == 'childEPCs':
                self.parse_epc_list(aevent, child)
            elif child.tag == 'action':
                aevent.action = child.text.strip().strip()
            elif child.tag == 'bizStep':
                aevent.biz_step = child.text.strip().strip()
            elif child.tag == 'disposition':
                aevent.disposition = child.text.strip().strip()
            elif child.tag == 'readPoint':
                self.parse_readpoint(aevent, child)
            elif child.tag == 'bizLocation':
                self.parse_biz_location(aevent, child)
            elif child.tag == 'extension':
                self.parse_extension(aevent, child)
            elif child.tag == 'baseExtension':
                self.parse_base_extension(aevent, child)
        logger.debug('clearing out the Element')
        aggregation_element.clear()
        self.handle_aggregation_event(aevent)

    def parse_transaction_event_element(self, event, transaction_element):
        tevent = None
        logger.debug('handling transaction event')
        tevent = template_events.TransactionEvent()
        for child in transaction_element:
            logger.debug('%s,%s', child.tag, child.text.strip())
            if child.tag == 'eventTime':
                tevent.event_time = child.text.strip()
            elif child.tag == 'bizTransactionList':
                self.parse_biz_transaction_list(tevent, child)
            elif child.tag == 'eventTimeZoneOffset':
                tevent.event_timezone_offset = child.text.strip()
            elif child.tag == 'recordTime':
                tevent.record_time = child.text.strip()
            elif child.tag == 'parentID':
                tevent.parent_id = child.text.strip()
            elif child.tag == 'epcList':
                self.parse_epc_list(tevent, child)
            elif child.tag == 'action':
                tevent.action = child.text.strip()
            elif child.tag == 'bizStep':
                tevent.biz_step = child.text.strip()
            elif child.tag == 'disposition':
                tevent.disposition = child.text.strip()
            elif child.tag == 'readPoint':
                self.parse_readpoint(tevent, child)
            elif child.tag == 'bizLocation':
                self.parse_biz_location(tevent, child)
            elif child.tag == 'extension':
                self.parse_extension(tevent, child)
            elif child.tag == 'baseExtension':
                self.parse_base_extension(tevent, child)
        logger.debug('clearing out the Element')
        transaction_element.clear()
        self.handle_transaction_event(tevent)

    def parse_transformation_event_element(
        self,
        event,
        transformation_element
    ):
        tevent = None
        logger.debug('handling transaction event')
        tevent = template_events.TransformationEvent()
        for child in transformation_element:
            if child.tag == 'eventTime':
                tevent.event_time = child.text.strip()
            elif child.tag == 'eventTimeZoneOffset':
                tevent.event_timezone_offset = child.text.strip()
            elif child.tag == 'recordTime':
                tevent.record_time = child.text.strip()
            elif child.tag == 'bizTransactionList':
                self.parse_biz_transaction_list(tevent, child)
            elif child.tag == 'eventTimeZoneOffset':
                tevent.event_timezone_offset = child.text.strip()
            elif child.tag == 'inputEPCList':
                self.parse_input_epc_list(tevent, child)
            elif child.tag == 'outputEPCList':
                self.parse_output_epc_list(tevent, child)
            elif child.tag == 'transformationID':
                tevent.transformation_id = child.text.strip()
            elif child.tag == 'bizStep':
                tevent.biz_step = child.text.strip()
            elif child.tag == 'disposition':
                tevent.disposition = child.text.strip()
            elif child.tag == 'readPoint':
                self.parse_readpoint(tevent, child)
            elif child.tag == 'bizLocation':
                self.parse_biz_location(tevent, child)
            elif child.tag == 'inputQuantityList':
                self.parse_input_quantity_list(tevent, child)
            elif child.tag == 'outputQuantityList':
                self.parse_output_quantity_list(tevent, child)
            elif child.tag == 'ilmd':
                self.parse_ilmd(tevent, child)
            elif child.tag == 'sourceList':
                self.parse_source_list(tevent, child)
            elif child.tag == 'destinationList':
                self.parse_destination_list(tevent, child)
            elif child.tag == 'baseExtension':
                self.parse_base_extension(tevent, child)
        logger.debug('clearing out the Element')
        transformation_element.clear()
        self.handle_transformation_event(tevent)

    def parse_biz_transaction_list(self, event, list):
        '''
        Parses the business transaction list if supplied in a
        given event and adds that info to the event.
        :param event: The EPCIS event
        :param list: The element containing the list.
        '''
        for child in list:
            bt = BusinessTransaction(
                child.text.strip()
            )
            for name, value in child.attrib.items():
                logger.debug('%s,%s', name, value)
                if name == 'type':
                    bt.type = value
            event.business_transaction_list.append(bt)

    def parse_epc_list(self, event, list):
        '''
        Parses the epc list clearing each epc as it finds one to conserve
        memory if the list is massive.
        :param event: The EPCIS event containing the list.
        :param list: The list itself.  Either an epcList or childEPCs.
        :return: None
        '''
        if hasattr(event, 'epc_list'):
            target = event.epc_list
        elif hasattr(event, 'child_epcs'):
            target = event.child_epcs
        for epc in list:
            target.append(epc.text)
            logger.debug(epc.text)
            epc.clear()

    def parse_input_epc_list(self,
                             event: template_events.TransformationEvent,
                             list):
        '''
        Parses the epc input list of a TransformationEvent
        clearing each epc as it finds one to conserve
        memory if the list is massive.
        :param event: The EPCIS event containing the list.
        :param list: The list itself.
        :return: None
        '''
        for epc in list:
            event.input_epc_list.append(epc.text)
            logger.debug(epc.text)
            epc.clear()

    def parse_output_epc_list(self,
                              event: template_events.TransformationEvent,
                              list):
        '''
        Parses the epc output list of a TransformationEvent
        clearing each epc as it finds one to conserve
        memory if the list is massive.
        :param event: The EPCIS event containing the list.
        :param list: The list itself.
        :return: None
        '''
        for epc in list:
            event.output_epc_list.append(epc.text)
            logger.debug(epc.text)
            epc.clear()

    def parse_readpoint(self, epcis_event, read_point):
        for child in read_point:
            if child.tag == 'id':
                epcis_event.read_point = child.text.strip()
                logger.debug('%s,%s', child.tag, child.text.strip())

    def parse_biz_location(self, epcis_event, biz_location):
        for child in biz_location:
            if child.tag == 'id':
                epcis_event.biz_location = child.text.strip()
                logger.debug('%s,%s', child.tag, child.text.strip())

    def parse_extension(self, epcis_event, extension):
        '''
        Called when the extension is encountered for each event.
        If you need to process custom extensions, override this function.
        :param epcis_event: The inbound event
        :param extension: The extension lxml element.
        :return: None
        '''
        # Transformation events don't have standardized extensions...
        if not isinstance(epcis_event, template_events.TransformationEvent):
            for child in extension:
                if child.tag == 'sourceList':
                    self.parse_source_list(epcis_event, child)
                elif child.tag == 'destinationList':
                    self.parse_destination_list(epcis_event, child)
                elif child.tag == 'ilmd':
                    self.parse_ilmd(epcis_event, child)
                elif child.tag == 'quantityList':
                    self.parse_quantity_list(epcis_event, child)
                elif child.tag == 'childQuantityList':
                    self.parse_child_quantity_list(epcis_event, child)

    def parse_base_extension(self, epcis_event, base_extension):
        '''
        Parses the EPCIS base extension.
        '''
        for child in base_extension:
            if child.tag == 'eventID':
                epcis_event.event_id = child.text.strip()
            elif child.tag == 'errorDeclaration':
                self.parse_error_declaration(epcis_event, child)

    def parse_error_declaration(self, epcis_event, error_declaration):
        '''
        Parses the error declaration element.
        :param epcis_event: The epcis EPCPyYes event.
        :param error_declaration: The error declaration element.
        :return: None.
        '''
        for child in error_declaration:
            epcis_event.error_declaration = ErrorDeclaration()
            if child.tag == 'declarationTime':
                epcis_event.error_declaration.declaration_time = \
                    child.text.strip()
            elif child.tag == 'reason':
                epcis_event.error_declaration.reason = child.text.strip()
            elif child.tag == 'correctiveEventIDs':
                self.parse_corrective_event_ids(epcis_event, child)

    def parse_corrective_event_ids(self, epcis_event, corrective_event_ids):
        '''
        Adds correcitve event ids to the error declaration property.
        '''
        for corrective_event_id in corrective_event_ids:
            epcis_event.error_declaration.corrective_event_ids.append(
                corrective_event_id.text.strip()
            )

    def parse_source_list(self, epcis_event, source_list):
        for child in source_list:
            urn = None
            for name, value in child.attrib.items():
                logger.debug('%s,%s', name, value)
                if name == 'type':
                    urn = value
            logger.debug('%s,%s', child.tag, child.text.strip())
            source = Source(urn, child.text.strip())
            epcis_event.source_list.append(source)
            logger.debug('Added %s, %s to the source_list.', urn,
                         child.text.strip())

    def parse_destination_list(self, epcis_event, destination_list):
        for child in destination_list:
            urn = None
            for name, value in child.attrib.items():
                logger.debug('%s,%s', name, value)
                if name == 'type':
                    urn = value
            logger.debug('%s,%s', child.tag, child.text.strip())
            destination = Destination(urn, child.text.strip())
            epcis_event.destination_list.append(destination)
            logger.debug('Added %s, %s to the destination_list.', urn,
                         child.text.strip())

    def parse_ilmd(self, epcis_event, ilmd):
        for child in ilmd:
            logger.debug('%s,%s', child.tag, child.text.strip())
            check_val = child.tag.split('}')[1]
            ilmd = InstanceLotMasterDataAttribute(check_val,
                                                  child.text.strip())
            epcis_event.ilmd.append(ilmd)

    def parse_quantity_list(self, epcis_event, quantity_list):
        '''
        Takes a quantity list element as an input and parses it
        into an EPCPyYes QuantityElement instance.
        :param epcis_event: The EPCPyYes event instance that will contain
        the parsed QuantityElement instance as an attribute.
        :param quantity_list: The Element containing the quantity_list.
        :return: None
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug(epcis_event.render())
        for child in quantity_list:
            if child.tag == 'quantityElement':
                self.parse_quantity_element(epcis_event, child)

    def parse_child_quantity_list(self, epcis_event, quantity_list):
        '''
        Takes a child quantity list element as an input and parses it
        into an EPCPyYes QuantityElement instance.
        :param epcis_event: The EPCPyYes event instance that will contain
        the parsed QuantityElement instance as an attribute.
        :param quantity_list: The Element containing the quantity_list.
        :return: None
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug(epcis_event.render())
        for child in quantity_list:
            if child.tag == 'quantityElement':
                epcis_event.child_quantity_list.append(
                    self.get_quantity_element(child)
                )

    def parse_input_quantity_list(self, epcis_event,
                                  quantity_list):
        '''
        Takes a transformation event input quantity list
        element as an input and parses it
        into an EPCPyYes QuantityElement instance.
        :param epcis_event: The EPCPyYes event instance that will contain
        the parsed QuantityElement instance as an attribute.
        :param quantity_list: The Element containing the quantity_list.
        :return: None
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug(epcis_event.render())
        for child in quantity_list:
            if child.tag == 'quantityElement':
                epcis_event.input_quantity_list.append(
                    self.get_quantity_element(child)
                )

    def parse_output_quantity_list(self, epcis_event,
                                   quantity_list):
        '''
        Takes a transformation event input quantity list
        element as an output and parses it
        into an EPCPyYes QuantityElement instance.
        :param epcis_event: The EPCPyYes event instance that will contain
        the parsed QuantityElement instance as an attribute.
        :param quantity_list: The Element containing the quantity_list.
        :return: None
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug(epcis_event.render())
        for child in quantity_list:
            if child.tag == 'quantityElement':
                epcis_event.output_quantity_list.append(
                    self.get_quantity_element(child)
                )

    def get_quantity_element(self, quantity_element):
        '''
        Parses and returns a quantity element.
        :param quantity_element:
        :return: An EPCPyYes QuantityElement.
        '''
        qe = QuantityElement('')
        for child in quantity_element:
            if child.tag == 'epcClass':
                qe.epc_class = child.text.strip()
            elif child.tag == 'quantity':
                qe.quantity = float(child.text.strip())
            elif child.tag == 'uom':
                qe.uom = child.text.strip()
        return qe

    def parse_quantity_element(self, epcis_event, quantity_element):
        qe = QuantityElement('')
        for child in quantity_element:
            if child.tag == 'epcClass':
                qe.epc_class = child.text.strip()
            elif child.tag == 'quantity':
                qe.quantity = float(child.text.strip())
            elif child.tag == 'uom':
                qe.uom = child.text.strip()
        logger.debug('Appending a quantity list element.')
        epcis_event.quantity_list.append(qe)

    def handle_sbdh(self,
                    header: template_sbdh.StandardBusinessDocumentHeader):
        '''
        Implement this method to support the handling of EPCPyYes
        StandardBusinessDocumentHeader info.
        :param header: The header value.
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.debug(header.render())
        logger.debug('handle_sbdh has been called.')

    def handle_object_event(self, epcis_event: template_events.ObjectEvent):
        '''
        Implement this method to support the handing of EPCPyYes ObjectEvent
        template class instances.
        :param epcis_event: The EPCPyYes template_events.ObjectEvent instance.
        :return: None
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            # since render is being called here, avoiding sending to logger
            # unless debug is set
            logger.debug(epcis_event.render())
        logger.debug('handle object event called...')

    def handle_aggregation_event(
        self,
        epcis_event: template_events.AggregationEvent
    ):
        '''
        Implement this method to handle template_event.AggregationEvent
        instances as they are created during XML parsing.
        :param epcis_event: The AggregationEvent instance.
        :return: None
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            # since render is being called here, avoiding sending to logger
            # unless debug is set
            logger.debug(epcis_event.render())
        logger.debug('handle aggregation event called...')

    def handle_transaction_event(
        self,
        epcis_event: template_events.TransactionEvent
    ):
        '''
        Implement this method to handle
        template_event.TransactionEvent instances as they are created during
        XML paring.
        :param epcis_event: The TransactionEvent instance.
        :return: None
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            # since render is being called here, avoiding sending to logger
            # unless debug is set
            logger.debug(epcis_event.render())
        logger.debug('handle transaction event called...')

    def handle_transformation_event(
        self,
        epcis_event: template_events.TransformationEvent
    ):
        '''
        Implement this method to handle any template_event.TransformationEvent
        instaces as the are created during the parsing process.

        :param epcis_event: An EPCPyYes TransformationEvent
        :return: None
        '''
        if logger.getEffectiveLevel() == logging.DEBUG:
            # since render is being called here, avoiding sending to logger
            # unless debug is set
            logger.debug(epcis_event.render())
        logger.debug('handle transaction event called...')

    def handle_unexpected_element(self, event, element):
        '''
        If an element is found within the EPCIS document that was unexpected
        it will be handed to this event.  Implement this function to handle
        any unexpected or custom elements.
        :param event: The event (usually "end")
        :param element: The lxml.etree.Element that was found.
        '''
        pass
