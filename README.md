# Carina Log Parser

Raw data from Carina is stored in `Data/<Test ID>/raw` with the filenames `data.log` and `events.log`. The script in `src/main.py` first parses these into CSVs for quicker re-run times. These CSVs are stored in `/cache/<Test ID>`. The script stored the rest of its output in `Data/<Test ID>/compiled` under six files.
- Three correspond to different windows of sensor data, three correspond to different windows of event data.
- The windows are user-selectable with the `LOWER` and `UPPER` variables, as well as the `LOWER_F` and `UPPER_F` variables. The approach I've been using is to select the full test data range (from the start of fill to a few seconds after the flow) with the first window, then to select just the flow with the second window. The other output file is a copy of the cached.

Each folder in `Data/<Test ID>` contains a python script `analysis.py` which automates the creation of graphs, and some data analysis/smoothing.

The file `plot_them_all.py` is a generalized script that plots all the flow data from each test in a single graph.

TODO:
- Make graph generation more user-friendly than copy-pasting and editing the `analysis.py` files. The best solution might be to keep a majority of the code in a shared library, and then instantiate that library with per-test specifics in each individual test folder. For instance: you may wish to write a generalized function that can rename a sensor/actuator, or one that can set the timestamps to reference a specific event. Consider doing something similar for the graphing scripts.
- Structure things better, make the code more dev-friendly.
- Make the code more generalizeable. Parsing should work fine, but there's a lot of potential improvement for analysis/plotting.
- Consider better ways to do range-selection. Maybe a CLI instead of setting global variables. For instance, you could have the user specify the name of a mass sensor via terminal, which is then graphed after the initial parsing. This makes finding the range(s) of interest more user-friendly than opening it in excel.