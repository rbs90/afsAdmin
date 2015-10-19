#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from tkFileDialog import *
import shlex
from subprocess import Popen, PIPE
import threading


class Window(Frame):


    rights = ["Lesen", "Ändern", "Erstellen", "Löschen", "Rechte ändern (Admin)"]
    rightsShort = ["rl", "wk", "i", "d", "a"]
    rightSel = []

    #find /afs/tu-chemnitz.de/project/... -type d -exec fs setacl {} tleh all \;


    def updateCommand(self, *args):


        rightString = ""
        for i, right in enumerate(self.rightSel):
            if(right.get()):
                rightString += self.rightsShort[i]

        if self.recursive.get():
            self.command.set("find " + self.folder.get() + " -type d -exec fs setacl {} " + self.user.get() + " " + rightString + " \; -exec echo {} \;")
        else:
            self.command.set("fs setacl " +  self.folder.get() + " " + self.user.get() + " " + rightString +  " && echo " + self.folder.get())

        if (self.user.get() == "" or self.folder.get() == ""):
            self.start.config(text="Bitte Felder ausfüllen", state=DISABLED)
        else:
            self.start.config(text="Ausführen", state=NORMAL)




    def get_exitcode_stdout_stderr(self, command):
        args = shlex.split(command)

        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode

        return exitcode, out, err



    def execute(self):
        self.start.config(text="Rechte werden gesetzt...", state=DISABLED)
        #status = call(self.command.get(), shell=True)


        resultWindow = Toplevel(self.parent)
        resultWindow.title("Setze Rechte...")

        scrollbar = Scrollbar(resultWindow)
        scrollbar.pack(side=RIGHT, fill=Y)

        resultText = Text(resultWindow, yscrollcommand=scrollbar.set, width=100, height=30)
        resultText.pack(fill=X)
        resultText.insert(END, "Führe folgendes Kommando aus:\n")
        resultText.insert(END, self.command.get() + "\n")

        if(self.recursive.get()):
            resultText.insert(END, "Bitte einen Moment Geduld...\n")

        resultText.insert(END, "\n")

        #force window draw:
        resultWindow.update_idletasks()


        exit, out, err = self.get_exitcode_stdout_stderr(self.command.get())
        if(exit == 0):
            resultText.insert(END, "OK! Folgende Ordner-Rechte wurde geändert:\n")
            resultText.insert(END, out)
        else:
            resultText.insert(END, "Es sind Fehler aufgetreten:\n")
            resultText.insert(END, err)
        self.start.config(text="Ausführen", state=NORMAL)

        thread = BackgroundThread(self)
        thread.start()

  
    def __init__(self, parent):


        self.recursive = BooleanVar()
        self.folder = StringVar()
        self.user = StringVar()
        self.command = StringVar()
        self.rightSel.append(BooleanVar());
        self.rightSel.append(BooleanVar());
        self.rightSel.append(BooleanVar());
        self.rightSel.append(BooleanVar());
        self.rightSel.append(BooleanVar());

        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

        self.folder.set("/afs/tu-chemnitz.de")
        self.user.set("")
        self.recursive.set(False)



        for right in self.rightSel:
            right.set(False);
            right.trace("w", self.updateCommand)

        self.rightSel[0].set(True)

        self.folder.trace("w", self.updateCommand)
        self.user.trace("w", self.updateCommand)
        self.recursive.trace("w", self.updateCommand)





    def selectFolder(self):
        dir = askdirectory(initialdir=self.folder)
        self.fileText.delete(0, END)
        self.fileText.insert(END,dir)

    def initUI(self):
        self.parent.title("AFS-Rechte setzen")
        Label(self.parent, text="Ordner:").grid(row=0, column=0)

        self.fileText = Entry(self.parent, width=80, textvariable=self.folder)
        self.fileText.grid(row=0, column=1)


        Button(self.parent, text="Durchsuchen", command=self.selectFolder).grid(row=0, column=2)

        Label(self.parent, text="Nutzer:").grid(row=1, column=0)

        self.userText=Entry(self.parent, width=10, textvariable=self.user)
        self.userText.grid(row=1, column=1, sticky=W)

        Label(self.parent, text="Rechte:").grid(row=2, column=0)


        for i, right in enumerate(self.rights):
            checkbox = Checkbutton(self.parent, text=right, variable=self.rightSel[i]);
            checkbox.grid(row=2+i, column=1, sticky=W)
            if self.rightSel[i].get():
                checkbox.select()

        self.recursive.trace("w", self.updateCommand)

        Label(self.parent, text="Rekursiv:").grid(row=7, column=0)
        Checkbutton(self.parent, text="Unterordner einbeziehen", variable=self.recursive).grid(row=7, column=1, sticky=W, pady=5)

        #empty row:
        self.parent.grid_rowconfigure(8, weight=2)

        Entry(self.parent, textvariable=self.command, width=100).grid(row=9, column=0, sticky="ew", columnspan=3, pady=5)

        self.start = Button(self.parent, text="Ausführen", command=self.execute, width=100)
        self.start.grid(row=10, column=0, columnspan=3)



def main():
    root = Tk()
    app = Window(root)
    root.mainloop()


if __name__ == '__main__':
    main()

"""
#!/bin/bash
folder=$(zenity --file-selection --directory --title "Bitte das AFS-Verzeichnis wählen welches geändert werden soll" --filename="/afs/tu-chemnitz.de/project/")

user=$(zenity --entry --text "Benutzer der geändert werden soll?")

rights=$(zenity  --list --height=250 --text "Welche Rechte soll der Nutzer '$user' bekommen?" --checklist  --column "X" --column "Rechte" TRUE "Lesen" FALSE "Ändern" FALSE "Erstellen" FALSE "Löschen" FALSE "Rechte ändern" --separator=" ")

zenity --question --text "Sollen die Rechte für alle Unterverzeichnisse gesetzt werden?"
recursive=$?
"""

