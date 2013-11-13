#! /usr/bin/python
 
''' 
Title:    backup.py
Author:   Johann Romero (johann.romero@gmail.com)
Date:     Jul022013
update:   Nov092013
Info:     "jrbackup" can be used to automatically backup given folder locations
          to another backup location. jrbackup is easily configurable through a
          configuration file. jrbackup uses tar to achieve Full and Incremental Archives.    



'''
 
import ConfigParser
import os
import tarfile
import logging.handlers
import datetime
import time
from optparse import OptionParser
import sendemail

#Usage and Description
usage = "usage: %prog [options]"
mydescription = ('backup.py is intended to be a simple yet powerful backup tool. ' +
'To backup your system edit the backup.conf file so that it has all the correct information, ' + 
'afterwards set backup.py to run automatically with cron or crontab.')

myversion = "jrbackup-1.1"

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
backupsize = config.getint("Config","MaxLogFileSize")
numbackups = config.getint("Config","NumLogs")
logfile = config.get("Config","LogFile")
backuploc  = config.get("Config","BackupLocation")
sectionList = config.sections()
full_archive_name = ".Full-backup-" + datetime.datetime.now().strftime("%m%d%Y%H%M")
inc_archive_name = backuploc  + "\Inc-backup-" + datetime.datetime.now().strftime("%m%d%Y%H%M")
email = config.get('Config', 'SendNotification')



##########################
# Setup logging
##########################
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=backupsize, backupCount=numbackups)
my_logger.addHandler(handler)
#now = time.time()
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def make_incrementalbkp():
    '''
    Makes Incremental backups
    '''
    
def make_new_backup(strname,strdir,tarType,tarExt):
    '''
    Creates a new backup every time it is run.
    The backups are named by date.
    '''    
    # Do the job
    my_logger.info("-----------------------------------------------------------------------------------------")
    my_logger.info("Starting backup")
    my_logger.info("Time: " + now)
    
    try:
        #create a tar file and open it with gz compression                    
        archiveName = backuploc + "\\" + strname + full_archive_name + tarExt
        print ('Created tar file %s ' %archiveName )
        archive = tarfile.open(archiveName, tarType)
 
        print '-'*50
        fileCount = 0
       
        print 'Compressing', strdir
        my_logger.info('Compressing ' + strdir)
        fileCount += 1
        archive.add(strdir)
        my_logger.info('adding to archive %s ' % strdir )
        my_logger.info("-----------------------------------------------------------------------------------------")
        my_logger.info("Backup Completed")
        strtime = "Time: " + now
        my_logger.info(strtime)
        archive.close()
    except OSError:
        strMessage = 'Could not compress ' + strdir 
        print strMessage
        my_logger.info(strMessage)
                 
def cleanup_Backups(strBkploc,strSection):
    '''
    Deletes old backups
    '''
    # Do the job
    my_logger.info("-----------------------------------------------------------------------------------------")
    my_logger.info("Start Clean Up of Old Backups...")
    my_logger.info("Time: " + now)
    
    for dirname, dirnames, filenames in os.walk(strBkploc):
        for name in filenames:
            #Get file extension
            (base, ext)=os.path.splitext(name)
            #if it is a tar.gz
            if ext.lower() == '.gz':   
                logFile = os.path.join(dirname, name)
                stats = os.stat(logFile)  
                modDate = time.localtime(stats[8])
                lastmodDate = time.strftime("%m-%d-%Y", modDate)
                expDate = returnRetentionperiod(config.getint(strSection, "retention"))            
                if  expDate > lastmodDate:
                    delete_Oldbackups(logfile)                                        
    
    my_logger.info("Completed Cleaning up old Backups...")
    strtime = "Time: " + now
    my_logger.info(strtime)
    my_logger.info("-----------------------------------------------------------------------------------------")
    
def main():
    '''
    Main Module
    '''
    parser = OptionParser(usage,version=myversion,description=mydescription)
    parser.add_option("-f", "--full", default=True, help="Do full backup", action="store_true", dest="full")
    parser.add_option("-i", "--incremental", default=False, help="Do incremental backup", action="store_true", dest="incremental")
    parser.add_option("-r", "--restore", default=False, help="restore system from the most recent backup", action="store_true", dest="restore")
    parser.add_option("-d", "--delete", default=True, help="delete backups that  have exceeded retention period", action="store_true", dest="delete")
    parser.add_option("-l", "--list", action="store_true", dest="listFiles", default=True, help="List all files that would be affected. This is the default option.")
    (options,args) = parser.parse_args()
    
    if options.restore and options.delete:
        parser.error("options -d and -r may not be run together.")
    
    if options.full and options.incremental:
        parser.error("options -f and -i may not be run together")
    
    # setup compression type
    tarType = "w:gz"
    tarExt = '.tar.gz'
    
    for s in sectionList:
        if config.has_option(s, "enabled"):    
            enabled = config.getboolean(s, "enabled")
            if enabled:
                if options.listFiles:
                    showAffecteditems(s)
            
                if options.full:                    
                    make_new_backup(config.get(s, "name"),s,tarType,tarExt)
            
                if options.delete:
                    cleanup_Backups(config.get("Config", "BackupLocation"),s)        
                
                if options.restore:
                    #restore_from_backup(conf)
                    print ('Do something here in the future')
        
                if options.incremental:
                    print ('Do something here in future')
    
    print 'Work Completed, pls check results'
    sendEmail('g')
    #my_logger.info('Work Completed, pls check results')

def delete_Oldbackups(strPath):
    '''
    It executes the actual deletion
    '''
    try:
        if  os.path.exists(strPath):
            #if os.stat(f).st_mtime < now - deadline:
            os.remove(strPath)
            my_logger.info("deleting: " + strPath)                                                                                        
            #print os.stat(f).st_mtime
    except OSError:
        strMessage = 'Error deleting file: ' + strPath 
        print strMessage
        my_logger.info(strMessage)
        
def returnRetentionperiod(bkpretention):
    '''
    Substract the delta from current date and returns it
    '''
    today = datetime.date.today()
    DD = datetime.timedelta(days=bkpretention)
    olderthandate = today - DD
    #padded the day to be a two digit int so that it would match the day digits on file modtime
    day = '%02d' % olderthandate.day
    month = olderthandate.month
    year = olderthandate.year
    
    #filterDate = str(year) + '-' + str(month) + '-' + str(day)
    filterDate = str(month) + '-' + str(day) + '-' + str(year)
    return  filterDate

def showAffecteditems(strName):
    '''
    Just list files or folders that will be affected
    '''             
    strMsg = 'Working on: %s' % strName
    print strMsg
    my_logger.info(strMsg)
    strMsg1 = 'The following files or folders will be affected:' 
    print strMsg1
    my_logger.info(strMsg1)
    print strName
    my_logger.info(strName)
                
def sendEmail(option):
    '''
    Sends email out after completing backup job
    '''
    stremail = config.getboolean("Config", "SendNotification")
    if stremail:
        if option == 'g':
            my_logger.info("Sending email with results...")
            sendemail.sendmail('Backup administrator message', 'Backup completed at ' + now)
        
        if option == 'b':
            my_logger.info("Something went wrong Sending email with results...")
            sendemail.sendmail('Backup administrator message', 'Backup completed at ' + now)
            
if __name__ == '__main__':
    main()