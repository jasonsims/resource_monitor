#!/usr/bin/python
"""Pulls CPU/IO data from /proc and displays resource statistics."""


__author__ = 'Jason Sims (jasonsims87@gmail.com)'

import sys
import time


class ResourceMonitor(object):
  """Class for monitoring disk and CPU resources.

  Attributes:
    SAMPLE_INTERVAL: Int The sleep interval (seconds) between samples
    RUN_TIME: Int Runtime for the monitoring services
    DISKS_TO_MONITOR: List Disks which will be monitored by the script
  """
  SAMPLE_INTERVAL = 2
  RUN_TIME = 60
  DISKS_TO_MONITOR = ['sda']
  CPU_DATA_FILE = '/proc/stat'
  IO_DATA_FILE = '/proc/diskstats'

  def __init__(self):
    """Initializes the ResourceMonitor class and starts monitoring."""
    self.Start()

  def Start(self):
    """Starts monitoring all resources.

    Attributes:
      start_time: String Time the monitoring services were started
      time_delta: String Differance between the start time and current time
      cpu: String CPU untilization value as a percentage
      ior: String IO Read bandwidth in kbps
      iow: String IO Write bandwidth in kbps
    """
    start_time = int('%.0f' % time.time())
    time_delta = 0
    while time_delta <= self.RUN_TIME:
      cpu, ior, iow = self.GetStatistics()
      print 'CPU %.2f%% IO rkbps %.3f IO wkbps %.3f' %  (cpu, ior, iow)
      time.sleep(2)
      time_delta = int('%.0f' % time.time()) - start_time

    self.Stop()

  def Stop(self):
    """Stop all monitoring and exit."""
    exit()

  def GetStatistics(self):
    """Get the latest resource statistics.

    Returns:
      cpu: String CPU untilization value as a percentage
      ior: String IO Read bandwidth in kbps
      iow: String IO Write bandwidth in kbps
    """
    cpu = self.GetCPUStats()
    ior, iow = self.GetIOReadStats()
    return cpu, ior, iow

  def GetCPUStats(self):
    """Gets the CPU usage stats and returns it as a percentage.

    Attributes:
      cpu_delta: String Differance between cpu sample 1 and 2
    Returns:
      cpu_percentage: String CPU usage percentage
    """
    cpu_delta = self.GetCPUDelta(self.GetCPUData())
    cpu_percentage = 100 - (cpu_delta[len(cpu_delta) - 1] * 100.00 / sum(
        cpu_delta))
    return cpu_percentage

  def GetCPUData(self):
    """Reads CPU data from proc and returns its values.

    Attributes:
      proc_cpu_data: File Object containing the contents of the CPU data file
    Returns:
      cpu_usage: List CPU values pulled from the CPU data file
    """
    proc_cpu_data = file(self.CPU_DATA_FILE, 'r')
    cpu_usage = proc_cpu_data.readline().split(' ')[2:6]
    proc_cpu_data.close()
    for i in range(len(cpu_usage)):
      cpu_usage[i] = int(cpu_usage[i])
    return cpu_usage

  def GetCPUDelta(self, first_sample):
    """Gets the CPU value delta based on two samples taken at different times.

    Args:
      first_sample: List of CPU load values
    Returns:
      second_sample: List of the CPU delta values
    """
    time.sleep(self.SAMPLE_INTERVAL)
    second_sample = self.GetCPUData()
    for i in range(len(first_sample)):
      second_sample[i] -= first_sample[i]

    return second_sample

  def GetIOReadStats(self):
    """Gets IO usage stats and returns them in kbps.

    Returns:
      io_delta: Tuple io read and io write values in kbps
    """
    io_delta = self.GetIODelta(self.GetIOData())
    return io_delta[0], io_delta[1]

  def GetIOData(self):
    """Reads IO data from proc and returns its values.

    Attributes:
      proc_io_data: File Object containing the contents of the IO data file
      io_fields: List IO data from the IO data file
    Returns:
      io_bandwidth: Float Bandwidth data in kbps
    """
    proc_io_data = file(self.IO_DATA_FILE, 'r')
    for line in proc_io_data:
      io_fields = line.split()

      if io_fields[2] not in self.DISKS_TO_MONITOR:
        continue

      io_bandwidth = self.CalculateIOBandwidth(io_fields)
    proc_io_data.close()
    return io_bandwidth

  def CalculateIOBandwidth(self, io_fields):
    """Handles conversion of IO statistics and kbps calculations.

    Args:
      io_fields: List IO data from the IO data file
    Attributes:
      sectors_read: Int Sectors read from disk (Bytes)
      reading_milliseconds: Int Milliseconds spent reading from disk
      sectors_wrote: Int Sectors written to disk (Bytes)
      writing_milliseconds: Int Milliseconds spent writing to disk
      kb_sectors_read: Int  Sectors read from disk (Kilobytes)
      kb_sectors_wrote: Int Sectors written to disk (Kilobytes)
      reading_seconds: Int Seconds spent reading from disk
      writing_seconds: Int Seconds spent writing to disk
    Returns:
      io_bandwidth: List IO values in kbps
    """
    io_bandwidth = []
    sectors_read = io_fields[5]
    reading_milliseconds = io_fields[6]
    sectors_wrote = io_fields[9]
    writing_milliseconds = io_fields[10]
    kb_sectors_read = (float(sectors_read) * 512) / 128
    kb_sectors_wrote = (float(sectors_wrote) * 512) / 128
    reading_seconds = float(reading_milliseconds) / 1000
    writing_seconds = float(writing_milliseconds) / 1000

    io_bandwidth.append((1 / reading_seconds) * kb_sectors_read)
    io_bandwidth.append((1 / writing_seconds) * kb_sectors_wrote)

    return io_bandwidth

  def GetIODelta(self, first_sample):
    """Gets the IO value delta based on two samples taken at different times.

    Args:
      first_sample: List of IO data
    Returns:
      second_sample: List of the CPU delta values
    """
    time.sleep(self.SAMPLE_INTERVAL)
    second_sample = self.GetIOData()
    for i in range(len(first_sample)):
      second_sample[i] -= first_sample[i]

    return second_sample


def Main():
  ResourceMonitor()

if __name__ == '__main__':
  sys.exit(Main())
