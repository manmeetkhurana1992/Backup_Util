import subprocess
import sys
import os
import shutil
from optparse import OptionParser
from shutil import copyfile

#defining some global variables
global TEMPSDCARD, defaultoutpath, BLACKLIST, CMD_ADB_ROOT, CMD_ADB_DEVICES, CMD_ADB_SHELL_GETPROP, CMD_ADB_SHELL_FIND
TEMPSDCARD = '/sdcard/'
defaultoutpath=os.getcwd()
defaultoutpath=os.path.normpath(os.path.normpath(defaultoutpath))
BLACKLIST = ['userdata']
CMD_ADB_ROOT = 'adb root'
CMD_ADB_DEVICES = 'adb devices'
CMD_ADB_SHELL_GETPROP = 'adb shell getprop'
CMD_ADB_SHELL_FIND = 'adb shell find /dev/block -name by-name'


#Checking for connected devices and root permissions
def DeviceSetup():
    check = subprocess.check_output(CMD_ADB_DEVICES.split())
    output_adb_devices = subprocess.check_output(CMD_ADB_DEVICES.split())                   
    copy_output_adb_devices=output_adb_devices
    copy_output_adb_devices=copy_output_adb_devices.rstrip('\n')
    output_adb_devices=output_adb_devices.split("\n",1)[1]
    output_adb_devices=output_adb_devices.rstrip('\n')
    device_count=output_adb_devices.count('device')
    if device_count>1:
        print 'More than one device connected, Make sure to connect only one device and try again.'
        sys.exit()
    if 'unauthorized' in output_adb_devices:
        print copy_output_adb_devices+'\nThe device is not authorized.'
        sys.exit()
    if 'device' not in output_adb_devices: 
        print 'No Device Connected, Connect the device and try again.'
        sys.exit()
    output_adb_root = subprocess.check_output(CMD_ADB_ROOT.split())
    if 'already' not in output_adb_root:
        print'Error putting device into root mode. Cannot backup the device.'
        sys.exit()
    return


#To get the Block names and corresponding paths
def GetBlockNamesAndPaths(): 
    output_adb_shell_find = subprocess.check_output(CMD_ADB_SHELL_FIND.split())
    line_count = output_adb_shell_find.count('by-name')
    while line_count>1:
        output_adb_shell_find = output_adb_shell_find.split('\n',1)[1]
        line_count -=1
    CMD_adb_shell_list = 'adb shell ls -l '+output_adb_shell_find
    output_adb_shell_list = subprocess.check_output(CMD_adb_shell_list.split())
    output_adb_shell_list=output_adb_shell_list.rstrip('\n')
    adb_out_file = open("temp.txt", "w")
    print>>adb_out_file,output_adb_shell_list
    adb_out_file.close()
    return


#To generate the mapper file of the Blocks with their paths
def Mapper():
    adb_read_file = open("temp.txt", "r") 
    mapfile = open("Mapping.txt", 'w')
    for line in adb_read_file:
        fields = line.split('->')
        block_name=fields[0].split(':')[1].split(' ')[1]
        block_addr=fields[1].split(' ')[1].rstrip('\n')
        print>>mapfile,block_name+"-->"+block_addr
    adb_read_file.close()
    mapfile.close()
    #os.remove("temp.txt")
    return


#Checking for accessibility of config file and backup directory
def CheckPaths():
    if not os.path.exists(options.filename):
        print options.filename+': does not exists. Cannot backup partitions.'
        sys.exit()
    if not os.path.isdir(options.dirname):
        print options.dirname+': does not exists. Trying to create the directory.'
        try:
            os.mkdir(options.dirname)
            print "Directory created, proceeding with backing the partitions."
        except:
            print "Coudn't create "+options.dirname+" \nCannot backup partitions"
            sys.exit()
    if not os.access(options.dirname, os.W_OK):
        print "Couldn't access "+options.dirname+" \nMake sure you it is writable"
        sys.exit()
    return


#To present the preview in case preview command is set
def Preview():
    if not os.path.isdir(options.dirname):
        print options.dirname+': does not exists.'
    if not os.access(options.dirname, os.W_OK):
        print "Couldn't access "+options.dirname+" \nMake sure you it is writable"
    print "Output Directory: "+options.dirname+"\n"       
    preview_file=open(options.filename, "r")
    for line in preview_file:
        fields = line.split('-->')
        block_name=fields[0]
        block_addr=fields[1]
        block_addr=block_addr.rstrip('\n')
        if block_name not in BLACKLIST:
            print block_name+'-->'+block_addr
    sys.exit()
    return


#Finally executing the backup
def Backup():
    output_adb_shell_getprop = subprocess.check_output(CMD_ADB_SHELL_GETPROP.split())
    print 'Device Properties : Backing-Up'
    out_file=open("GetProp_Output.txt", "w")
    output_adb_shell_getprop=output_adb_shell_getprop.rstrip('\n')
    print>>out_file,output_adb_shell_getprop
    print 'Device Properties: Backup Complete\n'
    out_file.close()
    filemove1=os.path.normpath(options.dirname+"/Mapping.txt")
    filemove2=os.path.normpath(options.dirname+"/GetProp_Output.txt")
    if options.dirname != os.getcwd():
        copyfile("Mapping.txt",filemove1)
    shutil.move("GetProp_Output.txt",filemove2)
    infile = open(options.filename, "r")
    for line in infile:
        fields = line.split('-->')
        block_name=fields[0]
        block_addr=fields[1]
        if block_name not in BLACKLIST:
            print block_name+': Backing-Up'
            CMD_adb_shell_dd = 'adb shell dd of='+TEMPSDCARD+block_name+' if='+block_addr
            subprocess.check_output(CMD_adb_shell_dd.split())
            CMD_adb_pull = 'adb pull '+TEMPSDCARD+block_name+' '+options.dirname
            subprocess.check_output(CMD_adb_pull.split())
            print block_name+': Backup Complete\n'
            CMD_adb_shell_rm = 'adb shell rm '+TEMPSDCARD+block_name
            subprocess.check_output(CMD_adb_shell_rm.split())
        else:
            print block_name+' is BLACKLISTed. Cannot Backup this field.\n'
    infile.close()
    os.remove("Mapping.txt")  
    print '\nBackup Complete'
    return


if __name__ == "__main__":
    #to add the customized options for command line arguments
    parser = OptionParser()
    parser.add_option("-o", "--outpath", dest="dirname", default=defaultoutpath,
                  help="Backup partitions to this output directory. For eg:- '/home/username/backup/'", metavar="PATH")
    parser.add_option("-c", "--configfile", dest="filename",default='Mapping.txt',
                  help="List of partitions to backup. For eg:- '/home/Download/config.txt'", metavar="FILE")
    parser.add_option("-p", "--preview",action="store_true", dest="preview",default=False,
                  help="Display preview of output files")
    (options, args) = parser.parse_args()

    #normalizing the paths of config file and backup directory
    options.filename=os.path.normpath(options.filename)
    options.dirname=os.path.normpath(options.dirname)

    #Execution starts from here
    DeviceSetup()
    GetBlockNamesAndPaths()
    Mapper()
    CheckPaths()
    if options.preview:
        Preview()
    else:
        Backup()
