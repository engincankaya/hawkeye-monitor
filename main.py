import platform
import datetime
import pandas as pd
import time
import psutil
import logging
import argparse

class SystemMonitor:
    def __init__(self, interval_seconds=1, output_file='data.csv'):
        self.interval_seconds = interval_seconds
        self.output_file = output_file
        self.data = {
            'timestamp': [],
            'cpu_usage': [],
            'ram_usage': [],
            'disk_usage': [],
            'network_usage': [],
            'cpu_temperature': [],
            'power_consumption': [],
        }
        self.logger = logging.getLogger('SystemMonitor')
        self.setup_logging()

    def setup_logging(self):
        # Initialize logging configuration
        logging.basicConfig(filename='monitor.log', level=logging.ERROR, format='%(asctime)s [%(levelname)s]: %(message)s')

    def monitor_system(self):
        while True:
            try:
                self.collect_data()
                self.save_data()
                self.analyze_data()
            except Exception as e:
                # Log errors encountered during monitoring
                self.logger.error(f'Error: {e}')
            
            # Sleep for the specified interval
            time.sleep(self.interval_seconds)

    def collect_data(self):
        now = datetime.datetime.now()
        self.data['timestamp'].append(now)
        self.data['cpu_usage'].append(psutil.cpu_percent())
        self.data['ram_usage'].append(psutil.virtual_memory().percent)
        self.data['disk_usage'].append(psutil.disk_usage('/').percent)

        if platform.system() == "Windows":
            network_io = psutil.net_io_counters()
            self.data['network_usage'].append(network_io.bytes_sent + network_io.bytes_recv)
            self.data['power_consumption'].append(self.get_windows_power_consumption())
        else:
            network_io = psutil.net_io_counters()
            self.data['network_usage'].append(network_io.bytes_recv + network_io.bytes_sent)
            self.data['power_consumption'].append(0)

        if platform.system() == "Linux":
            self.data['cpu_temperature'].append(self.get_linux_cpu_temperature())
        else:
            self.data['cpu_temperature'].append(0)

    def save_data(self):
        # Save collected data to a CSV file using Pandas
        df = pd.DataFrame(self.data)
        df.to_csv(self.output_file, index=False)

    def analyze_data(self):
        # Add your data analysis logic here
        pass

    def get_linux_cpu_temperature(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as file:
                temperature = int(file.read().strip()) / 1000.0
                return temperature
        except Exception as e:
            # Log errors encountered while reading CPU temperature
            self.logger.error(f'Error reading CPU temperature: {e}')
            return 0

    def get_windows_power_consumption(self):
        try:
            battery = psutil.sensors_battery()
            if battery is not None:
                return battery.power_plugged
            return 0
        except Exception as e:
            # Log errors encountered while reading power consumption
            self.logger.error(f'Error reading power consumption: {e}')
            return 0

if __name__ == '__main__':
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description='System Monitor')
    parser.add_argument('interval_seconds', type=int, help='Interval in seconds for monitoring')
    args = parser.parse_args()
    
    # Create a SystemMonitor instance with the specified interval
    monitor = SystemMonitor(interval_seconds=args.interval_seconds, output_file='data.csv')
    
    # Start monitoring the system
    monitor.monitor_system()
