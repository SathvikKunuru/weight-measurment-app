#simulate_sender.py
import serial
import time
import random

# Change COM6 to your paired virtual port if needed
PORT = 'COM6'
BAUD = 9600

def main():
    try:
        with serial.Serial(PORT, BAUD, timeout=1) as ser:
            print(f"Sending simulated data to {PORT} at {BAUD} baud...")
            while True:
                # Simulate a weight value between 0 and 100 (as string)
                value = round(random.uniform(0, 100), 2)
                line = f"{value}\n"
                ser.write(line.encode())
                print(f"Sent: {line.strip()}")
                time.sleep(1)
    except serial.SerialException as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    main()