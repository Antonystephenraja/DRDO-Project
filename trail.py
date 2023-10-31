from tkinter import *
from PIL import Image, ImageTk
import time
import customtkinter
from customtkinter import CTkButton
from tkinter import Tk
from tkinter import ttk
import os
from tkinter import simpledialog
from tkinter import *
from PIL import Image, ImageTk
import os
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
from customtkinter import CTkButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
from datetime import datetime
import ctypes

import numpy as np
import csv
import pandas as pd
from tkinter import filedialog
import pandas as pd
from datetime import datetime
import csv
from tkinter import filedialog
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk
from tkinter import simpledialog
from tkinter import messagebox
import pyautogui
from tkinter import Tk, Label, Canvas, Scrollbar

main = Tk()
main.title("Welcome to XYMA")
screen_width = main.winfo_screenwidth()
screen_height = main.winfo_screenheight()
x = (screen_width - (screen_width - 200)) // 2
y = (screen_height - (screen_height - 200)) // 2
main.geometry("{}x{}+{}+{}".format(screen_width - 200, screen_height - 300, x, y))
main.overrideredirect(1)





global desired_time_span
desired_time_span =5

global z
z=np.linspace(0,desired_time_span,1000000)

#Screen sizess
global screen
screen = 0.006

global fig_width
fig_width = int(screen_width * screen)

global fig_height
fig_height = int(fig_width * 6/10)

global Amplitude_Threshold1
Amplitude_Threshold1 = 2.5
global Amplitude_Threshold2
Amplitude_Threshold2 = 2.5
global Amplitude_Threshold3
Amplitude_Threshold3 = 2.5
global Amplitude_Threshold4
Amplitude_Threshold4 = 2.5

amplitude_thresholds = [Amplitude_Threshold1, Amplitude_Threshold2, Amplitude_Threshold3, Amplitude_Threshold4]

aa = []
bb = []
cc = []
dd = []



Distance = 15000
Trigger = 0
samplefreq_in_MHz = 200
dt=1/samplefreq_in_MHz

def timeButton():
    global desired_time_span
    new_time = simpledialog.askstring("Input", "Enter a Time Interval (in seconds):")
   
    if new_time:
        try:
            desired_time_span = float(new_time)
            #btn2.config(text=f"Time-{desired_time_span} s")
            print("Time span updated to:", desired_time_span, "seconds")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    else:
        print("No data entered")





#making animation
image_a=ImageTk.PhotoImage(Image.open('E:/xyma/Image/c2.png'))
image_b=ImageTk.PhotoImage(Image.open('E:/xyma/Image/c1.png'))

#xyma imgae
xyma_img = Image.open("E:/xyma/Image/xyma.png")
xyma_img = ImageTk.PhotoImage(xyma_img)
 
#drdo image
drdo_img = Image.open("E:/xyma/Image/drdo1.png")
drdo_img = ImageTk.PhotoImage(drdo_img)


fig, axes = plt.subplots(4, 1, figsize=(screen_width //240, screen_height //260))



# print(figsize)
for ax in axes:
    ax.set_ylim(0, 5)  # Set Y-axis limits
    ax.set_xlim(0, desired_time_span)  # Set X-axis limits
    ax.set_xlabel('Time (s)')  # Set X-axis label
    ax.set_ylabel('Volume (V)')





# Get the current timestam
start_time = datetime.now()
i = 2
time_difference_in_minutes = 0


chandle = ctypes.c_int16()
status = {}

status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(chandle), None)


try:
    assert_pico_ok(status["openunit"])
except: # PicoNotOkError:
    powerStatus = status["openunit"]

    if powerStatus == 286:
        status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
    elif powerStatus == 282:
        status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
    else:
        messagebox.showerror("Error","Device is Not Connected")
        raise

    assert_pico_ok(status["changePowerSource"])

def generate_Array():


    chARange = 8
    chBRange = 8
    chCRange = 8
    chDRange = 8
    status["setChA"] = ps.ps4000aSetChannel(chandle, 0, 1, 0, chARange, 0)
    assert_pico_ok(status["setChA"])
    status["setChB"] = ps.ps4000aSetChannel(chandle, 1, 1, 0, chBRange, 0)
    assert_pico_ok(status["setChB"])
    status["setChC"] = ps.ps4000aSetChannel(chandle, 2, 1, 0, chCRange, 0)
    assert_pico_ok(status["setChC"])
    status["setChD"] = ps.ps4000aSetChannel(chandle, 3, 1, 0, chDRange, 0)
    assert_pico_ok(status["setChD"])

    preTriggerSamples = 0
    postTriggerSamples = 1000000
    maxSamples = preTriggerSamples + postTriggerSamples

    #timeIntervalns = (maxSamples//desired_time_span)
    #timebase =(50+(2*timeIntervalns))//timeIntervalns)
    timebase = 252
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    oversample = ctypes.c_int16(1)
    status["getTimebase2"] = ps.ps4000aGetTimebase2(chandle, timebase, maxSamples, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(status["getTimebase2"])


           
    # create overflow location
    overflow = ctypes.c_int16()
    # create converted type maxSamples
    cmaxSamples = ctypes.c_int32(maxSamples)


       
    status["runBlock"] = ps.ps4000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, None, 0, None, None)
    if(status["runBlock"] == 7):
        messagebox.showerror("Error","Device is Not Connected")
    else:
        assert_pico_ok(status["runBlock"])

    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)

    while ready.value == check.value:
        status["isReady"] = ps.ps4000aIsReady(chandle, ctypes.byref(ready))
    bufferAMax = (ctypes.c_int16 * maxSamples)()
    bufferBMax = (ctypes.c_int16 * maxSamples)()
    bufferCMax = (ctypes.c_int16 * maxSamples)()
    bufferDMax = (ctypes.c_int16 * maxSamples)()
    bufferAMin = (ctypes.c_int16 * maxSamples)()
    bufferBMin = (ctypes.c_int16 * maxSamples)()
    bufferCMin = (ctypes.c_int16 * maxSamples)()
    bufferDMin = (ctypes.c_int16 * maxSamples)()

    status["setDataBuffersA"] = ps.ps4000aSetDataBuffers(chandle, 0, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxSamples, 0 , 0)
    assert_pico_ok(status["setDataBuffersA"])
    status["setDataBuffersB"] = ps.ps4000aSetDataBuffers(chandle, 1, ctypes.byref(bufferBMax), ctypes.byref(bufferBMin), maxSamples, 0 , 0)
    assert_pico_ok(status["setDataBuffersB"])
    status["setDataBuffersC"] = ps.ps4000aSetDataBuffers(chandle, 2, ctypes.byref(bufferCMax), ctypes.byref(bufferCMin), maxSamples, 0 , 0)
    assert_pico_ok(status["setDataBuffersC"])
    status["setDataBuffersD"] = ps.ps4000aSetDataBuffers(chandle, 3, ctypes.byref(bufferDMax), ctypes.byref(bufferDMin), maxSamples, 0 , 0)
    assert_pico_ok(status["setDataBuffersD"])

       
    status["getValues"] = ps.ps4000aGetValues(chandle, 0, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])

    maxADC = ctypes.c_int16(1000000)

    adc2mVChAMax = adc2mV(bufferAMax, chARange, maxADC)
    adc2mVChBMax = adc2mV(bufferBMax, chBRange, maxADC)
    adc2mVChCMax = adc2mV(bufferCMax, chCRange, maxADC)
    adc2mVChDMax = adc2mV(bufferDMax, chDRange, maxADC)

    print("A",np.array(adc2mVChAMax)/1000)
    print("B",np.array(adc2mVChBMax)/1000)
    print("C",np.array(adc2mVChCMax)/1000)
    print("D",np.array(adc2mVChDMax)/1000)

    a=np.array(adc2mVChAMax)/1000
    b=np.array(adc2mVChBMax)/1000
    c=np.array(adc2mVChCMax)/1000
    d=np.array(adc2mVChDMax)/1000
    e = np.linspace(0, (cmaxSamples.value - 1) * timeIntervalns.value, cmaxSamples.value)
    a=a[:int(200000*round(desired_time_span))]
    b=b[:int(200000*round(desired_time_span))]
    c=c[:int(200000*round(desired_time_span))]
    d=d[:int(200000*round(desired_time_span))]

    
   

 

    return a,b,c,d,e

# def timeButton():
#    desired_time_span = simpledialog.askstring("Input", "Enter a Data Frequency (in seconds):")
#    btn2.config(text=f"Time-{desired_time_span}")

#    if new_time:
#        try:
         
#            desired_time_span = float(desired_time_span)
#            print("Time span updated to:", desired_time_span, "seconds")
#        except ValueError:
#            print("Invalid input. Please enter a valid number.")
#    else:
#        print("No data entered")



def recorder():
    Recorded = Label(q,text="Recorded",bg="red",fg="white",width="10")
    Recorded.configure(font=('Calibri',15))
    Recorded.place(x=screen_width-350,y=50)
   
def recording():
    Recording1 = Label(q,text="Recording",bg="green",fg="white",width="10")
    Recording1.configure(font=("Calibri",15))
    Recording1.place(x=screen_width-350,y=50)

def peak_detection(data, amplitude_threshold):
    peaks, _ = find_peaks(data, height=amplitude_threshold, distance=Distance)
    return peaks


def plot_array(a, b, c, d,peak_indices,desired_time_span):
    common_colors = ['red', 'green', 'blue', 'orange']
    plot_colors = ['purple','blue','green','red']
    subplot = [a, b, c, d]
    amplitude_thresholds = [Amplitude_Threshold1, Amplitude_Threshold2, Amplitude_Threshold3, Amplitude_Threshold4]
\
    sample, axes = plt.subplots(4, 1, figsize=(fig_width, fig_height))
    z=np.linspace(0,round(desired_time_span),round(desired_time_span)*200000)
   
    for i in range(len(axes)):
        axes[i].plot(z,subplot[i],color=plot_colors[i])
        axes[i].plot(z[peak_indices[i]],subplot[i][peak_indices[i]], "ro", label=f'Channel {i + 1} Peaks', color=common_colors[i])
        axes[i].set_ylim(-5, 5)
        axes[i].set_xlim(0,desired_time_span)
        axes[i].set_xlabel('Time (s)')
        axes[i].set_ylabel('Ampilitude (V)')
        axes[i].legend()
    sample.subplots_adjust(hspace=0.3)

    canvas = FigureCanvasTkAgg(sample, master=q)
    canvas_widget = canvas.get_tk_widget()
    canvas_x = (screen_width - canvas_widget.winfo_reqwidth()) // 2
    canvas_y = (screen_height - canvas_widget.winfo_reqheight()) // 2
    canvas_widget.place(x=screen_width // 6.4, y=screen_height // 10.6)
   
def clear_generated_data():
    global a, b, c, d, e
    a = []  # Replace this with  initial data for channel A
    b = []  # Replace this with  initial data for channel B
    c = []  # Replace this with  initial data for channel C
    d = []  # Replace this with  initial data for channel D
    e = []    

def testing():
    global aa, bb, cc, dd, Tor_list, No_of_Tor_list  

    clear_generated_data()
    for ax in axes:
       ax.cla()
   
    a, b, c, d, e = generate_Array()

    #recording()
    current_time = datetime.now()
    eltime = (current_time - start_time)
    elapsed_time = (current_time - start_time).total_seconds()

    if elapsed_time >= desired_time_span:
       status["stop"] = ps.ps4000aStop(chandle)
       assert_pico_ok(status["stop"])


    peak_indices = [peak_detection(channel, threshold) for channel, threshold in zip([a, b, c, d], amplitude_thresholds)]
   
    plot_array(a, b, c, d, peak_indices,desired_time_span)
    aa, bb, cc, dd = a, b, c, d
    Tor_list, No_of_Tor_list = find_tor_and_no_of_tor_for_all_channels(a, b, c, d, amplitude_thresholds, Distance, dt)

##    # Update the Tor labels with the calculated Tor values and No_of_Tor
##    for i, label in enumerate(tor_labels):
##        channel_name = f"Channel {chr(65 + i)}"
##        no_of_tor = No_of_Tor_list[i]
##        tor_values = ", ".join([f"Tor_{j+1} = {value:.2f}" for j, value in enumerate(Tor_list[i])])
##        #label.config(text=f"{channel_name}   No_of_Tor: {no_of_tor}, {tor_values}")
##        label.config(text=f"{channel_name}\nNo_of_Tor: {no_of_tor}\n{tor_values}\n")

    for i, label in enumerate(tor_labels):
        channel_name = f"Channel {chr(65 + i)}"
        no_of_tor = No_of_Tor_list[i]
        tor_values = "\n".join([f"Tor_{j+1} = {value:.2f}" for j, value in enumerate(Tor_list[i])])
                # Define a fixed-width box format
        box_format = f"{'-'*15}\n{' '*2}{channel_name}\n{'-'*15}\n{' '*2}No_of_Tor: {no_of_tor}\n{'-'*15}\n{tor_values}\n{'-'*15}"

        label.config(text=box_format)

   
def on_button_click():
    recording()
    q.after(100,testing)
    q.after(7000,recorder)
    

def save_data_to_csv_with_dialog(aa, bb, cc, dd):
    current_time = datetime.now()
    date_str = current_time.strftime("%Y-%m-%d")
    time_str = current_time.strftime("%H:%M:%S")

    result = simpledialog.askstring("Input", "Enter a file name:")

    if result:
        # Construct the full file path
        file_path = f"E:/xyma/data_directory/{result}.csv"

        with open(file_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Time & Date", "ChannelA", "ChannelB", "ChannelC", "ChannelD"])
            for i, j, k, l in zip(aa, bb, cc, dd):
                csv_writer.writerow([f"{time_str} {date_str}", i, j, k, l])
        print("Data saved to", file_path)
    else:
        print("No file name provided.")
       
def show_save_success_message():
    messagebox.showinfo("File Saved", "File saved successfully!")

def savebutton():
    save_data_to_csv_with_dialog(aa,bb,cc,dd)
    print("file saved sucessfully")
    show_save_success_message()

def openbutton():
    q.destroy()
    global window2
    # Create a new tkinter window
    window2 = Tk()
    window2.title('Saved Data')
    window2.config(bg="#0A0A2A")
    window2.geometry("{}x{}".format(screen_width, screen_height))

    #fig, axes = plt.subplots(4, 1, figsize=(10, 6))
    openfig, axes = plt.subplots(4, 1, figsize=(fig_width, fig_height))

    canvas = FigureCanvasTkAgg(openfig, master=window2)
    canvas_widget = canvas.get_tk_widget()
    canvas_x = (screen_width - canvas_widget.winfo_reqwidth()) // 2
    canvas_y = (screen_height - canvas_widget.winfo_reqheight()) // 2
    canvas_widget.place(x=screen_width // 6.4, y=screen_height // 10.6)
   
    def on_combobox_select(event):
        #global openfig
        scaling_factor = screen
        fig_width = int(screen_width * scaling_factor)
        openfig, axes = plt.subplots(4, 1, figsize=(fig_width, fig_height))

        selected_value = combo.get()
        if selected_value:
            for ax in axes:
                 ax.cla()
            # Construct the full file path
            file_path = f"E:/xyma/data_directory/{selected_value}.csv"
           
            # Load data from the selected CSV file
            data = pd.read_csv(file_path)
           
            amplitude_thresholds = [Amplitude_Threshold1, Amplitude_Threshold2, Amplitude_Threshold3, Amplitude_Threshold4]
            # Plot the data and find Tor
            peak_indices = [peak_detection(channel, threshold) for channel, threshold in zip([data['ChannelA'],data['ChannelB'],data['ChannelC'],data['ChannelD']], amplitude_thresholds)]
            common_colors = ['red', 'green', 'blue', 'orange']
            plot_colors = ['purple','blue','green','pink']
            subplot = [data['ChannelA'],data['ChannelB'],data['ChannelC'],data['ChannelD']]
            length = len(data['ChannelA'])
            xtime = length/200000
            x=np.linspace(0,int(xtime),length)
           
            for i in range(len(axes)):
                axes[i].plot(x,subplot[i],color=plot_colors[i])
                axes[i].plot(x[peak_indices[i]],subplot[i][peak_indices[i]], "ro", label=f'Channel {i + 1} Peaks', color=common_colors[i])
                axes[i].set_ylim(-5,5)
                axes[i].set_xlabel('Time (S)')
                axes[i].set_ylabel('Ampilitude (V)')
                #axes[i].legend()
            plt.subplots_adjust(hspace=0.5)

            canvas = FigureCanvasTkAgg(openfig, master=window2)
            canvas_widget = canvas.get_tk_widget()
            canvas_x = (screen_width - canvas_widget.winfo_reqwidth()) // 2
            canvas_y = (screen_height - canvas_widget.winfo_reqheight()) // 2
            canvas_widget.place(x=screen_width // 6.4, y=screen_height // 10.6)
            # canvas_widget.place(x=0 , y=0)

            

           
        else:
            print("No file selected")
   

   
    directory_path = r'E:\xyma\data_directory'
    excel_files = [os.path.splitext(file)[0] for file in os.listdir(directory_path) if file.endswith('.csv')]

    lbel_name = Label(window2, text="Select the saved file", fg="white", bg="#0A0A2A")
    lbel_name.configure(font=("Calibri", 15))
    lbel_name.pack(padx=0, pady=10)
   
    combo = ttk.Combobox(window2, values=excel_files, width=50, height=50, state="readonly")
    combo.set("Select a file")
    combo.configure(font=("Calibri", 11))
    combo.pack()
    combo.bind("<<ComboboxSelected>>", on_combobox_select)

    back_button = Button(window2, text="Back",bg="green",fg="white",width=10, command=dashboard_window)
    back_button.configure(font=("Calibri", 11))
    back_button.place(x=20,y=screen_height-250)
   
    window2.mainloop()





def find_tor_and_no_of_tor_for_all_channels(a, b, c, d, amplitude_thresholds, distance, dt):
    Tor_list = []
    No_of_Tor_list = []

    drdo_img = Image.open("E:/xyma/Image/drdo1.png")
    drdo_img = ImageTk.PhotoImage(drdo_img)
    lst_size = drdo_img.height()


    lbt = Listbox(q, font=("Verdana", 10), height= img_height//3, width=screen_width //140,bg="#0A0A2A",fg="white")
    lbt.place(x=screen_width-200, y=lst_size + 50)


    for i, channel_data in enumerate([a, b, c, d]):
        peaks, _ = find_peaks(channel_data, height=amplitude_thresholds[i], distance=distance)
        peaks = peaks.tolist()
       
        Tor = [round((peak * dt) / 1000, 2) for peak in peaks]  
        No_of_Tor = len(Tor)
        lbt.insert(END, f"No_of_Tor for Channel {chr(65 + i)} = {No_of_Tor}\n")
    

        for j, value in enumerate(Tor):
            # print(f"Tor {j + 1} = {value}")
            lbt.insert(END, f"Tor {j + 1} = {value} sec")
         
     
        Tor_list.append(Tor)
        No_of_Tor_list.append(No_of_Tor)
   
    return Tor_list, No_of_Tor_list



def new_win():
    global q
    global img_height
  
    q =Tk()
    q.title('DAQ')
    q.config(bg="#0A0A2A")
    q.geometry("{}x{}".format(screen_width, screen_height))
    
    global tor_labels

    tor_labels = [Label(q, text="", fg="white", bg="#0A0A2A") for _ in range(4)]
    tor_labels_config = {"font": ("Calibri", 8)}

 
    global label_y
    label_y = -(screen_width // 2.555)
    channel_spacing = screen_height//5.33  # Adjust this value as needed

    # for i, label in enumerate(tor_labels):
    #     channel_name = f"Channel {chr(65 + i)}"
    #     label_x = screen_width - 200
    #     label.config(text=channel_name, font=("Calibri", 8))
    #     label.place(x=label_x, y=label_y)
    #     label_y += channel_spacing  # Move to the next channel

    # for i, label in enumerate(tor_labels):
    #     label_x = screen_width - 150
    #     label.place(x=label_x, y=label_y)
    #     label_y += channel_spacing
  

    openfig1, axes = plt.subplots(4, 1, figsize=(fig_width, fig_height))
    canvas = FigureCanvasTkAgg(openfig1, master=q)
    canvas_widget = canvas.get_tk_widget()
    canvas_x = (screen_width - canvas_widget.winfo_reqwidth()) // 4
    canvas_y = (screen_height - canvas_widget.winfo_reqheight()) // 2
    canvas_widget.place(x=screen_width // 6.4, y=screen_height // 10.6)

   
    xyma_img1 = Image.open("E:/xyma/Image/xyma_final.png")
    xyma_img1=ImageTk.PhotoImage(xyma_img1)
    drdo_img = Image.open("E:/xyma/Image/drdo_final.png")
    drdo_img = ImageTk.PhotoImage(drdo_img)

    img_height = xyma_img1.height()
    
    drdo_image = drdo_img.height()
    


#© 2023 XYMA Analytics Pvt Ltd,IIT Madras Research Park,Chennai,600113
    name = Label(q,text="DATA ACQUISITION SYSTEM",fg="white",bg="#0A0A2A")
    name.configure(font=("Calibri", 19))
    name.pack()

    img_label = Label(q, image=xyma_img1, bg="#0A0A2A")
    img_label.place(x=10,y=10)

    Drdo_img = Label(q,image=drdo_img,bg="#0A0A2A")
    Drdo_img.place(x=screen_width-120,y=10)

    a=img_height +30
    bt1_w = screen_height//10
    btn2_w = screen_height//26

    btn1 = CTkButton(master=q, text="Trigger", height=btn2_w, corner_radius=5, width=bt1_w, command=on_button_click)
    btn1.configure(font=("Calibri", 14))
    btn1.place(x=10, y=a)
   
    btn2 = CTkButton(master=q, text=f"Time", height=btn2_w, corner_radius=5, width=bt1_w, command=timeButton)
    btn2.configure(font=("Calibri", 14))
    btn2.place(x=10, y=a+100)

    btn3 = CTkButton(master=q, text="Save", height=btn2_w, corner_radius=5, width=bt1_w, command=savebutton)
    btn3.configure(font=("Calibri", 14))
    btn3.place(x=10, y=a+200)


    btn5 = CTkButton(master=q, text="Open", height=btn2_w, corner_radius=5, width=bt1_w, command=openbutton)
    btn5.configure(font=("Calibri", 14))
    btn5.place(x=10, y=a+300)
    q.mainloop()

def dashboard_window():
    window2.destroy()
    new_win()

Frame(main, width=screen_width - 200, height=screen_height - 200, bg='#0A0A2A').place(x=0,y=0)
image_label = Label(main, image=xyma_img, bg="#0A0A2A")
image_label.place(x=(screen_width - xyma_img.width() - 200) // 2, y=((screen_height - xyma_img.height()) - 300) // 2)

label2=Label(main, text='Loading...', fg='white', bg='#0A0A2A')
label2.configure(font=("Calibri", 11))
label2.place(x=0, y=(screen_height-360))

for i in range(2): #5loops
     l1=Label(main, image=image_a, border=0, relief=SUNKEN).place(x=(screen_width - xyma_img.width() - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l2=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 225 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l3=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 195 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l4=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 165 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     main.update_idletasks()
     time.sleep(0.5)

     l1=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - xyma_img.width() - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l2=Label(main, image=image_a, border=0, relief=SUNKEN).place(x=(screen_width - 225 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l3=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 195 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l4=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 165 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     main.update_idletasks()
     time.sleep(0.5)

     l1=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - xyma_img.width() - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l2=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 225- 1) // 2, y=((screen_height - 50) - 1) // 2)
     l3=Label(main, image=image_a, border=0, relief=SUNKEN).place(x=(screen_width - 195 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l4=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 165 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     main.update_idletasks()
     time.sleep(0.5)

     l1=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - xyma_img.width() - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l2=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 225 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l3=Label(main, image=image_b, border=0, relief=SUNKEN).place(x=(screen_width - 195 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     l4=Label(main, image=image_a, border=0, relief=SUNKEN).place(x=(screen_width - 165 - 1) // 2, y=((screen_height - 50) - 1) // 2)
     main.update_idletasks()
     time.sleep(0.5)

main.destroy()
new_win()
main.mainloop()
