from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
import numpy as np
from .insplorion_file_reader import InsplorionFileReader
from .insplorion_functions import InsplorionFunctions
import matplotlib.pyplot as plt


class Insplorion:

    def __init__(self, filename):
        self.filename = filename
        self.wavelength = InsplorionFileReader.read_wavelength(self.filename)
        self.time = InsplorionFileReader.read_time(self.filename)
        self.intensity = InsplorionFileReader.read_intensity(self.filename)

    def plotly_intensity(self):
        init_notebook_mode(connected=True)
        data = [
            go.Surface(
                x=self.wavelength,
                y=self.time[0::100],
                z=self.intensity[0::100]
            )
        ]
        fig = go.Figure(data=data, layout=Insplorion._get_plotly_layout())
        return iplot(fig, filename='elevations-3d-surface')

    def get_peak_position(self):
        peak_position = []
        for n, intensity in enumerate(self.intensity):
            if n%100==0:
                peak_position.append(InsplorionFunctions.find_peak_position(self.wavelength,intensity))
        return np.array(peak_position)

    def plot_peak_position(self):
        peak_position = self.get_peak_position()
        y = []
        err = []
        for peak in peak_position:
            y.append(peak[0])
            err.append(peak[1])
        ax = plt.errorbar(x=np.linspace(0,len(y),len(y)),y=y,yerr=err)
        plt.gca().set_xlabel('Time [a.u.]')
        plt.gca().set_ylabel('Peak position [nm]')
        return ax


    @staticmethod
    def _get_plotly_layout():
        return go.Layout(
            scene=dict(
                xaxis=dict(
                    title='Wavelength [nm]',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                ),
                yaxis=dict(
                    title='Time [s]',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                ),
                zaxis=dict(
                    title='Intensity [a.u.]',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                ), ),
            width=800,
            margin=dict(
                r=40, b=40,
                l=40, t=40)
            )
