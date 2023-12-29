# Jupyter Notebook for MOKE Automation

## Overview

This Jupyter Notebook serves as a comprehensive tool for automating the Magneto Optic Kerr Effect (MOKE) experiment using the KEPCO Bipolar Operational Power Supply (BOP) and the SRS Lock-in Amplifier (LIA). The script allows for efficient parameter setting, data acquisition, and visualization, streamlining the MOKE experimental process.

The magneto-optic Kerr effect (MOKE) is a non-invasive optical technique used to characterize magnetic materials. The Kerr effect is a phenomenon where the polarization of incident light changes when it is reflected from a magnetized surface. The change in polarization depends on the orientation and magnitude of the magnetization vector in the material. By performing MOKE, we can obtain hysteresis loops that show how the magnetization of a material changes by changing the applied magnetic field. Hysteresis loops have unique characteristics for different systems, such as saturation magnetization (Ms) which is the maximum value of magnetization that can be achieved, and coercivity ($H_c$) which is the minimum field required to reduce the magnetization to zero.

In our experiment, light from the He-Ne laser (λ = 632.8 nm) passes through a polarizer (set to horizontal polarization). An aspheric lens is used to focus the light on the sample surface. The sample holder is placed between the poles of an electromagnet. This electromagnet is connected to a KEPCO Bi-polar Operational Power (BOP) supply. As we change the input current of the power supply, the magnetic field can be controlled over the sample. The reflected light is then modulated sinusoidally by the photoelastic modulator (Hinds Instrument, PEM-100) operated at 50 kHz. The modulated signal is also used as a reference for the SRS Lock-in Amplifier (LIA). The modulated beam traverses through an analyzer to reach a high-speed photodetector (Hinds Instruments, DET-200). Since the modulated signal is very small, the output from the photodetector is fed to the lock-in amplifier. The intensities from the lock-in are then translated to magnetization and are plotted against the applied field.  


## Prerequisites

To run the Jupyter Notebook successfully, ensure you have the required Python libraries installed. You can install them using the following command:

```bash
pip install pyvisa numpy pandas matplotlib
```

## Use Case

1. **Importing Libraries:** The initial step involves importing necessary Python libraries, establishing the prerequisites for instrument communication, and preparing the environment for the MOKE automation.

```python
import pyvisa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from MOKE import Experiment
```

2. **Checking Connected Devices:** Using PyVISA, the script lists the connected devices to verify the proper setup of the KEPCO Bipolar Operational Power Supply and the SRS Lock-in Amplifier.

```python
rm = pyvisa.ResourceManager()
rm.list_resources()
```

3. **Initializing the MOKE Experiment Script:** The `Experiment` class from the MOKE module is instantiated to initialize the MOKE automation script.

```python
E = Experiment()
```

4. **Setting Parameters and Performing the Measurement:** The script utilizes a user-friendly interface to set key parameters such as the magnetic field range, number of data points, save directory, and filename. The `sweep_field` function executes the MOKE experiment and saves the acquired data.

```python
field_max = 100
num_points = 100

field = np.linspace(-field_max, field_max, num_points)

save_dir = r"C:\Users\physlab\Desktop\MOKE Automation\Data"
sample = 'NiFe_SPT4(50nm)'
filename = fr'{sample}_field_sweep_{field.min()}-{field.max()}_Oe'

E.sweep_field(field, save_dir, filename, read_reps=3, read_delay=0.002, sen=0.005)
```

## Expected Output

Upon running the notebook, you can anticipate the following outcomes:
  
- **MOKE Experiment Execution:** The script will initiate the MOKE experiment, systematically sweeping the magnetic field over the specified range. Data will be acquired and saved as a CSV file, facilitating further analysis.

- **Data Visualization:** After the experiment, the script provides functionality for visualizing the acquired MOKE data. Plotting functions within the notebook enable users to gain insights into the magnetization behavior concerning the applied magnetic field.

This Jupyter Notebook aims to enhance the user's ability to conduct MOKE experiments seamlessly, fostering a more accessible and efficient approach to data acquisition and analysis. For detailed instructions and considerations, please refer to the attached readme file in the repository.

________________________________

## Credits
This automation program is based on Shoaib Jamal's code for FMR automation (https://github.com/sjshamsi/SpinLab_FMR_Automation) and has been tailored to the specific requirements for the MOKE experiment.

________________________________

**Developer:** Mahad Naveed 

**Supervisor:** Dr. Sabieh Anwar

**Collaborator:** Wardah Mahmood

**Explore PhysLab:** www.physlab.org
