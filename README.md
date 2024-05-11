# Carina Log Parser

Takes a log file and parses it into a CSV file. Can be run multiple times to select different ranges once important timestamps are known.

Requires directory named `Data/`. `Data/` should contain a subdirectory for each test, which itself contain `Data/<test directory>/Raw/data.log` and `Data/<test directory>/Raw/events.log`.

Make sure to set the config variables correctly for each test run.