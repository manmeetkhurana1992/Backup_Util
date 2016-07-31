This is a python tool to automate the Backup Process of any android device. This tool works on Windows and Linux both.
For the successful backup, you should have a rooted device and usb debugging should be enabled from the device. 
The script basically uses the "dd" function to dump the backup of blocks first into the device and then those blocks are pulled to pc.

To run the script make sure you have python installed on your pc. Follow the steps below:
1. Open the terminal on Linux or cmd on Windows.  
2. Execute the following command - "python backup_util.py"

You can also specify the output directory where you want to store the backup and also the config file which will include the list of blocks to be backed up. To see the list of options, execute
"python backup_util.py -h" or "python backup_util.py --help"

You can also have the preview option, wherein you will be showed the blocks which will be backed up. For preview, execute "python backup_util.py -p" or "python backup_util.py --preview"

In case of any problems, please reach out to me at "manmeetkhurana1992@gmail.com"
