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


class SBDHNamespaceHelper(object):
    '''
    Creates all of the properly formatted namespace element tag strings
    for lookup and comparison when parsing.
    '''

    def __init__(self, header_namespace='sbdh'):
        self._sbdh = '{{{0}}}StandardBusinessDocumentHeader'.format(
            header_namespace)
        self._header_version = '{{{0}}}HeaderVersion'.format(header_namespace)
        self._sender = '{{{0}}}Sender'.format(header_namespace)
        self._identifier = '{{{0}}}Identifier'.format(header_namespace)
        self._contact_information = '{{{0}}}ContactInformation'.format(
            header_namespace)
        self._contact = '{{{0}}}Contact'.format(header_namespace)
        self._email_address = '{{{0}}}EmailAddress'.format(header_namespace)
        self._telephone_number = '{{{0}}}TelephoneNumber'.format(header_namespace)
        self._fax_number = '{{{0}}}FaxNumber'.format(header_namespace)
        self._contact_type_identifier = '{{{0}}}ContactTypeIdentifier'.format(
            header_namespace)
        self._receiver = '{{{0}}}Receiver'.format(header_namespace)
        self._document_identification = '{{{0}}}DocumentIdentification'.format(
            header_namespace)
        self._standard = '{{{0}}}Standard'.format(header_namespace)
        self._type_version = '{{{0}}}TypeVersion'.format(header_namespace)
        self._instance_identifier = '{{{0}}}InstanceIdentifier'.format(
            header_namespace)
        self._document_type = '{{{0}}}Type'.format(header_namespace)
        self._multiple_type = '{{{0}}}MultipleType'.format(header_namespace)
        self._creation_date_and_time = '{{{0}}}CreationDateAndTime'.format(
            header_namespace)

    @property
    def sbdh(self):
        return self._sbdh

    @property
    def header_version(self):
        return self._header_version

    @property
    def sender(self):
        return self._sender

    @property
    def identifier(self):
        return self._identifier

    @property
    def contact_information(self):
        return self._contact_information

    @property
    def contact(self):
        return self._contact

    @property
    def email_address(self):
        return self._email_address

    @property
    def telephone_number(self):
        return self._telephone_number

    @property
    def fax_number(self):
        return self._fax_number

    @property
    def contact_type_identifier(self):
        return self._contact_type_identifier

    @property
    def receiver(self):
        return self._receiver

    @property
    def document_identification(self):
        return self._document_identification

    @property
    def standard(self):
        return self._standard

    @property
    def type_version(self):
        return self._type_version

    @property
    def instance_identifier(self):
        return self._instance_identifier

    @property
    def document_type(self):
        return self._document_type

    @property
    def multiple_type(self):
        return self._multiple_type

    @property
    def CreationDateAndTime(self):
        return self._CreationDateAndTime
