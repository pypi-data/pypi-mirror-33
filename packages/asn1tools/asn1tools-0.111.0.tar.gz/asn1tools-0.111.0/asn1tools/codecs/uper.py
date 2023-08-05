"""Unaligned Packed Encoding Rules (UPER) codec.

"""

import logging
import string

from . import DecodeError
from . import per
from . import restricted_utc_time_to_datetime
from . import restricted_utc_time_from_datetime
from . import restricted_generalized_time_to_datetime
from . import restricted_generalized_time_from_datetime
from .per import integer_as_number_of_bits
from .per import PermittedAlphabet
from .per import Type
from .per import Boolean
from .per import Real
from .per import Null
from .per import Enumerated
from .per import ObjectIdentifier
from .per import Sequence
from .per import Set
from .per import SequenceOf
from .per import SetOf
from .per import Choice
from .per import UTF8String
from .per import Any
from .per import Recursive


LOGGER = logging.getLogger(__name__)


class Encoder(per.Encoder):

    def align(self):
        pass


class Decoder(per.Decoder):

    def align(self):
        pass


class KnownMultiplierStringType(Type):

    PERMITTED_ALPHABET = ''

    def __init__(self,
                 name,
                 minimum=None,
                 maximum=None,
                 has_extension_marker=None,
                 permitted_alphabet=None):
        super(KnownMultiplierStringType, self).__init__(name,
                                                        self.__class__.__name__)
        self.set_size_range(minimum, maximum, has_extension_marker)

        if permitted_alphabet is None:
            permitted_alphabet = self.PERMITTED_ALPHABET

        self.permitted_alphabet = permitted_alphabet
        self.bits_per_character = integer_as_number_of_bits(
            len(permitted_alphabet) - 1)

    def set_size_range(self, minimum, maximum, has_extension_marker):
        self.minimum = minimum
        self.maximum = maximum
        self.has_extension_marker = has_extension_marker

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = maximum - minimum
            self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        encoded = data.encode('ascii')

        if self.has_extension_marker:
            encoder.append_bit(0)

        if self.number_of_bits is None:
            encoder.append_length_determinant(len(encoded))
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(encoded) - self.minimum,
                                                       self.number_of_bits)

        for value in bytearray(encoded):
            encoder.append_non_negative_binary_integer(
                self.permitted_alphabet.encode(value),
                self.bits_per_character)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                raise NotImplementedError(
                    'String size extension is not yet implemented.')

        if self.number_of_bits is None:
            length = decoder.read_length_determinant()
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(self.number_of_bits)

        data = []

        for _ in range(length):
            value = decoder.read_non_negative_binary_integer(self.bits_per_character)
            data.append(self.permitted_alphabet.decode(value))

        return bytearray(data).decode('ascii')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER')
        self.minimum = None
        self.maximum = None
        self.has_extension_marker = None
        self.number_of_bits = None

    def set_restricted_to_range(self, minimum, maximum, has_extension_marker):
        self.minimum = minimum
        self.maximum = maximum
        self.has_extension_marker = has_extension_marker
        size = self.maximum - self.minimum
        self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.has_extension_marker:
            if self.minimum <= data <= self.maximum:
                encoder.append_bit(0)
            else:
                encoder.append_bit(1)
                encoder.append_unconstrained_whole_number(data)
                return

        if self.number_of_bits is None:
            encoder.append_unconstrained_whole_number(data)
        else:
            encoder.append_non_negative_binary_integer(data - self.minimum,
                                                       self.number_of_bits)

    def decode(self, decoder):
        if self.has_extension_marker:
            if decoder.read_bit():
                return decoder.read_unconstrained_whole_number()

        if self.number_of_bits is None:
            return decoder.read_unconstrained_whole_number()
        else:
            value = decoder.read_non_negative_binary_integer(self.number_of_bits)

            return value + self.minimum

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class BitString(per.BitString):

    def encode(self, data, encoder):
        data, number_of_bits = data

        if self.has_named_bits:
            data, number_of_bits = self.rstrip_zeros(data, number_of_bits)

        if self.number_of_bits is None:
            encoder.append_length_determinant(number_of_bits)
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(
                number_of_bits - self.minimum,
                self.number_of_bits)

        encoder.append_bits(data, number_of_bits)

    def decode(self, decoder):
        if self.number_of_bits is None:
            number_of_bits = decoder.read_length_determinant()
        else:
            number_of_bits = self.minimum

            if self.minimum != self.maximum:
                number_of_bits += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)

        value = decoder.read_bits(number_of_bits)

        return (value, number_of_bits)


class OctetString(Type):

    def __init__(self, name, minimum, maximum):
        super(OctetString, self).__init__(name, 'OCTET STRING')
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_length_determinant(len(data))
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(data) - self.minimum,
                                                       self.number_of_bits)

        encoder.append_bytes(data)

    def decode(self, decoder):
        if self.number_of_bits is None:
            length = decoder.read_length_determinant()
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)

        return decoder.read_bits(8 * length)

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class NumericString(KnownMultiplierStringType):

    ALPHABET = bytearray(b' 0123456789')
    ENCODE_MAP = {v: i for i, v in enumerate(ALPHABET)}
    DECODE_MAP = {i: v for i, v in enumerate(ALPHABET)}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_MAP,
                                           DECODE_MAP)


class PrintableString(KnownMultiplierStringType):

    ALPHABET = bytearray((string.ascii_uppercase
                          + string.ascii_lowercase
                          + string.digits
                          + " '()+,-./:=?").encode('ascii'))
    ENCODE_MAP = {v: v for v in ALPHABET}
    DECODE_MAP = {v: v for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_MAP,
                                           DECODE_MAP)


class IA5String(KnownMultiplierStringType):

    ENCODE_DECODE_MAP = {v: v for v in range(128)}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class VisibleString(KnownMultiplierStringType):

    ENCODE_DECODE_MAP = {v: v for v in range(32, 127)}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class GeneralString(Type):

    def __init__(self, name):
        super(GeneralString, self).__init__(name, 'GeneralString')

    def encode(self, _data, _encoder):
        raise NotImplementedError('GeneralString is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('GeneralString is not yet implemented.')

    def __repr__(self):
        return 'GeneralString({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name, 'BMPString')

    def encode(self, data, encoder):
        encoded = data.encode('utf-16-be')
        encoder.append_length_determinant(len(data))
        encoder.append_bytes(encoded)

    def decode(self, decoder):
        length = decoder.read_length_determinant()
        encoded = decoder.read_bits(16 * length)

        return encoded.decode('utf-16-be')

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class GraphicString(Type):

    def __init__(self, name):
        super(GraphicString, self).__init__(name, 'GraphicString')

    def encode(self, data, encoder):
        encoded = data.encode('latin-1')
        encoder.append_length_determinant(len(encoded))
        encoder.append_bytes(bytearray(encoded))

    def decode(self, decoder):
        length = decoder.read_length_determinant()
        encoded = decoder.read_bits(8 * length)

        return encoded.decode('latin-1')

    def __repr__(self):
        return 'GraphicString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name, 'UniversalString')

    def encode(self, _data, _encoder):
        raise NotImplementedError('UniversalString is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('UniversalString is not yet implemented.')

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, _data, _encoder):
        raise NotImplementedError('TeletexString is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('TeletexString is not yet implemented.')

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class UTCTime(VisibleString):

    def encode(self, data, encoder):
        encoded = restricted_utc_time_from_datetime(data)

        return super(UTCTime, self).encode(encoded, encoder)

    def decode(self, decoder):
        decoded = super(UTCTime, self).decode(decoder)

        return restricted_utc_time_to_datetime(decoded)


class GeneralizedTime(VisibleString):

    def encode(self, data, encoder):
        enceded = restricted_generalized_time_from_datetime(data)

        return super(GeneralizedTime, self).encode(enceded, encoder)

    def decode(self, decoder):
        decoded = super(GeneralizedTime, self).decode(decoder)

        return restricted_generalized_time_to_datetime(decoded)


class CompiledType(per.CompiledType):

    def encode(self, data):
        encoder = Encoder()
        self._type.encode(data, encoder)

        return encoder.as_bytearray()

    def decode(self, data):
        decoder = Decoder(bytearray(data))

        return self._type.decode(decoder)


class Compiler(per.Compiler):

    def process_type(self, type_name, type_descriptor, module_name):
        compiled_type = self.compile_type(type_name,
                                          type_descriptor,
                                          module_name)
        constraints = self.compile_constraints(type_name,
                                               type_descriptor,
                                               module_name)

        return CompiledType(compiled_type, constraints)

    def compile_type(self, name, type_descriptor, module_name):
        type_name = type_descriptor['type']

        if type_name == 'SEQUENCE':
            compiled = Sequence(name,
                                *self.compile_members(type_descriptor['members'],
                                                      module_name))
        elif type_name == 'SEQUENCE OF':
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name),
                                  *self.get_size_range(type_descriptor,
                                                       module_name))
        elif type_name == 'SET':
            compiled = Set(name,
                           *self.compile_members(
                               type_descriptor['members'],
                               module_name,
                               sort_by_tag=True))
        elif type_name == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name),
                             *self.get_size_range(type_descriptor,
                                                  module_name))
        elif type_name == 'CHOICE':
            compiled = Choice(name,
                              *self.compile_members(
                                  type_descriptor['members'],
                                  module_name,
                                  flat_additions=True))
        elif type_name == 'INTEGER':
            compiled = Integer(name)
        elif type_name == 'REAL':
            compiled = Real(name)
        elif type_name == 'ENUMERATED':
            compiled = Enumerated(name, type_descriptor['values'])
        elif type_name == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_name == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_name == 'OCTET STRING':
            minimum, maximum, _ = self.get_size_range(type_descriptor,
                                                      module_name)
            compiled = OctetString(name, minimum, maximum)
        elif type_name == 'TeletexString':
            compiled = TeletexString(name)
        elif type_name == 'NumericString':
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = NumericString(name,
                                     *self.get_size_range(type_descriptor,
                                                          module_name),
                                     permitted_alphabet=permitted_alphabet)
        elif type_name == 'PrintableString':
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = PrintableString(name,
                                       *self.get_size_range(type_descriptor,
                                                            module_name),
                                       permitted_alphabet=permitted_alphabet)
        elif type_name == 'IA5String':
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = IA5String(name,
                                 *self.get_size_range(type_descriptor,
                                                      module_name),
                                 permitted_alphabet=permitted_alphabet)
        elif type_name == 'VisibleString':
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = VisibleString(name,
                                     *self.get_size_range(type_descriptor,
                                                          module_name),
                                     permitted_alphabet=permitted_alphabet)
        elif type_name == 'GeneralString':
            compiled = GeneralString(name)
        elif type_name == 'UTF8String':
            compiled = UTF8String(name)
        elif type_name == 'GraphicString':
            compiled = GraphicString(name)
        elif type_name == 'BMPString':
            compiled = BMPString(name)
        elif type_name == 'UTCTime':
            compiled = UTCTime(name)
        elif type_name == 'UniversalString':
            compiled = UniversalString(name)
        elif type_name == 'GeneralizedTime':
            compiled = GeneralizedTime(name)
        elif type_name == 'BIT STRING':
            minimum, maximum, _ = self.get_size_range(type_descriptor,
                                                      module_name)
            has_named_bits = ('named-bits' in type_descriptor)
            compiled = BitString(name,
                                 minimum,
                                 maximum,
                                 has_named_bits)
        elif type_name == 'ANY':
            compiled = Any(name)
        elif type_name == 'ANY DEFINED BY':
            compiled = Any(name)
        elif type_name == 'NULL':
            compiled = Null(name)
        else:
            if type_name in self.types_backtrace:
                compiled = Recursive(name,
                                     type_name,
                                     module_name)
                self.recursive_types.append(compiled)
            else:
                compiled = self.compile_user_type(name,
                                                  type_name,
                                                  module_name)

        if 'tag' in type_descriptor:
            compiled = self.set_compiled_tag(compiled, type_descriptor)

        if 'restricted-to' in type_descriptor:
            compiled = self.set_compiled_restricted_to(compiled,
                                                       type_descriptor,
                                                       module_name)

        return compiled


def compile_dict(specification):
    return Compiler(specification).process()


def decode_length(_data):
    raise DecodeError('Decode length is not supported for this codec.')
