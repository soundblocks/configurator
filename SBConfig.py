from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QToolBar, QMessageBox, QFileDialog 
from PyQt5.QtWidgets import QDesktopWidget, QSplitter
from PyQt5.QtWidgets import QPlainTextEdit, QStatusBar
from PyQt5.QtWidgets import QApplication, QAction, QLabel, QActionGroup
from PyQt5.QtGui import QFontDatabase, QIcon, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrintDialog
import os
import sys
import imgqrc
import re
from pythonosc.udp_client import SimpleUDPClient 
from time import sleep
import netifaces

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window geometry
        
        self.setGeometry(100, 100, 800, 600)       
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
        self.setWindowIcon(QIcon(":/img/icon.jpg"))

        # Layout
        
        layout = QVBoxLayout()

        # QPlainTextEdit objects
        
        self.editor = QPlainTextEdit()
        self.console = QPlainTextEdit() 
        
        self.editor.setMinimumHeight(100)
        self.console.setMinimumHeight(100)

        # Set TextEdit properties, font and background
        
        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(10)
        
        self.editor.setFont(fixedfont)
        self.console.setFont(fixedfont)
        
        self.console.setReadOnly(True)
        self.console.setStyleSheet('QPlainTextEdit {background-color: black; color: white;}')
        
        # Path of the currently open file.

        self.path = None

        # Add editors to splitter and layout
        
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)

        splitter.addWidget(self.editor)
        splitter.addWidget(self.console)

        layout.addWidget(splitter)

        # Create a QWidget layout container and set in window
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Status bar
        
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.statuslabel = QLabel();
        self.statuslabel.setAlignment(Qt.AlignRight)
        self.statuslabel.setStyleSheet('border: 0px;')
        self.statuslabel.setFont(QFont('Arial', 9))
        
        self.status.setSizeGripEnabled(False)
        self.status.addWidget(self.statuslabel, 1)
        
        interfaces = netifaces.interfaces()
        self.ips = list()
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs.keys():
                ip = addrs[netifaces.AF_INET][0]['addr']
                if ip != '127.0.0.1':
                    self.ips.append(ip)
        
        self.iplocal = self.ips[0]
        self.network = self.iplocal[0:self.iplocal.rfind('.')+1]
        self.statuslabel.setText('NETWORK ' + self.network + '0 ' + '  IP ' + self.iplocal + "    ")

        # Menus
        
        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction("Open...", self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        
        file_menu.addSeparator()

        save_file_action = QAction("Save", self)
        save_file_action.setShortcut('Ctrl+S')
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)

        saveas_file_action = QAction("Save as...", self)
        saveas_file_action.setShortcut('Ctrl+Shift+S')
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        
        file_menu.addSeparator()

        print_action = QAction("Print...", self)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.file_quit)
        file_menu.addAction(quit_action)

        edit_menu = self.menuBar().addMenu("&Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()

        select_action = QAction("Select all", self)
        select_action.setShortcut('Ctrl+A')
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)

        wrap_action = QAction("Wrap text to window", self)
        wrap_action.setShortcut('Alt+Z')
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

        edit_menu.addSeparator()

        zoom_in_action = QAction("Increase font size", self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.triggered.connect(self.editor.zoomIn)
        edit_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Decrease font size", self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.editor.zoomOut)
        edit_menu.addAction(zoom_out_action)
        
        
        config_menu = self.menuBar().addMenu("&Configure")
        
        verify_action = QAction("Verify", self)
        verify_action.setShortcut('Ctrl+R')
        verify_action.triggered.connect(self.verify)
        config_menu.addAction(verify_action)
        
        upload_action = QAction("Upload", self)
        upload_action.setShortcut('Ctrl+U')
        upload_action.triggered.connect(self.upload)
        config_menu.addAction(upload_action)
        
        config_menu.addSeparator()
        ip_menu = config_menu.addMenu("IP Address (Network)")
        
        self.ip_action = list()
        IPGroup = QActionGroup(self)
        for n,ip in enumerate(self.ips):
            self.ip_action.append(QAction(ip + ' (' + ip[0:ip.rfind('.')+1] + '0)', self))
            self.ip_action[n].setCheckable(True)
            self.ip_action[n].setChecked(False)
            self.ip_action[n].triggered.connect(self.edit_toggle_ip)
            ip_menu.addAction(self.ip_action[n])
            IPGroup.addAction(self.ip_action[n])
        self.ip_action[0].setChecked(True)
        
        about_menu = self.menuBar().addMenu("&About")
        
        about_action = QAction("About SoundBlocks Configurator...", self)
        about_action.triggered.connect(self.about)
        about_menu.addAction(about_action)
        
        # Toolbar
        
        toolbar = QToolBar("Action")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        verify_toolbar_action = QAction(QIcon(":/img/check_icon.png"), "Verify", self)
        verify_toolbar_action.triggered.connect(self.verify)
        toolbar.addAction(verify_toolbar_action)
        
        upload_toolbar_action = QAction(QIcon(":/img/arrow_icon.png"), "Upload", self)
        upload_toolbar_action.triggered.connect(self.upload)
        toolbar.addAction(upload_toolbar_action)
        
        # Show window
        
        self.update_title()
        self.show()

        # Set split window sizes 
        
        s = splitter.sizes()
        s = [int(0.8*sum(s)),int(0.2*sum(s))]
        splitter.setSizes(s)

    def dialog_critical(self, s):
        # creating a QMessageBox object
        dlg = QMessageBox(self)

        # setting text to the dlg
        dlg.setText(s)

        # setting icon to it
        dlg.setIcon(QMessageBox.Critical)

        # showing it
        dlg.show()

    def file_open(self):
        # getting path and bool value
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", 
                            "SBC files (*.sbc)")

        # if path is true
        if path:
            # try opening path
            try:
                with open(path, 'r') as f:
                    # read the file
                    text = f.read()

            # if some error occurred
            except Exception as e:

                # show error using critical method
                self.dialog_critical(str(e))
            # else
            else:
                # update path value
                self.path = path

                # update the text
                self.editor.setPlainText(text)
            
                self.console.clear()
                self.console.setPlainText('File ' + os.path.basename(self.path) +
                                          ' loaded.'  + '\n')                
    
                # update the title
                self.update_title()

    def file_save(self):
        # if there is no save path
        if self.path is None:
            # call save as method
            return self.file_saveas()

        # else call save to path method
        self._save_to_path(self.path)

    def file_saveas(self):
        # opening path
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "",
                                              "SBC files (*.sbc)")

        # if dialog is cancelled i.e no path is selected
        if not path:
            # return this method
            # i.e no action performed
            return

        # else call save to path method
        self._save_to_path(path)

    def _save_to_path(self, path):
        # get the text
        text = self.editor.toPlainText()

        # try catch block
        try:
            if path[-4:] != '.sbc':
                path = path+'.sbc'
            # opening file to write
            with open(path, 'w') as f:

                # write text in the file
                f.write(text)

        # if error occurs
        except Exception as e:

            # show error using critical
            self.dialog_critical(str(e))

        # else do this
        else:
            # change path
            self.path = path
            # update the title
            self.update_title()

    def file_print(self):
        # creating a QPrintDialog
        dlg = QPrintDialog()

        # if executed
        if dlg.exec_():

            # print the text
            self.editor.print_(dlg.printer())

    def file_quit(self):
        self.close()

    def update_title(self):
        # setting window title with prefix as file name
        # suffix as PyQt5 Notepad
        self.setWindowTitle("%s | SoundBlocks Configurator" %(os.path.basename(self.path) 
                                                if self.path else "Untitled"))
        
    def edit_toggle_wrap(self):
        # chaining line wrap mode
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0 )

    def edit_toggle_ip(self):
        for n,action in enumerate(self.ip_action):
            if action.isChecked():
                self.iplocal = self.ips[n]
                self.network = self.iplocal[0:self.iplocal.rfind('.')+1]
                self.statuslabel.setText('NETWORK ' + self.network + '0 ' + '  IP ' + self.iplocal + "    ")
                break

    def verify(self):
        self.console.clear()
        self.console.insertPlainText('Parsing...\n')
        error = False
        send = dict()
        receive = dict()
        keylist = list()
        
        lines = self.editor.toPlainText().splitlines(keepends=False)
        if len(lines) == 0:
            error = True
            self.printerror('Error: empty file.')
            return error, send, receive, keylist 
        
        sens = ['t1','t2','t3','t4','t5','t6','t7','t8','ax','ay','az','gx','gy','gz','azimuth','bearing']
        acts = ['dfPlay', 'dfStop', 'dfSetEq', 'dfVolume', 'dfPlayFolder', 'dfPause']

        # Parse

        for n,line in enumerate(lines):
            
            if (re.search('^\\w+$', line)):
                error = True
                self.printerror('Error: syntax error in line ' + str(n+1) + ' "' + line + '"')
                return error, send, receive, keylist
            

            # Comments
            
            if (re.search('^\\s*#', line)):
                continue

            # Send
              
            if (re.search("->", line)):
                
                result = re.search("^(\\d{1,3})->(.*):(.*)$", line)
                if not result:
                    error = True
                    self.printerror('Error: Send ID must be a number. In line ' + str(n+1) + ' "' + line + '"')
                    return error, send, receive, keylist
                
                id_in = int(result.group(1))

                if result.group(2) == '':
                    error = True
                    self.printerror('Error: sensor list cannot be empty in line ' + str(n+1) + ' "' + line + '"')
                    return error, send, receive, keylist
                else:
                    sensores = result.group(2).split(",")
                    for sensor in sensores:
                        if sensor not in sens:
                            error = True
                            self.printerror('Error: sensor must be valid. In line ' + str(n+1) + ' "' + line + '"')
                            return error, send, receive, keylist

                if result.group(3) == '':
                    error = True
                    self.printerror('Error: Receive ID must be a number. In line ' + str(n+1) + ' "' + line + '"')
                    return error, send, receive, keylist
                
                id_out = result.group(3).split("#")[0].strip()
                
                listsend = []
                
                bits = 0
                for s in sensores:
                    bits += 2**sens.index(s)
                
                bits = list(bits.to_bytes(2,'big'))    
                listsend.append(bits[0])
                listsend.append(bits[1]) 
                
                id_out = id_out.split(",")
                
                if len(id_out) > 3:
                    error = True
                    self.printerror('Error: maximum 3 ID ranges for ' + 
                                    str(id_in) + '-> ' + '.')
                    return error, send, receive, keylist
                    
                listids = [0,0,0,0,0,0]
                for i in range(0,len(id_out)):   
                    out = id_out[i].split("-")
                    if len(out) == 1:
                        if not str.isdigit(out[0]):
                                error = True
                                self.printerror('Error: Receive ID must be a number. In line ' + str(n+1) + ' "' + line + '"')
                                return error, send, receive, keylist
                        out1 = int(out[0])
                        out2 = out1
                    else:
                       if (not str.isdigit(out[0]) or not str.isdigit(out[1])):
                            error = True
                            self.printerror('Error: syntax error in line ' + str(n+1) + ' "' + line + '"')
                            return error, send, receive, keylist
                            
                       out1 = int(out[0])
                       out2 = int(out[1])
                    listids[2*i] = out1
                    listids[2*i+1] = out2
                    
                for id in listids:    
                    listsend.append(id) 
                
                if id_in not in send:
                    send[id_in] = list()
                send[id_in].append(listsend)

            # Receieve
                 
            if (re.search("<-", line)):
                
                result = re.search("^(\\d*)<-(.*):(\\d{1,3})@(.*)\\[(.*),(.*)\\]", line)
                
                if result is None or result.group(1) == '':
                    error = True
                    self.printerror('Error: Receive ID must be a number. In line ' + str(n+1) + ' "' + line + '"')
                    return error, send, receive, keylist
                id_in = int(result.group(1))

                if result.group(2) == '':
                    error = True
                    self.printerror('Error: Send ID must be a number. In line ' + str(n+1) + ' "' + line + '"')
                    return error, send, receive, keylist
                else:
                    sensor = result.group(2)
                    if sensor not in sens:
                        error = True
                        self.printerror('Error: sensor must be valid. In line ' + str(n+1) + ' "' + line + '"')
                        return error, send, receive, keylist

                if result.group(3) == '':
                    error = True
                    self.printerror('Error: Send ID must be a number. In line ' + str(n+1) + ' "' + line + '"')
                    return error, send, receive, keylist
                id_out = result.group(3)

                if result.group(4) == '':
                    error = True
                    self.printerror('Error: action cannot be empty in line ' + str(n+1) + ' "' + line + '"')
                    return error, send, receive, keylist
                else:
                    actuador = result.group(4)
                    if actuador not in acts:
                        error = True
                        self.printerror('Error: action must be valid. In line ' + str(n+1) + ' "' + line + '"')
                        return error, send, receive, keylist

                map1 = result.group(5)
                map2 = result.group(6)
                
                listreceive = []
                
                listreceive.append(sens.index(sensor))    
                listreceive.append(int(id_out))
                listreceive.append(acts.index(actuador))
                listreceive.append(int(map1))
                listreceive.append(int(map2))
                
                if id_in not in receive:
                    receive[id_in] = list()
                receive[id_in].append(listreceive)   
           
        send = dict(sorted(send.items()))
        receive = dict(sorted(receive.items()))
        keylist = sorted(set(list(send.keys()) + list(receive.keys())))
         
        # self.console.insertPlainText('send: ' + str(send) + '\n' +
        #                           'receive: ' + str(receive) + '\n' +
        #                           'keylist: ' + str(receive) + '\n')
        self.console.insertPlainText('Verified... OK.' + '\n')
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setSliderPosition(scrollbar.maximum())
        app.processEvents()
        
        return error, send, receive, keylist
    
    def upload(self):
        error, send, receive, keylist = self.verify()
        if error: return
        
        self.console.insertPlainText('\n' + 'Uploading...' + '\n')
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setSliderPosition(scrollbar.maximum())
        app.processEvents()
        
        port = 12000
        
        for k in keylist:
            
            self.console.insertPlainText('\n' + str(k) + ': ' + self.network + 
                                      str(k) + '\n')
            client = SimpleUDPClient(self.network + str(k), port)
            client.send_message("/startprog", 0)
            scrollbar = self.console.verticalScrollBar()
            scrollbar.setSliderPosition(scrollbar.maximum())
            sleep(0.5)
            app.processEvents()

            if (k in send):
                for m in send[k]:
                    self.console.insertPlainText('send: ' + str(send) + '\n')
                    client.send_message("/send", m)
                    scrollbar = self.console.verticalScrollBar()
                    scrollbar.setSliderPosition(scrollbar.maximum())
                    sleep(0.5)
                    app.processEvents()  

            if (k in receive):
                for m in receive[k]:
                    self.console.insertPlainText('receive: ' + str(receive) + '\n')
                    client.send_message("/receive", m)
                    scrollbar = self.console.verticalScrollBar()
                    scrollbar.setSliderPosition(scrollbar.maximum())
                    sleep(0.5)
                    app.processEvents()
                
            client.send_message("/commit", 0)
            sleep(0.5)
            
            # client.send_message("/verify", 0)
            # sleep(0.25)
            
            client.send_message("/endprog", 0)
            sleep(0.5)
            
        self.console.insertPlainText('\n' + 'Uploaded... OK.' + '\n')
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setSliderPosition(scrollbar.maximum())
            
    
    def printerror(self, msg):
        self.console.insertPlainText(msg + '\n')
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setSliderPosition(scrollbar.maximum())
    
    def about(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("About SoundBlocks Configurator")
        msgBox.setText("SoundBlocks Configurator\n(C) 2024-2025\n\nSabrina García\nLaurence Bender\nGermán Ito\n")
        msgBox.exec()

# Main

if __name__ == '__main__':

    # Create PyQt5 application
    app = QApplication(sys.argv)
    
    # Set application name
    app.setApplicationName("SoundBlocks Configurator")
    
    # Create main window object
    window = MainWindow()
    
    # Loop
    app.exec_()
