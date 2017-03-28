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

from QtImport import *

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Utils.Qt4_widget_colors import color_to_hexa
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = "General"


class Qt4_AttenuatorsBrick(BlissWidget):
    """
    Descript. : 
    """

    states = {
       "ON":  color_to_hexa( Qt4_widget_colors.LIGHT_GREEN),
       "MOVING": color_to_hexa( Qt4_widget_colors.LIGHT_YELLOW),
       "FAULT":  color_to_hexa( Qt4_widget_colors.LIGHT_RED),
       "UNKNOWN": color_to_hexa( Qt4_widget_colors.DARK_GRAY),
    }

    def __init__(self, *args):
        """
        Descript. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.attenuators_hwobj = None

        # Internal variables --------------------------------------------------

        # Properties ---------------------------------------------------------- 
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('mockup_mnemonic', 'string', '')
        self.addProperty('formatString', 'formatString', '###.##')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = QGroupBox("Transmission", self)
        current_label = QLabel("Current:", self.group_box)
        current_label.setFixedWidth(75)
        self.transmission_ledit = QLineEdit(self.group_box)
        self.transmission_ledit.setReadOnly(True)
        set_to_label = QLabel("Set to:", self.group_box)
        self.new_value_ledit = QLineEdit(self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_gridlayout = QGridLayout(self.group_box)
        _group_box_gridlayout.addWidget(current_label, 0, 0)
        _group_box_gridlayout.addWidget(self.transmission_ledit, 0, 1)
        _group_box_gridlayout.addWidget(set_to_label, 1, 0)
        _group_box_gridlayout.addWidget(self.new_value_ledit, 1, 1)
        _group_box_gridlayout.setSpacing(0)
        _group_box_gridlayout.setContentsMargins(1, 1, 1, 1)

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 2, 2)
        _main_vlayout.addWidget(self.group_box)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.new_value_ledit.returnPressed.connect(self.current_value_changed)
        self.new_value_ledit.textChanged.connect(self.input_field_changed)

        # Other --------------------------------------------------------------- 
        Qt4_widget_colors.set_widget_color(self.new_value_ledit,
                                       Qt4_widget_colors.LINE_EDIT_ACTIVE,
                                       QPalette.Base)
        self.new_value_validator = QDoubleValidator(\
             0, 100, 2, self.new_value_ledit)
        self.new_value_ledit.setToolTip("Transmission limits 0 : 100 %")

        self.instance_synchronize("transmission_ledit", "new_value_ledit")

    def propertyChanged(self, property_value, old_value, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if property_value == 'mnemonic':
            if self.attenuators_hwobj is not None:
                self.disconnect(self.attenuators_hwobj,
                                'deviceReady',
                                self.connected)
                self.disconnect(self.attenuators_hwobj,
                                'deviceNotReady',
                                self.disconnected)
                self.disconnect(self.attenuators_hwobj,
                                'attStateChanged',
                                self.transmission_state_changed)
                self.disconnect(self.attenuators_hwobj,
                                'attFactorChanged',
                                self.transmission_value_changed)
            self.attenuators_hwobj = self.getHardwareObject(new_value)
            if self.attenuators_hwobj is not None:
                self.connect(self.attenuators_hwobj,
                             'deviceReady',
                             self.connected)
                self.connect(self.attenuators_hwobj,
                             'deviceNotReady',
                             self.disconnected)
                self.connect(self.attenuators_hwobj,
                             'attStateChanged',
                             self.transmission_state_changed)
                self.connect(self.attenuators_hwobj,
                             'attFactorChanged',
                             self.transmission_value_changed)
                if self.attenuators_hwobj.isReady():
                    self.connected()
                    self.attenuators_hwobj.update_values() 
                else:
                    self.disconnected()
            else:
                self.disconnected()
        else:
            BlissWidget.propertyChanged(self, property_value, old_value, new_value)

    def input_field_changed(self, input_field_text):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.new_value_validator.validate(input_field_text, 0)[0] == \
           QValidator.Acceptable:
            Qt4_widget_colors.set_widget_color(\
                self.new_value_ledit,
                Qt4_widget_colors.LINE_EDIT_CHANGED,
                QPalette.Base)
        else:
           Qt4_widget_colors.set_widget_color(\
                self.new_value_ledit,
                Qt4_widget_colors.LINE_EDIT_ERROR,
                QPalette.Base)

    def current_value_changed(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        input_field_text = self.new_value_ledit.text()

        if self.new_value_validator.validate(input_field_text, 0)[0] == \
           QValidator.Acceptable:
            self.attenuators_hwobj.setTransmission(\
                 float(input_field_text))
            self.new_value_ledit.setText("") 
            Qt4_widget_colors.set_widget_color(\
                 self.new_value_ledit,
                 Qt4_widget_colors.LINE_EDIT_ACTIVE,
                 QPalette.Base)

    def connected(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.setEnabled(True)

    def disconnected(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.setEnabled(False)

    def transmission_state_changed(self, transmission_state):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if transmission_state in self.states: 
            color = self.states[transmission_state]
        else: 
            color = self.states["UNKNOWN"]

    def transmission_value_changed(self, new_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        try:
           new_values_str = self['formatString'] % new_value
           self.transmission_ledit.setText("%s %%" % new_values_str)
        except:
           pass
