import requests
import time
import logging
import json
import os
import sys
import html
from datetime import datetime, timedelta
import config
import pytz

class SatellitePassTracker:
    def __init__(self):
        """
        Initialize the Satellite Pass Tracker
        """
        self.log_file = config.LOG_FILE
        self.setup_logging()

    def setup_logging(self):
        """
        Configure logging
        """
        logging.basicConfig(
            filename=self.log_file, 
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_satellite_passes(self, sat_id):
        """
        Retrieve satellite pass information from n2yo.com
        
        Args:
            sat_id (int): Satellite ID
        
        Returns:
            dict: JSON response with satellite pass information
        """
        url = (f"https://api.n2yo.com/rest/v1/satellite/radiopasses/"
               f"{sat_id}/{config.QTH_LATITUDE}/{config.QTH_LONGITUDE}/"
               f"{config.QTH_ELEVATION}/{config.DAYS}/{config.MIN_ELEVATION}/"
               f"&apiKey={config.N2YO_API_KEY}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error in API request for satellite {sat_id}: {e}")
            return None

    def generate_html_report(self):
        """
        Generate an HTML page with satellite passes
        """
        # Collect passes for all configured satellites
        all_passes = []

        for sat_id, color in config.SATELLITE_IDS:
            passes_data = self.get_satellite_passes(sat_id)

            if not passes_data or 'passes' not in passes_data:
                logging.warning(f"No pass data for satellite {sat_id}")
                continue

            # Extend passes with satellite information
            for pass_info in passes_data['passes']:
                pass_info['satid'] = sat_id
                pass_info['color'] = color
                pass_info['satname'] = passes_data['info']['satname']
                all_passes.append(pass_info)

        # Sort passes by start time
        all_passes.sort(key=lambda x: x['startUTC'])

        # Generate HTML
        html_content = self.create_html_template(all_passes)

        # Save HTML file
        try:
            with open(config.HTML_OUTPUT_FILE, 'w') as f:
                f.write(html_content)
            logging.info(f"HTML report successfully saved: {config.HTML_OUTPUT_FILE}")
        except IOError as e:
            logging.error(f"Error saving HTML file: {e}")

    def create_html_template(self, passes):
        """
        Create HTML template for satellite passes

        Args:
            passes (list): List of satellite passes

        Returns:
            str: Complete HTML report
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Satellite Passes</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>Satellite Passes</h1>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <table>
        <thead>
            <tr>
                <th>Satellite</th>
                <th>Start</th>
                <th>Max Elevation</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody>
            {''.join(self.create_pass_rows(passes))}
        </tbody>
    </table>
</body>
</html>
"""
        return html_content

    def create_pass_rows(self, passes):
        """
        Generate table rows for satellite passes

        Args:
            passes (list): List of satellite passes

        Returns:
            list: List of HTML table rows
        """
        user_tz = pytz.timezone(config.TIMEZONE)

        pass_rows = []
        for pass_info in passes:
            # Convert UTC timestamps to UTC datetime objects
            start_time_utc = datetime.utcfromtimestamp(pass_info['startUTC'])
            max_time_utc = datetime.utcfromtimestamp(pass_info['maxUTC'])
            end_time_utc = datetime.utcfromtimestamp(pass_info['endUTC'])

            # Convert UTC times to German local time
            start_time = pytz.utc.localize(start_time_utc).astimezone(user_tz)
            max_time = pytz.utc.localize(max_time_utc).astimezone(user_tz)
            end_time = pytz.utc.localize(end_time_utc).astimezone(user_tz)

            # Calculate pass duration
            duration = end_time - start_time

            row = f"""
            <tr bgcolor="{pass_info['color']}">
                <td>{html.escape(pass_info['satname'])}</td>
                <td>{start_time.strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>{pass_info['maxEl']:.2f}°</td>
                <td>{duration}</td>
            </tr>
            """
            pass_rows.append(row)

        return pass_rows

    def main(self):
        """
        Main function to execute the script
        """
        try:
            logging.info("Satellite Pass Tracking started")
            self.generate_html_report()
            logging.info("Satellite Pass Tracking completed")
        except Exception as e:
            logging.error(f"Unexpected error in main function: {e}", exc_info=True)
            sys.exit(1)

def main():
    """
    Script entry point
    """
    tracker = SatellitePassTracker()
    tracker.main()

if __name__ == "__main__":
    main()
