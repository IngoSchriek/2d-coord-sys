import tkinter as tk
from tkinter import ttk, messagebox
from src.Window import Window
from src.Viewport import Viewport, transform_coordinates
from src.DisplayFile import DisplayFile
from src.Line import Line
from src.Point import Point
from src.Wireframe import Wireframe
from src.ObjectCreationWindow import ObjectCreationWindow
import src.theme as theme


class GraphicsApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Coordenada 2D")
        self.root.resizable(False, False) # Importante para evitar problemas de distorção dos objetos criados

        self.root.config(bg=theme.BG_COLOR)
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure(".", background=theme.BG_COLOR, foreground=theme.FG_COLOR, bordercolor=theme.BORDER_COLOR)
        style.configure("TFrame", background=theme.BG_COLOR)
        style.configure("TLabel", background=theme.BG_COLOR, foreground=theme.FG_COLOR)
        style.configure("TLabelFrame", background=theme.BG_COLOR, bordercolor=theme.FG_COLOR)
        style.configure("TLabelFrame.Label", background=theme.BG_COLOR, foreground=theme.FG_COLOR)
        style.configure("TButton", background=theme.WIDGET_BG, foreground=theme.FG_COLOR, borderwidth=1)
        style.map("TButton", background=[('active', theme.SELECT_BG)])
        style.configure("TCombobox", fieldbackground=theme.WIDGET_BG, background=theme.WIDGET_BG,
                        foreground=theme.FG_COLOR, arrowcolor=theme.FG_COLOR)
        style.map('TCombobox', fieldbackground=[('readonly', theme.WIDGET_BG)],
                  foreground=[('readonly', theme.FG_COLOR)])
        style.configure("TEntry", fieldbackground=theme.WIDGET_BG, foreground=theme.FG_COLOR)
        self.root.option_add('*TCombobox*Listbox.background', theme.WIDGET_BG)
        self.root.option_add('*TCombobox*Listbox.foreground', theme.FG_COLOR)
        self.root.option_add('*TCombobox*Listbox.selectBackground', theme.SELECT_BG)
        self.root.option_add('*TCombobox*Listbox.selectForeground', theme.FG_COLOR)

        self.display_file = DisplayFile()
        self.viewport = Viewport(0, 0, 800, 800)
        self.window = Window(-500.0, -500.0, 500.0, 500.0)

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.controls_frame = ttk.LabelFrame(self.main_frame, text="Controles", padding="10")
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=800,
            height=800,
            bg=theme.CANVAS_BG,
            highlightthickness=1,
            highlightbackground=theme.BORDER_COLOR
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.controls_frame, text="Nome do Objeto:").pack(fill=tk.X, pady=(0, 5))
        self.obj_name_var = tk.StringVar()
        self.obj_name_entry = ttk.Entry(self.controls_frame, textvariable=self.obj_name_var)
        self.obj_name_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.controls_frame, text="Tipo:").pack(fill=tk.X, pady=(0, 5))
        self.obj_type_var = tk.StringVar(value="Point")
        self.obj_type_menu = ttk.Combobox(self.controls_frame, textvariable=self.obj_type_var,
                                          values=["Point", "Line", "Wireframe"], state="readonly")
        self.obj_type_menu.pack(fill=tk.X, pady=(0, 10))

        self.add_button = ttk.Button(self.controls_frame, text="Adicionar Objeto", command=self.add_object)
        self.add_button.pack(fill=tk.X, pady=5)

        ttk.Label(self.controls_frame, text="Objetos na Cena:").pack(fill=tk.X, pady=(10, 5))
        self.objects_listbox = tk.Listbox(
            self.controls_frame,
            background=theme.WIDGET_BG,
            foreground=theme.FG_COLOR,
            selectbackground=theme.SELECT_BG,
            borderwidth=0,
            highlightthickness=0
        )
        self.objects_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.clear_button = ttk.Button(self.controls_frame, text="Limpar Cena", command=self.clear_scene)
        self.clear_button.pack(fill=tk.X, pady=5)

        info_text = "Navegação:\n- Setas do teclado para mover\n- Scroll do mouse para zoom"
        ttk.Label(self.controls_frame, text=info_text, justify=tk.LEFT).pack(fill=tk.X, pady=(20, 0))

        self.root.bind("<KeyPress-Up>", lambda e: self.move_window(0, 50))
        self.root.bind("<KeyPress-Down>", lambda e: self.move_window(0, -50))
        self.root.bind("<KeyPress-Left>", lambda e: self.move_window(-50, 0))
        self.root.bind("<KeyPress-Right>", lambda e: self.move_window(50, 0))

        self.canvas.bind("<MouseWheel>", self.zoom_window)
        self.canvas.bind("<Button-4>", lambda e: self.zoom_window(e, 0.9))
        self.canvas.bind("<Button-5>", lambda e: self.zoom_window(e, 1.1))

        self.canvas.bind("<ButtonPress-1>", lambda e: self.on_mouse_press(e))
        self.canvas.bind("<B1-Motion>", lambda e: self.on_mouse_drag(e))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.on_mouse_release(e))
        self._drag_data = {"x": 0, "y": 0}

        self.redraw()

    def add_object(self):
        name = self.obj_name_var.get().strip()
        obj_type = self.obj_type_var.get()
        if not name:
            messagebox.showerror("Erro", "O nome do objeto não pode estar vazio.")
            return
        if self.display_file.get_object_by_name(name):
            messagebox.showerror("Erro", f"Já existe um objeto com o nome '{name}'.")
            return

        coords = ObjectCreationWindow(self.root, obj_type).result

        if coords:
            obj = None
            if obj_type == "Point":
                obj = Point(name, coords)
            elif obj_type == "Line":
                obj = Line(name, coords)
            elif obj_type == "Wireframe":
                obj = Wireframe(name, coords)

            if obj:
                self.display_file.add_object(obj)
                self.objects_listbox.insert(tk.END, f"{obj.name} ({obj.type})")
                self.redraw()

    def clear_scene(self):
        self.display_file.clear()
        self.objects_listbox.delete(0, tk.END)
        self.redraw()

    def move_window(self, dx_wc: float, dy_wc: float):
        move_factor = 0.05
        self.window.move(self.window.width() * move_factor * (dx_wc / 50),
                        self.window.height() * move_factor * (dy_wc / 50))
        self.redraw()

    def zoom_window(self, event, factor=None):
        if factor is None:
            if event.delta > 0:
                factor = 0.9
            else:
                factor = 1.1
        self.window.zoom(factor)
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        for obj in self.display_file.objects:
            screen_coords = [transform_coordinates(p, self.window, self.viewport) for p in obj.world_coords]

            if obj.type == "Point":
                for x, y in screen_coords:
                    self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=theme.POINT_COLOR,
                                            outline=theme.POINT_COLOR)
            elif obj.type == "Line":
                self.canvas.create_line(screen_coords, fill=theme.LINE_COLOR, width=2)
            elif obj.type == "Wireframe":
                if len(screen_coords) > 1:
                    self.canvas.create_line(screen_coords, fill=theme.WIREFRAME_COLOR, width=2)
                    self.canvas.create_line([screen_coords[-1], screen_coords[0]], fill=theme.WIREFRAME_COLOR, width=2)
        
    def on_mouse_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.canvas.config(cursor="fleur")

    def on_mouse_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        dx_wc = -dx * (self.window.width() / self.viewport.width())
        dy_wc = -dy * (self.window.height() / self.viewport.height())

        self.window.move(dx_wc, -dy_wc)
        self.redraw()

    def on_mouse_release(self, event):
        self.canvas.config(cursor="arrow")