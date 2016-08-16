#!/usr/bin/env python

import Tkinter as tk
from PIL import ImageTk, Image

import fingerpi
import serial
import serial.tools.list_ports as prts

class App:
    def __init__(self, master, img = './demo.png', *args, **kwargs):
        # tk.Frame.__init__(self, *args, **kwargs)
        self.master = master

        ##########################################################
        ## Column 0
        img_rowspan = 13
        pos = (0,0)
        # Image
        self.attach_image(img,
                          rowspan = img_rowspan,
                          pos = pos)

        # Button:
        self.button_save_image = tk.Button(self.master, text = "Save Image to File", callback=callback_save_image)
        self.button_save_image.grid(column = 0, row = img_rowspan+pos[1])

        self.string_information = tk.StringVar()
        self.string_information.set('This is a very long string ...')

        self.label_information = tk.Label(self.master, textvariable = self.string_information)
        self.label_information.grid(column = 1, row=img_rowspan+pos[1], columnspan = 2)

        
        ##########################################################
        ## Column 1
        # label_ports = tk.Label(self.master, text = 'Serial Port:')
        #label_ports.grid(column = 1, row = 0, sticky = tk.E)

        # label_bauds = tk.Label(self.master, text = 'Baudrate:')
        # label_bauds.grid(column = 1, row = 1, sticky = tk.E)

        self.OPTIONS_PORT = [x[0] for x in prts.comports()]
        self.var_port = tk.StringVar(self.master)
        self.var_port.set('Serial Port')
        self.var_port.trace('w', self.callback_port)
        self.list_ports = apply(tk.OptionMenu,
                           (self.master, self.var_port) + tuple(self.OPTIONS_PORT))
        self.list_ports.grid(column = 1, row = 0, sticky = tk.W+tk.E, columnspan = 2)


        self.OPTIONS_BAUD = serial.Serial.BAUDRATES
        self.OPTIONS_BAUD = self.OPTIONS_BAUD[
            self.OPTIONS_BAUD.index(9600):self.OPTIONS_BAUD.index(115200)+1]
        self.var_baud = tk.StringVar(self.master)
        self.var_baud.set('Baudrate')
        self.var_baud.trace('w', self.callback_baud)
        self.list_bauds = apply(tk.OptionMenu,
                           (self.master, self.var_baud) + tuple(self.OPTIONS_BAUD))
        self.list_bauds.grid(column = 1, row = 1, sticky = tk.W+tk.E, columnspan = 2)

        
        self.button_open = tk.Button(self.master, text = 'Open', callback=callback_open)
        self.button_open.grid(column = 1, row = 2, sticky = tk.E + tk.W)

        self.label_ID = tk.Label(self.master, text = 'ID:')
        self.label_ID.grid(column = 1, row = 3, sticky = tk.E)

        self.button_enroll = tk.Button(self.master, text = 'Enroll', callback=callback_enroll)
        self.button_enroll.grid(column = 1, row = 4, sticky = tk.E + tk.W)

        self.button_verify = tk.Button(self.master, text = 'Verify (1:1)', callback=callback_verify)
        self.button_verify.grid(column = 1, row = 5, sticky = tk.E + tk.W)

        self.button_identify = tk.Button(self.master, text = 'Identify (1:N)', callback=callback_identify)
        self.button_identify.grid(column = 1, row = 6, sticky = tk.E + tk.W)

        self.button_verify_template = tk.Button(self.master, text = 'Verify Template', callback=callback_verify_template)
        self.button_verify_template.grid(column = 1, row = 7, sticky = tk.E + tk.W)

        self.button_identify_template = tk.Button(self.master, text = 'Identify Template', callback=callback_identity_template)
        self.button_identify_template.grid(column = 1, row = 8, sticky = tk.E + tk.W)

        self.button_ispressfinger = tk.Button(self.master, text = 'Is Press Finger', callback=callback_ispressfinger)
        self.button_ispressfinger.grid(column = 1, row = 9, sticky = tk.E + tk.W)

        self.button_get_image = tk.Button(self.master, text = 'Get Image', callback=callback_get_image)
        self.button_get_image.grid(column = 1, row = 10, sticky = tk.E + tk.W)

        self.button_get_raw_image = tk.Button(self.master, text = 'Get Raw Image', callback=callback_get_raw_image)
        self.button_get_raw_image.grid(column = 1, row = 11, sticky = tk.E + tk.W)

        self.button_cancel = tk.Button(self.master, text = 'Cancel', callback=callback_cancel)
        self.button_cancel.grid(column = 1, row = 12, sticky = tk.E + tk.W)

        self.button_get_live_image = tk.Button(self.master, text = 'Get Live Image', callback=callback_get_live_image)
        self.button_get_live_image.grid(column = 1, row = 12, sticky = tk.E + tk.W)

        
        ##########################################################
        ## Column 2
        # OPTIONS_PORT = [x[0] for x in prts.comports()]
        # var_port = tk.StringVar(self.master)
        # var_port.set(OPTIONS_PORT[0])
        # list_ports = apply(tk.OptionMenu,
        #                    (self.master, var_port) + tuple(OPTIONS_PORT))
        # list_ports.grid(column = 1, row = 0, sticky = tk.W+tk.E, rowspan = 2)


        # OPTIONS_BAUD = serial.Serial.BAUDRATES
        # OPTIONS_BAUD = OPTIONS_BAUD[
        #     OPTIONS_BAUD.index(9600):OPTIONS_BAUD.index(115200)+1]
        # var_baud = tk.StringVar(self.master)
        # var_baud.set(OPTIONS_BAUD[0])
        # list_bauds = apply(tk.OptionMenu,
        #                    (self.master, var_baud) + tuple(OPTIONS_BAUD))
        # list_bauds.grid(column = 1, row = 1, sticky = tk.W+tk.E, rowspan = 2)
        
        
        self.button_close = tk.Button(self.master, text = 'Close', callback=callback_close)
        self.button_close.grid(column = 2, row = 2, sticky = tk.E + tk.W)

        self.scale_ID = tk.Spinbox(self.master, from_ = 0, to=199)
        self.scale_ID.grid(column = 2, row = 3, sticky = tk.E + tk.W)

        
        self.button_get_user_count = tk.Button(self.master, text = 'Get User Count', callback=callback_get_user_count)
        self.button_get_user_count.grid(column = 2, row = 4, sticky = tk.E + tk.W)

        self.button_delete_id = tk.Button(self.master, text = 'Delete ID', callback=callback_delete_id)
        self.button_delete_id.grid(column = 2, row = 5, sticky = tk.E + tk.W)

        self.button_delete_all = tk.Button(self.master, text = 'Delete ALl', callback=callback_delete_all)
        self.button_delete_all.grid(column = 2, row = 6, sticky = tk.E + tk.W)

        self.button_get_template = tk.Button(self.master, text = 'Get Template', callback=callback_get_template)
        self.button_get_template.grid(column = 2, row = 7, sticky = tk.E + tk.W)

        self.button_set_template = tk.Button(self.master, text = 'Set Template', callback=callback_set_template)
        self.button_set_template.grid(column = 2, row = 8, sticky = tk.E + tk.W)

        self.button_get_database = tk.Button(self.master, text = 'Get Database', callback=callback_get_database)
        self.button_get_database.grid(column = 2, row = 9, sticky = tk.E + tk.W)

        self.button_set_database = tk.Button(self.master, text = 'Set Database', callback=callback_set_database)
        self.button_set_database.grid(column = 2, row = 10, sticky = tk.E + tk.W)

        self.button_firmware_upgrade = tk.Button(self.master, text = 'Firmware Upgrade', callback=callback_firmware_upgrade)
        self.button_firmware_upgrade.grid(column = 2, row = 11, sticky = tk.E + tk.W)

        self.button_iso_upgrade = tk.Button(self.master, text = 'ISO Upgrade', callback=callback_iso_upgrade)
        self.button_iso_upgrade.grid(column = 2, row = 12, sticky = tk.E + tk.W)

        
        ### Settings
        self.change_states(tk.DISABLED)
        self.fp = None
        self.open = False

    def attach_image(self, img, rowspan = 10, pos = (0,0)):
        self.img_fp = ImageTk.PhotoImage(file = img)# Image.open(img))
        self.img_fp_panel = tk.Label(self.master)
        self.img_fp_panel.image = self.img_fp
        self.img_fp_panel.configure(image = self.img_fp)
        self.img_fp_panel.grid(column = pos[0], row = pos[1],
                               rowspan = rowspan,
                               sticky = tk.W+tk.E+tk.S+tk.N)

    def change_states(self, state):
        # self.list_ports.grid(column = 1, row = 0, sticky = tk.W+tk.E, columnspan = 2)
        list_of_stuff = [
        self.list_bauds,
        self.button_open,
        self.label_ID,
        self.button_enroll,
        self.button_verify,
        self.button_identify,
        self.button_verify_template,
        self.button_identify_template,
        self.button_ispressfinger,
        self.button_get_image,
        self.button_get_raw_image,
        self.button_cancel,
        self.button_get_live_image,

        self.button_close,
        self.scale_ID,
        self.button_get_user_count,
        self.button_delete_id,
        self.button_delete_all,
        self.button_get_template,
        self.button_set_template,
        self.button_get_database,
        self.button_set_database,
        self.button_firmware_upgrade,
        self.button_iso_upgrade,
        ]

        for thing in list_of_stuff:
            thing.config(state=state)

    def callback_port(self, *args):
        self.port = self.var_port.get()
        print 'Port set to:', self.port
        self.list_bauds.config(state='normal')
        if self.open:
            self.fp.ChangeBaudrate(self.port)

    def callback_baud(self, *args):
        self.baudrate = self.var_baud.get()
        print 'Baudrate set to:', self.baudrate

        # Attempt to open the port:
        self.fp = fingerpi.FingerPi(port = self.port, baudrate = self.baudrate)
        self.button_open.config(state='normal')

    def callback_open(self, *args):
        response = self.fp.Open(extra_info = True, check_baudrate = True)
        self.open = True
        self.var_baud.set(response[0]['Parameter'])

    def callback_enroll(self, *args):
        response = self.fp.EnrollStart(self.scale_ID.get())
        response = self.fp.CaptureFinger(best_image = True)
        response = self.fp.Enroll1()

        response = self.fp.IsPressFinger()
        response = self.fp.CaptureFinger(best_image = True)
        response = self.fp.Enroll2()

        response = self.fp.IsPressFinger()
        response = self.fp.CaptureFinger(best_image = True)
        response = self.fp.Enroll3()

    def callback_verify(self, *args):
        response = self.fp.CaptureFinger(best_image = False)
        response = self.fp.Verify(self.scale_ID.get())

    def callback_identify(self):
        response = self.fp.CaptureFinger(best_image = False)
        response = self.fp.Identify()

"""
    self.button_verify_template = tk.Button(self.master, text = 'Verify Template', callback=callback_verify_template)
    self.button_verify_template.grid(column = 1, row = 7, sticky = tk.E + tk.W)

    self.button_identify_template = tk.Button(self.master, text = 'Identify Template', callback=callback_identity_template)
    self.button_identify_template.grid(column = 1, row = 8, sticky = tk.E + tk.W)

    self.button_ispressfinger = tk.Button(self.master, text = 'Is Press Finger', callback=callback_ispressfinger)
    self.button_ispressfinger.grid(column = 1, row = 9, sticky = tk.E + tk.W)

    self.button_get_image = tk.Button(self.master, text = 'Get Image', callback=callback_get_image)
    self.button_get_image.grid(column = 1, row = 10, sticky = tk.E + tk.W)

    self.button_get_raw_image = tk.Button(self.master, text = 'Get Raw Image', callback=callback_get_raw_image)
    self.button_get_raw_image.grid(column = 1, row = 11, sticky = tk.E + tk.W)

    self.button_cancel = tk.Button(self.master, text = 'Cancel', callback=callback_cancel)
    self.button_cancel.grid(column = 1, row = 12, sticky = tk.E + tk.W)

    self.button_get_live_image = tk.Button(self.master, text = 'Get Live Image', callback=callback_get_live_image)
"""
        


if __name__ == '__main__':
    root = tk.Tk()

    app = App(root, img = './demo.png')
    
    root.mainloop()
    root.destroy()
