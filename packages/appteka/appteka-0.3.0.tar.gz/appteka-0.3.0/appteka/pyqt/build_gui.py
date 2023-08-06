""" Helper functions for building Qt GUI. """

from PyQt5 import QtWidgets, QtGui

def add_action(window, name, slot, pic=None, shortcut=None, menu=None):
    action = None
    if pic:
        action = QtWidgets.QAction(QtGui.QIcon(pic), name, window)
    else:
        action = QtWidgets.QAction(name, window)
    action.triggered.connect(slot)
    if shortcut:
        action.setShortcut(shortcut)
    if menu is not None:
        menu.addAction(action)
    return action

def add_sublayout(parent_layout, direction="h"):
    if direction.lower() == "h":
        layout = QtWidgets.QHBoxLayout()
    elif direction.lower() == "v":
        layout = QtWidgets.QVBoxLayout()
    else:
        return None
    parent_layout.addLayout(layout)
    return layout

def add_button(text, slot, layout):
    button = QtWidgets.QPushButton(text)
    button.clicked.connect(slot)
    layout.addWidget(button)
    return button

def add_edit(layout):
    edit = QtWidgets.QLineEdit()
    layout.addWidget(edit)
    return edit

def add_label(text, layout):
    label = QtWidgets.QLabel(text)
    layout.addWidget(label)
    return label

def add_widget(widget, layout):
    layout.addWidget(widget)
    return widget
