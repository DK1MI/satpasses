# SAT Pass Static HTML Page Generator

This is a very simple python script that generates a static HTML page with a single table showing all future satellite passes over a defined location for a defined time into the future. The color intensity of each row is related to the maximum elevation of this pass. Higher elevation leads to brighter colors. Here is a screenshot:

![screenshot](/img/screenshot2jpg)

The data is pulled from N2YO.com. You need an API key from there to use this script.

Just rename the file _config.py_dist_ to _config.py_, adapt it to your needs and execute the script _satpasses.py_.
