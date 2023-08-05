import re
from .mass_spectrometer_acquired_data_handler import MassSpectrometerAcquiredDataHandler
from .mass_spectrometer_date_handler import MassSpectrometerDateHandler


class MassSpectrometerFileReader:
    @staticmethod
    def read_start_time(filename):
        line_with_start_time = MassSpectrometerFileReader._read_line_nr(filename, 3)
        date = MassSpectrometerFileReader._extract_date(line_with_start_time)
        return MassSpectrometerDateHandler.convert_date_to_unix_time(date)

    @staticmethod
    def read_end_time(filename):
        line_with_end_time = MassSpectrometerFileReader._read_line_nr(filename, 4)
        date = MassSpectrometerFileReader._extract_date(line_with_end_time)
        return MassSpectrometerDateHandler.convert_date_to_unix_time(date)

    @staticmethod
    def read_gases(filename):
        line_with_gas_names = MassSpectrometerFileReader._read_line_nr(filename, 6)
        gases = line_with_gas_names.split('\t')
        return list(filter((lambda x: not (x == '' or x == '\n')), gases))

    @staticmethod
    def read_acquired_data(filename):
        gases = MassSpectrometerFileReader.read_gases(filename)
        acquired_data_handler = MassSpectrometerAcquiredDataHandler(gases)
        file = open(filename,'r')
        line_count = 0
        for line in file:
            if line_count > 7:
                acquired_data_handler.add_line_of_data(line)
            line_count += 1

        file.close()
        return acquired_data_handler.acquired_data

    @staticmethod
    def _extract_date(string):
        return re.findall('\d+/\d+/\d\d\d\d\s\d\d\:\d\d\:\d\d\.\d+\s\D\D', string)[0]

    @staticmethod
    def _read_line_nr(filename, nr):
        file = open(filename, 'r')
        i = 0
        for line in file:
            if i == nr:
                file.close()
                return line
            i += 1
        raise ValueError('Line nr: ' + str(nr) + ' does not exist in file ' + filename)
