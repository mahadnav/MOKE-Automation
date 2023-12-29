# Some generic packages we need
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Let's import our instrument classes
from srs_sr830 import SRS_SR830
from bop50_8d import KEPCO_BOP

class Experiment():
    """
    Class for automating the Magneto Optic Kerr Effect (MOKE) experiment using the KEPCO Bipolar Operational Power Supply (BOP)
    and the SRS Lock-in Amplifier (LIA).
    """
    def __init__(self, logFilePath=None):
        """
        Initializes the Experiment class.

        Parameters:
        - logFilePath (str): Path to the log file. If None, a default log file path is created.
        """
        if logFilePath is None:
            if not os.path.isdir(os.path.abspath('./Experiment_Logs')):
                os.mkdir(os.path.abspath('./Experiment_Logs'))
            logFilePath = './Experiment_Logs/MOKE_log_{}.log'.format(self._get_timestring())
        with open(logFilePath, 'w') as log:
            log.write('SpinLab Instruments LogFile @ {}\n'.format(datetime.utcnow()))
        self._logFile = os.path.abspath(logFilePath)
        self._logWrite('OPEN_')

        # Initialise our Instruments
        self.PS = KEPCO_BOP(logFile=self._logFile)
        self.LIA = SRS_SR830(logFile=self._logFile)

        # Some initial PS settings for safety
        self.PS.CurrentMode()
        self.PS.VoltageOut(20)
        self.PS.CurrentOut(0)

        # Various delays here
        self.sen = 0.0002
        self.sen_delay = 3
        self.read_reps = 1
        self.rep_delay = 0
        self.read_delay = 0.02
        self.from0delay = 4

        self._welcome()

    
    def __del__(self):
        """
        Closes the Experiment instance and deletes the associated instrument instances.
        """
        self._logWrite('CLOSE')
        del self.PS
        del self.LIA

    def __str__(self):
        """
        Returns a string representation of the Experiment instance.
        """
        return 'MOKE Experiment @ ' + self._get_timestring()
    
    def _logWrite(self, action, value=''):
        """
        Writes an entry to the log file.

        Parameters:
        - action (str): Action to be logged.
        - value: Value associated with the action.
        """
        if self._logFile is not None:
            with open(self._logFile, 'a') as log:
                timestamp = datetime.utcnow()
                log.write('%s %s : %s \n' % (timestamp, action, repr(value)))
    _log = _logWrite
       

    def _welcome(self):
        """
        Displays a welcome message and prints default experiment parameters.
        """
        print("Welcome to the MOKE Experiment!")
        print("Here are some default experiment parameters.\n")
        self._print_parameters()
        
    def _print_parameters(self):
        """
        Prints the current experiment parameters.
        """
        parameters = {
            'PS Output Current (A)': self.PS.current,
            'PS Output Voltage (V)': self.PS.voltage,
            'PS Output Mode (Current/Voltage)': self.PS.OperationMode,
            'LIA Time Constant': self.LIA.TC,
            'LIA Sensivity': self.sen,
            'Sensivity Delay (s)': self.sen_delay,
            'Read Repetitions': self.read_reps,
            'Read Repetition Delay': self.rep_delay,
            'Read Delay': self.read_delay,
            'From 0 Delay (s)': self.from0delay,
            'Log File': self._logFile}
        for key, val in parameters.items():
            print(key, ':\t', val)

    def _get_timestring(self):
        """
        Returns a formatted string representing the current date and time.
        """
        now = datetime.now()
        return '{}-{}-{}_{}-{}-{}'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    
    def _get_sen(self, sen):
        """
        Returns the sensitivity value, using the default if sen is None.

        Parameters:
        - sen: Sensitivity value.
        """
        if sen is None:
            sen = self.sen
        return sen
    
    def _get_sen_delay(self, sen_delay):
        """
        Returns the sensitivity delay, using the default if sen_delay is None.

        Parameters:
        - sen_delay: Sensitivity delay value.
        """
        if sen_delay is None:
            sen_delay = self.sen_delay
        return sen_delay
    
    def _get_read_reps(self, read_reps):
        """
        Returns the read repetitions value, using the default if read_reps is None.

        Parameters:
        - read_reps: Number of read repetitions.
        """
        if read_reps is None:
            read_reps = self.read_reps
        return read_reps
    
    def _get_rep_delay(self, rep_delay):
        """
        Returns the repetition delay value, using the default if rep_delay is None.

        Parameters:
        - rep_delay: Repetition delay value.
        """
        if rep_delay is None:
            rep_delay = self.rep_delay
        return rep_delay
    
    def _get_read_delay(self, read_delay):
        """
        Returns the read delay value, using the default if read_delay is None.

        Parameters:
        - read_delay: Read delay value.
        """
        if read_delay is None:
            read_delay = self.read_delay
        return read_delay
    
    def _get_from0delay(self, from0delay):
        """
        Returns the delay from 0 value, using the default if from0delay is None.

        Parameters:
        - from0delay: From 0 delay value.
        """
        if from0delay is None:
            from0delay = self.from0delay
        return from0delay

    def sweep_field(self, fields, save_dir, filename, close_loop=False, livefig=True, savefig=True, closefig=False,
                    file_prefix='', sen=0.002, sen_delay=None, read_reps=None, rep_delay=None,
                    read_delay=None, from0delay=None, return_XY=False):
        """
        Sweeps the magnetic field and performs the MOKE experiment.

        Parameters:
        - fields: Array of magnetic field values.
        - save_dir (str): Directory to save the experiment data.
        - filename (str): Name of the file to save the experiment data.
        - close_loop (bool): Whether to close the loop (i.e., connect the last point to the first).
        - livefig (bool): Whether to display a live plot during the experiment.
        - savefig (bool): Whether to save the final plot as an image file.
        - closefig (bool): Whether to close the plot after the experiment.
        - file_prefix (str): Prefix to add to the filename.
        - sen (float): Sensitivity value.
        - sen_delay (float): Sensitivity delay value.
        - read_reps (int): Number of read repetitions.
        - rep_delay (float): Repetition delay value.
        - read_delay (float): Read delay value.
        - from0delay (float): From 0 delay value.
        - return_XY (bool): Whether to return the X and Y arrays.

        Returns:
        - If return_XY is True, returns the X and Y arrays.
        """
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        fields = np.concatenate((fields, -fields))
        currents = self.field2current(fields)

        # Janky solution to the current not immediately jumping from 0 to the first value
        self.PS.set_current(currents[0])
        time.sleep(self._get_from0delay(from0delay))

        if livefig:
            plot_title = 'Field Sweep {:.4g} – {:.4g} Oe'.format(fields.min(), fields.max())
            self._make_fig(plot_title, 'Field (Oe)', 'Voltage (AU)')

        x_arr, y_arr = self._sweep_parameter(currents, self.PS.set_current, save_dir, livefig,
                                             savefig, closefig, sen, sen_delay, read_reps,
                                             rep_delay, read_delay, fields, filename, close_loop)

        if close_loop:
            currents, fields = np.append(currents, currents[0]), np.append(fields, fields[0])

        # Check if the file already exists and modify the filename if needed
        save_path = os.path.join(save_dir, filename + '.csv')
        counter = 1
        while os.path.exists(save_path):
            filename = filename + r'_({})'.format(counter)
            save_path = os.path.join(save_dir, filename + '.csv')
            counter += 1

        df = pd.DataFrame({'current_A': currents, 'field_Oe': fields, 'X': x_arr, 'Y': y_arr})
        df.to_csv(save_path, index=False)

        if return_XY:
            return x_arr, y_arr

    def _sweep_parameter(self, params, setter_method, save_dir, livefig, savefig, closefig, sen,
                         sen_delay, read_reps, rep_delay, read_delay, xrange, filename, close_loop):
        """
        Internal method for sweeping a parameter and performing the MOKE experiment.

        Parameters:
        - params: Array of parameter values.
        - setter_method: Method to set the parameter.

        Returns:
        - X_array: Array of X values.
        - Y_array: Array of Y values.
        """
        self.LIA.SEN = self._get_sen(sen)
        X_array, Y_array = np.array([], dtype=float), np.array([], dtype=float)
        
        for i, param in enumerate(params):
            setter_method(param)
            time.sleep(self._get_read_delay(read_delay))
            X, Y = self.readXY(read_reps, rep_delay, sen_delay)
            X_array = np.append(X_array, X)
            Y_array = np.append(Y_array, Y)
            
            if close_loop:
                if i == len(params) - 1:
                    xrange = np.append(xrange, self.current2field(params[0]))
                    X_array = np.append(X_array, X_array[0])
                    Y_array = np.append(Y_array, Y_array[0])

            if livefig:
                if close_loop:
                    if i == len(params) - 1:
                        self._update_sweep_plot(xrange[0:i + 2], X_array, Y_array)
                    else:
                        self._update_sweep_plot(xrange[0:i + 1], X_array, Y_array)
                else:
                    self._update_sweep_plot(xrange[0:i + 1], X_array, Y_array)
            plt.show()

        self.PS.current = 0

        # Check if the file already exists and modify the filename if needed
        save_path = os.path.join(save_dir, filename + '.png')
        counter = 1
        while os.path.exists(save_path):
            filename = filename + '_({})'.format(counter)
            save_path = os.path.join(save_dir, filename + '.png')
            counter += 1

        if savefig:
            self.fig.savefig(save_path, dpi=600)

        if closefig:
            plt.close(self.fig)

        return X_array, Y_array


    def field2current(self, field):
        """
        Converts magnetic field values to current values.

        Parameters:
        - field: Magnetic field values.

        Returns:
        - Current values.
        """
        return field / 193
    
    def current2field(self, current):
        """
        Converts current values to magnetic field values.

        Parameters:
        - current: Current values.

        Returns:
        - Magnetic field values.
        """
        return current * 193

    def _make_fig(self, title, xlabel, ylabel):
        """
        Creates a figure for plotting.

        Parameters:
        - title (str): Title of the plot.
        - xlabel (str): X-axis label.
        - ylabel (str): Y-axis label.
        """
        self.fig, self.ax = plt.subplots(figsize=(9,6))

        self.l1, = self.ax.plot([], [], label='Channel 1 (X)')
        self.l2, = self.ax.plot([], [], label='Channel 2 (Y)')

        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_title(title)
        self.ax.legend()
        plt.show()

    def _update_sweep_plot(self, xdata, ch1_data, ch2_data):
        """
        Updates the live plot during the experiment.

        Parameters:
        - xdata: Array of X-axis values.
        - ch1_data: Array of Channel 1 data (X values).
        - ch2_data: Array of Channel 2 data (Y values).
        """
        self.l1.remove()
        self.l2.remove()

        self.l1, = self.ax.plot(xdata, ch1_data, 'o-', color='green', markersize=6, alpha=0.5, label='Channel 1 (X)')
        self.l2, = self.ax.plot(xdata, ch2_data, 'o-', color='purple', markersize=6, alpha=0.5, label='Channel 2 (Y)')

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def readXY(self, read_reps, rep_delay, sen_delay):
        """
        Reads X and Y values from the Lock-in Amplifier.

        Parameters:
        - read_reps (int): Number of read repetitions.
        - rep_delay (float): Repetition delay value.
        - sen_delay (float): Sensitivity delay value.

        Returns:
        - Xval: Mean value of X readings.
        - Yval: Mean value of Y readings.
        """
        read_reps = self._get_read_reps(read_reps)
        rep_delay = self._get_rep_delay(rep_delay)
        sen_delay = self._get_sen_delay(sen_delay)
                
        X_arr, Y_arr = np.array([], dtype=float), np.array([], dtype=float)
        for i in range(read_reps):
            X, Y = self.LIA.getXY()
            X_arr = np.append(X_arr, X)
            Y_arr = np.append(Y_arr, Y)
            time.sleep(rep_delay)
        Xval = np.mean(X_arr)
        Yval = np.mean(Y_arr)

        sen_ratio = abs(max(abs(Xval), abs(Yval)))/self.LIA.SEN
        if sen_ratio > 0.8:
            self.LIA.decrease_sensitivity()
            time.sleep(sen_delay)
        return Xval, Yval
        

