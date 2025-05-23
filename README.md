# Weight Measurement App

A desktop application for Windows that reads weight measurements from a serial-connected weighing device using the **RS-232 protocol**. The app displays live data, evaluates test results, and generates PDF reports. Built with Python and Tkinter, it is designed for easy use in industrial or laboratory environments.

## Protocol Used

- **RS-232 Serial Protocol:**  
  The application communicates with the weighing device via a configurable COM port and baud rate using the RS-232 standard.

## Features

- **Serial Communication:** Connects to a weighing device using RS-232 (COM port, baud rate configurable).
- **Live Data Reading:** Reads and displays weight/load cell values in real time.
- **Test Details Entry:** User-friendly fields for equipment details, test parameters, and personnel information.
- **Result Evaluation:** Automatically determines test result (success/fail) based on capacity.
- **PDF Report Generation:** Exports all entered and measured data to a formatted PDF report.
- **Configuration Persistence:** Remembers last-used settings and details via a JSON config file.

## Requirements

- Python 3.7+
- [Tkinter](https://docs.python.org/3/library/tkinter.html) (usually included with Python)
- [pyserial](https://pypi.org/project/pyserial/)
- [reportlab](https://pypi.org/project/reportlab/)

Install dependencies with:

```sh
pip install pyserial reportlab
```

## Usage

1. Clone or download this repository.
2. Run the application:

   ```sh
   python "Weight Measurment app.py"
   ```

3. Enter the COM port and baud rate for your weighing device.
4. Fill in the test and equipment details.
5. Click **START** to begin reading data from the device.
6. Click **STOP** to end the reading.
7. Click **Save** to export the current data to a PDF report.

## File Structure

- `Weight Measurment app.py` - Main application script.
- `config.json` - Stores persistent configuration and last-used values.

## License

MIT License

---

*Created for weight measurement and reporting automation using RS-232 serial protocol.*
