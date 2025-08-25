import tkinter as tk
from src.GraphicsApp import GraphicsApp

if __name__ == "__main__":
    main_window = tk.Tk()
    app = GraphicsApp(main_window)
    main_window.mainloop()
