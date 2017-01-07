import from tkinter import Tk, Frame, BOTH

class ZScoutFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, background = 'white')
        self.parent = parent()
        self.init()

    def init(self):
        self.parent.title('ZScout')
        self.pack(fill=BOTH, expand=1)
        
def main():
    root = Tk()
    root.geometry('250x250+300+300')
    frame = ZScoutFrame(root)
    root.mainloop()

if __name__ == '__main__':
    main()
