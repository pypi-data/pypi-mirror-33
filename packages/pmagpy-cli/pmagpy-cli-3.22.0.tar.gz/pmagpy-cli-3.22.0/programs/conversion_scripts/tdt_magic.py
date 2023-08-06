#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
NAME
    tdt_magic.py

DESCRIPTION
    converts TDT formatted files to measurements format files

SYNTAX
    tdt_magic.py -WD <PATH>

INPUT:
    TDT formatted files with suffix .tdt

OUTPUT:
    combined measurement file saved in <PATH>


Log:
    Initial revision 4/24/2014
    some bug fix 06/12/2015
"""
from __future__ import print_function
from builtins import str
from builtins import range
import wx, sys, os
import pmagpy.new_builder as nb
import pmagpy.pmag as pmag

#===========================================
# GUI
#===========================================


class convert_tdt_files_to_MagIC(wx.Frame):
    """"""
    title = "Convert tdt files to MagIC format"

    def __init__(self,WD,noave=False):
        wx.Frame.__init__(self, None, wx.ID_ANY, self.title)
        self.panel = wx.Panel(self)
        self.max_files=10

        os.chdir(WD)
        self.WD=os.getcwd()+"/"
        self.noave=noave
        self.create_menu()
        self.InitUI()

    def InitUI(self):


        pnl = self.panel

        #---sizer infor ----

        TEXT1="Instructions:\n"
        TEXT2="1. Put all individual tdt files from the same location in one folder.\n"
        TEXT3="   Each tdt file file should end with '.tdt'\n"
        TEXT4="2. If there are more than one location use multiple folders. One folder for each location.\n"
        TEXT5="3. If the magnetization in in units are mA/m (as in the original TT program) volume is required to convert to moment.\n\n"
        TEXT6="For more information check the help menubar option.\n"

        TEXT7="(for support contact ron.shaar@mail.huji.ac.il)"

        TEXT=TEXT1+TEXT2+TEXT3+TEXT4+TEXT5+TEXT6+TEXT7
        bSizer_info = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.HORIZONTAL )
        bSizer_info.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_LEFT)

        #---sizer 0 ----
        TEXT="output file:"
        bSizer0 = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer0.Add(wx.StaticText(self.panel,label=TEXT),wx.ALIGN_LEFT)
        bSizer0.AddSpacer(5)
        self.output_file_path = wx.TextCtrl(self.panel, id=-1, size=(1000,25))
        #self.output_file_path.SetEditable(False)
        bSizer0.Add(self.output_file_path,wx.ALIGN_LEFT)
        self.output_file_path.SetValue(os.path.join(self.WD, "measurements.magic"))
        #---sizer 1 ----
        TEXT="\n choose a path\n with no spaces in name"
        bSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer1.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        bSizer1.AddSpacer(5)

        self.dir_paths = {}
        self.add_dir_buttons = {}
        self.bsizers = {}
        for i in range(self.max_files):
            self.dir_paths[i] = wx.TextCtrl(self.panel, id=-1, size=(100,25), style=wx.TE_READONLY)
            self.add_dir_buttons[i] = wx.Button(self.panel, id=-1, label='add',name='add_{}'.format(i))
            self.Bind(wx.EVT_BUTTON, self.on_add_dir_button, self.add_dir_buttons[i])
            self.bsizers[i] = wx.BoxSizer(wx.HORIZONTAL)
            self.bsizers[i].Add(wx.StaticText(pnl,label=('{}  '.format(i+1))), wx.ALIGN_LEFT)
            self.bsizers[i].Add(self.dir_paths[i], wx.ALIGN_LEFT)
            self.bsizers[i].Add(self.add_dir_buttons[i], wx.ALIGN_LEFT)
            bSizer1.Add(self.bsizers[i], wx.ALIGN_TOP)
            bSizer1.AddSpacer(5)


        #---sizer 1a ----

        TEXT="\n\nexperiment:"
        bSizer1a = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer1a.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        self.experiments_names=['Thellier','ATRM 6 positions','NLT']
        bSizer1a.AddSpacer(5)
        self.protocol_infos = {}
        for i in range(self.max_files):
            self.protocol_infos[i] = wx.ComboBox(self.panel, -1, self.experiments_names[0], size=(100,25), choices=self.experiments_names, style=wx.CB_DROPDOWN|wx.CB_READONLY)
            bSizer1a.Add(self.protocol_infos[i], wx.ALIGN_TOP)
            bSizer1a.AddSpacer(5)

        #---sizer 1b ----

        TEXT="\nBlab direction\n dec, inc: "
        bSizer1b = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer1b.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        bSizer1b.AddSpacer(5)
        self.file_info_Blab_dec = {}
        self.file_info_Blab_inc = {}
        self.bsizers_Blab = {}
        for i in range(self.max_files):
            self.file_info_Blab_dec[i] = wx.TextCtrl(self.panel, id=-1, size=(40,25))
            self.file_info_Blab_dec[i].SetValue('0')
            self.file_info_Blab_inc[i] = wx.TextCtrl(self.panel, id=-1, size=(40,25))
            self.file_info_Blab_inc[i].SetValue('90')
            self.bsizers_Blab[i] = wx.BoxSizer(wx.HORIZONTAL)
            self.bsizers_Blab[i].Add(self.file_info_Blab_dec[i],wx.ALIGN_LEFT)
            self.bsizers_Blab[i].Add(self.file_info_Blab_inc[i], wx.ALIGN_LEFT)
            bSizer1b.Add(self.bsizers_Blab[i], wx.ALIGN_TOP)
            bSizer1b.AddSpacer(5)

        #---sizer 1c ----

        TEXT="\nmoment\nunits:"
        bSizer1c = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer1c.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        self.moment_units_names=['mA/m','emu','Am^2']
        bSizer1c.AddSpacer(5)
        self.moment_units = {}
        for i in range(self.max_files):
            self.moment_units[i] = wx.ComboBox(self.panel, -1, self.moment_units_names[0], size=(80,25), choices=self.moment_units_names, style=wx.CB_DROPDOWN|wx.CB_READONLY)
            bSizer1c.Add(self.moment_units[i], wx.ALIGN_TOP)
            bSizer1c.AddSpacer(5)

        #---sizer 1d ----

        TEXT="\nvolume\n[cubic m]:"
        bSizer1d = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer1d.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        bSizer1d.AddSpacer(5)
        self.volumes = {}
        for i in range(self.max_files):
            self.volumes[i] = wx.TextCtrl(self.panel, id=-1, size=(80,25))
            self.volumes[i].SetValue('1.287555e-5')
            bSizer1d.Add(self.volumes[i], wx.ALIGN_TOP)
            bSizer1d.AddSpacer(5)


        #---sizer 1e ----

        TEXT="\nuser\nname:"
        bSizer1e = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer1e.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        bSizer1e.AddSpacer(5)
        self.file_info_users = {}
        for i in range(self.max_files):
            self.file_info_users[i] = wx.TextCtrl(self.panel, id=-1, size=(60,25))
            bSizer1e.Add(self.file_info_users[i], wx.ALIGN_TOP)
            bSizer1e.AddSpacer(5)

        #---sizer 2 ----


        TEXT="\nlocation\nname:"
        bSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer2.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        bSizer2.AddSpacer(5)
        self.file_locations = {}
        for i in range(self.max_files):
            self.file_locations[i] = wx.TextCtrl(self.panel, id=-1, size=(60,25))
            bSizer2.Add(self.file_locations[i], wx.ALIGN_TOP)
            bSizer2.AddSpacer(5)

##        #---sizer 3 ----
##
##        missing

        #---sizer 4 ----

        TEXT="\nsample-specimen\nnaming convention:"
        bSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer4.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        self.sample_naming_conventions=['sample=specimen','no. of terminate characters','charceter delimited']
        bSizer4.AddSpacer(5)
        self.sample_naming = {}
        self.sample_naming_char = {}
        self.bSizer4 = {}
        for i in range(self.max_files):
            self.sample_naming[i] = wx.ComboBox(self.panel, -1, self.sample_naming_conventions[0], size=(150,25), choices=self.sample_naming_conventions, style=wx.CB_DROPDOWN|wx.CB_READONLY)
            self.sample_naming_char[i] = wx.TextCtrl(self.panel, id=-1, size=(40,25))
            self.bSizer4[i] = wx.BoxSizer(wx.HORIZONTAL)
            self.bSizer4[i].Add(self.sample_naming[i], wx.ALIGN_LEFT)
            self.bSizer4[i].Add(self.sample_naming_char[i], wx.ALIGN_LEFT)
            bSizer4.Add(self.bSizer4[i], wx.ALIGN_TOP)

            bSizer4.AddSpacer(5)

        #---sizer 5 ----

        TEXT="\nsite-sample\nnaming convention:"
        bSizer5 = wx.StaticBoxSizer( wx.StaticBox( self.panel, wx.ID_ANY, "" ), wx.VERTICAL )
        bSizer5.Add(wx.StaticText(pnl,label=TEXT),wx.ALIGN_TOP)
        self.site_naming_conventions=['site=sample','no. of terminate characters','charceter delimited']
        bSizer5.AddSpacer(5)
        self.site_naming = {}
        self.site_naming_char = {}
        self.bSizer5 = {}
        for i in range(self.max_files):
            self.site_naming_char[i] = wx.TextCtrl(self.panel, id=-1, size=(40,25))
            self.site_naming[i] = wx.ComboBox(self.panel, -1, self.site_naming_conventions[0], size=(150,25), choices=self.site_naming_conventions, style=wx.CB_DROPDOWN|wx.CB_READONLY)
            self.bSizer5[i] = wx.BoxSizer(wx.HORIZONTAL)
            self.bSizer5[i].Add(self.site_naming[i])
            self.bSizer5[i].Add(self.site_naming_char[i], wx.ALIGN_LEFT)
            bSizer5.Add(self.bSizer5[i], wx.ALIGN_TOP)
            bSizer5.AddSpacer(5)

        #------------------

        self.okButton = wx.Button(self.panel, wx.ID_OK, "&OK")
        self.Bind(wx.EVT_BUTTON, self.on_okButton, self.okButton)

        self.cancelButton = wx.Button(self.panel, wx.ID_CANCEL, '&Cancel')
        self.Bind(wx.EVT_BUTTON, self.on_cancelButton, self.cancelButton)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        #hbox1.Add(self.add_file_button)
        #hbox1.Add(self.remove_file_button )

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.okButton)
        hbox2.Add(self.cancelButton )

        #------

        vbox=wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(1)
        hbox.Add(bSizer1, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)
        hbox.Add(bSizer1a, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)
        hbox.Add(bSizer1b, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)
        hbox.Add(bSizer1c, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)
        hbox.Add(bSizer1d, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)
        hbox.Add(bSizer1e, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)
        hbox.Add(bSizer2, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)
##        hbox.Add(bSizer3, flag=wx.ALIGN_LEFT)
##        hbox.AddSpacer(5)
        hbox.Add(bSizer4, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)
        hbox.Add(bSizer5, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(1)

        #-----

        vbox.AddSpacer(5)
        vbox.Add(bSizer_info,flag=wx.ALIGN_CENTER_HORIZONTAL)
        vbox.AddSpacer(2)
        vbox.Add(hbox)
        vbox.AddSpacer(5)
        vbox.Add(hbox1,flag=wx.ALIGN_CENTER_HORIZONTAL)
        #vbox.AddSpacer(20)
        vbox.AddSpacer(5)
        vbox.Add(bSizer0, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vbox.Add(hbox2,flag=wx.ALIGN_CENTER_HORIZONTAL)
        vbox.AddSpacer(5)

        self.panel.SetSizer(vbox)
        vbox.Fit(self)
        self.Show()
        self.Centre()

    def create_menu(self):
        """ Create menu
        """
        self.menubar = wx.MenuBar()

        menu_about = wx.Menu()
        menu_help = menu_about.Append(-1, "&Some notes", "")
        self.Bind(wx.EVT_MENU, self.on_menu_help, menu_help)

        self.menubar.Append(menu_about, "& Instructions")

        self.SetMenuBar(self.menubar)

    def on_menu_help (self,event):

        dia = message_box("Help")
        dia.Show()
        dia.Center()




    def on_add_dir_button(self,event):

        dlg = wx.DirDialog(
            None,message="choose directtory with tdt files",
            defaultPath ="./",
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            FILE = dlg.GetPath()
        else: return
        # fin=open(FILE,'r')
        button = event.GetEventObject()
        name=button.GetName()
        i=int((name).split("_")[-1])
        #print "The button's name is " + button.GetName()

        self.dir_paths[i].SetValue(FILE)


    def read_generic_file(self,path):
        Data={}
        Fin=open(path,'r')
        header=Fin.readline().strip('\n').split('\t')

        for line in Fin.readlines():
            tmp_data={}
            l=line.strip('\n').split('\t')
            if len(l)<len(header):
                continue
            else:
                for i in range(len(header)):
                    tmp_data[header[i]]=l[i]
                specimen=tmp_data['Specimen']
                if specimen not in list(Data.keys()):
                    Data[specimen]=[]
                # check dupliactes
                if len(Data[specimen]) >0:
                    if tmp_data['Treatment (aka field)']==Data[specimen][-1]['Treatment (aka field)']:
                        print("-W- WARNING: duplicate measurements specimen %s, Treatment %s. keeping onlt the last one"%(tmp_data['Specimen'],tmp_data['Treatment (aka field)']))
                        Data[specimen].pop()

                Data[specimen].append(tmp_data)
        Fin.close()
        return(Data)

    def on_okButton(self,event):


        DIRS_data={}

        for i in range(self.max_files):

            # read directiory path
            dir_path=""
            dir_path = self.dir_paths[i].GetValue()
            if dir_path!="":
                dir_name=str(dir_path.split("/")[-1])
                DIRS_data[dir_name]={}
                DIRS_data[dir_name]['path']=str(dir_path)
            else:
                continue

            # get experiment
            experiment = self.protocol_infos[i].GetValue()
            DIRS_data[dir_name]['experiment']=str(experiment)

            # get location
            user_name=""
            location_name = self.file_locations[i].GetValue()
            DIRS_data[dir_name]['location']=str(location_name)

            # get Blab direction
            labfield_DI=["0.","90."]
            labfield_DI[0] = self.file_info_Blab_dec[i].GetValue()
            labfield_DI[1] = self.file_info_Blab_inc[i].GetValue()
            DIRS_data[dir_name]['labfield_DI']=labfield_DI

            # get Moment units
            moment_units = self.moment_units[i].GetValue()
            DIRS_data[dir_name]['moment_units']=moment_units

            # get sample volume
            volume = self.volumes[i].GetValue()
            DIRS_data[dir_name]['volume']=volume

            # get User_name
            user_name=""
            user_name = self.file_info_users[i].GetValue()
            DIRS_data[dir_name]['user_name']=user_name


            # get sample-specimen naming convention

            sample_naming_convention=["",""]
            sample_naming_convention[0] = str(self.sample_naming[i].GetValue())
            sample_naming_convention[1] = str(self.sample_naming_char[i].GetValue())
            DIRS_data[dir_name]["sample_naming_convention"]=sample_naming_convention

            # get site-sample naming convention

            site_naming_convention=["",""]
            site_naming_convention[0] = str(self.site_naming[i].GetValue())
            site_naming_convention[1] = str(self.site_naming_char[i].GetValue())
            DIRS_data[dir_name]["site_naming_convention"]=site_naming_convention

        self.convert_2_magic(DIRS_data)



    def on_cancelButton(self,event):
        self.Destroy()

    def get_sample_name(self,specimen,sample_naming_convention):
        if sample_naming_convention[0]=="sample=specimen":
            sample=specimen
        elif sample_naming_convention[0]=="no. of terminate characters":
            n=int(sample_naming_convention[1])*-1
            sample=specimen[:n]
        elif sample_naming_convention[0]=="charceter delimited":
            d=sample_naming_convention[1]
            sample_splitted=specimen.split(d)
            if len(sample_splitted)==1:
                sample=sample_splitted[0]
            else:
                sample=d.join(sample_splitted[:-1])
        return sample

    def get_site_name(self,sample,site_naming_convention):
        if site_naming_convention[0]=="site=sample":
            site=sample
        elif site_naming_convention[0]=="no. of terminate characters":
            n=int(site_naming_convention[1])*-1
            site=sample[:n]
        elif site_naming_convention[0]=="charceter delimited":
            d=site_naming_convention[1]
            site_splitted=sample.split(d)
            if len(site_splitted)==1:
                site=site_splitted[0]
            else:
                site=d.join(site_splitted[:-1])
        return site




    #===========================================
    # Convert to MagIC format
    #===========================================



    def convert_2_magic(self,DIRS_data):
        #--------------------------------------
        # Read the files
        #
        # Database structure
        # Thellier_type experiment:
        #
        # 1) Each file contains the data one specimen
        # 2) First line is the header: "Thellier-tdt"
        # 3) Second line in header inlucdes 4 fields:
        #    [Blab] ,[unknown_1] , [unknown_2] , [unknown_3] , [unknown_4]
        # 4) Body includes 5 fields
        #    [specimen_name], [treatments], [moment],[meas_dec],[meas_dec
        # Tretment: XXX.0 (zerofield)
        #           XXX.1 (infield)
        #           XXX.2 (pTRM check)
        #           XXX.3 (Tail check)
        #           XXX.4 (Additivity check; Krasa et al., 2003)
        #           XXX.5 (Original Thellier-Thellier protocol. )
        #                 (where .5 is for the second direction and .1 in the first)
        # XXX = temperature in degrees
        #
        #
        # IMPORTANT ASSUMPTION:
        # (1) lab field is always in Z direction (theta=0, phi=90)
        # (2) Thermal demagnetization - NO MICROWAVE
        # (3) if if XXX <50 then assuming that this is NRM (273K)
        #
        # -------------------------------------
        #
        #   ATRM in six positions
        #
        # Tretment: XXX.0 zerofield
        #           XXX.1 +x
        #           XXX.2 +y
        #           XXX.3 +z
        #           XXX.4 -x
        #           XXX.5 -y
        #           XXX.6 -z
        #           XXX.7 alteration check
        #   IMPORTANT REMARKS:
        #
        # (1) If the program check if the direction of the magnetization fits the coding above
        # if not, an error message will appear
        # (2) Alteration ckeck can be in any direction
        # (3) the order of the measurements is not important
        #
        # For questions and support: rshaar@ucsd.edu
        # -------------------------------------------------------------

        Data={}
        for dir_name in list(DIRS_data.keys()):

            #-----------------------------------
            # First, read all files and sort data by specimen and by Experiment type
            #-----------------------------------

            for files in os.listdir(DIRS_data[dir_name]["path"]):
                if files.endswith(".tdt"):
                    print("Open file: ", DIRS_data[dir_name]["path"]+"/"+files)
                    fin=open(DIRS_data[dir_name]["path"]+"/"+files,'r')
                    header_codes=['labfield','core_azimuth','core_plunge','bedding_dip_direction','bedding_dip']
                    body_codes=['specimen_name','treatment','moment','dec','inc']
                    tmp_body=[]
                    tmp_header_data={}
                    line_number=0
                    continue_reading=True
                    line=fin.readline() # ignore first line
                    lines = fin.readlines()
                    fin.close()
                    for line in lines:

                        if "END" in line:
                            break

                        if line.strip('\n') =="":
                            break

                        this_line=line.strip('\n').split()

                        if len(this_line)<5:
                            continue


                        #---------------------------------------------------
                        # fix muxworthy funky data format
                        #---------------------------------------------------
                        if len(this_line)<5 and line_number!=0:
                            new_line=[]
                            for i in range(len(this_line)):
                                if i>1 and "-" in this_line[i]:
                                    tmp=this_line[i].replace("-"," -")
                                    tmp1=tmp.split()
                                    for i in range(len(tmp1)):
                                        new_line.append(tmp1[i])
                                else:
                                    new_line.append(this_line[i])
                            this_line=list(copy(new_line))



                        #-------------------------------
                        # Read infromation from Header and body
                        # The data is stored in a dictionary:
                        # Data[specimen][Experiment_Type]['header_data']=tmp_header_data  --> a dictionary with header data
                        # Data[specimen][Experiment_Type]['meas_data']=[dict1, dict2, ...] --> a list of dictionaries with measurement data
                        #-------------------------------

                        #---------------------------------------------------
                        # header
                        #---------------------------------------------------
                        if  line_number==0:

                            for i in range(len(this_line)):
                                tmp_header_data[header_codes[i]]=this_line[i]

                            line_number+=1

                        #---------------------------------------------------
                        # body
                        #---------------------------------------------------

                        else:
                            tmp_data={}
                            for i in range(min(len(this_line),len(body_codes))):
                                tmp_data[body_codes[i]]=this_line[i]
                            tmp_body.append(tmp_data)

                            #------------

                            specimen=tmp_body[0]['specimen_name']
                            line_number+=1

                    if specimen not in list(Data.keys()):
                        Data[specimen]={}
                    Experiment_Type=DIRS_data[dir_name]['experiment']
                    if Experiment_Type not in list(Data[specimen].keys()):
                        Data[specimen][Experiment_Type]={}
                    Data[specimen][Experiment_Type]['meas_data']=tmp_body
                    Data[specimen][Experiment_Type]['header_data']=tmp_header_data
                    Data[specimen][Experiment_Type]['sample_naming_convention']=DIRS_data[dir_name]['sample_naming_convention']
                    Data[specimen][Experiment_Type]['site_naming_convention']=DIRS_data[dir_name]['site_naming_convention']
                    Data[specimen][Experiment_Type]['location']=DIRS_data[dir_name]['location']
                    Data[specimen][Experiment_Type]['user_name']=DIRS_data[dir_name]['user_name']
                    Data[specimen][Experiment_Type]['volume']=DIRS_data[dir_name]['volume']
                    Data[specimen][Experiment_Type]['moment_units']=DIRS_data[dir_name]['moment_units']
                    Data[specimen][Experiment_Type]['labfield_DI']=DIRS_data[dir_name]['labfield_DI']



        #-----------------------------------
        # Convert Data{} to MagIC
        #-----------------------------------
        MeasRecs,SpecRecs,SampRecs,SiteRecs,LocRecs=[],[],[],[],[]
        specimens_list=list(Data.keys())
        specimens_list.sort()
        for specimen in specimens_list:
            Experiment_Types_list=list(Data[specimen].keys())
            Experiment_Types_list.sort()
            for Experiment_Type in Experiment_Types_list:
                if Experiment_Type in ["Thellier"]:

                    tmp_MeasRecs=[]

                    # IMORTANT:
                    # phi and theta of lab field are not defined
                    # defaults are defined here:
                    phi,theta='0.','90.'

                    header_line=Data[specimen][Experiment_Type]['header_data']
                    experiment_treatments=[]
                    measurement_running_number=0
                    methcodes=["LP-PI-TRM"] # start to make a list of the methcodes. and later will merge it to one string

                    for i in range(len(Data[specimen][Experiment_Type]['meas_data'])):
                        meas_line=Data[specimen][Experiment_Type]['meas_data'][i]

                        #------------------
                        # check if the same treatment appears more than once. If yes, assuming that the measurements is repeated twice,
                        # ignore the first, and take only the second one
                        #------------------

                        if i< (len(Data[specimen][Experiment_Type]['meas_data'])-2):
                            Repeating_measurements=True
                            for key in ['treatment','specimen_name']:
                                if Data[specimen][Experiment_Type]['meas_data'][i][key]!=Data[specimen][Experiment_Type]['meas_data'][i+1][key]:
                                    Repeating_measurements=False
                            if Repeating_measurements==True:
                                "Found a repeating measurement at line %i, sample %s. taking the last one"%(i,specimen)
                                continue
                        #------------------
                        # Special treatment for first line (NRM data).
                        #------------------

                        if i==0:
                            if "." not in meas_line['treatment']:
                                meas_line['treatment']="0.0"
                            elif meas_line['treatment'].split(".")[0]=="" and meas_line['treatment'].split(".")[1]=='0': # if NRM is in the form of ".0" instead of "0.0"
                                meas_line['treatment']="0.0"
                            elif  float(meas_line['treatment'].split(".")[0])<50 and float(meas_line['treatment'].split(".")[-1])==0: # if NRM is in the form of "20.0" instead of "0.0"
                                meas_line['treatment']="0.0"

                        #------------------
                        # fix line in format of XX instead of XX.YY
                        #------------------
                        if "." not in meas_line['treatment']:
                            meas_line['treatment']=meas_line['treatment']+".0"
                        if meas_line['treatment'].split(".")[1]=="":
                            meas_line['treatment']=meas_line['treatment']+"0"

                        #------------------
                        # init names and dictionaries
                        #------------------

                        MeasRec,SpecRec,SampRec,SiteRec,LocRec={},{},{},{},{}

                        labfield=float(header_line['labfield'])*1e-6 # convert from microT to Tesla
                        sample=self.get_sample_name(specimen,Data[specimen][Experiment_Type]['sample_naming_convention'])
                        site=self.get_site_name(sample,Data[specimen][Experiment_Type]['site_naming_convention'])
                        location=Data[specimen][Experiment_Type]['location']
                        if location=='':location='unknown'

                        #------------------
                        # Fill data
                        #------------------

                        #Start with S'tables and Loc Table
                        if specimen!="" and specimen not in [x['specimen'] if 'specimen' in list(x.keys()) else "" for x in SpecRecs]:
                            SpecRec['specimen'] = specimen
                            SpecRec['sample'] = sample
                            SpecRec['volume'] = Data[specimen][Experiment_Type]['volume']
                            SpecRec['citations']="This study"
                            SpecRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                            SpecRecs.append(SpecRec)
                        if sample!="" and sample not in [x['sample'] if 'sample' in list(x.keys()) else "" for x in SampRecs]:
                            SampRec['sample'] = sample
                            SampRec['site'] = site
                            SampRec['citations']="This study"
                            SampRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                            SampRecs.append(SampRec)
                        if site!="" and site not in [x['site'] if 'site' in list(x.keys()) else "" for x in SiteRecs]:
                            SiteRec['site'] = site
                            SiteRec['location'] = location
                            SiteRec['citations']="This study"
                            SiteRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                            SiteRecs.append(SiteRec)
                        if location!="" and location not in [x['location'] if 'location' in list(x.keys()) else "" for x in LocRecs]:
                            LocRec['location']=location
                            LocRec['citations']="This study"
                            LocRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                            LocRecs.append(LocRec)

                        #now the measurement Rec
                        MeasRec['citations']="This study"
                        # experiment is set in pmag.measurements_methods3
                        #MeasRec["experiments"]=""
                        MeasRec["specimen"]=specimen
                        MeasRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                        MeasRec["quality"]='g'
                        MeasRec["standard"]='u'
                        MeasRec["treat_step_num"]="%i"%measurement_running_number
                        MeasRec["dir_dec"]=meas_line['dec']
                        MeasRec["dir_inc"]=meas_line['inc']
                        if Data[specimen][Experiment_Type]['moment_units']=='mA/m':
                            MeasRec["magn_moment"]="%5e"%(float(meas_line['moment'])*1e-3*float(Data[specimen][Experiment_Type]['volume'])) # converted to Am^2
                        if Data[specimen][Experiment_Type]['moment_units']=='emu':
                            MeasRec["magn_moment"]="%5e"%(float(meas_line['moment'])*1e-3) # converted to Am^2
                        if Data[specimen][Experiment_Type]['moment_units']=='Am^2':
                            MeasRec["magn_moment"]="%5e"%(float(meas_line['moment'])) # converted to Am^2
                        MeasRec["meas_temp"]='273.' # room temp in kelvin

                        # Date and time
##                                    date=meas_line['Measurement Date'].strip("\"").split('-')
##                                    yyyy=date[2];dd=date[1];mm=date[0]
##                                    hour=meas_line['Measurement Time'].strip("\"")
##                                    MeasRec["measurement_date"]=yyyy+':'+mm+":"+dd+":"+hour

                        # lab field data: distinguish between PI experiments to AF/Thermal
                        treatments=meas_line['treatment'].split(".")
                        if float(treatments[1])==0:
                            MeasRec["treat_dc_field"]='0'
                            MeasRec["treat_dc_field_phi"]='0'
                            MeasRec["treat_dc_field_theta"]='0'
                        else:
                            MeasRec["treat_dc_field"]='%8.3e'%(labfield)
                            MeasRec["treat_dc_field_phi"]=Data[specimen][Experiment_Type]['labfield_DI'][0]
                            MeasRec["treat_dc_field_theta"]=Data[specimen][Experiment_Type]['labfield_DI'][1]

                        #------------------
                        # Lab Treatments
                        #------------------

                        # NRM
                        if float(treatments[0])==0 and float(treatments[1])==0:
                            MeasRec["method_codes"]="LT-NO"
                            experiment_treatments.append('0')
                            MeasRec["treat_temp"]='273.'
                            IZorZI=""

                        # Zerofield step
                        elif float(treatments[1])==0:
                            MeasRec["method_codes"]="LT-T-Z"
                            MeasRec["treat_temp"]='%8.3e' % (float(treatments[0])+273.) # temp in kelvin

                            #  check if this is ZI or IZ:
                            for j in range (0,i):
                                previous_lines=Data[specimen][Experiment_Type]['meas_data'][j]
                                if previous_lines['treatment'].split(".")[0] == meas_line['treatment'].split(".")[0]:
                                    if float(previous_lines['treatment'].split(".")[1]) == 1 or float(previous_lines['treatment'].split(".")[1]) == 10:
                                        if "LP-PI-TRM-IZ" not in methcodes:
                                            methcodes.append("LP-PI-TRM-IZ")
                                        IZorZI=""
                                    else:
                                        IZorZI="Z"

                        # Infield step
                        elif float(treatments[1])==1 or float(treatments[1])==10:
                            MeasRec["method_codes"]="LT-T-I"
                            MeasRec["treat_temp"]='%8.3e' % (float(treatments[0])+273.) # temp in kelvin

                            # check if this is ZI,IZ:
                            for j in range (0,i):
                                previous_lines=Data[specimen][Experiment_Type]['meas_data'][j]
                                if previous_lines['treatment'].split(".")[0] == meas_line['treatment'].split(".")[0]:
                                    if float(previous_lines['treatment'].split(".")[1]) == 0:
                                        if "LP-PI-TRM-ZI" not in methcodes:
                                            methcodes.append("LP-PI-TRM-ZI")
                                            IZorZI=""
                                    else:
                                        IZorZI="I"
                        # pTRM check step
                        elif float(treatments[1])==2 or float(treatments[1])==20:
                            MeasRec["method_codes"]="LT-PTRM-I"
                            MeasRec["treat_temp"]='%8.3e' % (float(treatments[0])+273.) # temp in kelvin
                            if "LP-PI-ALT" not in methcodes:
                                methcodes.append("LP-PI-ALT")

                        # Tail check step
                        elif float(treatments[1])==3 or float(treatments[1])==30:
                            MeasRec["method_codes"]="LT-PTRM-MD"
                            MeasRec["treat_temp"]='%8.3e' % (float(treatments[0])+273.) # temp in kelvin
                            if "LP-PI-BT-MD" not in methcodes:
                                methcodes.append("LP-PI-BT-MD")
                                MeasRec["treat_dc_field"]="0"
                                MeasRec["treat_dc_field_phi"]="0"
                                MeasRec["treat_dc_field_theta"]="0"

                        # Additivity check step
                        elif float(treatments[1])==4 or float(treatments[1])==40:
                            MeasRec["method_codes"]="LT-PTRM-AC"
                            MeasRec["treat_temp"]='%8.3e' % (float(treatments[0])+273.) # temp in kelvin
                            if "LP-PI-BT" not in methcodes:
                                methcodes.append("LP-PI-BT")

                        # Thellier Thellier protocol (1 for one direction and 5 for the antiparallel)
                        # Lab field direction of 1 is as put in the GUI dialog box
                        # Lab field direction of 5 is the anti-parallel direction of 1

                        elif float(treatments[1])==5 or float(treatments[1])==50:
                            MeasRec["method_codes"]="LT-T-I"
                            MeasRec["treat_temp"]='%8.3e' % (float(treatments[0])+273.) # temp in kelvin
                            MeasRec["treat_dc_field_phi"]="%.2f"%((float(Data[specimen][Experiment_Type]['labfield_DI'][0])+180.)%360.)
                            MeasRec["treat_dc_field_theta"]="%.2f"%(float(Data[specimen][Experiment_Type]['labfield_DI'][1])*-1.)
                            if "LP-PI-II" not in methcodes:
                                methcodes.append("LP-PI-II")

                        else:
                            print("-E- ERROR in file %s"%Experiment_Type)
                            print("-E- ERROR in treatment ",meas_line['treatment'])
                            print("... exiting until you fix the problem")


                        #-----------------------------------

                        #MeasRec["method_codes"]=lab_treatment+":"+lab_protocols_string
                        #MeasRec["experiments"]=specimen+":"+lab_protocols_string

                        tmp_MeasRecs.append(MeasRec)
                        measurement_running_number+=1

                    # arrange method_codes and experiments:
                    method_codes="LP-PI-TRM"
                    # Coe mothod
                    if "LP-PI-TRM-ZI" in methcodes and "LP-PI-TRM-IZ" not in methcodes and "LP-PI-II" not in methcodes:
                        method_codes=method_codes+":LP-PI-TRM-ZI"
                    if "LP-PI-TRM-ZI" not in methcodes and "LP-PI-TRM-IZ"  in methcodes and "LP-PI-II" not in methcodes:
                        method_codes=method_codes+":LP-PI-TRM-IZ"
                    if "LP-PI-TRM-ZI"  in methcodes and "LP-PI-TRM-IZ"  in methcodes and "LP-PI-II" not in methcodes:
                        method_codes=method_codes+":LP-PI-BT-IZZI"
                    if "LP-PI-II"  in methcodes:
                        method_codes=method_codes+":LP-PI-II"
                    if "LP-PI-ALT"  in methcodes:
                        method_codes=method_codes+":LP-PI-ALT"
                    if "LP-PI-BT-MD"  in methcodes:
                        method_codes=method_codes+":LP-PI-BT-MD"
                    if "LP-PI-BT"  in methcodes:
                        method_codes=method_codes+":LP-PI-BT"
                    for i in range(len(tmp_MeasRecs)):
                        STRING=":".join([tmp_MeasRecs[i]["method_codes"],method_codes])
                        tmp_MeasRecs[i]["method_codes"]=STRING
                        # experiment is set in pmag.measurements_methods3
                        #STRING=":".join([tmp_MeasRecs[i]["specimen"],method_codes])
                        #tmp_MeasRecs[i]["experiments"]=STRING
                        MeasRecs.append(tmp_MeasRecs[i])


                elif Experiment_Type in ["ATRM 6 positions"]:

                    tmp_MeasRecs=[]

                    header_line=Data[specimen][Experiment_Type]['header_data']
                    experiment_treatments=[]
                    measurement_running_number=0
                    methcodes=["LP-AN-TRM"] # start to make a list of the methcodes. and later will merge it to one string

                    for i in range(len(Data[specimen][Experiment_Type]['meas_data'])):
                        meas_line=Data[specimen][Experiment_Type]['meas_data'][i]

                        #------------------
                        # check if the same treatment appears more than once. If yes, assuming that the measurements is repeated twice,
                        # ignore the first, and take only the second one
                        #------------------

                        if i< (len(Data[specimen][Experiment_Type]['meas_data'])-2) :
                            Repeating_measurements=True
                            for key in ['treatment','specimen_name']:
                                if Data[specimen][Experiment_Type]['meas_data'][i][key]!=Data[specimen][Experiment_Type]['meas_data'][i+1][key]:
                                    Repeating_measurements=False
                            if Repeating_measurements==True:
                                "Found a repeating measurement at line %i, sample %s. taking the last one"%(i,specimen)
                                continue

                        #------------------
                        # fix line in format of XX instead of XX.0
                        #------------------
                        if "." not in meas_line['treatment']:
                            meas_line['treatment']=meas_line['treatment']+".0"
                        if meas_line['treatment'].split(".")[1]=="":
                            meas_line['treatment']=meas_line['treatment']+"0"

                        #------------------
                        # init names and dictionaries
                        #------------------

                        MeasRec,SpecRec,SampRec,SiteRec,LocRec={},{},{},{},{}

                        labfield=float(header_line['labfield'])*1e-6 # convert from microT to Tesla
                        sample=self.get_sample_name(specimen,Data[specimen][Experiment_Type]['sample_naming_convention'])
                        site=self.get_site_name(sample,Data[specimen][Experiment_Type]['site_naming_convention'])
                        location=Data[specimen][Experiment_Type]['location']

                        #------------------
                        # Fill data
                        #------------------

                        #Start with S'tables and Loc Table
                        if specimen!="" and specimen not in [x['specimen'] if 'specimen' in list(x.keys()) else "" for x in SpecRecs]:
                            SpecRec['specimen'] = specimen
                            SpecRec['sample'] = sample
                            SpecRec['volume'] = Data[specimen][Experiment_Type]['volume']
                            SpecRec['citations']="This study"
                            SpecRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                            SpecRecs.append(SpecRec)
                        if sample!="" and sample not in [x['sample'] if 'sample' in list(x.keys()) else "" for x in SampRecs]:
                            SampRec['sample'] = sample
                            SampRec['site'] = site
                            SampRec['citations']="This study"
                            SampRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                            SampRecs.append(SampRec)
                        if site!="" and site not in [x['site'] if 'site' in list(x.keys()) else "" for x in SiteRecs]:
                            SiteRec['site'] = site
                            SiteRec['location'] = location
                            SiteRec['citations']="This study"
                            SiteRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                            SiteRecs.append(SiteRec)
                        if location!="" and location not in [x['location'] if 'location' in list(x.keys()) else "" for x in LocRecs]:
                            LocRec['location']=location
                            LocRec['citations']="This study"
                            LocRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                            LocRecs.append(LocRec)

                        #Meas data now
                        MeasRec["specimen"]=specimen
                        MeasRec['analysts']=Data[specimen][Experiment_Type]['user_name']
                        MeasRec['citations']="This study"
                        MeasRec["quality"]='g'
                        MeasRec["standard"]='u'
                        MeasRec["treat_step_num"]="%i"%measurement_running_number
                        MeasRec["dir_dec"]=meas_line['dec']
                        MeasRec["dir_inc"]=meas_line['inc']
                        MeasRec["magn_moment"]="%5e"%(float(meas_line['moment'])*1e-3*float(Data[specimen][Experiment_Type]['volume'])) # converted to Am^2
                        MeasRec["meas_temp"]='273.' # room temp in kelvin

                        treatments=meas_line['treatment'].split(".")
                        if len(treatments[1])>1:
                            treatments[1]=treatments[1][0]

                        MeasRec["treat_temp"]='%8.3e' % (float(treatments[0])+273.) # temp in kelvin

                        # labfield direction
                        if float(treatments[1])==0:
                            MeasRec["treat_dc_field"]='0'
                            MeasRec["treat_dc_field_phi"]='0'
                            MeasRec["treat_dc_field_theta"]='0'
                            MeasRec["method_codes"]="LT-T-Z:LP-AN-TRM"
                        else:

                            MeasRec["treat_dc_field"]='%8.3e'%(labfield)

                            if float(treatments[1])==7 or float(treatments[1])==70: # alteration check as final measurement
                                MeasRec["method_codes"]="LT-PTRM-I:LP-AN-TRM"
                            else:
                                MeasRec["method_codes"]="LT-T-I:LP-AN-TRM"

                            # find the direction of the lab field in two ways:
                            # (1) using the treatment coding (XX.1=+x, XX.2=+y, XX.3=+z, XX.4=-x, XX.5=-y, XX.6=-z)
                            tdec=[0,90,0,180,270,0,0,90,0] # atrm declination/inlclination order
                            tinc=[0,0,90,0,0,-90,0,0,90] # atrm declination/inlclination order

                            ipos_code=int(treatments[1])-1
                            # (2) using the magnetization
                            DEC=float(MeasRec["dir_dec"])
                            INC=float(MeasRec["dir_inc"])
                            if INC < 45 and INC > -45:
                                if DEC>315  or DEC<45: ipos_guess=0
                                if DEC>45 and DEC<135: ipos_guess=1
                                if DEC>135 and DEC<225: ipos_guess=3
                                if DEC>225 and DEC<315: ipos_guess=4
                            else:
                                if INC >45: ipos_guess=2
                                if INC <-45: ipos_guess=5
                            # prefer the guess over the code
                            ipos=ipos_guess
                            MeasRec["treat_dc_field_phi"]='%7.1f' %(tdec[ipos])
                            MeasRec["treat_dc_field_theta"]='%7.1f'% (tinc[ipos])
                            # check it
                            if ipos_guess!=ipos_code and treatments[1]!='7':
                                print("-E- ERROR: check specimen %s step %s, ATRM measurements, coding does not match the direction of the lab field!"%(MeasRec["specimen"],".".join(list(treatments))))


                        MeasRecs.append(MeasRec)
                        measurement_running_number+=1

                else:
                    print("-E- ERROR. sorry, file format %s is not supported yet. Please contact rshaar@ucsd.edu"%Experiment_Type)


        #-------------------------------------------
        #  magic_measurements.txt
        #-------------------------------------------

        con = nb.Contribution(self.WD,read_tables=[])

        con.add_magic_table_from_data(dtype='specimens', data=SpecRecs)
        con.add_magic_table_from_data(dtype='samples', data=SampRecs)
        con.add_magic_table_from_data(dtype='sites', data=SiteRecs)
        con.add_magic_table_from_data(dtype='locations', data=LocRecs)
        MeasOuts=pmag.measurements_methods3(MeasRecs,noave=False)
        con.add_magic_table_from_data(dtype='measurements', data=MeasOuts)

        con.tables['specimens'].write_magic_file()
        con.tables['samples'].write_magic_file()
        con.tables['sites'].write_magic_file()
        con.tables['locations'].write_magic_file()
        res = con.tables['measurements'].write_magic_file()

        #-------------------------------------------

        if res:
            dlg1 = wx.MessageDialog(None,caption="Message:", message="file converted to {}\n you can try running thellier gui...\n".format(self.output_file_path.GetValue()) ,style=wx.OK|wx.ICON_INFORMATION)
        else:
            dlg1 = wx.MessageDialog(None, caption="Warning:", message="No file was created.  Make sure you have selected folders that contain .tdt format files")
        dlg1.ShowModal()
        dlg1.Destroy()
        self.Destroy()


class message_box(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self,title):
        wx.Frame.__init__(self, parent=None,size=(1000,500))

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_log = wx.TextCtrl(self.panel, id=-1, style=wx.TE_MULTILINE | wx.TE_READONLY  | wx.HSCROLL)
        self.sizer.Add(self.text_log, 1, wx.EXPAND)
        TEXT='''
        # -------------------------------------
        #
        # Programs assumptions:
        #
        # 1) Each file contains the data one specimen
        # 2) First line is the header: "Thellier-tdt"
        # 3) Second line in header inlucdes 4 fields:
        #    [Blab] ,['core_azimuth'] , ['core_plunge'] , ['bedding_dip_direction'] , ['bedding_dip']
        # 4) Body includes 5 fields
        #    [specimen_name], [treatments], [moment],[meas_dec],[meas_inc]
        # -------------------------------------
        # Thellier experiment:
        #
        # Tretments: XXX.0 (zerofield)
        #            XXX.1 (infield)
        #            XXX.2 (pTRM check)
        #            XXX.3 (Tail check)
        #            XXX.4 (Additivity check; Krasa et al., 2003)
        #            XXX.5 (Original Thellier-Thellier protocol. )
        #                 (where .5 is for the second direction and .1 in the first)
        # XXX = temperature in degrees
        #
        #
        # 1) If if XXX <50 then assuming that this is NRM (273K)
        # 2) Lab field defaul is Z direction (theta=0, phi=90)
        # 3) The program does not support Thermal demagnetization
        #
        # -------------------------------------
        #
        #   ATRM in six positions
        #
        # Tretments: XXX.0 zerofield
        #            XXX.1 +x
        #            XXX.2 +y
        #            XXX.3 +z
        #            XXX.4 -x
        #            XXX.5 -y
        #            XXX.6 -z
        #            XXX.7 alteration check
        #
        #
        # 1) The program checks if the direction of the magnetization fits the coding above.
        #    If not: an error message will appear
        # 2) Alteration check can be in any direction
        # 3) The order of the measurements is not important
        #
        # For questions and support: rshaar@ucsd.edu
        # -------------------------------------'''

        self.text_log.AppendText(TEXT)
##        fin =open(file_path,'r')
##        for line in fin.readlines():
##            if "-E-" in line :
##                self.text_log.SetDefaultStyle(wx.TextAttr(wx.RED))
##                self.text_log.AppendText(line)
##            if "-W-" in line:
##                self.text_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))
##                self.text_log.AppendText(line)
##        fin.close()
        #sizer.Fit(self)
        self.panel.SetSizer(self.sizer)


def convert(wd=None,noave=False):
    if not wd:
        WD = os.getcwd()
    else:
        WD = wd
    app = wx.App()
    app.frame = convert_tdt_files_to_MagIC(WD,noave)
    app.frame.Show()
    app.frame.Center()
    app.MainLoop()

def main():
    kwargs={}
    if '-h' in sys.argv:
        help(__name__)
        sys.exit()
    #if "-WD" in sys.argv:
    #    ind=sys.argv.index("-WD")
    #    kwargs['wd']=sys.argv[ind+1]
    wd = pmag.get_named_arg_from_sys('-WD', '.')
    kwargs['wd'] = wd
    if "-A" in sys.argv: kwargs['noave']=True
    #convert_tdt_files_to_MagIC(wd, **kwargs)
    convert(**kwargs)


if __name__ == '__main__':
    main()
