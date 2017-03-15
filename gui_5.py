# ver1 - working ok
# ver2 - add config file for source/dest/filetypes
# ver3 - converted gui into a classes
# ver4 - making auto start
# ver5 - making option to break auto start and enter manual mode
#           - cancel browser dialog should not change the source/destination fields
#           - cross of A_Dialog should not start auto copy

import tkinter
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from tkinter import font
import functools
import threading
import time
import logging
import atexit
#import email_uk as e_mail

import filesize3 as f
from filesize3 import l


#------------------------------------
# Main Dialog

class M_Dialog:

    def __init__(self, parent):

        l.debug("Main dialog begins")
        self.parent = parent

        
        # Giving option to break auto_start
        l.debug("Pausing Main to offer break into manual")
        self.a_window = tkinter.Toplevel(self.parent)
        self.a_app = A_Dialog(self.a_window)
        self.parent.withdraw()
        self.parent.wait_window(self.a_window)
        self.auto_start = self.a_app.result

        # Resume with Main dialog here...
        l.debug("Resuming with main dialog")
        self.parent.deiconify()

        top = parent                # to allow easy conversion to this GUI_v3
        top.geometry("400x210")
        top.wm_title("Copy Files")

        #self.auto_start = auto_start

        self.source = tkinter.StringVar()
        self.destination = tkinter.StringVar()
        self.filetype_input = tkinter.StringVar()
        self.progress = tkinter.IntVar()
        self.progress.set(0)

        self.abort_flag = threading.Event()
        self.abort_flag.clear()

        # Widgets:
        self.browse_source = tkinter.Button(top, text = "Browse", command=self.link_br_src)
        self.browse_destination = tkinter.Button(top, text = "Browse", command = self.link_br_dst)
        self.create_job = tkinter.Button(top, text="Create Job", command=self.link_create_job)
        self.abort = tkinter.Button(top, text="Abort", command=self.link_abort)
        self.source_entry = tkinter.Entry(top, textvariable=self.source)
        self.dest_entry = tkinter.Entry(top, textvariable=self.destination)
        self.filetype_entry = tkinter.Entry(top, textvariable=self.filetype_input)
        self.save_button = tkinter.Button(top, text="Save Config", command = self.link_save_config)
        self.l_filetypes = tkinter.Label(top, text="Filetypes:")
        self.l_ft_explain = tkinter.Label(top, font=font.Font(size=7),
                             text="Enter file extensions separated by a comma.")
        self.l_source = tkinter.Label(top, text= "Source:")
        self.l_dest = tkinter.Label(top, text="Destination:")
        self.l_prog = tkinter.Label(top, text="Progress:")

        self.prog_bar = ttk.Progressbar(top, orient=tkinter.HORIZONTAL, variable=self.progress)

        # Placements:

        self.src_y = 30
        self.dest_y = 60
        self.x_offset = 30

        self.l_source.place(x=self.x_offset, y=self.src_y)
        self.source_entry.place(height=20, width=200, x=self.x_offset+70, y=self.src_y)
        self.browse_source.place(height=20, width=60, x=self.x_offset+280, y=self.src_y)

        self.l_dest.place(x=self.x_offset, y=self.dest_y)
        self.dest_entry.place(height=20, width=200, x=self.x_offset+70, y=self.dest_y)
        self.browse_destination.place(height=20, width=60, x=self.x_offset+280, y=self.dest_y)

        self.l_filetypes.place(x=self.x_offset,y=90)
        self.filetype_entry.place(height=20, width=200, x=self.x_offset+70, y=90)
        self.l_ft_explain.place(x=self.x_offset+70,y=110)

        self.create_job.place(height=25, width=80, x=self.x_offset+70+15, y=135)
        self.save_button.place(height=25, width=80, x=self.x_offset+70+105, y=135)

        self.l_prog.place(x=self.x_offset, y=170)
        self.prog_bar.place(height=20, width=200, x=self.x_offset+70, y=170)
        self.abort.place(height=20, width=60, x=self.x_offset+280, y=170)

        self.load_config()

        if(self.auto_start):
            # create_job - get data, no need to show J_dialog
            self.link_create_job()
            # begin threads
            self.start_job()
            
        
    # End of __init__
    
    # Link Functions:

    def link_br_src(self):
        self.progress.set(0)         # reset progress bar
        filepath = filedialog.askdirectory(title="Select Source Directory...",
                                           mustexist=True,
                                           initialdir="C:/")
        filepath = filepath + "/"
        self.source.set(filepath)
        return

    def link_abort(self):
        l.debug("Abort Pressed")
        self.abort_flag.set()

        self.browse_source.config(state="normal")
        self.browse_destination.config(state="normal")
        self.create_job.config(state="normal")
        self.source_entry.config(state="normal")
        self.dest_entry.config(state="normal")
        self.filetype_entry.config(state="normal")
        self.save_button.config(state="normal")

    def safe_close(self):
        l.debug("Program Closed")

    def link_save_config(self):
        conf_file = "config.txt"
        with open(conf_file, 'w') as conf:
            conf.write(self.source.get() + "\n")
            conf.write(self.destination.get() + "\n")
            conf.write(self.filetype_entry.get() + "\n")
        l.debug("Config saved")
        return
        
    def load_config(self):
        conf_file = "config.txt"
        with open(conf_file, 'r') as conf:
            self.source.set(conf.readline().strip())
            self.destination.set(conf.readline().strip())
            self.filetype_input.set(conf.readline().strip())
##            tmp_auto_start = conf.readline().strip()
##            if (tmp_auto_start == "true"):
##                self.auto_start = True
##            else:
##                self.auto_start = False
        l.debug("Config Loaded")
        return

    def link_br_dst(self):

        self.progress.set(0)         # reset progress bar
        filepath = filedialog.askdirectory(title="Select Destination Directory...",
                                           mustexist=True,
                                           initialdir="C:/")
        filepath = filepath + "/"
        self.destination.set(filepath)
        return

    def link_create_job(self):

        self.abort_flag.clear()      # reset the abort flag
        self.progress.set(0)         # reset progress bar

        # Check User Input:
        if(self.source.get() == "" or self.destination.get() == ""):
            messagebox.showerror(title="Error", message="Please enter source & destination locations")
            return
        
        # (1) sort filetype input into list of file types
        # (2) send this, source and dest to copy job
        # (3) display the files that will be copied and request confirmation

        #(1) sort filetype input into list
        filetypes = self.filetype_input.get()
        filetypes = filetypes.split(',')
        for x in range(0, len(filetypes)):
            filetypes[x] = filetypes[x].strip()
            if(filetypes[x][0] != '.'):
                l.debug("Bad file extension - missing '.'")
                return
        
            
        # (2) send info to create job
        self.job_list, self.job_size = f.create_job(self.source.get(), filetypes)

        if(self.auto_start):
            return

        # (3) Display the job
##        show_joblist(job_list, job_size)
        self.job_window = tkinter.Toplevel(self.parent)
        self.job_window.transient(self.parent)
        self.job_window.grab_set()
        self.job_app = J_Dialog(self.job_window, self.job_list, self.job_size, self.destination)
        self.parent.wait_window(self.job_window)
        l.debug("Waiting for Job list window to start or cancel job")
        # Wait for 'create job' window to close
        # Get it's result - either start or cancle
        l.debug("Job list window closed")
        if (self.job_app.result):
            print("Job window should now be closed, result is true")
            self.start_job()
            
        else:
            print("Job window should now be closed, result is false")
        return

    # Job Functions: (GUI link to Copying program)
    def start_job(self):
        self.t_copyfile = threading.Thread()
        self.t_copyfile.__init__(target=f.CopyFile, args=(self.job_list, self.destination.get(), self.abort_flag))
##        self.t_progress = threading.Thread(target=self.progress_monitor, args=[self.job_size])
        self.t_progress = threading.Thread(target=self.progress_monitor)
        self.t_copyfile.start()
        self.t_progress.start()
        self.browse_source.config(state="disabled")
        self.browse_destination.config(state="disabled")
        self.create_job.config(state="disabled")
        self.source_entry.config(state="disabled")
        self.dest_entry.config(state="disabled")
        self.filetype_entry.config(state="disabled")
        self.save_button.config(state="disabled")
        return

    def progress_monitor(self):
        l.debug("Progress thread started")
        while self.t_copyfile.isAlive():
            current_size = f.dir_size(self.destination.get())
            percent = int((current_size/self.job_size)*100)
            self.progress.set(percent)
            time.sleep(1)

        # By here, t_copy thread has completed and died or has aborted

        if self.abort_flag.isSet():
            l.debug("Progress thread terminated")
            messagebox.showerror("Aborted", "Copy Job has been aborted.")
            #send_email("abort")
            return
        
        # Check and confirm final file sizes:
        dest_size = f.dir_size(self.destination.get())
        if dest_size == self.job_size:
            l.info("Copy Job Completed")
            self.progress.set(100)
            messagebox.showinfo("Complete", "Copy job has completed, filesizes are as expected")
            #send_email("success")
        else:
            messagebox.showerror("Error", "File sizes do not match...")
            #send_email("error")

        self.browse_source.config(state="normal")
        self.browse_destination.config(state="normal")
        self.create_job.config(state="normal")
        self.source_entry.config(state="normal")
        self.dest_entry.config(state="normal")
        self.filetype_entry.config(state="normal")
        self.save_button.config(state="normal")
        return
    
#-----------------------------
# Joblist Dialog:
class J_Dialog():

    def __init__(self, parent, job_list, job_size, destination):

        self.parent = parent
        j = self.parent             # Easy conversion to Class dialog

        j.title("Copy Joblist")
        j.geometry("340x200")

        self.result = None          # Result used to return to main dialog
        
        self.info_string = tkinter.StringVar()
        self.info_string.set("The following files will be copied to " + destination.get())
        self.info = tkinter.Label(j, textvariable=self.info_string)
        self.info.place(x=10,y=10)

        self.txt = tkinter.StringVar()
        self.txt.set("")

        for x in range(0,len(job_list)):
            self.txt.set(self.txt.get() + job_list[x][0] + "\n")

        self.msg = tkinter.Message(j,textvariable=self.txt, justify="left",
                              anchor="nw", relief="sunken", width=300)
        self.msg.place(width=300, height=100, x=20,y=30)

        self.info2_string = tkinter.StringVar()
        self.info2_string.set("Total size: " + str(job_size) + "Bytes")
        self.info2 = tkinter.Label(j, textvariable=self.info2_string)
        self.info2.place(x=10,y=130)

        self.begin = tkinter.Button(j, text="Start", command=self.link_begin)
        self.cancel = tkinter.Button(j, text="Cancel", command=self.link_cancel)

        self.begin.place(height=20, width=60, x=170-60-50, y=160)
        self.cancel.place(height=20, width=60, x=170+50, y=160)

    def link_begin(self):
        self.result = True
        self.parent.destroy()

    def link_cancel(self):
        self.result = False
        self.parent.destroy()

        
#-------------------------------------------------------    

class A_Dialog:

    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Manual Mode")
        self.parent.resizable(0,0)
        self.parent.geometry("250x35")
        self.counter = tkinter.IntVar()
        self.counter.set(5)
        self.result = True
        
        # Widgets:
        self.info = tkinter.Label(self.parent, text = "Press Shift to enter Manual Mode...")
        self.count = tkinter.Label(self.parent, textvariable=self.counter)

        # Layout:
        self.info.place(x=0, y=0)
        self.count.place(x=0,y=15)

        # Function:
        self.parent.bind("<Key>", self.get_shift)
        self.wait_manual()

    def wait_manual(self):
        l.debug("Waiting for shift")
        if(self.counter.get() > 0):
            self.counter.set(self.counter.get() - 1)
            self.parent.after(1000,self.wait_manual)
            return
        l.debug("Wait time expired")
        l.debug("Starting auto-copy")
        self.end_dialog()

    def get_shift(self, event):
        if(event.keycode == 16):
            l.debug("Shift pressed - entering manual mode")
            self.result = False
            #self.counter.set(0)
            self.end_dialog()

    def end_dialog(self):   
        self.parent.unbind("<Key>")
        self.parent.destroy()

#------------------------------------------------------
# Main

#atexit.register(safe_close)
##newroot = None
##main = None


root = tkinter.Tk()
main = M_Dialog(root)
root.mainloop()





