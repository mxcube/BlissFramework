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

from os import path

try:
   from PyQt5 import QtGui
except:
   from PyQt4 import QtGui


ICONS_DIR = path.join(path.dirname(__file__), 'Icons')


def load(icon_name): 
    """
    Descript. : Try to load an icon from file and return the QPixmap object
    """
    filename = path.join(ICONS_DIR, icon_name)

    if not path.exists(filename):
        for ext in ['png', 'xpm', 'gif', 'bmp']:
            f = '.'.join([filename, ext])
            if path.exists(f):
                filename = f
                break
        
    try:
        icon = QtGui.QPixmap(filename)
    except:
        return QtGui.QPixmap(path.join(ICONS_DIR, 'brick.png'))
    else:
        if icon.isNull():
            return QtGui.QPixmap(path.join(ICONS_DIR, 'brick.png'))
        else:
            return icon

def getIconPath(icon_name):
    """
    Descript. : Return path to an icon
    """
    filename = path.join(ICONS_DIR, icon_name)

    if not path.exists(filename):
        for ext in ['png', 'xpm', 'gif', 'bmp']:
            f = '.'.join([filename, ext])
            if path.exists(f):
                filename = f
                break
    
    if path.exists(filename):
        return filename
        
def load_icon(icon_name):
    return QtGui.QIcon(load(icon_name))

def load_pixmap(icon_name):
    return load(icon_name)
