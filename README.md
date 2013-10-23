DO-QAQC
=======
Dissolved Oxygen QAQC based on QARTOD demo RangeTests.py from https://code.google.com/p/qartod/

About
-------
Program built from specifications laid out in http://www.ioos.noaa.gov/qartod/dissolved_oxygen/qartod_dissolved_oxygen_manual.pdf
Covers first 7 tests*. Pages 13-16 most relevant. 

*Syntax test is relevant to data transmitted and received. It is not relevant for our purposes with data acquired directly off the sonde.

###Prerequisites
Install python 2.7 & SciPy library 
- http://www.python.org/download/releases/2.7.5/
- http://scipy.org/install.html

Running DOrangeTests.py
-----
To run this python script you must open up the command-line. (click ‘Start’ -> ‘Run’ and type ‘cmd’ and hit enter.)
Once the command prompt is open, navigate to the directory with the data using the ‘cd’ and ‘dir’ commands to change directory, and list the directory, respectively
__EX:__ 	`cd L:\DisolvedOxygenQAQC`


DOrangeTests.py is a python script that takes the input file name and outputs the same filename appended with ‘_DOresults.txt’

__EX__ `python DOrangeTests.py 8712AW.txt `

__Outputs__ `8712AW_DOresults.txt`

The input file is a sonde file[1], or can be some other space delimited text file[2]. It reads the date time in the format[4]  Month/Day/Year Hour:Minute:Second (ex: 08/07/12 11:01:12)

If the program is located in a different directory then data or vise-versa, you need to pass the full path & filename to the command.

__EX__ you are currently in the data directory 

`python L:\DissolvedOxygenQAQC\DOrangeTests.py 8712AW.txt`

__EX__ you are in the program directory

`python DOrangeTests.py “L:\Lab Database\Atwater 2012\Sonde Data\8712AW.txt”`

__EX__ you aren’t in either directory

`python L:\DissolvedOxygenQAQC\DOrangeTests.py “L:\Lab Database\Atwater 2012\Sonde Data\8712AW.txt”`

Setting Limits
------
The program contains limits that need to be determined by the operator/analyst

__GrossRangeLimits__ are max and min limits the sensor would ever report, if data falls outside this range it is marked ‘fail

__UserRangeLimits__ are max and min limits (optionally) set by the user, if data falls outside this range it is marked ‘suspect’ in the GrossRangeTest field.

__ClimateRangeLimits__ is the set of limits(mg/L) a value should fall between for a given month

__SpikeRangeLimits__ is absolute difference(mg/L) values may have between them before being marked ‘suspect’ or ‘fail’

__FlatRangeLimits__ is the number of times a value can repeat before being marked ‘suspect’(rangeLo), or ‘fail’(rangeHi)

__MaxGapLimit__ is the maximum time allowed between observations without failing the test (ie. data is logged every 30 minutes, so set max gap to 35 minutes)



Other Settings That May Be Useful:
-----

[1] Currently the system is setup to take a sonde file so when the input file is read, the first 4 lines are ignored since the data starts on line number 5. You can change this setting by adjusting the value of data_start in the program

[2] The program assumes the DO mg/L value is in column 12. You can adjust the column by modifying the value of sensor_col (*note: numbering starts from 0 so sensor_col = 11)

[3] To be able to run the Rate of Change range tests a number of samples must be read in before the standard deviation can be run, QARTOD recommends 25 hours worth of samples.
EX: the sonde logs DO twice an hour, so we need 50 samples to make 25 hours
		time_dev = 50
so adjust the time_dev variable as needed based on the data being read in.

[4] dt_fmt specifies the format to expect the date/time in, more info on syntax here http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior 
date_col & time_col specify the column numbers the date and time are in, respectively.

