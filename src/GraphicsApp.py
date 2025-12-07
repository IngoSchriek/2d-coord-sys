import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.Window import Window
from src.Viewport import Viewport, transform_coordinates
from src.DisplayFile import DisplayFile
from src.Line import Line
from src.Point import Point
from src.Wireframe import Wireframe
from src.BezierCurve import BezierCurve
from src.BSpline import BSpline
from src.ObjectCreationWindow import ObjectCreationWindow
import src.theme as theme
from src.Transformations import *
from src.OBJHandler import OBJHandler
from src.Clipping import *
import numpy as np
from math import cos, sin, radians

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
        # TODO: ajeitar dimensao da viewport nas prox entregas
        self.viewport = Viewport(10, 10, 780, 780)  # para testar clipping
        self.window = Window(-500.0, -500.0, 500.0, 500.0)

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.controls_frame = ttk.LabelFrame(self.main_frame, text="Controles", padding="10")
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(self.controls_frame, text="Rotação da Window (°):").pack(fill=tk.X, pady=(10, 5))
        self.win_angle_var = tk.StringVar(value="0")
        angle_row = ttk.Frame(self.controls_frame); angle_row.pack(fill=tk.X)
        ttk.Entry(angle_row, textvariable=self.win_angle_var, width=8).pack(side=tk.LEFT)
        ttk.Button(angle_row, text="Aplicar", command=self.apply_window_rotation).pack(side=tk.LEFT, padx=5)

        ttk.Label(self.controls_frame, text="Algoritmo de Clipping (Linhas):").pack(fill=tk.X, pady=(10, 5))
        self.line_clip_alg = tk.StringVar(value="CS")
        ttk.Radiobutton(self.controls_frame, text="Cohen-Sutherland", variable=self.line_clip_alg, value="CS").pack(anchor="w")
        ttk.Radiobutton(self.controls_frame, text="Liang-Barsky", variable=self.line_clip_alg, value="LB").pack(anchor="w")

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
                                          values=["Point", "Line", "Wireframe", "Bezier Curve", "BSpline"], state="readonly")
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
            elif obj_type == "Bezier Curve":
                obj = BezierCurve(name, coords)
            elif obj_type == "BSpline":
                obj = BSpline(name, coords)
            if obj:
                self.display_file.add_object(obj)
                self.objects_listbox.insert(tk.END, f"{obj.name} ({obj.type})")
                self.redraw()

    def clear_scene(self):
        self.display_file.clear()
        self.objects_listbox.delete(0, tk.END)
        self.redraw()

    def move_window(self, dx_local: float, dy_local: float):
        move_factor = 0.05
        self.window.move_local(self.window.width() * move_factor * (dx_local / 50), self.window.height() * move_factor * (-dy_local / 50))
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
            clipped = None

            if obj.type == "Point":
                if clip_point(obj.world_coords[0], self.window):
                    clipped = [obj.world_coords[0]]

            elif obj.type == "Line":
                if self.line_clip_alg.get() == "CS":
                    clipped = clip_line_cs(obj.world_coords[0], obj.world_coords[1], self.window)
                else:
                    clipped = clip_line_lb(obj.world_coords[0], obj.world_coords[1], self.window)

            elif obj.type == "Wireframe":
                clipped = clip_polygon_sh(obj.world_coords, self.window)

            elif obj.type == "Bezier Curve":
                clipped_segments = []
                for segment in obj.get_segments():
                    clipped_segments.extend(clip_bezier(segment, self.window))
                
                if clipped_segments:
                    screen_coords = []
                    for segment in clipped_segments:
                        points_to_draw = []
                        for t in np.linspace(0, 1, 100):
                            points_to_draw.append(de_casteljau(segment, t))
                        screen_coords.extend([transform_coordinates(p, self.window, self.viewport) for p in points_to_draw])
                    
                    if len(screen_coords) >= 2:
                        self.canvas.create_line(screen_coords, fill=theme.BEZIER_COLOR, width=2)
            elif obj.type == "BSpline":
                curve_points = obj.generate_points(num_steps=20) 
                
                for i in range(len(curve_points) - 1):
                    p1 = curve_points[i]
                    p2 = curve_points[i+1]
                    
                    segment_clipped = None
                    if self.line_clip_alg.get() == "CS":
                        segment_clipped = clip_line_cs(p1, p2, self.window)
                    else:
                        segment_clipped = clip_line_lb(p1, p2, self.window)
                    
                    if segment_clipped:
                        sc = [transform_coordinates(p, self.window, self.viewport) for p in segment_clipped]
                        if len(sc) >= 2:
                            self.canvas.create_line(sc, fill=theme.BSPLINE_COLOR, width=2)


            if clipped:
                if obj.type != "Bezier Curve": # A curva de Bézier já foi desenhada
                    screen_coords = [transform_coordinates(p, self.window, self.viewport) for p in clipped]

                    if obj.type == "Point":
                        for x, y in screen_coords:
                            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, 
                                                fill=theme.POINT_COLOR, outline=theme.POINT_COLOR)
                    
                    elif obj.type == "Line":
                        if len(screen_coords) >= 2:
                            self.canvas.create_line(screen_coords, fill=theme.LINE_COLOR, width=2)
                    
                    elif obj.type == "Wireframe":
                        if len(screen_coords) >= 2:
                            for i in range(len(screen_coords)):
                                next_i = (i + 1) % len(screen_coords)
                                self.canvas.create_line(
                                    screen_coords[i][0], screen_coords[i][1],
                                    screen_coords[next_i][0], screen_coords[next_i][1],
                                    fill=theme.WIREFRAME_COLOR, width=2
                                )
        
    def on_mouse_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.canvas.config(cursor="fleur")

    def on_mouse_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        dx_local_wc = -dx * (self.window.width()  / self.viewport.width())
        dy_local_wc =  dy * (self.window.height() / self.viewport.height())

        self.window.move_local(dx_local_wc, dy_local_wc)
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
        if not obj:
            return

        def apply():
            try:
                dx_local = float(entry_dx.get())
                dy_local = float(entry_dy.get())
                theta = radians(self.window.angle)
                dx_wc =  cos(theta) * dx_local - sin(theta) * dy_local
                dy_wc =  sin(theta) * dx_local + cos(theta) * dy_local
                matrix = translation_matrix(dx_wc, dy_wc)
                obj.apply_transformation(matrix)
                self.redraw()
                top.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Digite números válidos.")

        top = tk.Toplevel(self.root)
        top.title("Translação")
        tk.Label(top, text="dx:").grid(row=0, column=0)
        entry_dx = tk.Entry(top); entry_dx.grid(row=0, column=1)
        tk.Label(top, text="dy:").grid(row=1, column=0)
        entry_dy = tk.Entry(top); entry_dy.grid(row=1, column=1)
        tk.Button(top, text="Aplicar", command=apply).grid(row=2, column=0, columnspan=2)

    def scale_object(self):
        obj = self.get_selected_object()
        if not obj:
            return

        def apply():
            try:
                sx = float(entry_sx.get())
                sy = float(entry_sy.get())

                transforms = [('scale', (sx, sy))]
                matrix = build_transformation_matrix(transforms, center=obj.get_center())

                obj.apply_transformation(matrix)
                self.redraw()
                top.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Digite números válidos.")

        top = tk.Toplevel(self.root)
        top.title("Escala")
        tk.Label(top, text="sx:").grid(row=0, column=0)
        entry_sx = tk.Entry(top); entry_sx.grid(row=0, column=1)
        tk.Label(top, text="sy:").grid(row=1, column=0)
        entry_sy = tk.Entry(top); entry_sy.grid(row=1, column=1)
        tk.Button(top, text="Aplicar", command=apply).grid(row=2, column=0, columnspan=2)


    def rotate_object(self):
        obj = self.get_selected_object()
        if not obj:
            return

        def apply():
            try:
                angle = float(entry_angle.get())
                transforms = [('rotate', angle)]
                matrix = build_transformation_matrix(transforms, center=obj.get_center())

                obj.apply_transformation(matrix)
                self.redraw()
                top.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Digite números válidos.")

        top = tk.Toplevel(self.root)
        top.title("Rotação")
        tk.Label(top, text="Ângulo (graus):").grid(row=0, column=0)
        entry_angle = tk.Entry(top); entry_angle.grid(row=0, column=1)
        tk.Button(top, text="Aplicar", command=apply).grid(row=1, column=0, columnspan=2)

    def apply_window_rotation(self):
        try:
            angle = float(self.win_angle_var.get())
            self.window.set_angle(angle)
            self.redraw()
        except ValueError:
            messagebox.showerror("Erro", "Ângulo inválido.")
    
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
