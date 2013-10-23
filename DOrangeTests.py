import sys
import os
import math
import numpy
import copy
from datetime import datetime, timedelta
from collections import deque

"""
Class: qaqcTestFlags
Purpose: This is more of an enumeration class that details out the various quality flags.
"""    
class qaqcTestFlags:

  TQFLAG_DA = 0  #Data Availability               
  TQFLAG_SR = 1  #Sensor Range
  TQFLAG_GR = 2  #Gross Range
  TQFLAG_CR = 3  #Climatological Range
  TQFLAG_RC = 4  #Rate of Change
  TQFLAG_NN = 5  #Nearest Neighbor

  NO_TEST      = 0 # -1 in writeup Unable to perform the test  
  TEST_FAILED  = 3#1 # 0 in writeup The test failed.
  TEST_PASSED  = 1#2 #1 in writeup The test passed.
  TEST_SUSPECT = 2 # test inconclusive data suspect
  
  NO_DATA           = -9 #the data field is missing a value
  DATA_QUAL_NO_EVAL = 0  #the data quality is not evaluated
  DATA_QUAL_BAD     = 1  #the data quality is bad
  DATA_QUAL_SUSPECT = 2  #the data quality is questionable or suspect
  DATA_QUAL_GOOD    = 3  #the data quality is good
  

"""
Class: rangeLimits
Purpose: Simple structure containing a hi and lo range.
"""
class rangeLimits:
  def __init__(self, low=None, high=None):
    self.rangeLo = low
    self.rangeHi = high

"""
Class: rangeLimits
Purpose: Container for the various limits(sensor,gross,climate) for the given observation type.
"""    
class rangeLimitTests:
  def __init__(self,obsName):
    #Values for each of these flags can be: Values can be qaqcTestFlags.NO_TEST, qaqcTestFlags.TEST_FAILED, qaqcTestFlags.TEST_PASSED
    self.maxGapCheck        = qaqcTestFlags.NO_TEST 
    self.dataAvailable      = qaqcTestFlags.NO_TEST   #Flag specifing the validity of whether data is available. 1st test performed
    self.userRangeCheck  = qaqcTestFlags.NO_TEST   #Flag specifing the validity of the sensor range check. 3nd test performed
    self.grossRangeCheck    = qaqcTestFlags.NO_TEST   #Flag specifing the validity of the gross range check. 2rd test performed
    self.climateRangeCheck  = qaqcTestFlags.NO_TEST   #Flag specifing the validity of the climate range check. 4th test performed
    self.spikeRangeCheck    = qaqcTestFlags.NO_TEST
    self.rateofchangeCheck  = qaqcTestFlags.NO_TEST   #Flag specifing the validity of the rate of change check.
    self.nearneighborCheck  = qaqcTestFlags.NO_TEST   #Flag specifing the validity of the nearest neighbor check.
    self.flatLineCheck      = qaqcTestFlags.NO_TEST
    
    self.obsName            = obsName
    self.userRangeLimits  = rangeLimits()  #The limits for the sensor range.
    self.grossRangeLimits   = rangeLimits()  #The limits for the gross range.
    self.spikeRangeLimits   = rangeLimits() 
    self.flatRangeLimits   = rangeLimits() 
    self.climateRangeLimits = {}             #A dictionary keyed from 1-12 representing the climate ranges for the month.
    self.maxGapLimit        = timedelta() # a timedelta object 
    
    self.n_dev = 3 #number of std_dev to multiple by 
    self.eps = 0.01 # max difference between prev values #TODO
    self.rep_cnt = 0 # number of times value repeats continuously #internal use only

  def resetFlags(self):
    self.maxGapCheck        = qaqcTestFlags.NO_TEST 
    self.dataAvailable      = qaqcTestFlags.NO_TEST    
    self.userRangeCheck  = qaqcTestFlags.NO_TEST   
    self.grossRangeCheck    = qaqcTestFlags.NO_TEST   
    self.climateRangeCheck  = qaqcTestFlags.NO_TEST   
    self.rateofchangeCheck  = qaqcTestFlags.NO_TEST   
    self.nearneighborCheck  = qaqcTestFlags.NO_TEST
    self.spikeRangeCheck    = qaqcTestFlags.NO_TEST
    self.flatLineCheck      = qaqcTestFlags.NO_TEST
    
  def setUserRangeLimits(self, limits):    
    self.userRangeLimits.rangeLo = limits.rangeLo
    self.userRangeLimits.rangeHi = limits.rangeHi
  def setGrossRangeLimits(self, limits):    
    self.grossRangeLimits.rangeLo = limits.rangeLo
    self.grossRangeLimits.rangeHi = limits.rangeHi
  def setClimateRangeLimits(self, limits, month):
    self.climateRangeLimits[month] = copy.copy(limits) #assign new object, not reference
  def setClimateRangeLimits2(self, lo, hi, month):
    self.climateRangeLimits[month] = rangeLimits(lo, hi) #assign new object, not reference
  def setMaxGapLimit(self, limit):
    self.maxGapLimit = limit
  def setSpikeRangeLimits(self, limits):
    self.spikeRangeLimits.rangeLo = limits.rangeLo
    self.spikeRangeLimits.rangeHi = limits.rangeHi
  def setFlatRangeLimits(self, limits):
    self.flatRangeLimits.rangeLo = limits.rangeLo #rep_cnt_suspect
    self.flatRangeLimits.rangeHi = limits.rangeHi #rep_cnt_fail
  
  def testFlagToString(self, flag):
    if(flag == qaqcTestFlags.NO_TEST):
      return("N")#("No Test")
    elif(flag == qaqcTestFlags.TEST_FAILED):
      return("F")#("Failed")
    elif(flag == qaqcTestFlags.TEST_SUSPECT):
      return("?")#("Inconclusive")
    elif(flag == qaqcTestFlags.TEST_PASSED):
      return("P")#("Passed")
    else:
      return("Invalid Flag")
  """
  Function: rangeTest
  Purpose: performs the range test. Checks are done to verify limits were provided as well as a valid value. 
  Paramters: 
    value is the data we are range checking.
    limits is a rangeLimits object that has valid hi and low ranges to test against.
  Return:
    If the test is sucessful, qaqcTestFlags.TEST_PASSED is returned. 
    if the test fails, qaqcTestFlags.TEST_FAILED is returned.
    if the test is inconclusive, qaqcTestFlags.TEST_SUSPECT is returned
    if no limits or no value was provided, qaqcTestFlags.NO_TEST is returned.
  """
  def rangeTest(self, value, limits):
    if( value != None ):
      if( value < limits.rangeLo or value > limits.rangeHi ):
        return( qaqcTestFlags.TEST_FAILED )
      return( qaqcTestFlags.TEST_PASSED )      
    return( qaqcTestFlags.NO_TEST )

  def rangeTest2(self, value, limits):
    if( value != None ):
      if( value < limits.rangeLo ):
        return( qaqcTestFlags.TEST_PASSED )
      if ( value >= limits.rangeHi ): 
        return( qaqcTestFlags.TEST_FAILED )
      elif ( value >= limits.rangeLo ):
        return( qaqcTestFlags.TEST_SUSPECT )
    return( qaqcTestFlags.NO_TEST ) 
   
  def userRangeTest(self, value, limits):
    if( value != None ):
      if( value < limits.rangeLo or value > limits.rangeHi ):
        return( qaqcTestFlags.TEST_SUSPECT )
      return( qaqcTestFlags.TEST_PASSED )      
    return( qaqcTestFlags.NO_TEST )
    
  def rateofchangeTest(self, value, std_dev):
    if ( value > (self.n_dev*std_dev) ):
      return ( qaqcTestFlags.TEST_SUSPECT )
    else:
      return ( qaqcTestFlags.TEST_PASSED )
      
  def flatLineTest(self, value, prev_val, limits):
    if( value != None ):
      if ( value == prev_val ): #( self.eps <= abs(value - prev_val) ):
        self.rep_cnt = self.rep_cnt + 1
      else:
        self.rep_cnt = 0
    return self.rangeTest2(self.rep_cnt, limits)
 
  """
  Function: runRangeTests
  Purpose: Runs each of the limits tests, starting with the sensor range test. Each must pass to be able to move on to the next one.
  As the tests are run, this function is also setting the flags specifing the outcome of each test. These flags can be later used in the
  qclevel calculation.
  Parameters:
    value is the floating point value we are testing.
    month is the numeric representation of the month to use for the climate range tests.
    prev_value is data point n-1
    std_dev is the standard deviation calcualted over some prespecified time interval (25 hours for example)
  Return: Nothing, the follwing are set within the object
    qaqcTestFlags.TEST_PASSED is the tests were passed, 
    qaqcTestFlags.TEST_SUSPECT if inconclusive, 
    otherwise qaqcTestFlags.TEST_FAILED.
  """
  def runRangeTests(self, value, prev_value = None, month = 0, std_dev = 0):
    #Do we have a valid value?
    if(value != None):     
      self.dataAvailable = qaqcTestFlags.TEST_PASSED
      #Did we get a valid obsNfo that we need for the limits?
      if( self.grossRangeLimits.rangeLo != None and self.grossRangeLimits.rangeHi != None ):
        self.grossRangeCheck = self.rangeTest( value, self.grossRangeLimits )
        #If we don't pass the gross sensor range check, do not run any other tests.
        if( self.grossRangeCheck== qaqcTestFlags.TEST_PASSED ):    
          #Run the user range checks if we have limits.    
          if( self.userRangeLimits.rangeLo != None and self.userRangeLimits.rangeHi != None ):
            self.grossRangeCheck = self.userRangeTest( value, self.userRangeLimits )
          #Run the climatalogical range checks if we have limits.    
          if( len(self.climateRangeLimits) and month != 0 ):
            limits = self.climateRangeLimits[month]
            self.climateRangeCheck = self.rangeTest( value, limits )
          #if we have a previous value run the following tests
          if ( prev_value != None ):
            # Run the spike test if limits are available
            if ( self.spikeRangeLimits.rangeLo != None and self.spikeRangeLimits.rangeHi != None ):
                self.spikeRangeCheck = self.rangeTest2(abs((value - prev_value)), self.spikeRangeLimits)
            # Run rate of change test if we have a std_dev
            if ( std_dev != 0 ):
                self.rateofchangeCheck = self.rateofchangeTest(abs((value - prev_value)), std_dev)
            # Run flat line test for repeating values
            if ( self.flatRangeLimits.rangeLo != None and self.flatRangeLimits.rangeHi != None ):
                self.flatLineCheck = self.flatLineTest(value, prev_value, self.flatRangeLimits)
    #No value, so we can't perform any other tests.
    else:
      self.dataAvailable      = qaqcTestFlags.TEST_FAILED  


##################################################################################################################################
#To run this test script, at the command line type:
# python DOrangeTests inputfile
# where inputfile is a sonde raw txt file including heading.
##################################################################################################################################
if __name__ == '__main__':

  #Let's create a range test object for DO.  
  rangeTests = rangeLimitTests('dissolved oxygen')
  
  #Here we create a rangeLimits object to use to set the limits for the various tests.
  obsLimits = rangeLimits()
  
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# BEGIN LIMITS SECTION (EDIT THESE VALUES BELOW)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

  #Set Gross Range Limits. (max & min values sensor can output)
  obsLimits.rangeLo = 0 #DO_SENSOR_MIN
  obsLimits.rangeHi = 65536 #DO_SENSOR_MAX
  rangeTests.setGrossRangeLimits(obsLimits) # this will mark data outside the range 'fail'
  # ---
  #Set User Range Limits (max & min values sensor should output) 
  #uncomment the following three lines to enable (ie remove #)
  #obsLimits.rangeLo = 0 #DO_USER_MIN
  #obsLimits.rangeHi = 16 #DO_USER_MAX
  #rangeTests.setUserRangeLimits(obsLimits) # this will mark data outside the range 'suspect'
  # ---
  #Set the climate range for each month. (Low, High, Month)
  rangeTests.setClimateRangeLimits2(5,15, 1) #January
  rangeTests.setClimateRangeLimits2(5,15, 2) # February
  rangeTests.setClimateRangeLimits2(5,15, 3) # March
  rangeTests.setClimateRangeLimits2(5,15, 4) # April
  rangeTests.setClimateRangeLimits2(5,15, 5) # May
  rangeTests.setClimateRangeLimits2(5,15, 6) # June
  rangeTests.setClimateRangeLimits2(5,15, 7) # July
  rangeTests.setClimateRangeLimits2(5,15, 8) # August
  rangeTests.setClimateRangeLimits2(5,15, 9) # September
  rangeTests.setClimateRangeLimits2(5,15, 10) # October
  rangeTests.setClimateRangeLimits2(5,15, 11) # November
  rangeTests.setClimateRangeLimits2(5,15, 12) # December
  # ---
  # Set Spike Test High & Low Threshold
  obsLimits.rangeLo = 4.0 #mg/L  #suspect
  obsLimits.rangeHi = 8.0 #mg/L  #fail
  rangeTests.setSpikeRangeLimits(obsLimits)
  # ---
  # Set FlatLine Test High & Low Threshold
  obsLimits.rangeLo = 3 # suspect repeats
  obsLimits.rangeHi = 5 # fail repeats
  rangeTests.setFlatRangeLimits(obsLimits)
  # ---
  # Set max time difference between observations for Gap Test
  rangeTests.setMaxGapLimit(timedelta(minutes=35)) # max obs time difference

  sensor_col = 11 # column number sensor value is in
  data_start = 5 # line number the data actually starts on
  time_dev = 50 # number of samples for the std_dev (50 samples = 25 hours)
  
  # setup datetime format and objects for gap test
  dt_fmt = '%m/%d/%y %H:%M:%S' # ex 08/07/12 11:01:12
  date_col = 0
  time_col = 1
  
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# END LIMITS SECTION
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
  
  #Now let's open the source file passed in on the command line. The format the data files are "date,value".
  #There could be holes in the data, I did no continuity checks, just a raw dump of the last 3 months of data.
  #We open the file for reading.
  dataFilename = sys.argv[1]
  inputFile = open(dataFilename, "r")
  #Let's create our results file.
  resultsFilename = ( os.path.splitext(dataFilename)[0] ) + "_DOresults.txt" #sys.argv[2]
  outputFile = open(resultsFilename, "w")
  outputFile.write("Sonde Data, Data Available Test,  Gross Range Test, Climatalogical Range Test, Gap Test, Spike Range Test(Hi: %4.2f Low: %4.2f), Rate of Change Test, Flat Line Test(Hi: %d Low: %d)\n" %\
                   (rangeTests.spikeRangeLimits.rangeHi, rangeTests.spikeRangeLimits.rangeLo,
                    rangeTests.flatRangeLimits.rangeHi, rangeTests.flatRangeLimits.rangeLo,
                    ) )
  
  #Now let's loop through all the rows.
  line = inputFile.readline()
  line_num = 1
  sd_queue = deque() # collection for storing data for standard deviation
  sd = 0 # std_dev
  prev_val = None
  prev_obs_dt = None # previous datetime
  obs_dt_diff = None
  #Keep looping until we get an empty string, this means we have hit the end of file.
  while(len(line)):
    # read past the heading of sonde file
    if (line_num >= data_start):
        #Split the input line into the date and value.
        parseData = line.split()
        #convert string to datetime object for gap tests
        obs_dt = datetime.strptime(parseData[date_col]+' '+parseData[time_col], dt_fmt)
        if (prev_obs_dt != None): # check if not first data point
            obs_dt_diff = obs_dt - prev_obs_dt
            if (obs_dt_diff < rangeTests.maxGapLimit):
               rangeTests.maxGapCheck = qaqcTestFlags.TEST_PASSED 
            else:
               rangeTests.maxGapCheck = qaqcTestFlags.TEST_FAILED 
        #else skip gap test
        prev_obs_dt = obs_dt # update old value
        
        #convert the value to a float, it is a string when we read it out of the file.
        try:
            value = float(parseData[sensor_col])
        except ValueError:
            print("ValueError: expected number instead got: " + parseData[sensor_col])

        #collect samples for std_dev, update queue, recalculate value
        if (len(sd_queue) < time_dev):
          sd_queue.append(value)
        else:
          sd_queue.popleft()
          sd_queue.append(value)
          tmp = numpy.asarray(sd_queue)
          sd = numpy.std(tmp)
        
        #Run the tests.
        rangeTests.runRangeTests(value, prev_val, month=obs_dt.month, std_dev=sd)
        
        #if the tests are passed, dont output anything, for easier analysis
        '''if (rangeTests.dataAvailable != qaqcTestFlags.TEST_PASSED or \
            rangeTests.userRangeCheck!= qaqcTestFlags.TEST_PASSED or \
            rangeTests.grossRangeCheck != qaqcTestFlags.TEST_PASSED or \
            rangeTests.climateRangeCheck != qaqcTestFlags.TEST_PASSED or \
            rangeTests.maxGapCheck != qaqcTestFlags.TEST_PASSED or \
            rangeTests.spikeRangeCheck != qaqcTestFlags.TEST_PASSED or \
            rangeTests.rateofchangeCheck != qaqcTestFlags.TEST_PASSED or \
            rangeTests.flatLineCheck != qaqcTestFlags.TEST_PASSED
            ):'''
          #Build our output string which will consist of: Date(value we got from the input data file), value(from input data), Data available,
          #Sensor Range Test Result(Passed/Failed), Gross Range Test, Climatological range test, max gap test
        outputString = ("%s,\t%s,%s,%s,%s,%s,%s,%s\n"\
                        %( line.rstrip('\r\n'),
                          rangeTests.testFlagToString(rangeTests.dataAvailable),   #data available test result
                          rangeTests.testFlagToString(rangeTests.grossRangeCheck), #gross range check result
                          rangeTests.testFlagToString(rangeTests.climateRangeCheck),#Climatalogical test result
                          rangeTests.testFlagToString(rangeTests.maxGapCheck),  # time gap test result
                          rangeTests.testFlagToString(rangeTests.spikeRangeCheck), 
                          rangeTests.testFlagToString(rangeTests.rateofchangeCheck), 
                          rangeTests.testFlagToString(rangeTests.flatLineCheck), 
                          ) )
        outputFile.write(outputString)
        
        #Reset the test flags for the next pass.
        rangeTests.resetFlags()
        prev_val = value;
    
    #Read the next line, if there is one.
    line = inputFile.readline()
    line_num = line_num + 1
