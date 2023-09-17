# Mouse Keyboard Clicker Holder v2.0
# Website: https://sourceforge.net/projects/keyboard-clicker-holder/
from sys import argv
from sys import exit as app_exit
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QRadioButton, QHBoxLayout, QStackedLayout, QVBoxLayout, QButtonGroup, QFormLayout, QLineEdit, QGroupBox, QGridLayout, QTabWidget, QTextBrowser
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QIntValidator
from pynput import keyboard, mouse
from threading import Thread
from time import sleep
from os import path
class MainWindow(QMainWindow):
    # Variable used to check whether the program is currently autoclicking/holding or not
    isRunning = False
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Key Clicker Holder")
        # Disable maximize button
        # The window is made non-resizable at the end of the code, when the program is started
        # self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        MainWindow.actionWidget = actionWidget()
        MainWindow.buttonSelectionWidget = buttonWidget()
        MainWindow.deviceWidget = deviceWidget()
        MainWindow.holdWidget = holdWidget()
        MainWindow.autoclickWidget = autoclickWidget()
        MainWindow.infoText = infoText()
        MainWindow.isSettingKey = False
        MainWindow.isSettingHotkey = False
        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(MainWindow.actionWidget, alignment=Qt.AlignTop)
        self.masterLayout.addWidget(MainWindow.deviceWidget, alignment=Qt.AlignTop)
        self.masterLayout.addWidget(MainWindow.buttonSelectionWidget, alignment=Qt.AlignTop)
        self.masterLayout.addWidget(MainWindow.autoclickWidget, alignment=Qt.AlignTop)
        self.masterLayout.addWidget(MainWindow.holdWidget, alignment=Qt.AlignTop)
        self.masterLayout.addWidget(MainWindow.infoText, alignment=Qt.AlignBottom)
        self.masterWidget = QWidget()
        self.masterWidget.setLayout(self.masterLayout)
        self.setCentralWidget(self.masterWidget)
        MainWindow.keyboardListener = keyboardListener()
        MainWindow.selectedKey = None
        MainWindow.selectedHotkey = keyboard.Key.f6
        holdWidget.changeState(self=MainWindow.holdWidget, state=False)
    def changeWidgetState(self, stateToChange):
        # This method is used to quickly disable and enable the buttons of the UI while the program is changing the key to be pressed or the program hotkey
        # It links to the .changeState() methods of each widget class
        buttonWidget.changeState(self=MainWindow.buttonSelectionWidget, state=stateToChange)
        deviceWidget.changeState(self=MainWindow.deviceWidget, value=stateToChange)
        actionWidget.changeState(self=MainWindow.actionWidget, value=stateToChange)
        if MainWindow.actionWidget.actionGroup.checkedButton() == MainWindow.actionWidget.holdButton:
            holdWidget.changeState(self=MainWindow.holdWidget, state=stateToChange)
        else:
            autoclickWidget.changeState(self=MainWindow.autoclickWidget, state=stateToChange)
        infoText.changeState(self=MainWindow.infoText, value=stateToChange)
    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            window.close()
class keyboardListener():
    def __init__(self):
        self.keyboardListener = keyboard.Listener(on_press=self.handleKeyPress)
        self.keyboardListener.start()
    def handleKeyPress(self, key):
        if MainWindow.isSettingKey == True:
            if MainWindow.deviceWidget.isActiveWindow() == True:
                if key == MainWindow.selectedHotkey:
                    print('Cannot select the current hotkey as the key to be pressed')
                    MainWindow.infoText.setErrorLabelText('Cannot select the hotkey as the key to be pressed')
                    return
                MainWindow.selectedKey = key
                buttonWidget.changeSelectedKey(self=MainWindow.buttonSelectionWidget, key=key)
                MainWindow.changeWidgetState(self=MainWindow, stateToChange=True)
                MainWindow.infoText.setErrorLabelText('')
            elif MainWindow.deviceWidget.isActiveWindow() == False:
                return
            MainWindow.isSettingKey = False
        elif MainWindow.isSettingHotkey == True:
            if MainWindow.deviceWidget.isActiveWindow() == True:
                MainWindow.selectedHotkey = key
                if key == MainWindow.selectedKey:
                    print('Cannot select the current key to be pressed as the hotkey')
                    MainWindow.infoText.setErrorLabelText('Cannot select the current key as the hotkey')
                    return
                infoText.changeHotkey(self=MainWindow.infoText, key=key)
                MainWindow.changeWidgetState(self=MainWindow, stateToChange=True)
                MainWindow.infoText.setErrorLabelText('')
            elif MainWindow.deviceWidget.isActiveWindow() == False:
                return
            MainWindow.isSettingHotkey = False
        elif MainWindow.isSettingKey == False and MainWindow.isSettingHotkey == False:
            if key == MainWindow.selectedHotkey:
                # Check if already running
                if MainWindow.isRunning == False:
                    # Check if the autoclick button is toggled on
                    if MainWindow.actionWidget.actionGroup.checkedButton() == MainWindow.actionWidget.autoclickButton:
                        autoclickFrequency = int(MainWindow.autoclickWidget.frequencyField.text()) / 1000
                        if autoclickFrequency == 0:
                            MainWindow.infoText.setErrorLabelText('0 ms is not a valid frequency')
                            print('0 ms is not a valid frequency')
                            return
                        if MainWindow.autoclickWidget.repeatWidget.repeatButtonGroup.checkedButton() == MainWindow.autoclickWidget.repeatWidget.repeatInfinitelyButton:
                            repeatTimes = None
                        elif MainWindow.autoclickWidget.repeatWidget.repeatButtonGroup.checkedButton() == MainWindow.autoclickWidget.repeatWidget.repeatLimitedButton:
                            repeatTimes = int(MainWindow.autoclickWidget.repeatWidget.repeatLimitedField.text())
                            if repeatTimes == 0:
                                MainWindow.infoText.setErrorLabelText('Cannot autoclick 0 times')
                                print('Cannot autoclick 0 times')
                                return
                        MainWindow.infoText.setErrorLabelText('')
                        # Check if the mouse button is toggled on
                        if MainWindow.deviceWidget.deviceGroup.checkedButton() == MainWindow.deviceWidget.mouseButton:
                            selectedMouseButton = MainWindow.buttonSelectionWidget.mouseButtonSelectionGroup.checkedButton()
                            if selectedMouseButton == MainWindow.buttonSelectionWidget.leftClickButton:
                                selectedMouseButton = mouse.Button.left
                            elif selectedMouseButton == MainWindow.buttonSelectionWidget.middleClickButton:
                                selectedMouseButton = mouse.Button.middle
                            elif selectedMouseButton == MainWindow.buttonSelectionWidget.rightClickButton:
                                selectedMouseButton = mouse.Button.right
                            print(f'Starting autoclicking of the mouse (button: {str(selectedMouseButton)}, frequency: {str(autoclickFrequency)})')
                            MainWindow.isRunning = True
                            mouseAutoclicker = Thread(target=mouseAutoclick, args=(selectedMouseButton, autoclickFrequency, repeatTimes))
                            mouseAutoclicker.daemon = True
                            mouseAutoclicker.start()
                        if MainWindow.deviceWidget.deviceGroup.checkedButton() == MainWindow.deviceWidget.keyboardButton:
                            selectedKey = MainWindow.selectedKey
                            if selectedKey == None:
                                print('No key has been selected')
                                MainWindow.infoText.setErrorLabelText('No key has been selected')
                                return
                            print(f'Starting autoclicking of the keyboard (key: {str(selectedKey)}, frequency: {str(autoclickFrequency)})')
                            MainWindow.isRunning = True
                            keyboardAutoclicker = Thread(target=keyAutoclick, args=(selectedKey, autoclickFrequency, repeatTimes))
                            keyboardAutoclicker.daemon = True
                            keyboardAutoclicker.start()
                    elif MainWindow.actionWidget.actionGroup.checkedButton() == MainWindow.actionWidget.holdButton:
                        holdTime = int(MainWindow.holdWidget.holdTimeField.text()) / 1000
                        waitTime = int(MainWindow.holdWidget.waitTimeField.text()) / 1000
                        MainWindow.infoText.setErrorLabelText('')
                        if MainWindow.deviceWidget.deviceGroup.checkedButton() == MainWindow.deviceWidget.mouseButton:
                            selectedMouseButton = MainWindow.buttonSelectionWidget.mouseButtonSelectionGroup.checkedButton()
                            if selectedMouseButton == MainWindow.buttonSelectionWidget.leftClickButton:
                                selectedMouseButton = mouse.Button.left
                            elif selectedMouseButton == MainWindow.buttonSelectionWidget.middleClickButton:
                                selectedMouseButton = mouse.Button.middle
                            elif selectedMouseButton == MainWindow.buttonSelectionWidget.rightClickButton:
                                selectedMouseButton = mouse.Button.right
                            print(f'Starting holding of mouse (button: {str(selectedMouseButton)})')
                        if MainWindow.holdWidget.repeatWidget.repeatButtonGroup.checkedButton() == MainWindow.holdWidget.repeatWidget.repeatInfinitelyButton:
                            repeatTimes = None
                        elif MainWindow.holdWidget.repeatWidget.repeatButtonGroup.checkedButton() == MainWindow.holdWidget.repeatWidget.repeatLimitedButton:
                            repeatTimes = int(MainWindow.holdWidget.repeatWidget.repeatLimitedField.text())
                            if repeatTimes == 0:
                                MainWindow.infoText.setErrorLabelText('Cannot autoclick 0 times')
                                print('Cannot autoclick 0 times')
                                return
                            MainWindow.isRunning = True
                            self.mouseHolder = Thread(target=mouseHold, args=(selectedMouseButton, holdTime, waitTime, repeatTimes))
                            self.mouseHolder.daemon = True
                            self.mouseHolder.start()
                        if MainWindow.deviceWidget.deviceGroup.checkedButton() == MainWindow.deviceWidget.keyboardButton:
                            selectedKey = MainWindow.selectedKey
                            if selectedKey == None:
                                print('No key has been selected!')
                                pass
                            print(f'Starting holding of the keyboard (key: {str(selectedKey)})')
                            MainWindow.isRunning = True
                            keyboardHolder = Thread(target=keyHold, args=(selectedKey, holdTime, waitTime, repeatTimes))
                            keyboardHolder.daemon = True
                            keyboardHolder.start()
                elif MainWindow.isRunning == True:
                    print('Stopping activity')
                    MainWindow.isRunning = False
class actionWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Action')
        self.actionLayout = QHBoxLayout()
        self.actionGroup = QButtonGroup()
        self.autoclickButton = QRadioButton('Autoclick')
        self.autoclickButton.toggle()
        self.actionLayout.addWidget(self.autoclickButton)
        self.actionGroup.addButton(self.autoclickButton)
        self.holdButton = QRadioButton('Hold')
        self.actionLayout.addWidget(self.holdButton)
        self.actionGroup.addButton(self.holdButton)
        self.setLayout(self.actionLayout)
        self.actionGroup.buttonToggled.connect(self.updateAutoclickWidget)
    def updateAutoclickWidget(self, buttonPressed):
        if buttonPressed == self.autoclickButton:
            print('Autoclick radio button pressed, adjusting UI controls')
            MainWindow.autoclickWidget.changeState(True)
            MainWindow.holdWidget.changeState(False)
        elif buttonPressed == self.holdButton:
            print('Hold radio button pressed, adjusting UI controls')
            MainWindow.autoclickWidget.changeState(False)
            MainWindow.holdWidget.changeState(True)
    def changeState(self, value):
        self.autoclickButton.setEnabled(value)
        self.holdButton.setEnabled(value)
class deviceWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Device')
        self.deviceLayout = QHBoxLayout()
        self.deviceGroup = QButtonGroup()
        self.mouseButton = QRadioButton('Mouse')
        self.mouseButton.toggle()
        self.deviceLayout.addWidget(self.mouseButton)
        self.deviceGroup.addButton(self.mouseButton)
        self.keyboardButton = QRadioButton('Keyboard')
        self.deviceLayout.addWidget(self.keyboardButton)
        self.deviceGroup.addButton(self.keyboardButton)
        self.setLayout(self.deviceLayout)
        self.deviceGroup.buttonToggled.connect(self.updateSelectionWidget)
    def updateSelectionWidget(self, buttonPressed):
        if buttonPressed == self.mouseButton:
            print('Mouse radio button pressed, adjusting UI controls')
            MainWindow.buttonSelectionWidget.changeOptions(0)
        elif buttonPressed == self.keyboardButton:
            print('Keyboard radio button pressed, adjusting UI controls')
            MainWindow.buttonSelectionWidget.changeOptions(1)
    def changeState(self, value):
        self.mouseButton.setEnabled(value)
        self.keyboardButton.setEnabled(value)
class buttonWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Button')
        self.buttonSelectionLayout = QStackedLayout()
        
        self.mouseButtonSelectionWidget = QWidget()
        self.mouseButtonSelectionLayout = QHBoxLayout()
        self.mouseButtonSelectionGroup = QButtonGroup()
        self.leftClickButton = QRadioButton('Left Click')
        self.leftClickButton.toggle()
        self.mouseButtonSelectionLayout.addWidget(self.leftClickButton)
        self.mouseButtonSelectionGroup.addButton(self.leftClickButton)
        self.middleClickButton = QRadioButton('Middle Click')
        self.mouseButtonSelectionLayout.addWidget(self.middleClickButton)
        self.mouseButtonSelectionGroup.addButton(self.middleClickButton)
        self.rightClickButton = QRadioButton('Right Click')
        self.mouseButtonSelectionLayout.addWidget(self.rightClickButton)
        self.mouseButtonSelectionGroup.addButton(self.rightClickButton)
        self.mouseButtonSelectionWidget.setLayout(self.mouseButtonSelectionLayout)

        self.keySelectionWidget = QWidget()
        self.keySelectionLayout = QVBoxLayout()
        self.selectedKeyLabel = QLabel('No key selected')
        self.keySelectionLayout.addWidget(self.selectedKeyLabel)
        self.selectedKeyLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.keySelectionButton = QPushButton('Click and press a key')
        self.keySelectionButton.clicked.connect(self.listenForKey)
        self.keySelectionLayout.addWidget(self.keySelectionButton)
        self.keySelectionWidget.setLayout(self.keySelectionLayout)

        self.buttonSelectionLayout.addWidget(self.mouseButtonSelectionWidget)
        self.buttonSelectionLayout.addWidget(self.keySelectionWidget)
        self.buttonSelectionLayout.setCurrentIndex(0)
        self.setLayout(self.buttonSelectionLayout)

    def changeOptions(self, value):
        # This class method is used by the deviceWidget class
        self.buttonSelectionLayout.setCurrentIndex(value)
        if value == 0:
            self.setTitle('Button')
        elif value == 1:
            self.setTitle('Key')

    def changeSelectedKey(self, key):
        formattedKey = MainWindow.infoText.formatKeyString(key)
        self.selectedKeyLabel.setText(formattedKey)
        self.keySelectionButton.setText('Click and press a key')

    def listenForKey(self):
        self.keySelectionButton.setText('Listening...')
        MainWindow.changeWidgetState(self=MainWindow, stateToChange=False)
        MainWindow.isSettingKey = True

    def changeState(self, state):
        self.keySelectionButton.setEnabled(state)
        self.leftClickButton.setEnabled(state)
        self.middleClickButton.setEnabled(state)
        self.rightClickButton.setEnabled(state)
class holdWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Hold controls')
        self.holdSelectionWidget = QWidget()
        self.holdLayout = QFormLayout()
        
        self.holdTimeField = QLineEdit()
        self.holdTimeValidator = QIntValidator(bottom=1, top=100000000, parent=self.holdTimeField)
        self.holdTimeField.setText('100')
        self.holdTimeField.setValidator(self.holdTimeValidator)
        self.holdLayout.addRow('Hold time (ms):', self.holdTimeField)

        self.waitTimeField = QLineEdit()
        self.waitTimeValidator = QIntValidator(bottom=1, top=100000000, parent=self.waitTimeField)
        self.waitTimeField.setText('100')
        self.waitTimeField.setValidator(self.waitTimeValidator)
        self.holdLayout.addRow('Wait time (ms):', self.waitTimeField)

        self.repeatWidget = repeatWidget()
        self.holdLayout.addRow(self.repeatWidget)

        self.holdSelectionWidget.setLayout(self.holdLayout)

        # Create a widget whose layout only consists of spacing (set to 0)
        self.emptyWidget = QWidget()
        self.emptyLayout = QHBoxLayout()
        self.emptyLayout.addSpacing(0)
        self.emptyWidget.setLayout(self.emptyLayout)

        self.setLayout(self.holdLayout)
    
    def changeState(self, state):
        if state == True:
            self.setTitle('Hold controls')
        elif state == False:
            self.setTitle('Hold controls (disabled)')
        self.holdTimeField.setEnabled(state)
        self.waitTimeField.setEnabled(state)
        self.repeatWidget.repeatInfinitelyButton.setEnabled(state)
        self.repeatWidget.repeatLimitedButton.setEnabled(state)
        self.repeatWidget.repeatLimitedField.setEnabled(state)
class autoclickWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Autoclick controls')
        self.autoclickSelectionWidget = QWidget()
        self.autoclickLayout = QFormLayout()
        
        self.frequencyField = QLineEdit()
        self.autoclickValidator = QIntValidator(bottom=1, top=100000000, parent=self.frequencyField)
        self.frequencyField.setText('100')
        self.frequencyField.setValidator(self.autoclickValidator)
        self.autoclickLayout.addRow('Autoclick frequency (ms):', self.frequencyField)

        self.repeatWidget = repeatWidget()
        self.autoclickLayout.addRow(self.repeatWidget)

        self.autoclickSelectionWidget.setLayout(self.autoclickLayout)

        # Create a widget whose layout only consists of spacing (set to 0)
        self.emptyWidget = QWidget()
        self.emptyLayout = QHBoxLayout()
        self.emptyLayout.addSpacing(0)
        self.emptyWidget.setLayout(self.emptyLayout)

        self.setLayout(self.autoclickLayout)
    
    def changeState(self, state):
        if state == True:
            self.setTitle('Autoclick controls')
        elif state == False:
            self.setTitle('Autoclick controls (disabled)')
        self.frequencyField.setEnabled(state)
        self.repeatWidget.repeatInfinitelyButton.setEnabled(state)
        self.repeatWidget.repeatLimitedButton.setEnabled(state)
        self.repeatWidget.repeatLimitedField.setEnabled(state)

class repeatWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Repeat')
        self.repeatButtonGroup = QButtonGroup()
        self.repeatLayout = QGridLayout()

        self.repeatInfinitelyButton = QRadioButton('Repeat until stopped')
        self.repeatInfinitelyButton.toggle()
        self.repeatLimitedButton = QRadioButton('Repeat')
        self.repeatLimitedField = QLineEdit()
        self.repeatLimitedValidator = QIntValidator(bottom=1, top=100000000, parent=self.repeatLimitedField)
        self.repeatLimitedField.setValidator(self.repeatLimitedValidator)
        self.repeatLimitedField.setText('100')
        self.repeatLimitedLabel = QLabel('times')

        self.repeatButtonGroup.addButton(self.repeatInfinitelyButton)
        self.repeatButtonGroup.addButton(self.repeatLimitedButton)

        self.repeatLayout.addWidget(self.repeatInfinitelyButton, 0, 0, 1, 3)
        self.repeatLayout.addWidget(self.repeatLimitedButton, 1, 0)
        self.repeatLayout.addWidget(self.repeatLimitedField, 1, 1)
        self.repeatLayout.addWidget(self.repeatLimitedLabel, 1, 2)
        self.setLayout(self.repeatLayout)

class infoText(QWidget):
    def __init__(self):
        super().__init__()
        self.infoLabel = QLabel()
        self.programLabel = QLabel()
        self.linkLabel = QLabel()
        self.licenseLabel = QLabel()
        self.errorLabel = QLabel()
        self.changeHotkeyButton = QPushButton()
        self.LabelLayout = QVBoxLayout()
        self.licenseWindow = LicenseWindow()

        self.changeHotkeyButton.setText('Change hotkey')
        self.infoLabel.setText('Press F6 to start or stop')
        self.infoLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.programLabel.setText('Mouse Keyboard Clicker Holder v2.0')
        self.programLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.linkLabel.setText('<a href="https://sourceforge.net/projects/keyboard-clicker-holder/">Official Website</a>')
        self.linkLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.linkLabel.setOpenExternalLinks(True)
        self.licenseLabel.setText('<a href="licenseInformation">View license information</a>')
        self.licenseLabel.linkActivated.connect(lambda: self.licenseWindow.show())
        self.licenseLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.errorLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.errorLabel.setStyleSheet('color: red;')
        self.LabelLayout.addWidget(self.infoLabel, alignment=Qt.AlignTop)
        self.LabelLayout.addWidget(self.changeHotkeyButton, alignment=Qt.AlignCenter)
        self.LabelLayout.addWidget(self.errorLabel, alignment=Qt.AlignTop)
        self.LabelLayout.addWidget(self.programLabel, alignment=Qt.AlignBottom)
        self.LabelLayout.addWidget(self.linkLabel, alignment=Qt.AlignBottom)
        self.LabelLayout.addWidget(self.licenseLabel, alignment=Qt.AlignBottom)
        self.setLayout(self.LabelLayout)
        self.changeHotkeyButton.clicked.connect(self.listenForHotkey)

    def listenForHotkey(self):
        MainWindow.isSettingHotkey = True
        MainWindow.changeWidgetState(self=MainWindow, stateToChange=False)
        self.changeHotkeyButton.setText('Listening...')
    
    def changeHotkey(self, key):
        formattedKey = self.formatKeyString(key)
        print(f'Changing hotkey to {str(key)}')
        print(f'Formatted hotkey string: {formattedKey}')

        self.infoLabel.setText(f'Press {formattedKey} to start or stop')
        self.changeHotkeyButton.setText('Change hotkey')
        MainWindow.selectedHotkey = key
    def formatKeyString(self, key):
        # Format the hotkey for the UI
        # Example: Key.f6 becomes F6
        # Example 2: 'a' becomes a
        formattedKey = str(key)
        if 'Key.' in formattedKey:
            formattedKey = formattedKey.replace('Key.', '')
            formattedKey = formattedKey.upper()
        # If the key to format is the ' key, this makes it show as ' instead of "'"
        # The raw format of "'" is '"\'"'
        if repr(formattedKey) != repr('"\'"'):
            formattedKey = formattedKey.replace("'", "")
        else:
            formattedKey = "'"
        print(f'Formatted key string: {formattedKey} (original: {key})')
        return formattedKey
    def changeState(self, value):
        self.changeHotkeyButton.setEnabled(value)
    def setErrorLabelText(self, text):
        self.errorLabel.setText(text)

class LicenseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('License information')
        self.setMinimumWidth(250)
        self.setMinimumHeight(200)
        self.licenseTabs = QTabWidget()
        self.licenseLayout = QVBoxLayout()
        self.keyClickerLicense = KeyClickerLicenseWidget()
        self.otherSoftwareLicenses = OtherSoftwareLicensesWidget()

        self.licenseTabs.addTab(self.keyClickerLicense, 'License')
        self.licenseTabs.addTab(self.otherSoftwareLicenses, 'Other software used')

        self.licenseLayout.addWidget(self.licenseTabs)
        self.setLayout(self.licenseLayout)

    def closeEvent(self, event):
        self.close()

class KeyClickerLicenseWidget(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setHtml('<p>Mouse Keyboard Clicker Holder is distributed under the Unlicense.</p>\n\r<p>This is free and unencumbered software released into the public domain.</p>\n\r<p>Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.\n\rIn jurisdictions that recognize copyright laws, the author or authors of this software dedicate any and all copyright interest in the software to the public domain. We make this dedication for the benefit of the public at large and to the detriment of our heirs and successors. We intend this dedication to be an overt act of relinquishment in perpetuity of all present and future rights to this software under copyright law.</p>\n\r<p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>\n\r<p>For more information, please refer to <a href="https://unlicense.org">&lt;https://unlicense.org&gt;</a></p><p>Mouse Keyboard Clicker Holder is available at <a href="https://sourceforge.net/projects/keyboard-clicker-holder/">&lt;https://sourceforge.net/projects/keyboard-clicker-holder/&gt;</a></p>')
        self.setOpenExternalLinks(True)

class OtherSoftwareLicensesWidget(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setHtml("""<p>Mouse Keyboard Clicker Holder has been made using other software as libraries</p><p>Software used:<ul><li>Python 3.11.0</li><li>These default python libraries:<ul><li>sys</li><li>threading</li><li>time</li><li>os</li></ul></li><li>Other Python libraries:<ul><li>PySide6</li></ul></li></ul></p><p>PyInstaller has been used to create the compiled .exe files.</p><p>Additional licenses and copyright notices of the libraries:</p><p>Python 3.11.0:</p><p>Copyright notice: Copyright © 2001-2022 Python Software Foundation; All Rights Reserved</p><p>License:<br><br> 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and    the Individual or Organization ("Licensee") accessing and otherwise using Python    3.11.0 software in source or binary form and its associated documentation. <br><br> 2. Subject to the terms and conditions of this License Agreement, PSF hereby    grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,    analyze, test, perform and/or display publicly, prepare derivative works,    distribute, and otherwise use Python 3.11.0 alone or in any derivative    version, provided, however, that PSF's License Agreement and PSF's notice of    copyright, i.e., "Copyright © 2001-2022 Python Software Foundation; All Rights    Reserved" are retained in Python 3.11.0 alone or in any derivative version    prepared by Licensee. <br><br> 3. In the event Licensee prepares a derivative work that is based on or    incorporates Python 3.11.0 or any part thereof, and wants to make the    derivative work available to others as provided herein, then Licensee hereby    agrees to include in any such work a brief summary of the changes made to Python    3.11.0. <br><br> 4. PSF is making Python 3.11.0 available to Licensee on an "AS IS" basis.    PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED.  BY WAY OF    EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR    WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE    USE OF PYTHON 3.11.0 WILL NOT INFRINGE ANY THIRD PARTY RIGHTS. <br><br> 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON 3.11.0    FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS A RESULT OF    MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON 3.11.0, OR ANY DERIVATIVE    THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF. <br><br> 6. This License Agreement will automatically terminate upon a material breach of    its terms and conditions. <br><br> 7. Nothing in this License Agreement shall be deemed to create any relationship    of agency, partnership, or joint venture between PSF and Licensee.  This License    Agreement does not grant permission to use PSF trademarks or trade name in a    trademark sense to endorse or promote products or services of Licensee, or any    third party. <br><br> 8. By copying, installing or otherwise using Python 3.11.0, Licensee agrees    to be bound by the terms and conditions of this License Agreement.</p><p><br>PySide6:</p><p>Copyright notice: © 2022 The Qt Company</p><p>The source code of PySide6 can be obtained at <a href="https://pypi.org/project/PySide6/">&lt;https://pypi.org/project/PySide6/&gt;</a>. No modifications have been applied to the PySide6 library.</p><p>License:</p><p>                   GNU LESSER GENERAL PUBLIC LICENSE
<br>Version 3, 29 June 2007 <br>  Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>  Everyone is permitted to copy and distribute verbatim copies  of this license document, but changing it is not allowed. <br>   This version of the GNU Lesser General Public License incorporates the terms and conditions of version 3 of the GNU General Public License, supplemented by the additional permissions listed below. <br>   0. Additional Definitions. <br>   As used herein, "this License" refers to version 3 of the GNU Lesser General Public License, and the "GNU GPL" refers to version 3 of the GNU General Public License. <br>   "The Library" refers to a covered work governed by this License, other than an Application or a Combined Work as defined below. <br>   An "Application" is any work that makes use of an interface provided by the Library, but which is not otherwise based on the Library. Defining a subclass of a class defined by the Library is deemed a mode of using an interface provided by the Library. <br>   A "Combined Work" is a work produced by combining or linking an Application with the Library.  The particular version of the Library with which the Combined Work was made is also called the "Linked Version". <br>   The "Minimal Corresponding Source" for a Combined Work means the Corresponding Source for the Combined Work, excluding any source code for portions of the Combined Work that, considered in isolation, are based on the Application, and not on the Linked Version. <br>   The "Corresponding Application Code" for a Combined Work means the object code and/or source code for the Application, including any data and utility programs needed for reproducing the Combined Work from the Application, but excluding the System Libraries of the Combined Work. <br><br>   1. Exception to Section 3 of the GNU GPL. <br><br> You may convey a covered work under sections 3 and 4 of this License without being bound by section 3 of the GNU GPL. <br><br>   2. Conveying Modified Versions. <br><br>   If you modify a copy of the Library, and, in your modifications, a facility refers to a function or data to be supplied by an Application that uses the facility (other than as an argument passed when the facility is invoked), then you may convey a copy of the modified version: <br>    a) under this License, provided that you make a good faith effort to    ensure that, in the event an Application does not supply the    function or data, the facility still operates, and performs    whatever part of its purpose remains meaningful, or <br>    b) under the GNU GPL, with none of the additional permissions of    this License applicable to that copy. <br><br>   3. Object Code Incorporating Material from Library Header Files. <br><br>   The object code form of an Application may incorporate material from a header file that is part of the Library.  You may convey such object code under terms of your choice, provided that, if the incorporated material is not limited to numerical parameters, data structure layouts and accessors, or small macros, inline functions and templates (ten or fewer lines in length), you do both of the following: <br>    a) Give prominent notice with each copy of the object code that the    Library is used in it and that the Library and its use are    covered by this License. <br>    b) Accompany the object code with a copy of the GNU GPL and this license    document. <br><br>   4. Combined Works. <br><br> You may convey a Combined Work under terms of your choice that, taken together, effectively do not restrict modification of the portions of the Library contained in the Combined Work and reverse engineering for debugging such modifications, if you also do each of the following: <br>    a) Give prominent notice with each copy of the Combined Work that    the Library is used in it and that the Library and its use are    covered by this License. <br>    b) Accompany the Combined Work with a copy of the GNU GPL and this license    document. <br>    c) For a Combined Work that displays copyright notices during    execution, include the copyright notice for the Library among    these notices, as well as a reference directing the user to the    copies of the GNU GPL and this license document. <br>    d) Do one of the following: <br>        0) Convey the Minimal Corresponding Source under the terms of this        License, and the Corresponding Application Code in a form        suitable for, and under terms that permit, the user to        recombine or relink the Application with a modified version of        the Linked Version to produce a modified Combined Work, in the        manner specified by section 6 of the GNU GPL for conveying        Corresponding Source. <br>        1) Use a suitable shared library mechanism for linking with the        Library.  A suitable mechanism is one that (a) uses at run time        a copy of the Library already present on the user's computer        system, and (b) will operate properly with a modified version        of the Library that is interface-compatible with the Linked        Version. <br>    e) Provide Installation Information, but only if you would otherwise    be required to provide such information under section 6 of the    GNU GPL, and only to the extent that such information is    necessary to install and execute a modified version of the    Combined Work produced by recombining or relinking the    Application with a modified version of the Linked Version. (If    you use option 4d0, the Installation Information must accompany    the Minimal Corresponding Source and Corresponding Application    Code. If you use option 4d1, you must provide the Installation    Information in the manner specified by section 6 of the GNU GPL    for conveying Corresponding Source.) <br><br>   5. Combined Libraries. <br><br>   You may place library facilities that are a work based on the Library side by side in a single library together with other library facilities that are not Applications and are not covered by this License, and convey such a combined library under terms of your choice, if you do both of the following: <br>    a) Accompany the combined library with a copy of the same work based    on the Library, uncombined with any other library facilities,    conveyed under the terms of this License. <br>    b) Give prominent notice with the combined library that part of it    is a work based on the Library, and explaining where to find the    accompanying uncombined form of the same work. <br><br>   6. Revised Versions of the GNU Lesser General Public License. <br><br> The Free Software Foundation may publish revised and/or new versions of the GNU Lesser General Public License from time to time. Such new versions will be similar in spirit to the present version, but may differ in detail to address new problems or concerns. <br> Each version is given a distinguishing version number. If the Library as you received it specifies that a certain numbered version of the GNU Lesser General Public License "or any later version" applies to it, you have the option of following the terms and conditions either of that published version or of any later version published by the Free Software Foundation. If the Library as you received it does not specify a version number of the GNU Lesser General Public License, you may choose any version of the GNU Lesser General Public License ever published by the Free Software Foundation. <br> If the Library as you received it specifies that a proxy can decide whether future versions of the GNU Lesser General Public License shall apply, that proxy's public statement of acceptance of any version is permanent authorization for you to choose that version for the
Library.</p><br><br><p>PyInstaller:</p><p>The source code of Pyinstaller can be obtained at <a href="https://pypi.org/project/pyinstaller/">&lt;https://pypi.org/project/pyinstaller/&gt;</a>. No modifications have been applied to PyInstaller</p><p>License:</p><br><p>GNU GENERAL PUBLIC LICENSE<br><br>Version 2, June 1991<br><br>Copyright (C) 1989, 1991 Free Software Foundation, Inc.  51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA<br><br>Everyone is permitted to copy and distribute verbatim copiesof this license document, but changing it is not allowed.<br><br>PreambleThe licenses for most software are designed to take away your freedom to share and change it. By contrast, the GNU General Public License is intended to guarantee your freedom to share and change free software--to make sure the software is free for all its users. This General Public License applies to most of the Free Software Foundation's software and to any other program whose authors commit to using it. (Some other Free Software Foundation software is covered by the GNU Lesser General Public License instead.) You can apply it to your programs, too.<br><br>When we speak of free software, we are referring to freedom, not price. Our General Public Licenses are designed to make sure that you have the freedom to distribute copies of free software (and charge for this service if you wish), that you receive source code or can get it if you want it, that you can change the software or use pieces of it in new free programs; and that you know you can do these things.<br><br>To protect your rights, we need to make restrictions that forbid anyone to deny you these rights or to ask you to surrender the rights. These restrictions translate to certain responsibilities for you if you distribute copies of the software, or if you modify it.<br><br>For example, if you distribute copies of such a program, whether gratis or for a fee, you must give the recipients all the rights that you have. You must make sure that they, too, receive or can get the source code. And you must show them these terms so they know their rights.<br><br>We protect your rights with two steps: (1) copyright the software, and (2) offer you this license which gives you legal permission to copy, distribute and/or modify the software.<br><br>Also, for each author's protection and ours, we want to make certain that everyone understands that there is no warranty for this free software. If the software is modified by someone else and passed on, we want its recipients to know that what they have is not the original, so that any problems introduced by others will not reflect on the original authors' reputations.<br><br>Finally, any free program is threatened constantly by software patents. We wish to avoid the danger that redistributors of a free program will individually obtain patent licenses, in effect making the program proprietary. To prevent this, we have made it clear that any patent must be licensed for everyone's free use or not licensed at all.<br><br>The precise terms and conditions for copying, distribution and modification follow.<br><br>TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION0. This License applies to any program or other work which contains a notice placed by the copyright holder saying it may be distributed under the terms of this General Public License. The "Program", below, refers to any such program or work, and a "work based on the Program" means either the Program or any derivative work under copyright law: that is to say, a work containing the Program or a portion of it, either verbatim or with modifications and/or translated into another language. (Hereinafter, translation is included without limitation in the term "modification".) Each licensee is addressed as "you".<br><br>Activities other than copying, distribution and modification are not covered by this License; they are outside its scope. The act of running the Program is not restricted, and the output from the Program is covered only if its contents constitute a work based on the Program (independent of having been made by running the Program). Whether that is true depends on what the Program does.<br><br>1. You may copy and distribute verbatim copies of the Program's source code as you receive it, in any medium, provided that you conspicuously and appropriately publish on each copy an appropriate copyright notice and disclaimer of warranty; keep intact all the notices that refer to this License and to the absence of any warranty; and give any other recipients of the Program a copy of this License along with the Program.<br><br>You may charge a fee for the physical act of transferring a copy, and you may at your option offer warranty protection in exchange for a fee.<br><br>2. You may modify your copy or copies of the Program or any portion of it, thus forming a work based on the Program, and copy and distribute such modifications or work under the terms of Section 1 above, provided that you also meet all of these conditions:<br><br>a) You must cause the modified files to carry prominent notices stating that you changed the files and the date of any change.<br>b) You must cause any work that you distribute or publish, that in whole or in part contains or is derived from the Program or any part thereof, to be licensed as a whole at no charge to all third parties under the terms of this License.<br>c) If the modified program normally reads commands interactively when run, you must cause it, when started running for such interactive use in the most ordinary way, to print or display an announcement including an appropriate copyright notice and a notice that there is no warranty (or else, saying that you provide a warranty) and that users may redistribute the program under these conditions, and telling the user how to view a copy of this License. (Exception: if the Program itself is interactive but does not normally print such an announcement, your work based on the Program is not required to print an announcement.)<br>These requirements apply to the modified work as a whole. If identifiable sections of that work are not derived from the Program, and can be reasonably considered independent and separate works in themselves, then this License, and its terms, do not apply to those sections when you distribute them as separate works. But when you distribute the same sections as part of a whole which is a work based on the Program, the distribution of the whole must be on the terms of this License, whose permissions for other licensees extend to the entire whole, and thus to each and every part regardless of who wrote it.<br><br>Thus, it is not the intent of this section to claim rights or contest your rights to work written entirely by you; rather, the intent is to exercise the right to control the distribution of derivative or collective works based on the Program.<br><br>In addition, mere aggregation of another work not based on the Program with the Program (or with a work based on the Program) on a volume of a storage or distribution medium does not bring the other work under the scope of this License.<br><br>3. You may copy and distribute the Program (or a work based on it, under Section 2) in object code or executable form under the terms of Sections 1 and 2 above provided that you also do one of the following:<br><br>a) Accompany it with the complete corresponding machine-readable source code, which must be distributed under the terms of Sections 1 and 2 above on a medium customarily used for software interchange; or,<br>b) Accompany it with a written offer, valid for at least three years, to give any third party, for a charge no more than your cost of physically performing source distribution, a complete machine-readable copy of the corresponding source code, to be distributed under the terms of Sections 1 and 2 above on a medium customarily used for software interchange; or,<br>c) Accompany it with the information you received as to the offer to distribute corresponding source code. (This alternative is allowed only for noncommercial distribution and only if you received the program in object code or executable form with such an offer, in accord with Subsection b above.)<br>The source code for a work means the preferred form of the work for making modifications to it. For an executable work, complete source code means all the source code for all modules it contains, plus any associated interface definition files, plus the scripts used to control compilation and installation of the executable. However, as a special exception, the source code distributed need not include anything that is normally distributed (in either source or binary form) with the major components (compiler, kernel, and so on) of the operating system on which the executable runs, unless that component itself accompanies the executable.<br><br>If distribution of executable or object code is made by offering access to copy from a designated place, then offering equivalent access to copy the source code from the same place counts as distribution of the source code, even though third parties are not compelled to copy the source along with the object code.<br><br>4. You may not copy, modify, sublicense, or distribute the Program except as expressly provided under this License. Any attempt otherwise to copy, modify, sublicense or distribute the Program is void, and will automatically terminate your rights under this License. However, parties who have received copies, or rights, from you under this License will not have their licenses terminated so long as such parties remain in full compliance.<br><br>5. You are not required to accept this License, since you have not signed it. However, nothing else grants you permission to modify or distribute the Program or its derivative works. These actions are prohibited by law if you do not accept this License. Therefore, by modifying or distributing the Program (or any work based on the Program), you indicate your acceptance of this License to do so, and all its terms and conditions for copying, distributing or modifying the Program or works based on it.<br><br>6. Each time you redistribute the Program (or any work based on the Program), the recipient automatically receives a license from the original licensor to copy, distribute or modify the Program subject to these terms and conditions. You may not impose any further restrictions on the recipients' exercise of the rights granted herein. You are not responsible for enforcing compliance by third parties to this License.<br><br>7. If, as a consequence of a court judgment or allegation of patent infringement or for any other reason (not limited to patent issues), conditions are imposed on you (whether by court order, agreement or otherwise) that contradict the conditions of this License, they do not excuse you from the conditions of this License. If you cannot distribute so as to satisfy simultaneously your obligations under this License and any other pertinent obligations, then as a consequence you may not distribute the Program at all. For example, if a patent license would not permit royalty-free redistribution of the Program by all those who receive copies directly or indirectly through you, then the only way you could satisfy both it and this License would be to refrain entirely from distribution of the Program.<br><br>If any portion of this section is held invalid or unenforceable under any particular circumstance, the balance of the section is intended to apply and the section as a whole is intended to apply in other circumstances.<br><br>It is not the purpose of this section to induce you to infringe any patents or other property right claims or to contest validity of any such claims; this section has the sole purpose of protecting the integrity of the free software distribution system, which is implemented by public license practices. Many people have made generous contributions to the wide range of software distributed through that system in reliance on consistent application of that system; it is up to the author/donor to decide if he or she is willing to distribute software through any other system and a licensee cannot impose that choice.<br><br>This section is intended to make thoroughly clear what is believed to be a consequence of the rest of this License.<br><br>8. If the distribution and/or use of the Program is restricted in certain countries either by patents or by copyrighted interfaces, the original copyright holder who places the Program under this License may add an explicit geographical distribution limitation excluding those countries, so that distribution is permitted only in or among countries not thus excluded. In such case, this License incorporates the limitation as if written in the body of this License.<br><br>9. The Free Software Foundation may publish revised and/or new versions of the General Public License from time to time. Such new versions will be similar in spirit to the present version, but may differ in detail to address new problems or concerns.<br><br>Each version is given a distinguishing version number. If the Program specifies a version number of this License which applies to it and "any later version", you have the option of following the terms and conditions either of that version or of any later version published by the Free Software Foundation. If the Program does not specify a version number of this License, you may choose any version ever published by the Free Software Foundation.<br><br>10. If you wish to incorporate parts of the Program into other free programs whose distribution conditions are different, write to the author to ask for permission. For software which is copyrighted by the Free Software Foundation, write to the Free Software Foundation; we sometimes make exceptions for this. Our decision will be guided by the two goals of preserving the free status of all derivatives of our free software and of promoting the sharing and reuse of software generally.<br><br>NO WARRANTY<br><br>11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.<br><br>12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.</p>""")
        self.setOpenExternalLinks(True)

class mouseAutoclick():
    def __init__(self, button, frequency, repeatTimes):
        mouseController = mouse.Controller()
        if repeatTimes == None:
            while MainWindow.isRunning == True:
                mouseController.click(button=button)
                sleep(frequency)
        else:
            currentRepeat = 1
            while currentRepeat <= repeatTimes and MainWindow.isRunning == True:
                mouseController.click(button=button)
                currentRepeat += 1
                sleep(frequency)
            MainWindow.isRunning = False
class mouseHold():
    def __init__(self, button, holdTime, waitTime, repeatTimes):
        self.mouseController = mouse.Controller()
        if repeatTimes == None:
            while MainWindow.isRunning == True:
                self.mouseController.press(button=button)
                sleep(holdTime)
                self.mouseController.release(button=button)
                sleep(waitTime)
        else:
            currentRepeat = 1
            while currentRepeat <= repeatTimes and MainWindow.isRunning == True:
                self.mouseController.press(button=button)
                sleep(holdTime)
                self.mouseController.release(button=button)
                sleep(waitTime)
                currentRepeat += 1
            MainWindow.isRunning = False
class keyAutoclick():
    def __init__(self, key, frequency, repeatTimes):
        keyboardController = keyboard.Controller()
        if repeatTimes == None:
            while MainWindow.isRunning == True:
                keyboardController.press(key=key)
                keyboardController.release(key=key)
                sleep(frequency)
        else:
            currentRepeat = 1
            while currentRepeat <= repeatTimes and MainWindow.isRunning == True:
                keyboardController.press(key=key)
                keyboardController.release(key=key)
                currentRepeat += 1
                sleep(frequency)
            MainWindow.isRunning = False
class keyHold():
    def __init__(self, key):
        keyboardController = keyboard.Controller()
        # Holding keyboard keys down doesn't work well if done exactly the same way as mouseHold()
        # However, pressing keyboard keys every 30 ms without .release() works as a replacement
        while MainWindow.isRunning == True:
            keyboardController.press(key=key)
            sleep(0.03)
        keyboardController.release(key=key)

if __name__ == '__main__':
    app = QApplication(argv)
    window = MainWindow()
    appIcon = QIcon()
    # Set the app icon
    basedir = path.dirname(__file__)
    appIcon.addFile(path.join(basedir, 'Key-Clicker-Holder-white-bg-svg.svg'))
    window.setWindowIcon(appIcon)
    window.infoText.licenseWindow.setWindowIcon(appIcon)
    window.show()
    window.activateWindow()
    window.raise_()
    # Make window non-resizable
    # The maximize button is disabled in MainWindow.__init__()
    # window.setFixedSize(window.frameSize())
    app_exit(app.exec())