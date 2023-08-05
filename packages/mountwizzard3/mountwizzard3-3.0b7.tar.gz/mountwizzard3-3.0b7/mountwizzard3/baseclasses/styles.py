############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #  ####
#      ##  ##  #  ##  #     #
#     # # # #  # # # #     ###
#    #  ##  #  ##  ##        #
#   #   #   #  #   #     ####
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.4
#
# Michael Würtenberger
# (c) 2016, 2017, 2018
#
# Licence APL2.0
#
###########################################################
import logging
import PyQt5


class MWStyles:

    COLOR_ASTRO = PyQt5.QtGui.QColor(32, 144, 192)
    COLOR_BLUE = PyQt5.QtGui.QColor(0, 0, 255)
    COLOR_YELLOW = PyQt5.QtGui.QColor(192, 192, 0)
    COLOR_GREEN = PyQt5.QtGui.QColor(0, 255, 0)
    COLOR_WHITE = PyQt5.QtGui.QColor(255, 255, 255)
    COLOR_RED = PyQt5.QtGui.QColor(255, 0, 0)
    COLOR_ORANGE = PyQt5.QtGui.QColor(192, 96, 96)
    COLOR_BLACK = PyQt5.QtGui.QColor(0, 0, 0)

    # define the basic style of the mountwizzard3 theme
    # rise the font size for retina displays
    MAC_STYLE = """
    QWidget {
        background-color: #181818;
        font-family: Arial;
        font-style: normal;
        font-size: 13pt;
    }
    QWidget[large='true'] {
        font-size: 36pt;
    }
    QGroupBox{
        font-family: Arial;
        font-style: normal;
        font-size: 10pt;
    } 
    """
    NON_MAC_STYLE = """
    QWidget {
        background-color: #181818;
        font-family: Arial;
        font-style: normal;
        font-size: 10pt;
    }
    QWidget[large='true'] {
        font-size: 28pt;
    } 
    QGroupBox{
        font-family: Arial;
        font-style: normal;
        font-size: 8pt;
    }     
    """
    BASIC_STYLE = """
    QToolTip {
        border-width: 2px;
        border-style: outset;
        border-color: #404040;
        background-color: #202020;
        color: #C0C0C0;
        padding: 5px;
    }
    QLabel {
        background-color: transparent;
        color: #C0C0C0;
    }
    QLabel[color='blue'] {
        border-width: 3px;
        border-color: rgb(16, 72, 96);
        border-style: outset;
        border-radius: 2px;
        background-color: rgb(9, 36, 48);
    }
    QLabel[iconpicture='true'] {
        border-width: 2px;
        border-color: #404040;
        border-style: outset;
        border-radius: 2px;
    }
    
    /* QLine Edit*/
    QLineEdit {
        background-color: #000000;
        color: rgb(32, 144, 192);
        text-align: right;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
        border-radius: 2px;
    }
    QLineEdit:disabled {
        border-width: 1px;
        border-color: #000000;
        border-style: flat;
        border-radius: 2px;
    }
    QLineEdit {
        border-width: 1px;
        border-color: red;
        border-style: flat;
        border-radius: 2px;
    }
    QLineEdit[check='false'] {
        background-color: #101010;
        color: rgb(255, 0, 0);
    }
    QLineEdit[check='true'] {
        background-color: #101010;
        color: rgb(32, 144, 192);
    }
    
    /* Checkboxes */
    QCheckBox {
        color: #C0C0C0;
        spacing: 8px;
        background-color: transparent;
    }
    QCheckBox::indicator {
        border-width: 1px;
        border-color: #404040;
        background-color: #101010;
        border-style: outset;
        border-radius: 2px;
        width: 13px;
        height: 13px;
    }
    QCheckBox::indicator:checked {
        background-color: rgb(32, 144, 192);
        image: url(:/checkmark.ico);
    }

    /* Group Box */
    QGroupBox {
        background-color: #181818;
        border-width: 1px;
        border-style: outset;
        border-radius: 3px;
        border-color: #404040;
        margin-top: 6px;
    }
    QGroupBox::title {
        left: 5px;
        subcontrol-origin: margin;
        subcontrol-position: top left; /* position at the top center */
        color: #C0C0C0;
        background-color: #181818;
    }
    QRadioButton {
        color: #C0C0C0;
        background-color: transparent;
    }
    QRadioButton:disabled {
        color: #404040;
        background-color: transparent;
    }
    QRadioButton::indicator {
        border-width: 1px;
        border-color: #404040;
        background-color: #101010;
        border-style: outset;
        border-radius: 2px;
        width: 13px;
        height: 13px;
    }
    QRadioButton::indicator:checked {
        background-color: rgb(32, 144, 192);
        image: url(:/checkmark.ico);
    }
    
    /* Spin Boxes */
    QDoubleSpinBox {
        background-color: #101010;
        color: rgb(32, 144, 192);
        text-align: right;

        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        padding-right: 2px;
    }
    QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right; /* position at the top right corner */
        width: 12px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
        border-width: 1px;
        border-radius: 2px;
        border-color: #404040;
        border-style: outset;
        background-color: #181818;
    }
    QDoubleSpinBox::up-arrow {
        image: url(:/arrow-up.ico);
        width: 12px;
        height: 16px;
    }
    QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right; /* position at the top right corner */
        width: 12px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        border-color: #404040;
        background-color: #181818;
    }
    QDoubleSpinBox::down-arrow {
        image: url(:/arrow-down.ico);
        width: 12px;
        height: 16px;
    }
    
    /* Push Buttons */
    QPushButton {
        background-color: #202020;
        color: #C0C0C0;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        min - width: 10em;
    }

    QInputDialog QPushButton {
        background-color: #202020;
        color: #C0C0C0;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        min-width: 90px;
        min-height: 25px;
    }
    QInputDialog QPushButton:default {
        border-width: 2px;
        border-color: rgb(32, 144, 192);
    }

    QMessageBox QPushButton {
        background-color: #202020;
        color: #C0C0C0;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        min-width: 90px;
        min-height: 25px;
    }
    QMessageBox QPushButton:default {
        border-width: 2px;
        border-color: rgb(32, 144, 192);
    }

    QListWidget {
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        color: #C0C0C0;
        padding-left: 5px;
        padding-top: 5px;
    }

    QPushButton:pressed {
        border-color: #404040;
        border-width: 2px;
        border-style: inset;
        border-radius: 2px;
    }
    QPushButton[running='false'] {
        background-color: #202020;
        color: #C0C0C0;
    }     
    QPushButton[running='true'] {
        background-color: rgb(32, 144, 192);
        color: #000000;
    } 
    QPushButton[cancel='true'] {
        background-color: rgb(192,0, 0);
        color: #C0C0C0;
    } 
    QPushButton[cancel='false'] {
        background-color: #202020;
        color: #C0C0C0;
    }
    QPushButton[iconset='true'] {
        text-align: center;
        padding-left: 3px;
        padding-right: 3px;
    }
    QPushButton:focus {
        outline: none;
    }
    QPushButton:disabled {
        background-color: #101010;
        color: #202020;
        border-color: #202020;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
    }
    QPushButton[color='gray'] {
        background-color: gray;
        color: #000000;
    }
    QPushButton[color='red'] {
        background-color: red;
        color: #000000;
    }
    QPushButton[color='yellow'] {
        background-color: yellow;
        color: #000000;
    }
    QPushButton[color='green'] {
        background-color: green;
        color: #000000;
    }
    /* Combo Boxes */
    QComboBox {
        combobox-popup: 0;
        color: #C0C0C0;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        padding-left: 5px;
        background-color: #202020;
    }
    QComboBox::drop-down {
        subcontrol-origin: border;
        subcontrol-position: right; /* position at the top right corner */
        width: 20px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        background-color: #202020;
    }
    QComboBox::down-arrow {
        image: url(:/arrow-down.ico);
        width: 20px;
        height: 31px;
    }
     QComboBox QListView {
        border-width: 2px;
        border-style: outset;
        border-color: #404040;
        border-radius: 2px;
        color: #C0C0C0;
        background-color: #101010;
        min-height: 60px;
    }
    QComboBox QListView::item {
        min-height: 28px;
    }
    QComboBox QListView::item:selected { 
        border-width: 1px;
        border-style: outset;
        border-color: #404040;
        border-radius: 2px; 
        color: #101010;
        background-color: rgb(32, 144, 192);
    }
    QComboBox QListView::item:!selected { 
    }

    /* lines */
    QFrame[frameShape="4"] {/* horizontal lines */
        color: rgb(16, 72, 96);
    }
    QFrame[frameShape="5"] {/* vertical lines */
        color: rgb(16, 72, 96);
    }
    
    /* tab widget */
    QTabWidget:pane {
        border-width: 2px;
        border-color: #404040;
        border-radius: 2px;
        border-style: outset;
    }
    /* needed for MAC OSX */
    QTabWidget:tab-bar {
        alignment: center;
    }
    QTabBar::tab {
        background-color: #202020;
        color: #C0C0C0;
        border-width: 2px;
        border-color: rgb(16, 72, 96);
        border-radius: 2px;
        border-style: outset;
        padding: 4px;
        padding-left: 4px;
        padding-right: 4px;
    }
    QTabBar::tab:selected {
        color: #000000;
        background: rgb(32, 144, 192);
    }
    QTabBar::tab:!selected {
        margin-top: 4px;
    }
    QTabBar::tab:only-one {
        margin: 1;
    }
    QTabBar::tab:!enabled {
        color: #404040;
        border-color: #202020;
    }
    
    /* scroll bar */
    QScrollBar:vertical
    {   background-color: #202020;
        width: 20px;
        margin: 20px 3px 20px 3px;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical
    {   background-color:  rgb(32, 144, 192);
        min-height: 10px;
        border-radius: 3px;
    }
    QScrollBar::sub-line:vertical
    {   margin: 3px 0px 3px 0px;
        border-image: url(:arrow-up.ico);
        height: 16px;
        width: 16px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::add-line:vertical
    {   margin: 3px 0px 3px 0px;
        border-image: url(:arrow-down.ico);
        height: 16px;
        width: 16px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical:on
    {   border-image: url(:arrow-up.png);
        height: 16px;
        width: 16px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::add-line:vertical:on
    {   border-image: url(:arrow-down.png);
        height: 16px;
        width: 16px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
    {   background: none;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
        border-radius: 4px;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
    {   background: none;
    }    

    /* progress bar */
    QProgressBar {
        background-color: #101010;
        border-radius: 3px;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
    }
    QProgressBar::chunk {
        background-color: rgb(32, 144, 192);
        width: 1px;
        margin: 0px;
        border-width: 0px; 
        border-color: #404040;
        border-radius: 0px;
        border-style: outset;
    }
    QTextBrowser {
        background-color: #101010;
        border-radius: 3px;
        border-width: 2px;
        border-color: #404040;
        border-style: outset;
        margin: -5px;
    }
    """