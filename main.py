import tkinter as tk

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Community Credit Mesh')
        self.geometry('400x300')
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text='Welcome to the Community Credit Mesh App!')
        self.label.pack(pady=20)
        self.quit_button = tk.Button(self, text='Quit', command=self.quit)
        self.quit_button.pack(pady=10)

if __name__ == '__main__':
    app = Application()
    app.mainloop()