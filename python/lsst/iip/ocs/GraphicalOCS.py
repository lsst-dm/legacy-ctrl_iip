import pygtk
import gtk
import subprocess


class GraphicalOCS:

    def __init__(self):
        self.command_list = { "standby":"./commands/standby_commander",
                              "disable":"./commands/disable_commander",
                              "enable":"./commands/enable_commander",
                              "exit":"./commands/exit_commander" }
        self.event_list = { "next_visit":"./commands/next_visit",
                              "start_int":"./commands/start_integration",
                              "readout":"./commands/readout" }
        self.device_param = None

        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title("Command and Event Publisher")
        self.win.set_size_request(860,950)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.connect("delete_event", self.delete_event)
        self.win.connect("destroy", gtk.main_quit)

        self.win.set_border_width(10)

        ## Overall VBox
        overall_vbox = gtk.VBox(False, 5)

        ## VBox for top label and HBox
        upper_vbox = gtk.VBox(False, 3)

        command_label = gtk.Label("Device Commands")
        command_label.set_justify(gtk.JUSTIFY_CENTER)
        command_label.set_use_markup(gtk.TRUE)
        command_label.set_markup('<span size="38000"><b>Device Commands</b></span>')

        ## HBox for upper button sets
        upper_hbox = gtk.HBox(False, 4)

        ## Three vboxes...one for command radiobuttons, one for device buttons, and one for send button
        command_vbox = gtk.VBox(False, 10)
        device_vbox = gtk.VBox(False, 10)
        send_vbox = gtk.VBox(False, 10)

        # command_vbox contents...
        cmds_label = gtk.Label("Choose Command")
        cmds_label.set_use_markup(gtk.TRUE)
        cmds_label.set_markup('<span size="16000"><b>Choose Command</b></span>')
        separator1 = gtk.HSeparator()
        self.standby = gtk.RadioButton(None, "Standby")
        self.standby.connect("toggled", self.run_standby_command, None)
        self.disable = gtk.RadioButton(self.standby, "Disable")
        self.disable.connect("toggled", self.run_disable_command, None)
        self.enable = gtk.RadioButton(self.standby, "Enable")
        self.enable.connect("toggled", self.run_enable_command, None)
        self.exit = gtk.RadioButton(self.standby, "Exit")
        self.exit.connect("toggled", self.run_exit_command, None)

        command_vbox.set_border_width(10)
        command_vbox.pack_start(cmds_label, True, True, 4)
        cmds_label.show()

        command_vbox.pack_start(separator1, True, True, 4)
        separator1.show()

        command_vbox.pack_start(self.standby, True, True, 4)
        self.standby.show()

        command_vbox.pack_start(self.disable, True, True, 4)
        self.disable.show()

        command_vbox.pack_start(self.enable, True, True, 4)
        self.enable.show()

        command_vbox.pack_start(self.exit, True, True, 4)
        self.exit.show()

        command_vbox.show()

        # device_vbox contents...
        dev_label = gtk.Label("Select Device")
        dev_label.set_use_markup(gtk.TRUE)
        dev_label.set_markup('<span size="16000"><b>Select Device</b></span>')
        separator2 = gtk.HSeparator()
        self.ar = gtk.RadioButton(None, "Archive")
        self.ar.connect("toggled", self.run_ar_command, None)
        self.pp = gtk.RadioButton(self.ar, "Prompt Process")
        self.pp.connect("toggled", self.run_pp_command, None)
        self.cu = gtk.RadioButton(self.ar, "Catch Up")
        self.cu.connect("toggled", self.run_cu_command, None)

        device_vbox.set_border_width(10)
        device_vbox.pack_start(dev_label, True, True, 4)
        dev_label.show()

        device_vbox.pack_start(separator2, True, True, 6)
        separator2.show()

        device_vbox.pack_start(self.ar, True, True, 7)
        self.ar.show()

        device_vbox.pack_start(self.pp, True, True, 7)
        self.pp.show()

        device_vbox.pack_start(self.cu, True, True, 7)
        self.cu.show()

        device_vbox.show()

        # send_vbox contents...
        send_label = gtk.Label("Send Command")
        send_label.set_use_markup(gtk.TRUE)
        send_label.set_markup('<span size="16000"><b>Send Command</b></span>')
        separator3 = gtk.HSeparator()
        self.send_button = gtk.Button("Send Command")
        self.send_button.connect("clicked", self.process_send_command, None)

        send_vbox.set_border_width(10)
        #send_vbox.pack_start(send_label, True, True, 0)
        #send_label.show()

        #send_vbox.pack_start(separator3, True, True, 0)
        #separator3.show()

        send_vbox.pack_start(self.send_button, True, True, 90)
        self.send_button.show()

        send_vbox.show()

        upper_hbox.pack_start(command_vbox, True, True, 4)
        upper_hbox.pack_start(device_vbox, True, True, 4)
        upper_hbox.pack_start(send_vbox, True, True, 4)
        upper_hbox.show()

        upper_vbox.set_border_width(10)
        upper_vbox.pack_start(command_label, True, True, 4)
        command_label.show()
        upper_vbox.pack_start(upper_hbox, True, True, 4)
        separator4 = gtk.HSeparator()
        upper_vbox.pack_start(separator4, True, True, 4)
        separator4.show()
        upper_vbox.show()
         

        middle_vbox = gtk.VBox(False, 3)
        middle_hbox = gtk.HBox(False, 3)
        event_choices_box = gtk.VBox(True, 3)

        event_label = gtk.Label()
        event_label.set_use_markup(gtk.TRUE)
        event_label.set_markup('<span size="38000"><b>Event Commands</b></span>')

        events_label = gtk.Label("Choose event type")
        events_label.set_use_markup(gtk.TRUE)
        events_label.set_markup('<span size="16000"><b>Choose Event Type</b></span>')
        event_choices_box.pack_start(events_label, True, True, 5)
        events_label.show()
        separator5 = gtk.HSeparator()
        event_choices_box.pack_start(separator5, True, True, 5)
        separator5.show()
        self.next_visit = gtk.RadioButton(None, "Next Visit")
        #self.next_visit.set_active(True)
        self.next_visit.connect("toggled", self.select_next_visit)
        event_choices_box.pack_start(self.next_visit, True, True, 5)
        self.next_visit.show()
        self.start_int = gtk.RadioButton(self.next_visit, "Start Integration")
        self.start_int.connect("toggled", self.select_start_int)
        event_choices_box.pack_start(self.start_int, True, True, 5)
        self.start_int.show()
        self.readout = gtk.RadioButton(self.next_visit, "Readout")
        self.readout.connect("toggled", self.select_readout)
        event_choices_box.pack_start(self.readout, True, True, 5)
        self.readout.show()
        event_choices_box.show()

        entry_box = gtk.VBox(True, 20)

        # Add text inputs
        visit_id = gtk.Label("Visit ID")
        entry_box.pack_start(visit_id, True, True, 5)
        visit_id.show()
        self.visit_entry = gtk.Entry(max=10)
        entry_box.pack_start( self.visit_entry, True, True, 5)
        self.visit_entry.show()
        image_id = gtk.Label("Image ID")
        entry_box.pack_start(image_id, True, True, 5)
        image_id.show()
        self.image_entry = gtk.Entry(max=10) 
        self.image_entry.set_max_length(10) 
        entry_box.pack_start(self.image_entry, True, True, 5)
        self.image_entry.show()
        self.image_entry.set_sensitive(False)
        entry_box.show()

        event_send_box = gtk.VBox(True, 10)

        self.send_event_button = gtk.Button("Send Event")
        self.send_event_button.connect("clicked", self.process_event_send_command, None)
        self.send_event_button.show()
        event_send_box.pack_start(self.send_event_button, True, True, 80)
        event_send_box.show()

        middle_hbox.pack_start(event_choices_box, True, True, 5)
        middle_hbox.pack_start(entry_box, True, True, 5)
        middle_hbox.pack_start(event_send_box, True, True, 10)

        middle_vbox.pack_start(event_label, True, True, 10)
        middle_vbox.pack_start(middle_hbox, True, True, 10)
        
        event_label.show()
        middle_hbox.show()
        middle_vbox.show()

        lower_hbox = gtk.HBox(True, 10)
        lower_hbox.set_size_request(700, 200)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #sw.set_size_request(100, 200)

        # Big Text View
        self.textview = gtk.TextView()
        #self.textview.set_size_request(100, 200)
        self.textbuffer = self.textview.get_buffer()
        self.r_tag = self.textbuffer.create_tag( "colored", foreground="#FF0000", background="#FFFFFF")
        sw.add(self.textview)
        sw.show()
        self.textview.show()
        lower_hbox.pack_start(sw, True, True, 5)
        lower_hbox.show()


        overall_vbox.pack_start(upper_vbox, True, True, 4)
        overall_vbox.pack_start(middle_vbox, True, True, 4)
        overall_vbox.pack_start(lower_hbox, True, True, 4)

         
        overall_vbox.show()
        self.win.add(overall_vbox)
        self.win.show()


    def run_standby_command(self, widget, data=None):
        pass

    def run_disable_command(self, widget, data=None):
        pass

    def run_enable_command(self, widget, data=None):
        pass

    def run_exit_command(self, widget, data=None):
        pass

    def run_ar_command(self, widget, data=None):
        pass

    def run_pp_command(self, widget, data=None):
        pass

    def run_cu_command(self, widget, data=None):
        pass

    def process_send_command(self, widget, data=None):
        st_str = ""
        c_list = self.standby.get_group()
        dex = None
        for i in range (0, len(c_list)):
            if c_list[i].get_active():
                dex = i
                break

        if dex == None:
            print "Dex is none - cannot find active command button"
        else:
            if dex == 3:
                cmd = "standby" #self.command_list["standby"]
                st_str = "Standby"
            elif dex == 2:
                cmd = "disable" #self.command_list["disable"]
                st_str = "Disable"
            elif dex == 1:
                cmd = "enable" #self.command_list["enable"]
                st_str = "Enable"
            else:
                cmd = "abort" #self.command_list["exit"]
                st_str = "Exit"
        

        r_list = self.ar.get_group()
        dex = None
        for i in range (0, len(r_list)):
            if r_list[i].get_active():
                dex = i
                break

        if dex == None:
            print "Dex is none - cannot find active device button"
        else:
            if dex == 2:
                self.device_param = "archiver" #"Archiver"
            elif dex == 1:
                self.device_param = "processingcluster" #"PromptProccesor"
            else:
                self.device_param = "catchuparchiver" #"CatchupArchiver"

        #command = cmd + " " + self.device_param
	command = "./commands/sacpp_" + self.device_param + "_" + cmd + "_commander 0"
	print "XXXXXXXX command: ", command
        status_str = "\nSending %s command to the %s device" % (st_str,self.device_param)
        cmd_str =  "\nShell command to be run is: %s\n" % command
        
        insert_point = self.textbuffer.get_end_iter()
        self.textbuffer.insert_with_tags(insert_point, status_str, self.r_tag)
        insert_point = self.textbuffer.get_end_iter()
        self.textbuffer.insert(insert_point, cmd_str)

        #veritek = os.system(cmd)
        veritek = subprocess.check_output(command, shell=True)
        insert_point = self.textbuffer.get_end_iter()
        self.textbuffer.insert(insert_point, veritek)


    def process_event_send_command(self, eidget, data=None):
        pass
        e_list = self.next_visit.get_group()
        dex = None
        data = None
        ev_str = None

        for i in range (0, len(e_list)):
            if e_list[i].get_active():
                dex = i
                break

        if dex == None:
            print "Dex is none - cannot find active device button"
        else:
            if dex == 2:
                cmd = self.event_list['next_visit'] 
                data = self.visit_entry.get_text()
                ev_str = "Next Visit"
            elif dex == 1:
                cmd = self.event_list['start_int'] 
                data = self.image_entry.get_text()
                ev_str = "Start Integration"
            else:
                cmd = self.event_list['readout'] 
                data = self.image_entry.get_text()
                ev_str = "Readout"

        command = cmd + " " + data
        #print "Event to be sent is: %s with Image ID of" % command
        if dex == 3:
            status_str = "\nSending %s Event with Visit ID: %s" % (ev_str,data)
        else:
            status_str = "\nSending %s Event with Image ID: %s" % (ev_str,data)
        cmd_str =  "\nShell command to be run is: %s\n" % command
        
        insert_point = self.textbuffer.get_end_iter()
        self.textbuffer.insert(insert_point, status_str)
        insert_point = self.textbuffer.get_end_iter()
        self.textbuffer.insert(insert_point, cmd_str)

        #veritek = os.system(cmd)
        veritek = subprocess.check_output(command, shell=True)

        insert_point = self.textbuffer.get_end_iter()
        self.textbuffer.insert(insert_point, veritek)




    def select_next_visit(self, widget, data=None):
        #Gray out image_id
        self.image_entry.set_sensitive(False)
        #Ungray visit_id 
        self.visit_entry.set_sensitive(True)

    def select_readout(self, widget, data=None):
        #Gray out visit_id
        self.visit_entry.set_sensitive(False)
        #Ungray image_id 
        self.image_entry.set_sensitive(True)

    def select_start_int(self, widget, data=None):
        #Gray out visit_id
        self.visit_entry.set_sensitive(False)
        #Ungray image_id 
        self.image_entry.set_sensitive(True)

    def delete_event(self, widget, event, data=None):
        return False

    def main(self):
        gtk.main()

if __name__=="__main__":
    gocs = GraphicalOCS()
    gocs.main()


