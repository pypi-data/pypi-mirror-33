# coding: utf-8

from drescher.utils import to_date, to_uuid


class InputFile(object):
    __slots__ = (
        'unit',
        'id', 'name', 'checksum',
        'size', 'type',
        'parameters', 'received_at'
    )

    _RESERVED = frozenset(('unit', ))
    _TRANSLATE = {
        'type': 'tipe'
    }
    _CAST = {
        'id': to_uuid,
        'received_at': to_date,
    }

    DATA_FILE = 1
    HELPER_FILE = 2

    def __init__(self, unit, input_file_data):
        """
        :type unit: Unit
        :type input_file_data: dict
        """
        
        self.unit = unit

        for name in self.__slots__:
            if name not in self._RESERVED:
                translated = self._TRANSLATE.get(name, name)
                value = input_file_data[translated]

                if translated in self._CAST:
                    value = self._CAST[translated](value)

                setattr(self, name, value)


class Unit(object):
    __slots__ = (
        'id', 'year', 'production_id', 
        'status', 'is_test', 'notes',
        'input_files',
        'created_at', 'created_by'
    )

    _RESERVED = frozenset(('files', 'created_by', 'notes'))
    _TRANSLATE = {
        'input_files': 'files'
    }
    _CAST = {
        'created_at': to_date
    }

    DATA_RECEIVING = 1
    STARTED = 2
    IN_PROGRESS = 20
    DEPRECATED = 'deprecated'

    def __init__(self, unit_data):
        """
        :type unit_data: dict
        """

        for name in self.__slots__:
            if name not in self._RESERVED:
                translated = self._TRANSLATE.get(name, name)
                value = unit_data[translated]

                if translated in self._CAST:
                    value = self._CAST[translated](value)

                setattr(self, name, value)
                
        self.input_files = tuple(InputFile(self, _) for _ in unit_data['files'])
        self.created_by = self.DEPRECATED
        self.notes = self.DEPRECATED
