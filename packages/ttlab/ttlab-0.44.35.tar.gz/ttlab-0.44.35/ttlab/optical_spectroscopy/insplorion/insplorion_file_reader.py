import numpy as np


class InsplorionFileReader:

    @staticmethod
    def read_wavelength(filename):
        line_nr = InsplorionFileReader._find_line_with_string(filename, 'x vector:')
        line_with_wavelengths = InsplorionFileReader._read_line_nr(filename, line_nr + 1)
        values = line_with_wavelengths.split('\t')
        wavelengths = InsplorionFileReader._convert_to_floats(values)
        return np.array(wavelengths)


    @staticmethod
    def read_time(filename):
        line_nr = InsplorionFileReader._find_line_with_string(filename, 'Run data:')
        file = open(filename, 'r')
        time = []
        for count, line in enumerate(file):
            if count > line_nr:
                values = line.split('\t')
                time.append(float(values[1]))
        file.close()
        return np.array(time)

    @staticmethod
    def read_intensity(filename):
        intensity_ref = InsplorionFileReader._read_bright_ref(filename)
        line_nr = InsplorionFileReader._find_line_with_string(filename, 'Run data:')
        file = open(filename, 'r')
        intensity = []
        for count, line in enumerate(file):
            if count > line_nr:
                values = line.split('\t')
                values = InsplorionFileReader._convert_to_floats(values[2:])
                intensity.append(intensity_ref-np.array(values))
        file.close()

        return np.array(intensity)

    @staticmethod
    def _read_line_nr(filename, nr):
        file = open(filename, 'r')
        for count, line in enumerate(file):
            if count == nr:
                file.close()
                return line
        raise ValueError('Line nr: ' + str(nr) + ' does not exist in file ' + filename)

    @staticmethod
    def _find_line_with_string(filename,string):
        file = open(filename, 'r')
        for count, line in enumerate(file):
            if string in line:
                file.close()
                return count

    @staticmethod
    def _convert_to_floats(list_with_strings):
        return list(map(float,list_with_strings))

    @staticmethod
    def _read_bright_ref(filename):
        line_nr = InsplorionFileReader._find_line_with_string(filename, 'Bright ref:')
        line_with_bright_ref = InsplorionFileReader._read_line_nr(filename, line_nr + 1)
        values = line_with_bright_ref.split('\t')
        intensity = InsplorionFileReader._convert_to_floats(values[1:])
        return np.array(intensity)


