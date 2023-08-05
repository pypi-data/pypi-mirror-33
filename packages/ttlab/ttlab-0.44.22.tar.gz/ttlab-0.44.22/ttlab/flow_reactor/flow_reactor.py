import numpy as np
import matplotlib.pyplot as plt
from .flow_reactor_file_reader import FlowReactorFileReader


class FlowReactor:

    def __init__(self, filename):
        self.filename = filename
        self.start_time = FlowReactorFileReader.read_start_time(filename)
        self.gases = FlowReactorFileReader.read_gases(filename)
        self.gas_concentrations = FlowReactorFileReader.read_gas_concentrations(filename)
        self.mfcs = FlowReactorFileReader.read_mfcs(filename)
        self.max_flow_rates = FlowReactorFileReader.read_max_flow_rates(filename)
        self.k_factors = FlowReactorFileReader.read_k_factors(filename)
        values = FlowReactorFileReader.read_temperature_and_flow_rates(filename)
        self.set_values = values['set_values']
        self.measured_values = values['measured_values']

    def plot_flow_rate(self,mfc):
        if mfc not in self.mfcs:
            raise ValueError(mfc + ' does not exist in file: ' + self.filename)
        x = self.measured_values['Time']
        y = self.measured_values['Flow Rate'][mfc]
        return plt.plot(x,y)

    def plot_reactor_temperature(self):
        x = self.measured_values['Time']
        y = self.measured_values['Temperature']['Reactor']
        return plt.plot(x,y)

    def plot_sample_temperature(self,ax):
        x = self.measured_values['Time']
        y = self.measured_values['Temperature']['Sample']
        if ax is not None:
            return ax.plot(x,y)
        return plt.plot(x,y)

    def get_time(self):
        time = self.measured_values['Time']
        return np.array(time)

    def get_reactor_temperature(self):
        reactor_temperature = self.measured_values['Temperature']['Reactor']
        return np.array(reactor_temperature)

    def get_sample_temperature(self):
        sample_temperature = self.measured_values['Temperature']['Sample']
        return np.array(sample_temperature)

    def get_sample_temperature_at_time(self,time):
        index = FlowReactor._find_index_of_nearest(self.get_time(),time)
        return self.get_sample_temperature()[index]

    def shift_start_time_back(self,time):
        self.start_time = self.start_time - time
        for index in len(0,self.set_values['Time']):
            self.set_values['Time'][index] += time

        for index in len(0,self.measured_values['Time']):
            self.measured_values['Time'][index] += time

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()
