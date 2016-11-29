#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import math
import logging

import BlissFramework
if BlissFramework.get_gui_version() == "QT5":
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
else:
    from PyQt4.QtCore import*
    from PyQt4.QtGui import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__credits__ = ["MXCuBE colaboration"]
__version__ = "2.2."
__category__ = 'Motor'


class Qt4_MotorSpinBoxBrick(BlissWidget):
    """
    Descript. :
    """
    STATE_COLORS = (Qt4_widget_colors.LIGHT_RED,     # error
                    Qt4_widget_colors.DARK_GRAY,     # unknown
                    Qt4_widget_colors.LIGHT_GREEN,   # ready
                    Qt4_widget_colors.LIGHT_YELLOW,  
                    Qt4_widget_colors.LIGHT_YELLOW,
                    Qt4_widget_colors.LIGHT_YELLOW)

    MAX_HISTORY = 20

    def __init__(self, *args):
        """
        Descript. :
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.motor_hwobj = None

        # Internal values ----------------------------------------------------- 
        self.step_editor = None
        self.move_step = None
        self.demand_move = 0
        self.in_expert_mode = None

        # Properties ----------------------------------------------------------
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('formatString', 'formatString', '+##.##')
        self.addProperty('label', 'string', '')
        self.addProperty('showLabel', 'boolean', True)
        self.addProperty('showMoveButtons', 'boolean', True)
        self.addProperty('showSlider', 'boolean', False)
        self.addProperty('showStop', 'boolean', True)
        self.addProperty('showStep', 'boolean', True)
        self.addProperty('showStepList', 'boolean', False)
        self.addProperty('showPosition', 'boolean', True)
        self.addProperty('invertButtons', 'boolean', False)
        self.addProperty('delta', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('helpDecrease', 'string', '')
        self.addProperty('helpIncrease', 'string', '')
        self.addProperty('hideInUser', 'boolean', False)
        self.addProperty('defaultSteps', 'string', '180 90 45 30 10')
        self.addProperty('enableSliderTracking', 'boolean', False)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot('toggle_enabled',())

        # Graphic elements-----------------------------------------------------
        self.main_gbox = QGroupBox(self)
        self.motor_label = QLabel(self.main_gbox)

        #Main controls
        self.control_box = QWidget(self.main_gbox)
        self.move_left_button = QPushButton(self.control_box)
        self.move_left_button.setIcon(Qt4_Icons.load_icon('Left2'))
        self.move_left_button.setToolTip("Moves the motor down (while pressed)")
        self.move_left_button.setFixedWidth(25)
        self.move_right_button = QPushButton(self.control_box)
        self.move_right_button.setIcon(Qt4_Icons.load_icon('Right2'))
        self.move_right_button.setToolTip("Moves the motor up (while pressed)")  
        self.move_right_button.setFixedWidth(25)
        
        self.position_spinbox = QDoubleSpinBox(self.control_box)
        self.position_spinbox.setMinimum(-10000)
        self.position_spinbox.setMaximum(10000)
        self.position_spinbox.setMinimumSize(QSize(75, 25))
        self.position_spinbox.setMaximumSize(QSize(75, 25))
        self.position_spinbox.setToolTip("Moves the motor to a specific " + \
              "position or step by step; right-click for motor history")

        #Extra controls
        self.extra_button_box = QWidget(self.main_gbox)
        self.stop_button = QPushButton(self.extra_button_box)
        self.stop_button.setIcon(Qt4_Icons.load_icon('Stop2'))
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stops the motor")
        self.stop_button.setFixedWidth(25)
        self.step_button = QPushButton(self.extra_button_box)
        self.step_button_icon = Qt4_Icons.load_icon('TileCascade2')
        self.step_button.setIcon(self.step_button_icon)
        self.step_button.setToolTip("Changes the motor step")
        self.step_combo = QComboBox(self.extra_button_box)
        self.step_combo.setEditable(True)
        self.step_combo.setValidator(QDoubleValidator(0, 360, 5, self.step_combo))
        self.step_combo.setDuplicatesEnabled(False)

        self.position_slider = QSlider(Qt.Horizontal, self.main_gbox)
    
        # Layout --------------------------------------------------------------
        self.control_box_layout = QHBoxLayout(self.control_box)
        self.control_box_layout.addWidget(self.position_spinbox)
        self.control_box_layout.addWidget(self.move_left_button)
        self.control_box_layout.addWidget(self.move_right_button)
        self.control_box_layout.setSpacing(2)
        self.control_box_layout.setContentsMargins(0, 0, 0, 0)

        self.extra_button_box_layout = QHBoxLayout(self.extra_button_box)
        self.extra_button_box_layout.addWidget(self.stop_button)
        self.extra_button_box_layout.addWidget(self.step_button)
        self.extra_button_box_layout.addWidget(self.step_combo)
        self.extra_button_box_layout.setSpacing(2)
        self.extra_button_box_layout.setContentsMargins(0, 0, 0, 0)

        self.main_gbox_layout = QHBoxLayout(self.main_gbox)
        self.main_gbox_layout.addWidget(self.motor_label)
        self.main_gbox_layout.addWidget(self.control_box)
        self.main_gbox_layout.addWidget(self.extra_button_box)
        self.main_gbox_layout.addWidget(self.position_slider)
        self.main_gbox_layout.setSpacing(2)
        self.main_gbox_layout.setContentsMargins(2, 2, 2, 2)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.main_gbox)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # SizePolicy (horizontal, vertical) -----------------------------------
        self.move_left_button.setSizePolicy(QSizePolicy.Fixed, 
                                            QSizePolicy.Minimum)
        self.move_right_button.setSizePolicy(QSizePolicy.Fixed, 
                                             QSizePolicy.Minimum)
        self.stop_button.setSizePolicy(QSizePolicy.Fixed, 
                                       QSizePolicy.Minimum)
        self.step_button.setSizePolicy(QSizePolicy.Fixed, 
                                       QSizePolicy.Minimum)
        self.extra_button_box.setSizePolicy(QSizePolicy.Fixed,
                                            QSizePolicy.Fixed)

        # Object events ------------------------------------------------------
        spinbox_event = SpinBoxEvent(self.position_spinbox) 
        self.position_spinbox.installEventFilter(spinbox_event)
        spinbox_event.returnPressedSignal.connect(self.change_position) 
        spinbox_event.contextMenuSignal.connect(self.open_history_menu) 
        self.position_spinbox.lineEdit().textEdited.connect(self.position_value_edited)

        self.step_combo.activated.connect(self.go_to_step)
        self.step_combo.activated.connect(self.step_changed)
        self.step_combo.editTextChanged.connect(self.step_edited)

        self.stop_button.clicked.connect(self.stop_motor)
        self.step_button.clicked.connect(self.open_step_editor)

        self.move_left_button.pressed.connect(self.move_down)
        self.move_left_button.released.connect(self.stop_moving)
        self.move_right_button.pressed.connect(self.move_up)
        self.move_right_button.released.connect(self.stop_moving)

        self.position_slider.valueChanged.connect(\
             self.position_slider_value_changed)

        # Other ---------------------------------------------------------------
        self.instance_synchronize("position_spinbox", "step_combo")
 
    def setExpertMode(self, mode):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.in_expert_mode = mode
        if self['hideInUser']:
            if mode:
                self.main_gbox.show()
            else:
                self.main_gbox.hide()

    def step_edited(self, step):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        Qt4_widget_colors.set_widget_color(self.step_combo,
                                           Qt4_widget_colors.LINE_EDIT_CHANGED, 
                                           QPalette.Button)

    def step_changed(self, step):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        Qt4_widget_colors.set_widget_color(self.step_combo.lineEdit(),
             Qt.white, QPalette.Base)

    def toggle_enabled(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.setEnabled(not self.isEnabled())

    def run(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.in_expert_mode is not None:
            self.setExpertMode(self.in_expert_mode)

    def stop(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.main_gbox.show()

    def get_line_step(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        return self.position_spinbox.singleStep()

    def set_line_step(self, val):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.move_step = float(val)
        self.position_spinbox.setSingleStep(self.move_step)
        found = False
        for i in range(self.step_combo.count()):
            if float(str(self.step_combo.itemText(i))) == self.move_step:
                found = True
                self.step_combo.setItemIcon(i, self.step_button_icon)
        if not found:
            self.step_combo.addItem(self.step_button_icon, str(self.move_step))
            self.step_combo.setCurrentIndex(self.step_combo.count() - 1)

    def go_to_step(self, step_index):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        step = str(self.step_combo.currentText())
        if step != "":
            self.set_line_step(step)

    def set_step_button_icon(self, icon_name):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.step_button_icon = Qt4_Icons.load_icon(icon_name)
        self.step_button.setIcon(self.step_button_icon)
        for i in range(self.step_combo.count()):
            #xt = self.step_combo.itemText(i)
            self.step_combo.setItemIcon(i, self.step_button_icon)
            #elf.step_cbox.changeItem(self.step_button_icon, txt, i)

    def stop_motor(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.motor_hwobj.stop()

    def stop_moving(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.demand_move = 0

    def move_up(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        #self.demand_move = 1
        self.update_gui()
        state = self.motor_hwobj.getState()
        if state == self.motor_hwobj.READY:
            if self['invertButtons']:
                self.really_move_down()
            else:
                self.really_move_up()

    def move_down(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        #self.demand_move = -1
        self.update_gui()
        state = self.motor_hwobj.getState()
        if state == self.motor_hwobj.READY:
            if self['invertButtons']:
                self.really_move_up()
            else:
                self.really_move_down()

    def really_move_up(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        step = 1.0
        if self.move_step is not None:
            step = self.move_step
        elif self['delta'] != "":
            step = float(self['delta'])
        else:        
            try:
                step = self.motor_hwobj.GUIstep
            except:
                pass

        print step 
        if self.motor_hwobj.isReady():
            self.set_position_spinbox_color(self.motor_hwobj.READY)
            print self.motor_hwobj
            self.motor_hwobj.moveRelative(step)

    def really_move_down(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        step = 1.0
        if self.move_step is not None:
            step = self.move_step
        elif self['delta'] != "":
            step = float(self['delta'])
        else:        
            try:
                step = self.motor_hwobj.GUIstep
            except:
                pass

        if self.motor_hwobj.isReady():
            self.set_position_spinbox_color(self.motor_hwobj.READY)
            self.motor_hwobj.moveRelative(-step)

    def update_gui(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.motor_hwobj is not None: 
            self.main_gbox.setEnabled(True)
            try:
                if self.motor_hwobj.isReady():
                    self.limits_changed(self.motor_hwobj.getLimits())
                    self.position_changed(self.motor_hwobj.getPosition())
                self.state_changed(self.motor_hwobj.getState())
            except:
                if self.motor_hwobj is not None:
                    self.state_changed(self.motor_hwobj.UNUSABLE)
                else:
                    pass
        else:
            self.main_gbox.setEnabled(False)

    def limits_changed(self, limits):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.position_spinbox.blockSignals(True)
        self.position_spinbox.setMinimum(limits[0])
        self.position_spinbox.setMaximum(limits[1])
        self.position_spinbox.blockSignals(False)

        self.position_slider.blockSignals(True)
        self.position_slider.setMinimum(limits[0])
        self.position_slider.setMaximum(limits[1])
        self.position_slider.blockSignals(False)

        self.set_tool_tip(limits=limits)

    def open_history_menu(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        menu = QMenu(self)
        menu.addAction("Previous positions")
        #menu.insertSeparator()
        for i in range(len(self.pos_history)):
            menu.addAction(self.pos_history[i], i)
        menu.popup(QCursor.pos())
        menu.activated.connect(self.go_to_history_pos)

    def go_to_history_pos(self, index):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        pos = self.pos_history[index]
        self.motor_hwobj.move(float(pos))

    def update_history(self, pos):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        pos = str(pos)
        if pos not in self.pos_history:
            if len(self.pos_history) == Qt4_MotorSpinBoxBrick.MAX_HISTORY:
                del self.pos_history[-1]
            self.pos_history.insert(0, pos)

    def open_step_editor(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.isRunning():
            if self.step_editor is None:
                self.step_editor = StepEditorDialog(self)
            self.step_editor.set_motor(self.motor_hwobj, 
                                       self, 
                                       self['label'], 
                                       self['default_steps'])
            s = self.font().pointSize()
            f = self.step_editor.font()
            f.setPointSize(s)
            self.step_editor.setFont(f)
            self.step_editor.updateGeometry()
            self.step_editor.show()

    def position_changed(self, new_position):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        try:
           self.position_spinbox.setValue(float(new_position))
           self.position_slider.setValue(float(new_position))
        except:
           print(('ERROR!!! Setting position...' + str(new_position)))
           pass

    def set_position_spinbox_color(self, state):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        color = Qt4_MotorSpinBoxBrick.STATE_COLORS[state]
        Qt4_widget_colors.set_widget_color(self.position_spinbox.lineEdit(), 
                                           color,
                                           QPalette.Base) 

    def state_changed(self, state):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.set_position_spinbox_color(state)
        if state == self.motor_hwobj.MOVESTARTED:
            self.update_history(self.motor_hwobj.getPosition())
        if state == self.motor_hwobj.READY:
            if self.demand_move == 1:
                if self['invertButtons']:
                    self.really_move_down()
                else:
                    self.really_move_up()
                return
            elif self.demand_move == -1:
                if self['invertButtons']:
                    self.really_move_up()
                else:
                    self.really_move_down()
                return

            self.position_spinbox.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
            self.step_combo.setEnabled(True)
        elif state in (self.motor_hwobj.NOTINITIALIZED, self.motor_hwobj.UNUSABLE):
            self.position_spinbox.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
        elif state in (self.motor_hwobj.MOVING, self.motor_hwobj.MOVESTARTED):
            self.position_spinbox.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
            self.step_combo.setEnabled(False)
        elif state == self.motor_hwobj.ONLIMIT:
            self.position_spinbox.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
        self.set_tool_tip(state=state)

    def motor_position_changed_relativ(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.motor_hwobj is not None:
            if self.motor_hwobj.isReady():
                self.motor_hwobj.moveRelative(self.position_spinbox.lineStep())

    def change_position(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.motor_hwobj is not None:
            self.motor_hwobj.move(self.position_spinbox.value())

    def position_value_edited(self, value):
        Qt4_widget_colors.set_widget_color(self.position_spinbox.lineEdit(),
                                           QColor(255,165,0),
                                           QPalette.Base)

    def set_tool_tip(self, name=None, state=None, limits=None):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        states = ("NOTINITIALIZED", "UNUSABLE", "READY", 
                  "MOVESTARTED", "MOVING", "ONLIMIT")
        if name is None:
            name = self['mnemonic']

        if self.motor_hwobj is None:
            tip = "Status: unknown motor "+name
        else:
            try:
                if state is None:
                    state = self.motor_hwobj.getState()
            except:
                logging.exception("%s: could not get motor state", self.objectName())
                state = self.motor_hwobj.UNUSABLE
                
            try:
                if limits is None and self.motor_hwobj.isReady():
                    limits = self.motor_hwobj.getLimits()
            except:
                logging.exception("%s: could not get motor limits", self.objectName())
                limits = None

            try:
                state_str = states[state]
            except IndexError:
                state_str = "UNKNOWN"
                
            limits_str = ""
            if limits is not None:
                l_bot = self['formatString'] % float(limits[0])
                l_top = self['formatString'] % float(limits[1])
                limits_str = " Limits:%s,%s" % (l_bot, l_top)
            tip = "State: " + state_str + limits_str

        self.motor_label.setToolTip(tip)
        if not self['showBox']:
            tip = ""
        self.main_gbox.setToolTip(tip)

    def setLabel(self, label):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if not self['showLabel']:
            label = None

        if label is None:
            self.motor_label.hide()
            self.containerBox.setTitle("")
            return
    
        if label == "":
            if self.motor_hwobj is not None:
                label = self.motor_hwobj.username

        if self['showBox']:
            self.motor_label.hide()
            self.main_gbox.setTitle(label)
        else:
            if label != "":
                label += ": "
            self.main_gbox.setTitle("")
            self.motor_label.setText(label)
            self.motor_label.show()

    def set_motor(self, motor, motor_ho_name = None):
        """
        . :
        Args.     :
        Return.   : 
        """
        if self.motor_hwobj is not None:
            self.disconnect(self.motor_hwobj, 
                            'limitsChanged',
                            self.limits_changed)
            self.disconnect(self.motor_hwobj,
                            'positionChanged', 
                            self.position_changed)
            self.disconnect(self.motor_hwobj,
                            'stateChanged',
                            self.state_changed)

        if motor_ho_name is not None:
            self.motor_hwobj = self.getHardwareObject(motor_ho_name)
        
        if self.motor_hwobj is None:
          # first time motor is set
            try:
                s = float(self.default_step)
            except:
                try:
                    s = motor_hwobj.GUIstep
                except:
                    s = 1.0
            self.set_line_step(s)

        if self.motor_hwobj is not None:
            self.connect(self.motor_hwobj,
                         'limitsChanged',
                         self.limits_changed)
            self.connect(self.motor_hwobj,'positionChanged',
                         self.position_changed,
                         instanceFilter=True)
            self.connect(self.motor_hwobj,
                         'stateChanged',
                         self.state_changed,
                         instanceFilter=True)

        self.pos_history = []
        self.update_gui()
        #self['label'] = self['label']
        #self['defaultStep']=self['defaultStep']

    def position_slider_value_changed(self, value):
        """Sets motor postion based on the slider value"""

        if self.motor_hwobj is not None:
            self.motor_hwobj.move(value) 

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_name == 'mnemonic':
            self.set_motor(self.motor_hwobj, new_value)
        elif property_name == 'formatString':
            if self.motor_hwobj is not None:
                self.update_GUI()
        elif property_name == 'label':
            self.setLabel(new_value)
        elif property_name == 'showLabel':
            if new_value:
                self.setLabel(self['label'])
            else:
                self.setLabel(None)
        elif property_name == 'showMoveButtons':
            if new_value:
                self.move_left_button.show()
                self.move_right_button.show()
            else:            
                self.move_left_button.hide()
                self.move_right_button.hide()
        elif property_name == 'showStop':
            if new_value:
                self.stop_button.show()
            else:
                self.stop_button.hide()
        elif property_name == 'showStep':
            if new_value:
                self.step_button.show()
            else:
                self.step_button.hide()
        elif property_name == 'showStepList':
            if new_value:
                self.step_combo.show()
            else:
                self.step_combo.hide()
        elif property_name == 'showPosition':
            if new_value:
                self.position_spinbox.show()
            else:
                self.position_spinbox.hide()
        elif property_name == 'icons':
            icons_list = new_value.split()
            try:
                self.move_left_button.setIcon(Qt4_Icons.load_icon(icons_list[0]))
                self.move_right_button.setIcon(Qt4_Icons.load_icon(icons_list[1]))
                self.stop_button.setIcon(Qt4_Icons.load_icon(icons_list[2]))
                self.set_step_button_icon(icons_list[3])
            except IndexError:
                pass                
        elif property_name == 'helpDecrease':
            if new_value == "":
                self.move_left_button.setToolTip("Moves the motor down (while pressed)")
            else:
                self.move_left_button.set_tool_tip(new_value)
        elif property_name == 'helpIncrease':
            if new_value == "" :
                self.move_right_button.setToolTip("Moves the motor up (while pressed)")
            else:
                self.move_right_button.setToolTip(new_value)
        elif property_name == 'defaultSteps':
            if new_value != "":
                default_step_list = new_value.split()
                for default_step in default_step_list:
                    self.set_line_step(float(default_step))
                self.step_changed(None)
        elif property_name == 'showSlider':
            self.position_slider.setVisible(new_value)
        elif property_name == 'enableSliderTracking':
            self.position_slider.setTracking(new_value)  
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

class StepEditorDialog(QDialog):
    """
    Descript. :
    """

    def __init__(self, parent):
        """
        Descript. :
        """
        QDialog.__init__(self, parent)
        # Graphic elements-----------------------------------------------------
        #self.main_gbox = QtGui.QGroupBox('Motor step', self)
        #box2 = QtGui.QWidget(self)
        self.grid = QWidget(self)
        label1 = QLabel("Current:", self)
        self.current_step = QLineEdit(self)
        self.current_step.setEnabled(False)
        label2 = QLabel("Set to:", self)
        self.new_step = QLineEdit(self)
        self.new_step.setAlignment(Qt.AlignRight)
        self.new_step.setValidator(QDoubleValidator(self))

        self.button_box = QWidget(self)
        self.apply_button = QPushButton("Apply", self.button_box)
        self.close_button = QPushButton("Dismiss", self.button_box)

        # Layout --------------------------------------------------------------
        self.button_box_layout = QHBoxLayout(self.button_box)
        self.button_box_layout.addWidget(self.apply_button)
        self.button_box_layout.addWidget(self.close_button)

        self.grid_layout = QGridLayout(self.grid)
        self.grid_layout.addWidget(label1, 0, 0)
        self.grid_layout.addWidget(self.current_step, 0, 1)
        self.grid_layout.addWidget(label2, 1, 0)
        self.grid_layout.addWidget(self.new_step, 1, 1)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.grid)
        self.main_layout.addWidget(self.button_box)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections -----------------------------------------
        self.new_step.returnPressed.connect(self.apply_clicked)
        self.apply_button.clicked.connect(self.apply_clicked)
        self.close_button.clicked.connect(self.accept)

        # SizePolicies --------------------------------------------------------
        self.close_button.setSizePolicy(QSizePolicy.Fixed,
                                        QSizePolicy.Fixed)
        self.setSizePolicy(QSizePolicy.Minimum,
                           QSizePolicy.Minimum)
 
        # Other ---------------------------------------------------------------
        self.setWindowTitle("Motor step editor")
        self.apply_button.setIcon(Qt4_Icons.load_icon("Check"))
        self.close_button.setIcon(Qt4_Icons.load_icon("Delete"))

    def set_motor(self, motor, brick, name, default_step):
        self.motor_hwobj = motor
        self.brick = brick

        if name is None or name == "":
            name = motor.userName()
        self.setWindowTitle(name)
        self.setWindowTitle('%s step editor' % name)
        self.current_step.setText(str(brick.get_line_step()))

    def apply_clicked(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        try:
            val = float(str(self.new_step.text()))
        except ValueError:
            return
        self.brick.set_line_step(val)
        self.new_step.setText('')
        self.current_step.setText(str(val))
        self.close()

class SpinBoxEvent(QObject):
    returnPressedSignal = pyqtSignal()
    contextMenuSignal = pyqtSignal()

    def eventFilter(self,  obj,  event):
        if event.type() == QEvent.KeyPress:
            if event.key() in [Qt.Key_Enter, 
                               Qt.Key_Return]:
                self.returnPressedSignal.emit()
            
        elif event.type() == QEvent.MouseButtonRelease:
            self.returnPressedSignal.emit()
        elif event.type() == QEvent.ContextMenu:
            self.contextMenuSignal.emit()
        return False
