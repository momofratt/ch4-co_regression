Scripts to perform linear regressions on CH4 and CO data measured at ICOS sites. The script can run for each ICOS atmospheric site. For each site, some parameters must be specified in the config.py file.
The main script linear_regression.py is used to read ICOS L2 and NRT data and perform elaborations on the data. Results from the scripts in the project momofratt/seleziona_emissioni are needed.
The linear_regression script performs regressions on CH4 and CO and estimate total CH4 emissions using the results from the regressions and from the CO emission obtained by the momofratt/seleziona_emissioni scripts.
A scientific description of the project can be found at https://meetingorganizer.copernicus.org/EGU22/EGU22-5736.html .

