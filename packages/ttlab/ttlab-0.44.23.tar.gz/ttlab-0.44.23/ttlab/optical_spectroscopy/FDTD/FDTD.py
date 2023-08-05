from .FDTD_file_reader import FDTDFileReader
from plotly.offline import init_notebook_mode, iplot, plot
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


class FDTD:

    def __init__(self, filename_cross_section, filename_wavelength, simulation_names):
        self.data = FDTDFileReader.read_data(filename_cross_section=filename_cross_section, filename_wavelength=filename_wavelength, simulation_names=simulation_names)

    def get_wavelength(self, sample):
        return self.data[sample].wavelength

    def get_cross_section(self, sample):
        return self.data[sample].cross_section

    def get_samples(self):
        return self.data.keys()

    def plotly_all(self, title=''):
        init_notebook_mode(connected=True)
        data = []
        for sample in self.get_samples():
            x = self.data[sample].wavelength
            y = self.data[sample].cross_section
            trace = FDTD._create_x_y_trace(x, y, sample)
            data.append(trace)
        layout = FDTD._get_plotly_layout(title)
        fig = go.Figure(data=data, layout=layout)
        return iplot(fig)

    def plot_sample(self,sample,ax=None, label=None):
        if ax is None:
            ax = plt.axes()
        if label is None:
            ax.plot(self.get_wavelength(sample),self.get_cross_section(sample),label=sample)
        else:
            ax.plot(self.get_wavelength(sample),self.get_cross_section(sample),label=label)
        return ax

    def find_peak(self,sample):
        cross_section = self.get_cross_section(sample)
        wavelength = self.get_wavelength(sample)
        index_of_max = np.argmax(cross_section)
        return wavelength[index_of_max], cross_section[index_of_max], index_of_max

    @staticmethod
    def _find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    @staticmethod
    def _create_x_y_trace(x, y, name):
        return go.Scatter(x=x, y=y, name=name)

    @staticmethod
    def _get_plotly_layout(title=''):
        return go.Layout(
                title = title,
                xaxis=dict(
                    title='Wavelength [nm]'
                ),
                yaxis=dict(
                    title='Scattering cross section [m<sup>2</sup>]'
                )
            )
