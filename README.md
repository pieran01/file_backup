# file_backup
Auto backup files with a specific file extension from a source folder to destination folder. Confirms successful backup by comparing filesizes of source and destination copies. 

Designed to be turned into an executable so another scheduling program can execute the backup program
When executed, it will auto load a 'config' file and begin the backup process, unless the auto-start is interrupted with a press of the <shift> key.
Interrupting the auto-start will enter manual mode. Here the source folder, destination folder and desired filetypes to be coppied can be set and stored to the config file. The backup can then be started manually, by pressing 'Create Job' to view the files that will be coppied and view the total size of the copy. Clicking 'start' will then begin the backup. The progress bar will indicate how far along the backup is. Once complete, the size of the files coppied will be compared with the source destination to confirm a successful backup.

gui_v5.py is the main program to handle everything and is the GUI
filesize3.py is the code that handles creating a copy job and comparing file sizes
shutil_edit.py is an edited python module that provides the copying function. The edit adds a 'check for abort' so the copying can be aborted safely.


To Do:
- Add email confirmation when job has completed
- Catch folders that don't exist
- Check what happens with subfolders
