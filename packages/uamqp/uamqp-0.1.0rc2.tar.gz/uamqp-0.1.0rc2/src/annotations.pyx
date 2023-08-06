#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Python imports
import logging

# C imports
from libc cimport stdint

cimport c_amqpvalue
cimport c_amqp_definitions
cimport c_utils


_logger = logging.getLogger(__name__)


cdef annotations_factory(c_amqpvalue.AMQP_VALUE value):
    wrapped = value_factory(value)
    if c_amqp_definitions.is_delivery_annotations_type_by_descriptor(<c_amqp_definitions.delivery_annotations>value):
        new_obj = create_delivery_annotations(wrapped)
    elif c_amqp_definitions.is_message_annotations_type_by_descriptor(<c_amqp_definitions.message_annotations>value):
        new_obj = create_message_annotations(wrapped)
    elif c_amqp_definitions.is_footer_type_by_descriptor(<c_amqp_definitions.footer>value):
        new_obj = create_footer(wrapped)
    else:
        new_obj = create_annotations(wrapped)
    return new_obj


cpdef create_annotations(AMQPValue value):
    annotations = cAnnotations()
    annotations.create(value)
    return annotations


cpdef create_application_properties(AMQPValue value):
    annotations = cApplicationProperties()
    annotations.create(value)
    return annotations


cpdef create_delivery_annotations(AMQPValue value):
    annotations = cDeliveryAnnotations()
    annotations.create(value)
    return annotations


cpdef create_message_annotations(AMQPValue value):
    annotations = cMessageAnnotations()
    annotations.create(value)
    return annotations


cpdef create_fields(AMQPValue value):
    annotations = cFields()
    annotations.create(value)
    return annotations


cpdef create_footer(AMQPValue value):
    annotations = cFooter()
    annotations.create(value)
    return annotations


cdef class cAnnotations(StructBase):

    cdef c_amqpvalue.AMQP_VALUE _c_value

    def __cinit__(self):
        pass

    def __dealloc__(self):
        _logger.debug("Deallocating {}".format(self.__class__.__name__))
        #self.destroy()

    cdef _validate(self):
        if <void*>self._c_value is NULL:
            self._memory_error()

    cpdef destroy(self):
        if <void*>self._c_value is not NULL:
            _logger.debug("Destroying {}".format(self.__class__.__name__))
            c_amqpvalue.amqpvalue_destroy(<c_amqpvalue.AMQP_VALUE>self._c_value)
            self._c_value = <c_amqpvalue.AMQP_VALUE>NULL

    cpdef clone(self):
        cdef c_amqp_definitions.annotations value
        value = c_amqpvalue.amqpvalue_clone(<c_amqpvalue.AMQP_VALUE>self._c_value)
        if <void*>value == NULL:
            self._value_error()
        amqp_value = value_factory(value)
        return cAnnotations(amqp_value)

    cpdef get_encoded_size(self):
        cdef size_t length
        if c_amqpvalue.amqpvalue_get_encoded_size(self._c_value, &length) != 0:
            self._value_error("Failed to get encoded size.")
        return length

    cpdef create(self, AMQPValue value):
        self.destroy()
        self._c_value = c_amqp_definitions.amqpvalue_create_annotations(<c_amqpvalue.AMQP_VALUE>value._c_value)
        self._validate()

    cdef wrap(self, c_amqp_definitions.annotations value):
        self.destroy()
        self._c_value = value
        self._validate()

    @property
    def value(self):
        return value_factory(self._c_value)

    @property
    def map(self):
        cdef c_amqpvalue.AMQP_VALUE value
        if c_amqpvalue.amqpvalue_get_map(self._c_value, &value) == 0:
            if <void*>value == NULL:
                return None
            return value_factory(value).value
        else:
            #self._value_error("Failed to get map.")
            return None


cdef class cApplicationProperties(cAnnotations):

    cpdef create(self, AMQPValue value):
        self.destroy()
        self._c_value = c_amqp_definitions.amqpvalue_create_application_properties(
            <c_amqp_definitions.application_properties>value._c_value)
        self._validate()

    @property
    def map(self):
        cdef c_amqpvalue.AMQP_VALUE extracted
        cdef c_amqpvalue.AMQP_VALUE value
        extracted = c_amqpvalue.amqpvalue_get_inplace_described_value(self._c_value)
        if <void*>extracted == NULL:
            return None

        if c_amqpvalue.amqpvalue_get_map(extracted, &value) == 0:
            if <void*>value == NULL:
                return None
            return value_factory(value).value
        else:
            return None


cdef class cDeliveryAnnotations(cAnnotations):

    cpdef create(self, AMQPValue value):
        self.destroy()
        self._c_value = c_amqp_definitions.amqpvalue_create_delivery_annotations(
            <c_amqp_definitions.delivery_annotations>value._c_value)
        self._validate()


cdef class cMessageAnnotations(cAnnotations):

    cpdef create(self, AMQPValue value):
        self.destroy()
        self._c_value = c_amqp_definitions.amqpvalue_create_message_annotations(
            <c_amqp_definitions.message_annotations>value._c_value)
        self._validate()


cdef class cFields(cAnnotations):

    cpdef create(self, AMQPValue value):
        self.destroy()
        self._c_value = c_amqp_definitions.amqpvalue_create_fields(<c_amqp_definitions.fields>value._c_value)
        self._validate()


cdef class cFooter(cAnnotations):

    cpdef create(self, AMQPValue value):
        self.destroy()
        self._c_value = c_amqp_definitions.amqpvalue_create_footer(<c_amqp_definitions.footer>value._c_value)
        self._validate()
