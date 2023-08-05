from .cary5000 import Cary5000
from .insplorion import Insplorion


class OpticalSpectroscopy:

    def __init__(self, filename, equipment_name):
        print('Hello')

    def __new__(cls, filename, equipment_name):
        if equipment_name is EquipmentNames.cary5000:
            return Cary5000(filename)
        elif equipment_name is EquipmentNames.insplorion:
            return Insplorion(filename)
        else:
            raise NameError('Equipment name: ' + equipment_name + ' do not exist')

    @staticmethod
    def get_list_of_equipment_names():
        return [x for x in dir(EquipmentNames) if not x.startswith('__')]


class EquipmentNames:
    cary5000 = 'cary5000'
    insplorion = 'insplorion'
