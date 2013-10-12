#! /usr/bin/python
 
''' 
Title:    backup.py
Author:   Johann Romero (johann.romero@gmail.com)
Date:     Jul022013
Info:     "jrbackup" can be used to automatically backup given folder locations
          to another backup location. jrbackup is easily configurable through a
          configuration file. jrbackup uses tar to achieve Full and Incremental Archives.    



'''
 
import ConfigParser
import re
import os
import sys
import glob
import logging
import logging.handlers
import subprocess
import datetime
import shlex
import time
from optparse import OptionParser
import sendemail

#Usage and Description
usage = "%prog -R | -D"
mydescription = ('backup.py is intended to be a simple yet powerful backup tool. ' +
'To backup your system edit the backup.conf file so that it has all the correct information, ' + 
'afterwards set backup.py to run automatically with cron or crontab without.')

myversion = "jrbackup-1.0"

def splitNStripArgs(inputStr, charToStrip):
    data = inputStr.split(charToStrip)
    return ' '.join(data)

def splitNreturn(inputStr):
    data = inputStr.split(',')
    retData = []
    for item in data:
        retData.append((item.strip()))
    return retData

#########################
# Read configuration data
#########################
confpath = os.path.dirname(__file__)
config = ConfigParser.ConfigParser()
config.read(confpath + "/backup.conf")
backupsize = int(config.get("Config","MaxLogFileSize"))
numbackups = int(config.get("Config","NumLogs"))
logfile = config.get("Config","LogFile")
deadline = int(config.get("Config", "offset"))
imageName = config.get("Config", "imageName")
backuploc  = config.get("Config","BackupLocation")
folderlist = splitNStripArgs((config.get("Folders", "FolderList")),',')
full_archive_name = backuploc  + "/Full-backup-" + datetime.datetime.now().strftime("%m%d%Y%H%M") + ".tar.gz"
inc_archive_name = backuploc  + "/Inc-backup-" + datetime.datetime.now().strftime("%m%d%Y%H%M") + ".tar.gz"
excludelist = splitNStripArgs((config.get("Exclude", "ExcludeList")),'"')
bkpretention = int(config.get('Config', 'offset'))
email = config.get('Config', 'SendNotification')



##########################
# Setup logging
##########################
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=backupsize, backupCount=numbackups)
my_logger.addHandler(handler)
now = time.time()

def make_incrementalbkp():
    '''Makes Incremental backups'''
    command = "nice -10 tar -g '%s' -czvf '%s' %s %s " % (imageName, inc_archive_name, folderlist, excludelist)
    my_logger.info("Executing: " + command)
    print('Executing: ' + command)
    out = subprocess.check_output(shlex.split(command))
    #my_logger.info(out)
    
def make_new_backup():
    """mk_new_backups() will create a new backup every time it is run.
    The backups are named by date.
    """    
    # Do the job
    my_logger.info("#########################################################################################")
    my_logger.info("-----------------------------------------------------------------------------------------")
    my_logger.info("Starting backup")
    my_logger.info("Time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    my_logger.info("-----------------------------------------------------------------------------------------")
    
    try:
        command = "nice -10 tar -czvf '%s' %s %s " % (full_archive_name, folderlist, excludelist)
        my_logger.info("Executing: " + command)
        out = subprocess.check_output(shlex.split(command))
        my_logger.info(out)
    
        my_logger.info("-----------------------------------------------------------------------------------------")
        my_logger.info("Backup Complete")
        strtime = "Time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        my_logger.info(strtime)
        stremail = str.upper(email)
        if stremail == 'Y':
            my_logger.info("Sending email with results...")
            sendemail.sendmail('Backup administrator message', 'Backup completed at ' + strtime)
        my_logger.info("-----------------------------------------------------------------------------------------")
        my_logger.info("#########################################################################################")
    except Exception as e:
        my_logger.info("Unexpected error:", e)
        print "Unexpected error:", e
            
def delete_old_backups():
    '''Deletes old backups'''
    # Do the job
    my_logger.info("#########################################################################################")
    my_logger.info("-----------------------------------------------------------------------------------------")
    my_logger.info("Start Clean Up of Old Backups...")
    my_logger.info("Time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    my_logger.info("-----------------------------------------------------------------------------------------")
    
    for root, dirs, files in os.walk(backuploc, topdown=False):
        for name in files:
            #Get file extension
            (base, ext)=os.path.splitext(name)
            #if it is a tar.gz
            if ext.lower() == '.gz':
                f = backuploc + '/' + name                
                if os.path.exists(f):
                    if os.stat(f).st_mtime < now - deadline:
                        os.remove(f)
                        my_logger.info("deleting: " + f)                                                                                        
                        #print os.stat(f).st_mtime
                else:                                        
                    my_logger.info("Did no find any old backups that meet the criteria for deletion")                                        
    
    my_logger.info("-----------------------------------------------------------------------------------------")
    my_logger.info("Completed Cleaning up old Backups...")
    strtime = "Time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    my_logger.info(strtime)
    my_logger.info("-----------------------------------------------------------------------------------------")
    my_logger.info("#########################################################################################")
    
def main():
    '''Main Module'''
    
    parser = OptionParser(usage,version=myversion,description=mydescription)
    parser.add_option("-i", "--incremental", help="Do incremental backup", action="store_true", dest="incremental")
    parser.add_option("-r", "--restore", help="restore system from the most recent backup", action="store_true", dest="restore")
    parser.add_option("-d", "--delete", help="delete backups that are %i day(s) old" % bkpretention, action="store_true", dest="delete")

    (options,args) = parser.parse_args()
    
    if options.restore and options.delete:
        parser.error("options -d and -r may not be run together.")
    
    elif options.restore:
        #restore_from_backup(conf)
        print 'Do something here'
    elif options.delete:
        #delete_old_backups(conf['bkdir'],deadline,i.name)
        print 'Do something here'
    else:
        make_new_backup()
        delete_old_backups()
                
if __name__ == '__main__':
    main()