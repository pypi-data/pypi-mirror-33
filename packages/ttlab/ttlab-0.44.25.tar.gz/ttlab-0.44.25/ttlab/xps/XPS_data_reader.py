import numpy as np


class Survey:

    def __init__(self):
        self.energy = []
        self.counts = []


class Multi:

    def __init__(self):
        self.energy = {}
        self.counts = {}


class XPSDataReader:

    @staticmethod
    def read_survey(filename):
        survey = Survey()
        if filename:
            with open(filename, "r") as file:
                for count, line in enumerate(file):
                    if count == 2:
                        if not XPSDataReader._is_survey(line):
                            raise ImportError(filename + ' is not a survey')
                    elif count == 4:
                        start_energy = float(line)
                    elif count == 5:
                        step_size = float(line)
                    elif count == 6:
                        data_points = int(line)
                        survey.energy = np.linspace(start_energy, start_energy + ((data_points-1) * step_size), data_points)
                    elif 6 < count< data_points + 7:
                        survey.counts.append(float(line))

                survey.counts = np.array(survey.counts)
            return survey
        else:
            return

    @staticmethod
    def read_multi(filename):
        multi = Multi()
        if filename:
            with open(filename, "r") as file:
                count = 0
                for line in file:
                    if count == 2:
                        if XPSDataReader._is_survey(line):
                            raise ImportError(filename + ' is a survey')
                        orbital = line.rstrip()
                        multi.counts[orbital] = []
                        multi.energy[orbital] = []
                    elif count == 4:
                        start_energy = float(line)
                    elif count == 5:
                        step_size = float(line)
                    elif count == 6:
                        data_points = int(line)
                        multi.energy[orbital] = np.linspace(start_energy, start_energy + ((data_points-1) * step_size), data_points)
                    elif 6 < count < data_points + 7:
                        multi.counts[orbital].append(float(line))
                    elif count > 6 and count == data_points + 7:
                        multi.counts[orbital] = np.array(multi.counts[orbital])
                        count = -1
                    count += 1
            return multi
        else:
            return

    @staticmethod
    def _is_survey(line):
        return line.rstrip() == 'Sur1'

    @staticmethod
    def _is_multi(line):
        return line.rstrip() == 'Full'
