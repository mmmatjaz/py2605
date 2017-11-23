from Tkinter import *

from Ar2c import Ar2c
from table import patternNames

# hardware
BOARDS = [0x55, 0x58, 0x5A]
isLRA = [0, 0, 0]


class DemoGui:
    def __init__(self):

        self.ar2c = Ar2c()
        self.ar2c.setupTypes(isLRA)

        self.root = Tk()
        self.root.title("Demo")
        self.title = Label(self.root, text="Pattern", font=("Helvetica", 18))
        self.title.grid(row=0, columnspan=len(BOARDS)+1, pady=5)

        # Create a Tkinter variable
        self.tkvar = StringVar(self.root)
        # swap key-value in dict
        self.pats = dict((v, k) for k, v in patternNames.iteritems())
        # set the default option
        self.tkvar.set(patternNames[44])
        popupMenu = OptionMenu(self.root, self.tkvar, *self.pats)
        popupMenu.grid(row=1, columnspan=len(BOARDS)+1, pady=5)
        # link function to change dropdown
        self.tkvar.trace('w', self.changeDropdown)

        # buttons
        self.btns = []
        for address in BOARDS+[0]:
            id=len(self.btns)
            b = Button(self.root,
                       text=("%#X"%(address) + ("LRA" if isLRA[id] else ""))
                                if address>0 else "all",
                       font=("Helvetica", 24), width=12,
                       command=lambda a=(id+1 if address>0 else 0): self.buttonClick(a))
            b.grid(row=3, column=id, pady=100, padx=30)
            self.btns.append(b)


    # on change dropdown value
    def changeDropdown(self,*args):
        print "selected %d - %s"%\
              (self.pats[self.tkvar.get()],self.tkvar.get())

    def buttonClick(self,address):
        print "%#X"%(address)
        if address>0:
            self.ar2c.play(address, self.pats[self.tkvar.get()], 1)
        else:
            for a in [1,2,3]:
                self.ar2c.play(a, self.pats[self.tkvar.get()], 1)


    def start(self):
        self.isOpen = True
        #self.root.protocol("WM_DELETE_WINDOW", self.closeHandler)
        self.root.after(100, self.root.focus_force)
        self.root.mainloop()

if __name__ == "__main__":
    print "start ui"
    g = DemoGui()
    g.start()