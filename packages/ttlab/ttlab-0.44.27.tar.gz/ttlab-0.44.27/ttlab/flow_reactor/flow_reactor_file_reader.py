import re
from .flow_reactor_date_handler import FlowReactorDateHandler
from .flow_reactor_set_and_measured_values_handler import FlowReactorSetAndMeasuredValuesHandler


class FlowReactorFileReader:
    @staticmethod
    def read_start_time(filename):
        line_with_start_time = FlowReactorFileReader._read_line_nr(filename, 14)
        date = FlowReactorFileReader._extract_date(line_with_start_time)
        return FlowReactorDateHandler.convert_date_to_unix_time(date)

    @staticmethod
    def read_gases(filename):
        line_with_gases = FlowReactorFileReader._read_line_nr(filename, 1)
        list_with_gases = line_with_gases.split('\t')
        return list(filter((lambda x: not (x == '' or x == 'Gas Name:' or x == '\n')), list_with_gases))

    @staticmethod
    def read_gas_concentrations(filename):
        line_with_gas_concentrations = FlowReactorFileReader._read_line_nr(filename, 7)
        list_with_gas_concentrations = line_with_gas_concentrations.split('\t')
        list_with_gas_concentrations = list(
            filter((lambda x: not (x == '' or x == 'Gas Conc.:' or x == '\n')), list_with_gas_concentrations))
        return list(map((lambda x: float(x)), list_with_gas_concentrations))

    @staticmethod
    def read_k_factors(filename):
        line_with_k_factors = FlowReactorFileReader._read_line_nr(filename, 5)
        list_with_k_factors = line_with_k_factors.split('\t')
        list_with_k_factors = list(
            filter((lambda x: not (x == '' or x == 'K-factor:' or x == '\n')), list_with_k_factors))
        list_with_k_factors = list(map((lambda x: x.replace(',', '.')), list_with_k_factors))
        return list(map((lambda x: float(x)), list_with_k_factors))

    @staticmethod
    def read_mfcs(filename):
        line_with_mfcs = FlowReactorFileReader._read_line_nr(filename, 2)
        list_with_mfcs = line_with_mfcs.split('\t')
        return list(filter((lambda x: not (x == '' or x == 'MFC Name:' or x == '\n')), list_with_mfcs))

    @staticmethod
    def read_max_flow_rates(filename):
        line_with_flow_rates = FlowReactorFileReader._read_line_nr(filename, 4)
        list_with_flow_rates = line_with_flow_rates.split('\t')
        list_with_flow_rates = list(
            filter((lambda x: not (x == '' or x == 'Max Flow:' or x == '\n')), list_with_flow_rates))
        return list(map((lambda x: float(x)), list_with_flow_rates))

    @staticmethod
    def read_temperature_and_flow_rates(filename):
        mfcs = FlowReactorFileReader.read_mfcs(filename)
        set_and_measured_values_handler = FlowReactorSetAndMeasuredValuesHandler(mfcs)
        file = open(filename, 'r')
        line_count = 0
        for line in file:
            if line_count > 14:
                set_and_measured_values_handler.add_line_of_data(line)
            line_count += 1

        file.close()
        return {'set_values': set_and_measured_values_handler.set_values,
                'measured_values': set_and_measured_values_handler.measured_values}

    @staticmethod
    def _extract_date(string):
        date = re.findall('\d+-\d+-\d+\s\d+.\d+.\d+.', string)[0]
        return date

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
