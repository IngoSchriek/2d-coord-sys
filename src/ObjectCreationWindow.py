import tkinter as tk
from tkinter import ttk, messagebox
import src.theme as theme
import re

class ObjectCreationWindow(tk.Toplevel):
    def __init__(self, parent, obj_type: str):
        super().__init__(parent)
        self.transient(parent)
        self.title(f"Adicionar {obj_type}")
        self.result = None
        self.obj_type = obj_type
        
        self.config(bg=theme.BG_COLOR)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure(".", background=theme.BG_COLOR, foreground=theme.FG_COLOR)
        style.configure("TFrame", background=theme.BG_COLOR)
        style.configure("TLabel", background=theme.BG_COLOR)
        style.configure("TLabelFrame", background=theme.BG_COLOR)
        style.configure("TLabelFrame.Label", background=theme.BG_COLOR, foreground=theme.FG_COLOR)
        style.configure("TEntry", fieldbackground=theme.WIDGET_BG, foreground=theme.FG_COLOR)
        style.configure("TButton", background=theme.WIDGET_BG, foreground=theme.FG_COLOR)
        style.map("TButton", background=[('active', theme.SELECT_BG)])

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 10))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        if self.obj_type == "Point":
            self.create_point()
        elif self.obj_type == "Line":
            self.create_line()
        elif self.obj_type == "Wireframe":
            self.create_wireframe()
        elif self.obj_type in ["Bezier Curve", "BSpline"]:
            self.create_bezier()
        elif self.obj_type == "Bicubic Surface":
            self.create_bicubic_bezier()
        elif self.obj_type == "BSpline Surface":
            self.create_bicubic_bspline()

        ok_button = ttk.Button(button_frame, text="Criar", command=self.on_ok)
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))
        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.on_cancel)
        cancel_button.pack(side=tk.RIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.grab_set()
        self.wait_window(self)

    def create_point(self):
        ttk.Label(self.content_frame, text="Coordenada X:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_x = ttk.Entry(self.content_frame, width=15)
        self.entry_x.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(self.content_frame, text="Coordenada Y:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_y = ttk.Entry(self.content_frame, width=15)
        self.entry_y.grid(row=1, column=1, sticky="ew", pady=2)
        self.entry_x.focus_set()

    def create_line(self):
        ttk.Label(self.content_frame, text="Ponto Inicial (Xi):").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_x1 = ttk.Entry(self.content_frame, width=15)
        self.entry_x1.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(self.content_frame, text="Ponto Inicial (Yi):").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_y1 = ttk.Entry(self.content_frame, width=15)
        self.entry_y1.grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Label(self.content_frame, text="Ponto Final (Xj):").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_x2 = ttk.Entry(self.content_frame, width=15)
        self.entry_x2.grid(row=2, column=1, sticky="ew", pady=2)
        ttk.Label(self.content_frame, text="Ponto Final (Yj):").grid(row=3, column=0, sticky="w", pady=2)
        self.entry_y2 = ttk.Entry(self.content_frame, width=15)
        self.entry_y2.grid(row=3, column=1, sticky="ew", pady=2)
        self.entry_x1.focus_set()

    def create_wireframe(self):
        self.wireframe_points = []
        add_frame = ttk.LabelFrame(self.content_frame, text="Novo Ponto", padding=5)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(add_frame, text="X:").grid(row=0, column=0)
        self.wf_entry_x = ttk.Entry(add_frame, width=8)
        self.wf_entry_x.grid(row=0, column=1, padx=5)
        ttk.Label(add_frame, text="Y:").grid(row=0, column=2)
        self.wf_entry_y = ttk.Entry(add_frame, width=8)
        self.wf_entry_y.grid(row=0, column=3, padx=5)
        add_button = ttk.Button(add_frame, text="Adicionar Ponto", command=self.add_point)
        add_button.grid(row=0, column=4, padx=5)
        self.wf_entry_x.focus_set()
        list_frame = ttk.LabelFrame(self.content_frame, text="Pontos Adicionados", padding=5)
        list_frame.pack(expand=True, fill=tk.BOTH)
        self.points_listbox = tk.Listbox(list_frame, background=theme.WIDGET_BG, foreground=theme.FG_COLOR, selectbackground=theme.SELECT_BG)
        self.points_listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        remove_button = ttk.Button(list_frame, text="Remover Selecionado", command=self.remove_point)
        remove_button.pack(side=tk.LEFT, padx=5)

    def create_bezier(self):
        ttk.Label(self.content_frame, text="Pontos de Controle: (x1,y1),(x2,y2),...").pack(anchor="w")
        self.bezier_text = tk.Text(self.content_frame, height=10, width=40, background=theme.WIDGET_BG, foreground=theme.FG_COLOR, insertbackground=theme.FG_COLOR)
        self.bezier_text.pack(fill=tk.BOTH, expand=True)
        self.bezier_text.focus_set()
    
    def add_point(self):
        try:
            x = float(self.wf_entry_x.get())
            y = float(self.wf_entry_y.get())
            self.wireframe_points.append((x, y))
            self.points_listbox.insert(tk.END, f"({x}, {y})")
            self.wf_entry_x.delete(0, tk.END)
            self.wf_entry_y.delete(0, tk.END)
            self.wf_entry_x.focus_set()
        except ValueError:
            messagebox.showerror("Erro de Formato", "Insira números válidos.", parent=self)

    def remove_point(self):
        idx = self.points_listbox.curselection()
        if not idx: return
        for i in reversed(idx):
            self.points_listbox.delete(i)
            del self.wireframe_points[i]

    def create_bicubic_bezier(self):
        instrucoes = "Formato: (x,y,z),(x,y,z)... \nSepare as 4 linhas com ';'. Necessários 16 pontos."
        ttk.Label(self.content_frame, text=instrucoes).pack(anchor="w", pady=(0,5))
        self.bezier_text = tk.Text(self.content_frame, height=12, width=50, background=theme.WIDGET_BG, foreground=theme.FG_COLOR, insertbackground=theme.FG_COLOR)
        self.bezier_text.pack(fill=tk.BOTH, expand=True)
        example = "(0,0,0),(30,0,10),(60,0,10),(90,0,0);\n(0,30,10),(30,30,30),(60,30,30),(90,30,10);\n(0,60,10),(30,60,30),(60,60,30),(90,60,10);\n(0,90,0),(30,90,10),(60,90,10),(90,90,0)"
        self.bezier_text.insert("1.0", example)

    def create_bicubic_bspline(self):
        instrucoes = "Formato B-Spline: (x,y,z),(x,y,z)... ; (x,y,z)...\nUse ';' para nova linha. Mínimo 4x4. Suporta até 20x20."
        ttk.Label(self.content_frame, text=instrucoes).pack(anchor="w", pady=(0,5))
        self.bezier_text = tk.Text(self.content_frame, height=12, width=50, background=theme.WIDGET_BG, foreground=theme.FG_COLOR, insertbackground=theme.FG_COLOR)
        self.bezier_text.pack(fill=tk.BOTH, expand=True)
        
        example = "(0,0,0),(20,0,10),(40,0,10),(60,0,10),(80,0,0);\n(0,20,10),(20,20,30),(40,20,30),(60,20,30),(80,20,10);\n(0,40,10),(20,40,30),(40,40,30),(60,40,30),(80,40,10);\n(0,60,0),(20,60,10),(40,60,10),(60,60,10),(80,60,0)"
        self.bezier_text.insert("1.0", example)

    def on_ok(self):
        try:
            if self.obj_type == "Point":
                self.result = [(float(self.entry_x.get()), float(self.entry_y.get()))]
            elif self.obj_type == "Line":
                self.result = [(float(self.entry_x1.get()), float(self.entry_y1.get())), (float(self.entry_x2.get()), float(self.entry_y2.get()))]
            elif self.obj_type == "Wireframe":
                if len(self.wireframe_points) < 3: raise ValueError("Wireframe precisa de 3 pontos.")
                self.result = self.wireframe_points
            elif self.obj_type in ["Bezier Curve", "BSpline"]:
                text = self.bezier_text.get("1.0", tk.END).strip()
                points = re.findall(r"\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)", text)
                if len(points) < 4: raise ValueError("Mínimo de 4 pontos.")
                self.result = [(float(x), float(y)) for x, y in points]

            elif self.obj_type == "Bicubic Surface":
                text = self.bezier_text.get("1.0", tk.END).strip()
                points = re.findall(r"\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)", text)
                if len(points) != 16: raise ValueError(f"Bicubic Bezier precisa de exatamente 16 pontos. Encontrados {len(points)}.")
                self.result = [(float(x), float(y), float(z)) for x, y, z in points]
            
            elif self.obj_type == "BSpline Surface":
                text = self.bezier_text.get("1.0", tk.END).strip()
                rows_text = text.split(';')
                matrix = []
                for row_str in rows_text:
                    if not row_str.strip(): continue
                    row_points = re.findall(r"\(\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)", row_str)
                    if row_points:
                        matrix.append([(float(x), float(y), float(z)) for x, y, z in row_points])
                
                if not matrix: raise ValueError("Nenhum ponto encontrado.")
                
                n_rows = len(matrix)
                n_cols = len(matrix[0])
                if n_rows < 4 or n_cols < 4:
                    raise ValueError(f"Grid B-Spline deve ser pelo menos 4x4. Atual: {n_rows}x{n_cols}")
                
                for i, row in enumerate(matrix):
                    if len(row) != n_cols:
                        raise ValueError(f"Linha {i+1} tem {len(row)} colunas, esperado {n_cols}.")
                
                self.result = matrix

            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}", parent=self)

    def on_cancel(self):
        self.result = None
        self.destroy()
