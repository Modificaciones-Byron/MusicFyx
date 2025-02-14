import tkinter as tk
from PIL import Image, ImageTk
import json
import os
import datetime
import sys

class Inicio:
    def __init__(self, parent_frame, main_app):
        self.parent = parent_frame
        self.main_app = main_app
        self.historial_file = "historial.json"
        self.historial = self.cargar_historial()
        self.iconos_referencias = []  # Para mantener referencias de imágenes
        
        self.frame_principal = tk.Frame(self.parent, bg="#1a1a1d")
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        self.crear_interfaz()

    def crear_interfaz(self):
        # Saludo según la hora
        self.saludo = tk.Label(
            self.frame_principal,
            text="",
            font=("Helvetica", 16, "bold"),
            bg="#1a1a1d",
            fg="white",
            compound=tk.LEFT
        )
        self.saludo.pack(pady=10, anchor="w", padx=20)
        self.obtener_saludo()  # Iniciar animación
        
        # Últimas canciones
        self.frame_canciones = tk.Frame(self.frame_principal, bg="#1a1a1d")
        self.frame_canciones.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        tk.Label(
            self.frame_canciones, 
            text="Últimas canciones reproducidas:",
            font=("Helvetica", 12),
            bg="#1a1a1d",
            fg="white"
        ).pack(anchor="w")
        self.mostrar_ultimas_canciones()
        
        # Últimos álbumes
        self.frame_albumes = tk.Frame(self.frame_principal, bg="#1a1a1d")
        self.frame_albumes.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        tk.Label(
            self.frame_albumes, 
            text="Álbumes escuchados recientemente:",
            font=("Helvetica", 12),
            bg="#1a1a1d",
            fg="white"
        ).pack(anchor="w")
        self.mostrar_ultimos_albumes()

    def reproducir_cancion(self, cancion):
        """Reproducir la canción seleccionada desde la página de inicio"""
        album_path = os.path.join("DataMusic", cancion['album'])
        song_path = os.path.join(album_path, cancion['nombre'])
        
        if os.path.exists(song_path):
            # Actualizar el estado del reproductor
            self.main_app.current_album = cancion['album']
            self.main_app.current_song = cancion['nombre']
            self.main_app.selected_song = cancion['nombre']
            
            # Reproducir la canción
            self.main_app.play_song(cancion['nombre'])
            
            # Actualizar la interfaz del reproductor
            self.main_app.update_cover_image()
            self.main_app.update_active_song_selection()

    def navegar_a_album(self, album_nombre):
        """Navegar a un álbum específico en la biblioteca"""
        # Cambiar a la vista de biblioteca
        self.main_app.show_library()
        
        # Seleccionar el álbum específico
        self.main_app.select_album(album_nombre)

    def mostrar_ultimas_canciones(self):
        contenedor = tk.Frame(self.frame_canciones, bg="#1a1a1d")
        contenedor.pack(fill=tk.BOTH, expand=True)
        
        for col in range(2):
            contenedor.grid_columnconfigure(col, weight=1, uniform="group1")
        for row in range(3):
            contenedor.grid_rowconfigure(row, weight=1)

        for i, cancion in enumerate(self.historial.get('canciones', [])[:6]):
            frame = tk.Frame(
                contenedor, 
                bg="#2b2e4a", 
                width=300,
                height=60
            )
            frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            frame.grid_propagate(False)

            # Imagen
            img = Image.new('RGB', (55,55), (0,0,0))
            try:
                ruta = os.path.join("DataMusic", cancion['album'], cancion['nombre'])
                img = self.main_app.load_album_cover(ruta)
                if not img:
                    raise Exception("No hay portada")
            except:
                default_path = os.path.join(os.path.dirname(__file__), "default_cover.png")
                img = Image.open(default_path)
            
            img = img.resize((55,55), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            label_img = tk.Label(frame, image=img_tk, bg="#2b2e4a")
            label_img.image = img_tk
            label_img.place(x=5, y=1)

            # Texto
            texto = os.path.splitext(cancion['nombre'])[0]
            label_texto = tk.Label(
                frame, 
                text=texto,
                bg="#2b2e4a",
                fg="white",
                font=("Segoe UI", 11, "bold"),
                width=30,
                wraplength=450,
                anchor="w"
            )
            label_texto.place(x=65, y=19)

            # Configurar eventos de clic para reproducción
            frame.bind("<Button-1>", lambda e, c=cancion: self.reproducir_cancion(c))
            label_img.bind("<Button-1>", lambda e, c=cancion: self.reproducir_cancion(c))
            label_texto.bind("<Button-1>", lambda e, c=cancion: self.reproducir_cancion(c))

            # Hover
            frame.bind("<Enter>", lambda e, f=frame: f.config(bg="#373d5a"))
            frame.bind("<Leave>", lambda e, f=frame: f.config(bg="#2b2e4a"))

    def mostrar_ultimos_albumes(self):
        contenedor = tk.Frame(self.frame_albumes, bg="#1a1a1d")
        contenedor.pack(fill=tk.BOTH, expand=True)
        
        for col in range(3):
            contenedor.grid_columnconfigure(col, weight=1, uniform="group2")
        for row in range(2):
            contenedor.grid_rowconfigure(row, weight=1)

        for i, album in enumerate(self.historial.get('albumes', [])[:6]):
            color = "#2b2e4a"
            if hasattr(self.main_app, 'album_colors'):
                color = self.main_app.album_colors[i % len(self.main_app.album_colors)]
            
            container = tk.Frame(
                contenedor, 
                bg=color, 
                width=180,
                height=70
            )
            container.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            container.grid_propagate(False)

            # Collage
            collage = Image.new("RGB", (60,60), (0,0,0))
            try:
                album_path = os.path.join("DataMusic", album)
                songs = [f for f in os.listdir(album_path) if f.endswith(".mp3")][:4]
                for idx, song in enumerate(songs):
                    img = self.main_app.load_album_cover(os.path.join(album_path, song))
                    if img: 
                        img = img.resize((30,30), Image.LANCZOS)
                        x = (idx % 2) * 30
                        y = (idx // 2) * 30
                        collage.paste(img, (x,y))
            except: pass
            
            collage_tk = ImageTk.PhotoImage(collage)
            label_img = tk.Label(container, image=collage_tk, bg=color)
            label_img.image = collage_tk
            label_img.place(x=5, y=4)

            # Texto del álbum
            label_album = tk.Label(
                container, 
                text=album,
                bg=color,
                fg="black",
                font=("Helvetica", 12, "bold"),
                wraplength=100,
                width=15
            )
            label_album.place(relx=0.30, rely=0.34)

            # Configurar eventos de clic para navegación
            container.bind("<Button-1>", lambda e, a=album: self.navegar_a_album(a))
            label_img.bind("<Button-1>", lambda e, a=album: self.navegar_a_album(a))
            label_album.bind("<Button-1>", lambda e, a=album: self.navegar_a_album(a))

            # Hover effects
            container.bind("<Enter>", lambda e, f=container: f.config(relief="raised"))
            container.bind("<Leave>", lambda e, f=container: f.config(relief="flat"))

    def obtener_saludo(self):
        hora = datetime.datetime.now().hour
        saludos = {
            "mañana": ("¡Buenos días! ", "#FFD700", "sun.png"),
            "tarde": ("¡Buenas tardes! ", "#FFA500", "sunset.png"),
            "noche": ("¡Buenas noches! ", "#4169E1", "moon.png")
        }
        
        if 5 <= hora < 12:
            periodo = "mañana"
        elif 12 <= hora < 19:
            periodo = "tarde"
        else:
            periodo = "noche"
        
        self.animar_saludo(saludos[periodo])

    def animar_saludo(self, datos_saludo):
        texto, color, icono = datos_saludo

        try:
            if hasattr(sys, '_MEIPASS'):
                ruta_icono = os.path.join(sys._MEIPASS, "icons", icono)
            else:
                ruta_icono = os.path.join("icons", icono)
            
            img = Image.open(ruta_icono)
            img = img.resize((40, 40), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.iconos_referencias.append(img_tk)
        except Exception as e:
            print(f"Error cargando icono: {e}")
            img_tk = None

        self.saludo.config(
            text=texto,
            fg=color,
            image=img_tk,
            compound=tk.LEFT
        )
        self.saludo.image = img_tk

    def animar_color(self, color_base):
        if self.parpadear:
            nuevo_color = self.aumentar_brillo(color_base, 30)
            self.saludo.config(fg=nuevo_color)
            self.parent.after(500, lambda: self.saludo.config(fg=color_base))
            self.parent.after(1000, lambda: self.animar_color(color_base))

    def aumentar_brillo(self, hex_color, incremento):
        rgb = [int(hex_color[i+1:i+3], 16) for i in (0, 2, 4)]
        rgb = [min(255, c + incremento) for c in rgb]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()

    def cargar_historial(self):
        try:
            with open(self.historial_file, 'r') as f:
                data = json.load(f)
                return {
                    'canciones': [c for c in data.get('canciones', []) 
                                if os.path.exists(os.path.join("DataMusic", c['album'], c['nombre']))],
                    'albumes': [a for a in data.get('albumes', []) 
                              if os.path.exists(os.path.join("DataMusic", a))]
                }
        except:
            return {'canciones': [], 'albumes': []}

    def guardar_historial(self):
        with open(self.historial_file, 'w') as f:
            json.dump(self.historial, f)

    def actualizar_historial(self, tipo, dato):
        if tipo == 'albumes' and not isinstance(dato, str):
            dato = str(dato)
        
        lista = self.historial.get(tipo, [])
        lista = [item for item in lista if item != dato]
        lista.insert(0, dato)
        self.historial[tipo] = lista[:6]
        self.guardar_historial()