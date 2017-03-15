# ver1 - set up basics
# ver2 - stayed as python copy2
# ver3 - 

import os
from shutil_edit import copyfile
from shutil_edit import copy2
import threading
import time
import logging
import logging.handlers

#***********************************************************************
# WARNING!
# Even the higher-level file copying functions (shutil.copy(),
# shutil.copy2()) can’t copy all file metadata.
# On POSIX platforms, this means that file owner and group are lost as
# well as ACLs. On Mac OS, the resource fork and other metadata are not
# used. This means that resources will be lost and file type and creator
# codes will not be correct. On Windows, file owners, ACLs and alternate
# data streams are not copied.
#***********************************************************************



#two files
#.vbm always has the same name
#.vbk filename changes daily
#Auto pick the .vbm and the current .vbk and copy to drive letter daily
#Send email on complete or GUI?

# Program will create 'job' of files to be copied. Then for each
#  file in 'job' do a copy.


#--- Set up Logging -----
l = logging.getLogger("Copy_Log")
l.setLevel(logging.DEBUG)
hand = logging.StreamHandler()
hand.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s: (%(levelname)s)\t- %(message)s',
                              datefmt='%d/%m/%Y %H:%M:%S')
hand.setFormatter(formatter)
l.addHandler(hand)
l.debug("Logging Started")

#--- Thread to copy source file to dest dir ----

import subprocess 

def CopyFile(*args):
    job, dest, abort_flag = args
    l.debug("Joblist:")
    l.debug(job)
    l.debug("Selected Destination: " + dest)
    for file in range(0,len(job)):
        l.info("Begin copying: " + job[file][0])
        copy2(job[file][0], dest, abort_flag)
        if(abort_flag.isSet()):
            l.debug("Aborting current job")
            break
        else:
            l.info(job[file][0] + " copy complete")

    if(abort_flag.isSet()):
        return
    
    l.info("Copy Job Complete")
    l.debug("Exiting Thread")
    return

# Function to return size of folder/directory
def dir_size(path):
    size = 0
    for file in os.listdir(path):
        f_path = path + file
        size = size + os.path.getsize(f_path)
    return size


# Function to create job list
def create_job(source, file_type):
    copy_job_list = []                                  # Create new list
                                                        # Job list made up of file, file_size
    for file in os.listdir(source):                     # Search the source directory
        for extension in range(0, len(file_type)):      # Check against file types
            if(file.endswith(file_type[extension])):    # for 'BIN' files
                path = source + file                    # generate file path for file
                size = os.path.getsize(path)            # get size of file
                tmp = [path, size]                      #
                if(tmp not in copy_job_list):           # <-- prevent duplicates
                    copy_job_list.append(tmp)           # and add to job list

    l.debug(copy_job_list)


    # Calculate size of job list
    job_size = 0
    for file in range(0,len(copy_job_list)):
        job_size = job_size + copy_job_list[file][1]

    return copy_job_list, job_size

def update_progress():

    dest_size = dir_size(dest)
    percent = int((dest_size/job_size)*100)
    print(str(percent) + "% Complete")

######################################
#----main----------------------

##source = "c:/"                              # Source directory - contains files to be copied
##dest = "h:/p/"                              # Destination directory - where the files will be copied to
##file_type = ['.BIN']                        # List of file types to be copied:
##                                            # Any file with one of these extensions in the source dir will be
##                                            #  copied to the dest dir.
##
### Generate list of files and sizes that will be copied
##job_list, job_size = create_job(source, file_type)
##
### begin the copy job    
##t1 = threading.Thread(target=CopyFile, args=(job_list, dest))
##t1.start()
##
##
##while(t1.isAlive()):
##    time.sleep(3)
##    dest_size = dir_size(dest)
##    percent = int((dest_size/job_size)*100)
##    print(str(percent) + "% Complete")
##
##
##        
##dest_size = dir_size(dest)  # Get final destination folder size
##
##print("Source: " + str(job_size) + "Bytes")
##print("Destination: " + str(dest_size) + "Bytes")
##
##if(dest_size == job_size):
##    print("Sizes Match - Copy OK")
##else:
##    print("Size mismatch - Failed Copy")


