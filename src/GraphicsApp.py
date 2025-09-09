import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.Window import Window
from src.Viewport import Viewport, transform_coordinates
from src.DisplayFile import DisplayFile
from src.Line import Line
from src.Point import Point
from src.Wireframe import Wireframe
from src.ObjectCreationWindow import ObjectCreationWindow
import src.theme as theme
from src.Transformations import *
from src.OBJHandler import OBJHandler
import numpy as np
import math

class GraphicsApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Coordenada 2D")
        self.root.resizable(False, False)

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
        
        # Lista de Objetos
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
        
        # Controles da Window
        window_controls_frame = ttk.LabelFrame(self.controls_frame, text="Controles da Window", padding="5")
        window_controls_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(window_controls_frame, text="Rotação (graus):").grid(row=0, column=0, sticky="w")
        self.window_angle_var = tk.DoubleVar(value=0.0)
        self.window_angle_entry = ttk.Entry(window_controls_frame, textvariable=self.window_angle_var, width=10)
        self.window_angle_entry.grid(row=0, column=1, padx=5)
        self.rotate_window_button = ttk.Button(window_controls_frame, text="Aplicar", command=self.rotate_window, width=8)
        self.rotate_window_button.grid(row=0, column=2)

        # Informações de Navegação
        info_text = "Navegação:\n- Setas do teclado para mover\n- Scroll do mouse para zoom"
        ttk.Label(self.controls_frame, text=info_text, justify=tk.LEFT).pack(fill=tk.X, pady=(20, 0))

        # Menus
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Importar .obj", command=self.import_obj)
        file_menu.add_command(label="Exportar .obj", command=self.export_obj)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        transform_menu = tk.Menu(menubar, tearoff=0)
        transform_menu.add_command(label="Translação", command=self.translate_object)
        transform_menu.add_command(label="Escala", command=self.scale_object)
        transform_menu.add_command(label="Rotação", command=self.rotate_object)
        menubar.add_cascade(label="Transformações", menu=transform_menu)
        self.root.config(menu=menubar)

        self.root.bind("<KeyPress-Up>", lambda e: self.move_window(0, 50))
        self.root.bind("<KeyPress-Down>", lambda e: self.move_window(0, -50))
        self.root.bind("<KeyPress-Left>", lambda e: self.move_window(-50, 0))
        self.root.bind("<KeyPress-Right>", lambda e: self.move_window(50, 0))

        self.canvas.bind("<MouseWheel>", self.zoom_window)
        self.canvas.bind("<Button-4>", lambda e: self.zoom_window(e, 0.9))
        self.canvas.bind("<Button-5>", lambda e: self.zoom_window(e, 1.1))

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self._drag_data = {"x": 0, "y": 0}

        self.redraw()

    def get_view_transform_matrix(self):
        """Calcula a matriz de transformação do mundo para o sistema de coordenadas da window (VCS)."""
        wc_center = self.window.center()
        
        # 1. Transladar a window para a origem
        t1 = translation_matrix(-wc_center[0], -wc_center[1])
        # 2. Rotacionar para alinhar com os eixos
        r = rotation_matrix(-self.window.angle)
        
        # A matriz de transformação é a combinação das duas operações
        return np.dot(r, t1)
        
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
        self.window = Window(-500.0, -500.0, 500.0, 500.0) # Reseta a window
        self.window_angle_var.set(0.0)
        self.redraw()

    def move_window(self, dx_wc: float, dy_wc: float):
        move_factor = 0.05
        
        # Rotaciona o vetor de movimento para alinhar com a orientação da window
        angle_rad = math.radians(self.window.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        dx = (dx_wc * cos_a - dy_wc * sin_a)
        dy = (dx_wc * sin_a + dy_wc * cos_a)

        self.window.move(self.window.width() * move_factor * (dx / 50),
                         self.window.height() * move_factor * (dy / 50))
        self.redraw()

    def zoom_window(self, event, factor=None):
        if factor is None:
            if event.delta > 0:
                factor = 0.9
            else:
                factor = 1.1
        self.window.zoom(factor)
        self.redraw()

    def rotate_window(self):
        try:
            target_angle = self.window_angle_var.get()
            self.window.angle = target_angle
            self.redraw()
        except ValueError:
            messagebox.showerror("Erro de Formato", "Por favor, insira um número válido para o ângulo.")

    def redraw(self):
        self.canvas.delete("all")
        
        # Matriz de transformação de SCM para SCN (normalizado)
        view_matrix = self.get_view_transform_matrix()

        for obj in self.display_file.objects:
            normalized_coords = []
            for x, y in obj.world_coords:
                vec = np.array([x, y, 1])
                res = np.dot(view_matrix, vec)
                normalized_coords.append((res[0], res[1]))

            normalized_window = Window(
                -self.window.width() / 2, -self.window.height() / 2,
                self.window.width() / 2, self.window.height() / 2
            )

            screen_coords = [transform_coordinates(p, normalized_window, self.viewport) for p in normalized_coords]

            if obj.type == "Point":
                for x, y in screen_coords:
                    self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=theme.POINT_COLOR, outline=theme.POINT_COLOR)
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
        dy_wc = dy * (self.window.height() / self.viewport.height())
        
        angle_rad = math.radians(self.window.angle)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        
        final_dx = dx_wc * cos_a - dy_wc * sin_a
        final_dy = dx_wc * sin_a + dy_wc * cos_a

        self.window.move(final_dx, -final_dy)
        self.redraw()

    def on_mouse_release(self, event):
        self.canvas.config(cursor="arrow")

    def get_selected_object(self):
        selection = self.objects_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um objeto na lista.")
            return None
        index = selection[0]
        return self.display_file.objects[index]

    def translate_object(self):
        obj = self.get_selected_object()
        if not obj: return
        def apply():
            try:
                dx = float(entry_dx.get())
                dy = float(entry_dy.get())
                matrix = translation_matrix(dx, dy)
                obj.apply_transformation(matrix)
                self.redraw()
                top.destroy()
            except ValueError: messagebox.showerror("Erro", "Digite números válidos.")
        top = tk.Toplevel(self.root); top.title("Translação")
        tk.Label(top, text="dx:").grid(row=0, column=0); entry_dx = tk.Entry(top); entry_dx.grid(row=0, column=1)
        tk.Label(top, text="dy:").grid(row=1, column=0); entry_dy = tk.Entry(top); entry_dy.grid(row=1, column=1)
        tk.Button(top, text="Aplicar", command=apply).grid(row=2, column=0, columnspan=2)

    def scale_object(self):
        obj = self.get_selected_object()
        if not obj: return
        def apply():
            try:
                sx = float(entry_sx.get())
                sy = float(entry_sy.get())
                matrix = build_transformation_matrix([('scale', (sx, sy))], center=obj.get_center())
                obj.apply_transformation(matrix)
                self.redraw()
                top.destroy()
            except ValueError: messagebox.showerror("Erro", "Digite números válidos.")
        top = tk.Toplevel(self.root); top.title("Escala")
        tk.Label(top, text="sx:").grid(row=0, column=0); entry_sx = tk.Entry(top); entry_sx.grid(row=0, column=1)
        tk.Label(top, text="sy:").grid(row=1, column=0); entry_sy = tk.Entry(top); entry_sy.grid(row=1, column=1)
        tk.Button(top, text="Aplicar", command=apply).grid(row=2, column=0, columnspan=2)

    def rotate_object(self):
        obj = self.get_selected_object()
        if not obj: return
        def apply():
            try:
                angle = float(entry_angle.get())
                matrix = build_transformation_matrix([('rotate', angle)], center=obj.get_center())
                obj.apply_transformation(matrix)
                self.redraw()
                top.destroy()
            except ValueError: messagebox.showerror("Erro", "Digite números válidos.")
        top = tk.Toplevel(self.root); top.title("Rotação")
        tk.Label(top, text="Ângulo (graus):").grid(row=0, column=0); entry_angle = tk.Entry(top); entry_angle.grid(row=0, column=1)
        tk.Button(top, text="Aplicar", command=apply).grid(row=1, column=0, columnspan=2)

    def import_obj(self):
        filepath = filedialog.askopenfilename(
            title="Abrir Arquivo .obj",
            filetypes=(("Wavefront OBJ", "*.obj"), ("Todos os arquivos", "*.*"))
        )
        if not filepath:
            return
        
        try:
            self.display_file = OBJHandler.load_from_obj(filepath)
            self.objects_listbox.delete(0, tk.END)
            for obj in self.display_file.objects:
                self.objects_listbox.insert(tk.END, f"{obj.name} ({obj.type})")
            self.redraw()
        except Exception as e:
            messagebox.showerror("Erro de Importação", f"Não foi possível ler o arquivo:\n{e}")

    def export_obj(self):
        filepath = filedialog.asksaveasfilename(
            title="Salvar Arquivo .obj",
            defaultextension=".obj",
            filetypes=(("Wavefront OBJ", "*.obj"), ("Todos os arquivos", "*.*"))
        )
        if not filepath:
            return
        
        try:
            OBJHandler.save_to_obj(self.display_file, filepath)
            messagebox.showinfo("Sucesso", f"Cena salva em {filepath}")
        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Não foi possível salvar o arquivo:\n{e}")