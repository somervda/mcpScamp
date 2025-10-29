import pynmea2
import serial
import json
import sys
import os
import traceback

# uv add pyserial
# uv add pynmea2

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("Usage: python gpsLogger.py <directory_path>")
    sys.exit(1) # Exit with an error code

directory_path = sys.argv[1]

# Check if the provided path exists and is a directory
if not os.path.exists(directory_path):
    print(f"Error: Path '{directory_path}' does not exist.")
    sys.exit(1)
elif not os.path.isdir(directory_path):
    print(f"Error: Path '{directory_path}' is not a directory.")
    sys.exit(1)

# Define the port and baud rate (commonly 9600 for GPS devices)
port = '/dev/ttyACM0'  # Change this to your actual device port
baud_rate = 9600
carryOn=True





while carryOn:
    try:
        # Open a serial connection
        with serial.Serial(port, baud_rate) as ser:
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith('$GPGGA'): 
                    msg = pynmea2.parse(line) 
                    # print(repr(msg))
                    if hasattr(msg, 'num_sats') and hasattr(msg, 'gps_qual'):
                        print("$GPGGA num_sats:",msg.num_sats, " gps_qual:",msg.gps_qual)
                if line.startswith('$GPRMC'):  # Check for NMEA sentences you are interested in
                    msg = pynmea2.parse(line) 
                    print("$GPRMC",repr(msg))
                    if msg:
                        if hasattr(msg, 'datetime') and hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                            if msg.latitude!=0 and msg.longitude!=0 and msg.datetime:
                                print("date time:",str(msg.datetime)," Latitude:",msg.latitude," Longitude:",msg.longitude)
                                # Write the Longitude, latitude to a file
                                gps = {
                                    "timestamp" :str(msg.datetime),
                                    "latitude": msg.latitude,
                                    "longitude": msg.longitude,
                                }
                                with open(directory_path + "/gps.json", "w", encoding="utf-8") as f:
                                    json.dump(gps, f, indent=4) # indent for pretty printing

    except serial.SerialException as e:
        print(f"* Error opening the port {port}: {e}")
        carryOn=False
    except KeyboardInterrupt:
        print("Script terminated by user.")
        carryOn=False
    except pynmea2.nmea.ParseError as e:
        print("* ParseError - Carry on and keep calm ",e)
        carryOn=True
    except UnicodeDecodeError as e:
        print("* UnicodeDecodeError - Carry on and keep calm ",e)
        carryOn=True
    except TypeError as e:
        print("* TypeError - Carry on and keep calm ",e)
        # traceback.print_exc()
        carryOn=True

    # except Exception as e:
    #     print("Other Error:",e)
    #     carryOn=False  
    carryon=False      