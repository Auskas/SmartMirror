#! python3
# wave_widget.py

from tkinter import *
import wave
import threading
import alsaaudio

class WaveWidget:

    def __init__(self, window, status=False):
        self.window = window
        self.status = status
        self.frames = [PhotoImage(file='wave.gif',format = 'gif -index %i' %(i)) for i in range(1,40)]
        self.waveLbl = Label(self.window, bg='black', bd=0)
        self.waveLbl.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.device = alsaaudio.PCM(device='default')
        self.file = wave.open('siri.wav', 'rb')
        self.wavegif()

    def wavegif(self, flag=False):
        def update(ind):
            frame = self.frames[ind]
            ind += 1
            if ind == len(self.frames) - 1:
                self.waveLbl.after(10, self.wavegif, flag)
            else:
                self.waveLbl.configure(image=frame)
                self.waveLbl.after(100, update, ind)
        if self.status:
            if flag == False:
                flag = True
                playwavThread = threading.Thread(target=self.play)
                playwavThread.start()
            ind = 1
            update(ind)
        else:
            self.waveLbl.configure(image='')
            self.waveLbl.after(1000, self.wavegif)

    def change_status(self):
        if self.status == False:
            self.status = True
        else:
            self.status = False

    def play(self):
        self.file = wave.open('siri.wav', 'rb')
        self.device.setchannels(self.file.getnchannels())
        self.device.setrate(self.file.getframerate())
        # 8bit is unsigned in wav files
        if self.file.getsampwidth() == 1:
            self.device.setformat(alsaaudio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif self.file.getsampwidth() == 2:
            self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif self.file.getsampwidth() == 3:
            self.device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
        elif self.file.getsampwidth() == 4:
            self.device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')   
        periodsize = self.file.getframerate() // 8
        self.device.setperiodsize(periodsize)
        data = self.file.readframes(periodsize)
        while data:
            # Read data from stdin
            self.device.write(data)
            data = self.file.readframes(periodsize)  
   
if __name__ == '__main__':
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    #window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = WaveWidget(window, True)
    window.mainloop()
