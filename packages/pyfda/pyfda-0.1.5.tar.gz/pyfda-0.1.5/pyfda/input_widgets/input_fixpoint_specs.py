# -*- coding: utf-8 -*-
#
# This file is part of the pyFDA project hosted at https://github.com/chipmuenk/pyfda
#
# Copyright © pyFDA Project Contributors
# Licensed under the terms of the MIT License
# (see file LICENSE in root directory for details)

"""
Widget for simulating fixpoint filters and
generating VHDL and Verilog Code
"""
from __future__ import print_function, division, unicode_literals, absolute_import
import sys, os, importlib
import logging
logger = logging.getLogger(__name__)

from ..compat import (Qt, QWidget, QPushButton, QComboBox, QFD, QSplitter, QLabel,
                      QPixmap, QVBoxLayout, QHBoxLayout, pyqtSignal, QFrame, 
                      QEvent, QSizePolicy)

#from myhdl import (toVerilog, toVHDL, Signal, always, always_comb, delay,
#               instance, instances, intbv, traceSignals,
#               Simulation, StopSimulation)

import pyfda.filterbroker as fb # importing filterbroker initializes all its globals
import pyfda.pyfda_dirs as dirs
from pyfda.pyfda_lib import cmp_version
from pyfda.pyfda_io_lib import extract_file_ext
from pyfda.pyfda_qt_lib import qstr, qget_cmb_box
from pyfda.pyfda_rc import params

if cmp_version("myhdl", "0.10") >= 0:
    import myhdl
    HAS_MYHDL = True
else:
    HAS_MYHDL = False


# see C. Feltons "FPGA IIR Lowpass Direct Form I Filter Generator"
#                 @ http://www.dsprelated.com/showcode/211.php

#------------------------------------------------------------------------------

class Input_Fixpoint_Specs(QWidget):
    """
    Create the widget for entering exporting / importing / saving / loading data
    """
    # emit a signal when the image has been resized
    sig_resize = pyqtSignal()
    # incoming, connected to input_tab_widget.sig_tx in pyfdax
    sig_rx = pyqtSignal(object)
    # outgoing: emitted by process_sig_rx
    # sig_tx = pyqtSignal(object)

    def __init__(self, parent):
        super(Input_Fixpoint_Specs, self).__init__(parent)

        self.tab_label = 'Fixpoint'
        self.tool_tip = ("<span>Select a fixpoint implementation for the filter,"
                " simulate it and generate a Verilog / VHDL netlist.</span>")

        if HAS_MYHDL:
            self._construct_UI()
        else:
            self.state = "deactivated" # "invisible", "disabled"


#------------------------------------------------------------------------------
    def process_sig_rx(self, dict_sig=None):
        """
        Process signals coming in via subwidgets and sig_rx
        """
        logger.debug("Processing {0}: {1}".format(type(dict_sig).__name__, dict_sig))
        if dict_sig['sender'] == __name__:
            logger.warning("Infinite loop detected")
            return
        if 'filt_changed' in dict_sig:
            # update list of available filter topologies here
            self._update_filter_cmb()
        if 'view_changed' in dict_sig and dict_sig['view_changed'] == 'q_coeff':
            # update fields in the filter topology widget - wordlength may have
            # been changed
            self.update_wdg_UI()

#------------------------------------------------------------------------------

    def _construct_UI(self):
        """
        Intitialize the main GUI, consisting of:
        - an image of the filter topology
        - the UI for the HDL filter settings
        - and the myHDL interface:
        """
        self.cmb_wdg_fixp = QComboBox(self)
        self.cmb_wdg_fixp.setSizeAdjustPolicy(QComboBox.AdjustToContents)
                

#------------------------------------------------------------------------------        
        # Define frame and layout for the dynamically updated filter widget
        # The actual filter widget is instantiated in self.set_fixp_widget() later on
        self.layHWdg = QHBoxLayout()
        #self.layHWdg.setContentsMargins(*params['wdg_margins'])
        frmHDL_wdg = QFrame(self)
        frmHDL_wdg.setLayout(self.layHWdg)

#------------------------------------------------------------------------------
        self.lblTitle = QLabel("not set", self)
        self.lblTitle.setWordWrap(True)
        self.lblTitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layHTitle = QHBoxLayout()
        layHTitle.addWidget(self.cmb_wdg_fixp)
        layHTitle.addWidget(self.lblTitle)

        self.frmTitle = QFrame(self)
        self.frmTitle.setLayout(layHTitle)
        self.frmTitle.setContentsMargins(*params['wdg_margins'])
#------------------------------------------------------------------------------        
        self.lbl_img_hdl = QLabel(self)
        self.img_dir = os.path.dirname(os.path.realpath(__file__))  
        self.img_file = os.path.join(self.img_dir, 'hdl_dummy.png')
        self.img_fixp = QPixmap(self.img_file)
        self.resize_img()
        layHImg = QHBoxLayout()
        layHImg.setContentsMargins(0,0,0,0)
        layHImg.addWidget(self.lbl_img_hdl)#, Qt.AlignCenter)
        self.frmImg = QFrame(self)
        self.frmImg.setLayout(layHImg)
        self.frmImg.setContentsMargins(*params['wdg_margins'])
#------------------------------------------------------------------------------        
        self.butExportHDL = QPushButton(self)
        self.butExportHDL.setToolTip("Create VHDL and Verilog files.")
        self.butExportHDL.setText("Create HDL")

        self.butSimFixPoint = QPushButton(self)
        self.butSimFixPoint.setToolTip("Simulate filter with fixpoint effects.")
        self.butSimFixPoint.setText("Simulate")

        self.layHBtns = QHBoxLayout()
        self.layHBtns.addWidget(self.butSimFixPoint)
        self.layHBtns.addWidget(self.butExportHDL)

        # This frame encompasses all the buttons
        frmBtns = QFrame(self)
        #frmBtns.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        frmBtns.setLayout(self.layHBtns)
        frmBtns.setContentsMargins(*params['wdg_margins'])

    # -------------------------------------------------------------------
    # Top level layout
    # -------------------------------------------------------------------
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.addWidget(self.frmImg)
        splitter.addWidget(frmHDL_wdg)
        # setSizes uses absolute pixel values, but can be "misused" by specifying values
        # that are way too large: in this case, the space is distributed according
        # to the _ratio_ of the values:
        splitter.setSizes([3000, 5000])

        layVMain = QVBoxLayout()
        layVMain.addWidget(self.frmTitle)
        layVMain.addWidget(splitter)
        layVMain.addWidget(frmBtns)
        layVMain.addStretch()
        layVMain.setContentsMargins(*params['wdg_margins'])

        self.setLayout(layVMain)

        #----------------------------------------------------------------------
        # GLOBAL SIGNALS & SLOTs
        #----------------------------------------------------------------------
        self.sig_rx.connect(self.process_sig_rx)

        #----------------------------------------------------------------------
        # LOCAL SIGNALS & SLOTs & EVENTFILTERS
        #----------------------------------------------------------------------
        # monitor events and generate sig_resize event when resized
        self.lbl_img_hdl.installEventFilter(self)
        # ... then redraw image when resized
        self.sig_resize.connect(self.resize_img)

        self.cmb_wdg_fixp.currentIndexChanged.connect(self._update_fixp_widget)
        self.butExportHDL.clicked.connect(self.exportHDL)
        self.butSimFixPoint.clicked.connect(self.simFixPoint)
        #----------------------------------------------------------------------
        inst_wdg_list = self._update_filter_cmb()
        if len(inst_wdg_list) == 0:
            logger.warning("No fixpoint filters found!")
        else:
            logger.info("Imported {0:d} fixpoint filters:\n{1}"
                        .format(len(inst_wdg_list.split("\n"))-1, inst_wdg_list))

        self._update_fixp_widget()

#------------------------------------------------------------------------------
    def _update_filter_cmb(self):
        """
        (Re-)Read list of fixpoint filters, try to import them and populate the 
        corresponding combo box. The list should be updated everytime a new
        filter design type is selected.
        """
        inst_wdg_str = "" # full names of successfully instantiated widgets

        self.cmb_wdg_fixp.clear()

        # wdg = (class_name, args, dir)
        for wdg in fb.fixpoint_widgets_list:
            if not wdg[2]:
                # use standard module
                pckg_name = 'pyfda'
            else:
                # check and extract user directory
                if os.path.isdir(wdg[2]):
                    pckg_path = os.path.normpath(wdg[2])
                    # split the path into the dir containing the module and its name
                    user_dir_name, pckg_name = os.path.split(pckg_path)

                    if user_dir_name not in sys.path:
                        sys.path.append(user_dir_name)
                else:
                    logger.warning("Path {0:s} doesn't exist!".format(wdg[2]))
                    continue
            mod_name = pckg_name + '.fixpoint_widgets.' + wdg[0].lower()
            class_name = pckg_name + '.fixpoint_widgets.' + wdg[0]

            try:  # Try to import the module from the  package ...
                mod = importlib.import_module(mod_name)
                # get the class belonging to wdg[0] ...
                _ = getattr(mod, wdg[0]) # try to resolve the class       
                # everything worked fine, add it to the combo box:
                self.cmb_wdg_fixp.addItem(wdg[0], mod_name)
                
                inst_wdg_str += '\t' + class_name + '\n'

            except ImportError:
                logger.warning("Could not import {0}!".format(mod_name))
                continue
        return inst_wdg_str
        
#------------------------------------------------------------------------------
    def eventFilter(self, source, event):
        """
        Filter all events generated by monitored QLabel, only resize events are
        processed here, generating a `sig_resize` signal. All other events
        are passed on to the next hierarchy level.
        """
        if event.type() == QEvent.Resize:
            self.sig_resize.emit()

        # Call base class method to continue normal event processing:
        return super(Input_Fixpoint_Specs, self).eventFilter(source, event)
#------------------------------------------------------------------------------
    def resize_img(self):
        """ 
        Resize the image inside QLabel to completely fill the label while
        keeping the aspect ratio.
        """
        img_scaled = self.img_fixp.scaled(self.lbl_img_hdl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_img_hdl.setPixmap(QPixmap(img_scaled))

#------------------------------------------------------------------------------
    def update_all(self):
        """
        Import new module and update UI after changing the filter topology
        """
        self._construct_dyn_widget()
        self.update_UI()

#------------------------------------------------------------------------------
    def _update_fixp_widget(self):
        """
        This method is called at the initialization of this widget.

        It will also be called in the future every time a new filter design is
        selected, bringing a new selection of available fixpoint filter
        implementations (not implemented yet).
        
        - Destruct old fixpoint filter widget and instance
        - Import and instantiate new fixpoint filter widget e.g. after changing the 
          filter topology
        - Try to load image for filter topology
        - Update the UI of the widget
        """
        if hasattr(self, "hdl_wdg_inst"): # is a fixpoint widget loaded?
            try:
                self.layHWdg.removeWidget(self.hdl_wdg_inst) # remove widget from layout
                self.hdl_wdg_inst.deleteLater() # delete QWidget when scope has been left
            except AttributeError as e:
                logger.error("Could not destruct_UI!\n{0}".format(e))

        cmb_wdg_fx_cur = qget_cmb_box(self.cmb_wdg_fixp, data=False)

        if cmb_wdg_fx_cur: # at least one valid hdl widget found
            self.fx_wdg_found = True
            fx_mod_name = qget_cmb_box(self.cmb_wdg_fixp, data=True) # module name and path
            fx_mod = importlib.import_module(fx_mod_name) # get module 
            fx_wdg_class = getattr(fx_mod, cmb_wdg_fx_cur) # get class
            self.hdl_wdg_inst = fx_wdg_class(self)
            self.layHWdg.addWidget(self.hdl_wdg_inst, stretch=1)
           
            if hasattr(self.hdl_wdg_inst, "sig_rx"):
                self.sig_rx.connect(self.hdl_wdg_inst.sig_rx)
            #if hasattr(self.hdl_wdg_inst, "sig_tx"):
                #self.hdl_wdg_inst.sig_tx.connect(self.sig_rx)
        
            if hasattr(self.hdl_wdg_inst, "img_name") and self.hdl_wdg_inst.img_name: # is an image name defined?
                # check whether file exists
                file_path = os.path.dirname(fx_mod.__file__) # get path of imported fixpoint widget and 
                img_file = os.path.join(file_path, self.hdl_wdg_inst.img_name) # construct full image name from it
                # _, file_extension = os.path.splitext(self.hdl_wdg_inst.img_name)
    
                if os.path.exists(img_file):
                    self.img_fixp = QPixmap(img_file)
    #                if file_extension == '.png':
    #                    self.img_fixp = QPixmap(img_file)
    #                elif file_extension == '.svg':
    #                    self.img_fixp = QtSvg.QSvgWidget(img_file)
                else:
                    logger.warning("Image file {0} doesn't exist.".format(img_file))
                    img_file = os.path.join(file_path, "hdl_dummy.png")                
                    self.img_fixp = QPixmap(img_file)
                    #self.lbl_img_hdl.setPixmap(QPixmap(self.img_fixp)) # fixed size
                self.resize_img()
                
            self.lblTitle.setText(self.hdl_wdg_inst.title)

        else:
            self.fx_wdg_found = False

 
#------------------------------------------------------------------------------
    def update_wdg_UI(self):
        """
        Update the fixpoint widget UI when view (i.e. fixpoint coefficient format) 
        has been changed outside this class
        """
        if hasattr(self.hdl_wdg_inst, "update_UI"):
            self.hdl_wdg_inst.update_UI()

#------------------------------------------------------------------------------
    def setupHDL(self, file_name = "", dir_name = ""):
        """
        Setup instance of myHDL object with word lengths and coefficients
        """

        # @todo: always use sos?  The filter object is setup to always
        # @todo: generate a second order filter
        # get filter coefficients etc. from filter dict
        coeffs = fb.fil[0]['ba']
        # zpk =  fb.fil[0]['zpk'] # not implemented yet
        # sos = fb.fil[0]['sos']  # not implemented yet

        self.hdl_wdg_inst.setup_HDL(coeffs) # call setup method of filter widget
        self.hdl_wdg_inst.flt.hdl_name = file_name
        self.hdl_wdg_inst.flt.hdl_directory = dir_name

#------------------------------------------------------------------------------
    def exportHDL(self):
        """
        Synthesize HDL description of filter using myHDL module
        """
        dlg = QFD(self) # instantiate file dialog object

        file_types = "Verilog (*.v);;VHDL (*.vhd)"

        hdl_file, hdl_filter = dlg.getSaveFileName_(
                caption="Save HDL as", directory=dirs.save_dir,
                filter=file_types)
        hdl_file = qstr(hdl_file)

        if hdl_file != "": # "operation cancelled" gives back an empty string
            hdl_file = os.path.normpath(hdl_file)
            hdl_type = extract_file_ext(qstr(hdl_filter))[0] # return '.v' or '.vhd'

            hdl_dir_name = os.path.dirname(hdl_file) # extract the directory path
            if not os.path.isdir(hdl_dir_name): # create directory if it doesn't exist
                os.mkdir(hdl_dir_name)
            dirs.save_dir = hdl_dir_name # make this directory the new default / base dir

            # return the filename without suffix
            hdl_file_name = os.path.splitext(os.path.basename(hdl_file))[0]

            self.setupHDL(file_name = hdl_file_name, dir_name = hdl_dir_name)

            if str(hdl_type) == '.vhd':
                self.hdl_wdg_inst.flt.hdl_target = 'vhdl'
                suffix = '.vhd'
            else:
                self.hdl_wdg_inst.flt.hdl_target = 'verilog'
                suffix = '.v'


            logger.info('Creating hdl_file "{0}"'.format(
                        os.path.join(hdl_dir_name, hdl_file_name + suffix)))

            self.hdl_wdg_inst.flt.convert()
            logger.info("HDL conversion finished!")

#------------------------------------------------------------------------------
    def simFixPoint(self):
        """
        Simulate filter in fix-point description
        """
        # Setup the Testbench and run

        dlg = QFD(self)  # instantiate file dialog object

        plt_types = "png (*.png);;svg (*.svg)"

        plt_dir_file, plt_type = dlg.getSaveFileName_(
                caption = "Save plots as", directory=dirs.save_dir,
                filter = plt_types)
        plt_dir_file = qstr(plt_dir_file) # dir + file name without suffix

        if plt_dir_file != "":
            plt_type = extract_file_ext(qstr(plt_type)) # suffix
            plt_dir_file += plt_type[0] # file name with suffix
            plt_dir_file = os.path.normpath(plt_dir_file) # "sanitize" path

            plt_dir = os.path.dirname(plt_dir_file)  # extract the directory path
            if not os.path.isdir(plt_dir): # create directory if it doesn't exist
                os.mkdir(plt_dir)
            dirs.save_dir = plt_dir # make this directory the new default / base dir

            plt_file = os.path.basename(plt_dir_file)

            logger.info('Creating plot file "{0}"'.format(
                        os.path.join(plt_dir, plt_file)))

            self.setupHDL(file_name = plt_file, dir_name = plt_dir)

            logger.info("Fixpoint simulation setup")
            W = self.hdl_wdg_inst.W # Matlab format : W = (W_len,WF)
            tb = self.hdl_wdg_inst.flt.simulate_freqz(num_loops=3, Nfft=1024)
            clk = myhdl.Signal(False)
            ts  = myhdl.Signal(False)
            x   = myhdl.Signal(myhdl.intbv(0,min=-2**(W[0]-1), max=2**(W[0]-1)))
            y   = myhdl.Signal(myhdl.intbv(0,min=-2**(W[0]-1), max=2**(W[0]-1)))

            try:
                sim = myhdl.Simulation(tb)
                logger.info("Fixpoint simulation started")
                sim.run()
                logger.info("Fixpoint plotting started")
                self.hdl_wdg_inst.flt.plot_response()
                logger.info("Fixpoint plotting finished")
            except myhdl.SimulationError as e:
                logger.warning("Simulation failed:\n{0}".format(e))

#------------------------------------------------------------------------------

if __name__ == '__main__':

    from ..compat import QApplication
    app = QApplication(sys.argv)
    mainw = Input_Fixpoint_Specs(None)
    mainw.show()

    app.exec_()
    
# test using "python -m pyfda.fixpoint_filters.fixpoint_specs"