import os
import tkinter as tk
from Inicio import Inicio
from Perfil import Perfil
from tkinter import ttk
from tkinter import filedialog, simpledialog, messagebox
from pygame import mixer
import pygame
import shutil
from mutagen.id3 import ID3, APIC
from PIL import Image, ImageTk
import io
import ctypes

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.image_cache = {}
        self.root.title("MusicFix")
        self.root.geometry("798x650")

        self.root.resizable(False, False)
        self.albums = {}
        self.song_frames = []
        self.current_album = None
        self.current_song = None
        self.is_playing = False
        self.auto_play = False

        self.cover_image_label = None
        self.album_history = []
        self.song_history = []
        self.album_colors = [
            "#FF5733", "#33FF57", "#3357FF", "#FFC300",
            "#DAF7A6", "#C70039", "#900C3F", "#581845",
            "#1ABC9C", "#9B59B6", "#34495E", "#E74C3C"
        ]
        self.create_widgets()         # Crear widgets
        self.set_default_cover_image()  # Configurar la imagen predeterminada
        self.update_cover_image()     # Actualizar portada (si aplica)

        # Inicializar Pygame mixer
        mixer.init()
        pygame.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.schedule_check_song_end()  # Iniciar la verificación periódica

        # Crear widgets

        self.load_albums()  # Cargar los álbumes de la carpeta por defecto

        # Mostrar la escena de inicio cuando la aplicación inicie
        self.show_home()

        self.album_colors = [
            "#FF5733",  # Rojo intenso
            "#33FF57",  # Verde lima
            "#3357FF",  # Azul brillante
            "#FFC300",  # Amarillo dorado
            "#DAF7A6",  # Verde claro
            "#C70039",  # Rojo oscuro
            "#900C3F",  # Burdeos
            "#581845",  # Púrpura oscuro
            "#1ABC9C",  # Turquesa
            "#9B59B6",  # Morado
            "#34495E",  # Gris azul
            "#E74C3C"   # Rojo coral
        ]


    def create_widgets(self):
        # Colores y configuración de la ventana
        bg_color = "#1a1a1d"
        fg_color = "#e0e0e0"
        btn_color = "#1f4068"
        hover_color = "#31a84f"
        listbox_color = "#2b2e4a"
        album_font = ("Helvetica", 12, "bold")
        song_font = ("Helvetica", 10, "normal")

        # Configurar ventana principal
        self.root.configure(bg=bg_color)

        # Crear barra de navegación superior
        nav_frame = tk.Frame(self.root, bg=bg_color)
        nav_frame.pack(side=tk.TOP, fill=tk.X, anchor="w")

        nav_buttons = [
            ("Inicio", self.show_home),
            ("Biblioteca", self.show_library),
            ("Perfil", self.show_profile),
        ]

        # Crear botones de navegación superior
        for text, command in nav_buttons:
            btn = tk.Button(
                nav_frame,
                text=text,
                bg=btn_color,
                fg=fg_color,
                font=album_font,
                bd=2,
                relief="solid",
                command=command,
                padx=10,
                width=22,
            )
            btn.pack(side=tk.LEFT, padx=10, anchor="w")

        # Crear un frame principal que se llenará con el contenido central
        self.main_frame = tk.Frame(self.root, bg=bg_color)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10, expand=True)

        # Crear marco para controles y portada
        self.control_frame = tk.Frame(self.main_frame, bg=bg_color)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        # Crear la etiqueta para la portada
        self.cover_image_label = tk.Label(self.control_frame, bg="#1a1a1d")
        self.cover_image_label.pack(pady=10, fill=tk.X)
        self.set_default_cover_image()

        # Imprimir la referencia de cover_image_label para verificar su creación
        print(f"cover_image_label: {self.cover_image_label}")
        # Inicializar imágenes
        # Use the method we just created
        self.set_default_cover_image()

        # Crear los botones
        self.create_control_buttons(self.control_frame, btn_color, fg_color, hover_color, song_font, 2)

        # Crear marco para álbumes (para la escena de biblioteca)
        self.album_frame = tk.Frame(self.main_frame, bg=bg_color)
        self.album_buttons = []  # Lista para almacenar botones de álbumes
        self.update_album_buttons()


    def show_home(self):
        self.hide_all_frames()
        self.inicio = Inicio(self.main_frame, self)
        self.inicio.frame_principal.pack(fill=tk.BOTH, expand=True)
                # Añadir contenido para la escena de inicio
        welcome_label = tk.Label(
            self.main_frame,
            text="Bienvenido a Music.",
            bg="#1a1a1d",
            fg="#e0e0e0",
            font=("Helvetica", 16, "bold")
        )
        welcome_label.pack(pady=14)


    def show_library(self):
        self.hide_all_frames()
        """Mostrar la escena de biblioteca."""
        self.clear_main_frame()  # Limpiar el contenido existente
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=True)

        # Crear un marco para los botones de control (lado derecho)
        self.control_frame = tk.Frame(self.main_frame, bg="#1a1a1d")
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        # Portada (una sola vez)
        self.cover_image_label.pack(side=tk.TOP, pady=10)

        # Botón "Añadir Álbum"
        self.add_album_button = tk.Button(
            self.control_frame,
            text="Añadir Álbum",
            bg="#14b814",
            fg="#e0e0e0",
            font=("Helvetica", 12, "bold"),
            bd=3,
            relief="solid",
            command=self.add_album,
            activebackground="#31a84f",  # Color al presionar el botón
            activeforeground="white",  # Color del texto al presionar
            width=12,  # Ancho más grande
            height=2,  # Más alto
        )
        self.add_album_button.pack(pady=10, fill=tk.X)
        # Efecto de hover para el botón "Añadir Álbum"
        self.add_album_button.bind("<Enter>", lambda event, b=self.add_album_button: b.config(bg="#31a84f", relief="raised"))
        self.add_album_button.bind("<Leave>", lambda event, b=self.add_album_button: b.config(bg="#14b814", relief="solid"))

        # Botón "Eliminar Álbum"
        self.remove_album_button = tk.Button(
            self.control_frame,
            text="Eliminar Álbum",
            bg="red",
            fg="#e0e0e0",
            font=("Helvetica", 12, "bold"),
            bd=3,
            relief="solid",
            command=self.remove_album,
            activebackground="#ff4040",  # Color al presionar el botón
            activeforeground="white",  # Color del texto al presionar
            width=12,  # Ancho más grande
            height=2,  # Más alto
        )
        self.remove_album_button.pack(pady=10, fill=tk.X)
        # Efecto de hover para el botón "Eliminar Álbum"
        self.remove_album_button.bind("<Enter>", lambda event, b=self.remove_album_button: b.config(bg="#ff4040", relief="raised"))
        self.remove_album_button.bind("<Leave>", lambda event, b=self.remove_album_button: b.config(bg="red", relief="solid"))


        # Crear un marco para los álbumes (lado izquierdo)
        self.album_frame = tk.Frame(self.main_frame, bg="#1a1a1d")
        self.album_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Etiqueta para indicar álbumes
        album_label = tk.Label(
            self.album_frame,
            text="Álbumes",
            bg="#1a1a1d",
            fg="#e0e0e0",
            font=("Helvetica", 14, "bold")
        )
        album_label.pack(anchor="w", pady=5)

        # Cargar los botones de los álbumes
        self.update_album_buttons()

    def on_enter(event, button, hover_color):
        """Cuando el mouse entra, cambia el color de fondo y aumenta el tamaño."""
        button.config(bg=hover_color, relief="raised", font=("Helvetica", 13, "bold"))
        button.place(relx=0.5, rely=0.5, anchor="center")  # Animación de agrandado

    def on_leave(event, button, color):
        """Cuando el mouse sale, vuelve al color original y al tamaño."""
        button.config(bg=color, relief="solid", font=("Helvetica", 13, "bold"))
        button.place(relx=0.5, rely=0.5, anchor="center")  # Animación de tamaño original

    def select_song(self, song):
        """Selecciona una canción y actualiza la interfaz."""
        if song and song != self.current_song:  # Evita reprocesar la misma canción
            self.selected_song = song
            self.current_song = song
            print(f"DEBUG: Canción seleccionada: {self.selected_song}")
            self.update_cover_image()
            self.update_active_song_selection()  # Actualizar la selección en la lista


    def clear_main_frame(self):
        """Ocultar todos los widgets del marco principal antes de cambiar de escena."""
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()



    def show_profile(self):
        self.hide_all_frames()
        self.perfil = Perfil(self.main_frame)
        self.perfil.frame_principal.pack(fill=tk.BOTH, expand=True)

    def hide_all_frames(self):
        """Ocultar todos los frames secundarios del main_frame."""
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()  # Ocultar widgets sin destruirlos


    def create_control_buttons(self, parent, btn_color, fg_color, hover_color, font, border_width):
        # Variables de configuración
        button_width = 0
        volume_bar_width = 200
        slider_size = 14  # Tamaño del círculo deslizante
        
        # Contenedor principal
        controls_container = tk.Frame(parent, bg=parent.cget('bg'), width=160)
        controls_container.pack_propagate(False)
        controls_container.pack(pady=5, fill=tk.Y, side=tk.LEFT)
        
        # Botones principales
        button_frame = tk.Frame(controls_container, bg=parent.cget('bg'))
        button_frame.pack(fill=tk.X, expand=True)
        
        control_buttons = [
            ("Reproducir", self.play_selected_song),
            ("Pausar", self.pause_song),
            ("Detener", self.stop_song),
            (f"Auto-Reproducir: {'ON' if self.auto_play else 'OFF'}", self.toggle_auto_play)
        ]
        
        for text, cmd in control_buttons:
            btn = tk.Button(
                button_frame,
                text=text, # Aquí se usará el texto formateado
                bg=btn_color,
                fg=fg_color,
                font=font,
                bd=border_width,
                relief="raised",
                command=cmd,
                width=button_width
            )
            btn.pack(pady=5, fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=hover_color))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=btn_color))
            
            if "Auto-Reproducir" in text:
                self.auto_play_button = btn  # Nombre consistente

        # Control de volumen personalizado
        volume_container = tk.Frame(controls_container, bg='#1a1a1d')
        volume_container.pack(fill=tk.X, pady=5)
        
        # Icono de volumen
        self.vol_icon = tk.Label(
            volume_container,
            text="🔊",
            bg='#1a1a1d',
            fg=fg_color,
            font=("Arial", 12),
            width=1
        )
        self.vol_icon.pack(side=tk.LEFT, padx=2)
        
        # Canvas para la barra de volumen personalizada
        self.vol_canvas = tk.Canvas(
            volume_container,
            bg='#1a1a1d',
            width=volume_bar_width,
            height=20,
            highlightthickness=0
        )
        self.vol_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Línea de fondo
        self.vol_canvas.create_line(
            10, 10, volume_bar_width-10, 10,
            fill='#2b2e4a',
            width=2
        )
        
        # Círculo deslizante
        self.slider = self.vol_canvas.create_oval(
            95-6, 10-6, 95+6, 10+6,  # Posición inicial al 50%
            fill='#31a84f',
            outline='#1a1a1d',
            width=1
        )
        
        # Etiqueta de porcentaje
        self.vol_percent = tk.Label(
            volume_container,
            text="50%",
            bg='#1a1a1d',
            fg=fg_color,
            font=("Helvetica", 9),
            width=1
        )
        self.vol_percent.pack(side=tk.LEFT, padx=2)
        
        # Eventos de arrastre
        self.vol_canvas.bind("<B1-Motion>", self.on_volume_drag)
        self.vol_canvas.bind("<Button-1>", self.on_volume_click)
        self.vol_icon.bind("<Button-1>", self.toggle_mute)
        
        # Variables de estado
        self.current_volume = 50
        self.last_volume = 50

    def on_volume_drag(self, event):
        """Controlar el arrastre del círculo"""
        self.update_volume(event.x)

    def on_volume_click(self, event):
        """Mover el círculo al hacer clic en cualquier parte de la barra"""
        self.update_volume(event.x)

    def update_volume(self, x_pos):
        """Actualizar posición y volumen"""
        # Limitar movimiento dentro de la barra
        x = max(10, min(x_pos, self.vol_canvas.winfo_width() - 10))
        
        # Calcular porcentaje
        bar_width = self.vol_canvas.winfo_width() - 20
        vol = int(((x - 10) / bar_width) * 100)
        
        # Actualizar posición del círculo
        self.vol_canvas.coords(self.slider, x-6, 4, x+6, 16)
        
        # Actualizar valores
        self.current_volume = vol
        mixer.music.set_volume(vol / 100)
        self.vol_percent.config(text=f"{vol}%")
        
        # Actualizar icono
        icon = "🔇" if vol == 0 else "🔈" if vol < 30 else "🔉" if vol < 70 else "🔊"
        self.vol_icon.config(text=icon)

    def toggle_mute(self, event):
        """Alternar silencio"""
        if self.current_volume > 0:
            self.last_volume = self.current_volume
            self.update_volume(10)  # Mover a posición mínima
        else:
            target_x = 10 + (self.last_volume / 100) * (self.vol_canvas.winfo_width() - 20)
            self.update_volume(target_x)
        


    def toggle_auto_play(self):
        """Alternar el estado de auto-reproducción."""
        self.auto_play = not self.auto_play
        if hasattr(self, 'auto_play_button'):  # Mismo nombre de atributo
            nuevo_texto = f"🔁 Auto-Reproduducir: {'ON' if self.auto_play else 'OFF'}"
            self.auto_play_button.config(text=nuevo_texto)
            
            # Feedback visual adicional (opcional)
            color_original = self.auto_play_button.cget("bg")
            self.auto_play_button.config(bg="#31a84f" if self.auto_play else "#1f4068")
            self.root.after(200, lambda: self.auto_play_button.config(bg=color_original))
        else:
            print("Error: Botón no encontrado")




    def play_selected_song(self):
        """Reproducir la canción seleccionada."""
        if hasattr(self, 'selected_song') and self.selected_song:
            song_name = self.selected_song
            album_path = os.path.join("DataMusic", self.current_album)
            song_path = os.path.join(album_path, song_name)

            if os.path.exists(song_path):
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                print(f"Reproduciendo: {song_name}")
            else:
                print(f"Error: El archivo {song_path} no existe.")
        else:
            print("Error: No se ha seleccionado ninguna canción.")


        def on_album_selected(self, album_name):
            """Actualizar el álbum actual cuando el usuario seleccione uno."""
            if album_name in self.albums:
                self.current_album = album_name
                print(f"Álbum seleccionado: {self.current_album}")



    def load_album_cover(self, mp3_path):
        """Carga la portada incrustada de un archivo MP3 y la almacena en caché."""
        if mp3_path in self.image_cache:
            return self.image_cache[mp3_path]  # Retorna la imagen desde el caché

        try:
            audio = ID3(mp3_path)
            for tag in audio.values():
                if isinstance(tag, APIC):
                    image_data = tag.data
                    image = Image.open(io.BytesIO(image_data))
                    self.image_cache[mp3_path] = image  # Almacena la imagen en caché
                    return image
        except Exception as e:
            print(f"Error al cargar la portada desde {mp3_path}: {e}")
        return None

    def load_albums(self):
        """Cargar álbumes desde la carpeta de música."""
        album_folder = "DataMusic"
        
        # Verificar si la carpeta 'DataMusic' existe, si no, crearla
        if not os.path.exists(album_folder):
            os.makedirs(album_folder)  # Crear la carpeta si no existe
            print(f"Carpeta '{album_folder}' creada.")
        
        # Cargar los álbumes desde la carpeta 'DataMusic'
        for album in os.listdir(album_folder):
            album_path = os.path.join(album_folder, album)
            if os.path.isdir(album_path):
                self.albums[album] = [
                    song for song in os.listdir(album_path) if song.endswith(".mp3")
                ]

        # No establecer álbum predeterminado inmediatamente
        if self.albums:
            print(f"Álbumes cargados: {list(self.albums.keys())}")
        else:
            print("No se encontraron álbumes en 'DataMusic'.")


    def ensure_album_selected(self):
        """Asegurarse de que un álbum esté seleccionado."""
        if not self.current_album and self.albums:
            self.current_album = list(self.albums.keys())[0]
            print(f"Álbum predeterminado seleccionado: {self.current_album}")



    def get_next_song(self):
        """Obtener la siguiente canción en el álbum actual."""
        if self.current_album:
            # Normalizar nombres para comparación exacta
            songs = [os.path.basename(song) for song in self.albums[self.current_album]]
            current_song = os.path.basename(self.current_song)
            
            if current_song not in songs:
                print(f"Error: Canción '{current_song}' no existe en el álbum. Reiniciando selección.")
                return songs[0] if songs else None

            current_index = songs.index(current_song)
            next_index = (current_index + 1) % len(songs)
            return songs[next_index]
        return None


    def show_recent_songs(self):
        # Código para mostrar las canciones recientes
        print("Mostrando canciones recientes...")

    def play_song(self, song_name):
        """Reproducir la canción seleccionada."""
        if not self.current_album:
            print("Error: No se ha seleccionado un álbum.")
            return

        album_path = os.path.join("DataMusic", self.current_album)
        song_path = os.path.join(album_path, song_name)

        if os.path.exists(song_path):
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.current_song = song_name  # Actualizar la canción actual
            print(f"Reproduciendo: {song_name}")
        else:
            print(f"Error: No se encontró la canción en {song_path}.")
        
        if self.current_album:
            self.inicio.actualizar_historial('canciones', {
                'nombre': song_name,
                'album': self.current_album
            })
            self.inicio.actualizar_historial('albumes', self.current_album)

    def pause_song(self):
        if self.is_playing:
            mixer.music.pause()
            self.is_playing = False
            print("Canción en pausa")
        else:
            mixer.music.unpause()
            self.is_playing = True
            print("Canción reanudada")

    def stop_song(self):
        if self.is_playing:
            mixer.music.stop()
            self.is_playing = False
            print("Música detenida.")




    def update_album_buttons(self):
        """Actualizar botones de álbumes con carátulas en formato 2x2."""
        # Eliminar botones existentes
        for widget in self.album_frame.winfo_children():
            widget.destroy()  # Eliminar todos los widgets previos

        self.album_images = []  # Referencias para imágenes

        # Variables para posicionar en la cuadrícula
        row, col = 0, 0
        for i, album_name in enumerate(self.albums):
            # Verificar si el álbum existe
            album_path = os.path.join("DataMusic", album_name)
            if not os.path.exists(album_path):
                print(f"Advertencia: El álbum '{album_name}' no existe. Saltando...")
                continue

            # Seleccionar el color correspondiente
            color = self.album_colors[i % len(self.album_colors)]

            # Cargar imágenes
            images = []
            try:
                for song in os.listdir(album_path):
                    if song.endswith(".mp3"):
                        song_path = os.path.join(album_path, song)
                        image = self.load_album_cover(song_path)
                        if image:
                            images.append(image)
                    if len(images) == 4:  # Solo necesitamos 4 imágenes
                        break
            except Exception as e:
                print(f"Error al cargar canciones en '{album_name}': {e}")
                continue

            # Crear collage
            if images:
                collage = Image.new("RGB", (60, 60), (0, 0, 0))
                for idx, img in enumerate(images[:4]):
                    img_resized = img.resize((30, 30), Image.LANCZOS)
                    x_offset = (idx % 2) * 30
                    y_offset = (idx // 2) * 30
                    collage.paste(img_resized, (x_offset, y_offset))
            else:
                default_cover_path = os.path.join(os.path.dirname(__file__), "default_cover.png")
                default_cover = Image.open(default_cover_path)
                collage = default_cover.resize((60, 60), Image.LANCZOS)

            # Convertir a formato Tkinter
            collage_tk = ImageTk.PhotoImage(collage)
            self.album_images.append(collage_tk)  # Guardar referencia

            # Crear contenedor
            container = tk.Frame(self.album_frame, bg=color, relief="solid", bd=2)
            container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Imagen
            image_label = tk.Label(container, image=collage_tk, bg=color)
            image_label.image = collage_tk
            image_label.pack(side=tk.LEFT, padx=1)

            # Botón
            album_btn = tk.Button(
                container,
                text=album_name,
                bg=color,
                fg="black",
                font=("Helvetica", 12, "bold"),
                bd=0,
                width=20,
                height=1,
                relief="flat",
                command=lambda album=album_name: self.select_album(album),
            )
            album_btn.album_name = album_name  # Etiqueta personalizada
            album_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            # Posición en cuadrícula
            col += 1
            if col >= 2:
                col = 0
                row += 1






    def select_album(self, album_name):
        """Mostrar las canciones del álbum seleccionado con diseño moderno."""
        self.current_album = album_name
        self.clear_main_frame()

        # Marco principal
        album_content_frame = tk.Frame(self.main_frame, bg="#1a1a1d")
        album_content_frame.pack(fill=tk.BOTH, expand=True)

        # Cabecera con botón de regreso y título
        header_frame = tk.Frame(album_content_frame, bg="#1a1a1d")
        header_frame.pack(fill=tk.X, pady=10, padx=10)

        tk.Button(
            header_frame,
            text="← Biblioteca",
            bg="#31a84f",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            command=self.show_library
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            header_frame,
            text=f"Álbum: {album_name}",
            bg="#1a1a1d",
            fg="white",
            font=("Helvetica", 14, "bold")
        ).pack(side=tk.LEFT, padx=10)

        # Contenedor principal
        main_container = tk.Frame(album_content_frame, bg="#1a1a1d")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Panel de canciones
        songs_frame = tk.Frame(main_container, bg="#2b2e4a")
        songs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

        # Canvas para scroll
        canvas = tk.Canvas(songs_frame, bg="#2b2e4a", highlightthickness=0)
        scroll_frame = tk.Frame(canvas, bg="#2b2e4a")
        
        # Configuración del scroll
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=lambda *args: None)  # Deshabilitar scrollbar
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Scroll con rueda del mouse y teclas
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind_all("<Up>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Down>", lambda e: canvas.yview_scroll(1, "units"))

        # Cargar canciones
        album_path = os.path.join("DataMusic", album_name)
        songs = [f for f in os.listdir(album_path) if f.endswith(('.mp3', '.wav'))]
        
        # En el método select_album, modificar la creación de los frames de las canciones:
        for song in songs:
            # Frame para cada canción
            song_frame = tk.Frame(scroll_frame, bg="#2b2e4a", padx=15, pady=8)
            song_frame.pack(fill=tk.X, pady=0)
            self.song_frames.append(song_frame)
            
            # Borde inferior más grueso y negro
            tk.Frame(song_frame, height=2, bg="#000000").pack(side=tk.BOTTOM, fill=tk.X)
            
            # Efecto hover
            song_frame.bind("<Enter>", lambda e, f=song_frame: f.config(bg="#373d5a"))
            song_frame.bind("<Leave>", lambda e, f=song_frame: f.config(bg="#2b2e4a"))
            
            # Selección de canción (vinculado al frame)
            song_frame.bind("<Button-1>", lambda e, s=song: self.select_song(s))
            
            # Cargar portada
            song_path = os.path.join(album_path, song)
            img = self.load_album_cover(song_path) or Image.open(default_cover_path)
            img = img.resize((55, 55), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            # Mostrar elementos
            tk.Label(song_frame, image=img_tk, bg="#2b2e4a").pack(side=tk.LEFT)
            
            # Label para el nombre de la canción
            song_name_label = tk.Label(
                song_frame, 
                text=os.path.splitext(song)[0],  # Mostrar el nombre sin la extensión
                bg="#2b2e4a", 
                fg="white", 
                font=("Segoe UI", 11), 
                anchor="w"
            )
            song_name_label.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
            
            # Vincular el evento de clic al label del nombre de la canción
            song_name_label.bind("<Button-1>", lambda e, s=song: self.select_song(s))
            
            # Guardar referencia de la imagen
            song_frame.img = img_tk

        # Empaquetar canvas
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Panel de controles derecho
        controls_frame = tk.Frame(main_container, bg="#1a1a1d", width=300)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Botones de gestión (añadir/eliminar canción)
        action_btn_style = {
            "font": ("Helvetica", 12, "bold"),
            "bd": 2,
            "relief": "solid",
            "width": 15,
            "height": 1
        }
        
        add_song_button = tk.Button(
            controls_frame,
            text="Añadir Canción",
            bg="#31a84f",
            fg="white",
            command=lambda: self.add_song_to_album(album_name, scroll_frame),  # Usar scroll_frame
            **action_btn_style
        )
        add_song_button.pack(pady=10, fill=tk.X)

        delete_song_button = tk.Button(
            controls_frame,
            text="Eliminar Canción",
            bg="#dc143c",
            fg="white",
            command=lambda: self.delete_song_from_album(album_name, scroll_frame),  # Usar scroll_frame
            **action_btn_style
        )
        delete_song_button.pack(pady=10, fill=tk.X)

        # Sección de portada
        cover_frame = tk.Frame(controls_frame, bg="#1a1a1d", pady=15)
        self.cover_image_label = tk.Label(cover_frame, bg="#1a1a1d")
        self.cover_image_label.pack()
        self.set_default_cover_image()
        cover_frame.pack()

        # Controles de reproducción
        self.create_control_buttons(controls_frame, "#1f4068", "#e0e0e0", "#31a84f", ("Helvetica", 10, "bold"), 2)

        # Actualizar selección de canción
        if self.current_song:
            self.update_active_song_selection()

    def on_song_select(self, event):
        """Maneja la selección en el Listbox."""
        try:
            index = self.song_listbox.curselection()[0]
            song_name = self.song_listbox.get(index)
            self.select_song(song_name)
        except IndexError:
            return


    def load_album_cover(self, mp3_path):
        """Carga la portada incrustada de un archivo MP3."""
        try:
            print(f"Intentando cargar portada desde: {mp3_path}")
            audio = ID3(mp3_path)  # Carga las etiquetas ID3 del archivo
            for tag in audio.values():
                if isinstance(tag, APIC):  # Busca una etiqueta APIC (portada incrustada)
                    image_data = tag.data
                    print("Portada incrustada encontrada")
                    # Convertir los bytes de la imagen a un formato PIL
                    image = Image.open(io.BytesIO(image_data))
                    return image
            print("No se encontró ninguna portada incrustada.")
        except Exception as e:
            print(f"Error al cargar la portada desde {mp3_path}: {e}")
        return None
    
    def update_cover_image(self):
        """Actualiza la portada según el álbum y canción seleccionados."""
        try:
            if not self.current_album or not self.current_song:
                self.set_default_cover_image()
                return

            song_path = os.path.join("DataMusic", self.current_album, self.current_song)

            if not os.path.exists(song_path):
                self.set_default_cover_image()
                return

            # Intentar cargar portada de la canción
            album_cover_image = self.load_album_cover(song_path)

            if album_cover_image:
                # Redimensionar imagen
                album_cover_image = album_cover_image.resize((136, 130), Image.LANCZOS)
                self.album_cover_image_tk = ImageTk.PhotoImage(album_cover_image)  # Almacenar como atributo

                # Actualizar imagen en el label
                self.cover_image_label.config(image=self.album_cover_image_tk)
            else:
                self.set_default_cover_image()

        except Exception as e:
            print(f"Error al actualizar la portada: {e}")
            self.set_default_cover_image()



    def set_default_cover_image(self):
        """Carga y muestra la imagen predeterminada si no se encuentra una portada."""
        default_cover_path = os.path.join(os.path.dirname(__file__), "default_cover.png")

        # Imprimir la ruta de la imagen predeterminada para depuración
        print(f"Ruta de imagen predeterminada: {default_cover_path}")

        try:
            # Verificar si el cover_image_label existe antes de configurarlo
            if hasattr(self, 'cover_image_label') and self.cover_image_label is not None:
                # Abrir y redimensionar la imagen
                default_cover_image = Image.open(default_cover_path)
                default_cover_image = default_cover_image.resize((136, 130), Image.LANCZOS)
                
                # Convertir a PhotoImage
                default_cover_image_tk = ImageTk.PhotoImage(default_cover_image)
                
                # Configurar la etiqueta de imagen
                self.cover_image_label.config(image=default_cover_image_tk)
                self.cover_image_label.image = default_cover_image_tk  # Mantener referencia
                print("Imagen predeterminada cargada correctamente.")
            else:
                print("Error: cover_image_label no está inicializado correctamente.")
        except Exception as e:
            print(f"Error al cargar la imagen predeterminada: {e}")


    def update_active_song_selection(self):
        """Resalta la canción seleccionada en verde."""
        if hasattr(self, 'song_frames') and self.current_song:
            try:
                for song_frame in self.song_frames:
                    # Obtener el nombre del archivo desde el Label
                    song_label = song_frame.winfo_children()[1]  # El Label de texto es el segundo hijo
                    displayed_name = song_label.cget("text")
                    song_file_name = f"{displayed_name}.mp3"  # Reconstruir nombre del archivo

                    if song_file_name == self.current_song:
                        song_frame.config(bg="#31a84f")
                        for child in song_frame.winfo_children():
                            if isinstance(child, tk.Label):
                                child.config(bg="#31a84f", fg="white")  # Solo aplicar a Labels
                    else:
                        song_frame.config(bg="#2b2e4a")
                        for child in song_frame.winfo_children():
                            if isinstance(child, tk.Label):
                                child.config(bg="#2b2e4a", fg="white")
            except Exception as e:
                print(f"Error al actualizar selección: {e}")



    def schedule_check_song_end(self):
        """Programar la verificación periódica del evento de finalización de canción."""
        self.handle_song_end_event()
        self.root.after(100, self.schedule_check_song_end)  # Llamar nuevamente cada 100ms


    def handle_song_end_event(self):
        """Manejar el evento de finalización de canción."""
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:  # Canción terminó
                print("Evento: La canción ha terminado.")
                if self.auto_play:
                    next_song = self.get_next_song()
                    if next_song:
                        self.play_song(next_song)

                        # Actualizar la selección en la lista
                        self.current_song = next_song
                        self.update_active_song_selection()
                        self.update_cover_image()  # Actualizar la portada
                    else:
                        print("No hay más canciones para reproducir.")




    def toggle_auto_play(self):
        self.auto_play = not self.auto_play
        self.auto_play_button.config(text=f"Auto-Reproducir: {'ON' if self.auto_play else 'OFF'}")
        
    def get_next_song(self):
        """Obtener la siguiente canción en el álbum actual."""
        if self.current_album:
            songs = self.albums.get(self.current_album, [])  # Lista de canciones del álbum
            if not songs:
                print(f"Error: El álbum '{self.current_album}' no tiene canciones.")
                return None

            if self.current_song not in songs:
                print(f"Error: La canción actual '{self.current_song}' no está en el álbum '{self.current_album}'.")
                return None

            current_index = songs.index(self.current_song)  # Índice de la canción actual
            next_index = (current_index + 1) % len(songs)  # Índice de la siguiente canción
            next_song = songs[next_index]

            print(f"Siguiente canción: {next_song}")
            return next_song

        print("Error: No hay un álbum seleccionado.")
        return None



    
    def add_album(self):
        """Agregar un nuevo álbum."""
        album_name = simpledialog.askstring("Nombre del Álbum", "Ingrese el nombre del álbum:")
        if album_name:
            album_path = os.path.join("DataMusic", album_name)
            if not os.path.exists(album_path):
                os.makedirs(album_path)
                self.albums[album_name] = []  # Registrar el álbum en el diccionario
                print(f"Álbum '{album_name}' creado.")
                self.update_album_buttons()  # Actualizar la interfaz en tiempo real
            else:
                messagebox.showwarning("Advertencia", f"El álbum '{album_name}' ya existe.")

    def remove_album(self):
        if self.current_album is None:
            messagebox.showerror("Error", "Por favor, selecciona un álbum para eliminar.")
            return

        confirmation = messagebox.askyesno("Confirmación", f"¿Estás seguro de que quieres eliminar el álbum '{self.current_album}'?")
        if confirmation:
            if self.is_playing:
                self.stop_song()

            album_path = os.path.join("DataMusic", self.current_album)
            if os.path.exists(album_path):
                # Eliminar las canciones dentro del álbum
                for file_name in os.listdir(album_path):
                    file_path = os.path.join(album_path, file_name)
                    try:
                        os.remove(file_path)
                    except PermissionError:
                        messagebox.showerror("Error", f"No se puede eliminar el archivo '{file_name}' porque está en uso.")
                        return
                # Eliminar la carpeta del álbum
                os.rmdir(album_path)

                # Eliminar el botón del álbum (asegurándose de que sea un botón)
                for widget in self.album_frame.winfo_children():
                    if isinstance(widget, tk.Button) and widget.cget("text") == self.current_album:
                        widget.destroy()  # Elimina el botón correspondiente al álbum

                del self.albums[self.current_album]  # Elimina el álbum del diccionario
                self.current_album = None
                self.song_listbox.delete(0, tk.END)  # Limpia la lista de canciones
                self.cover_image_label.config(image="")  # Limpiar imagen de portada
                print(f"Álbum '{self.current_album}' eliminado.")
                
                # Forzar actualización de la interfaz
                self.update_album_buttons()  # Actualiza la lista de botones de álbumes en la interfaz

            else:
                messagebox.showerror("Error", "No se pudo encontrar la carpeta del álbum.")




    def add_song_to_album(self, album_name, scroll_frame):
        """Añadir canciones y actualizar la lista."""
        song_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
        album_path = os.path.join("DataMusic", album_name)
        
        if song_paths:
            for file_path in song_paths:
                file_name = os.path.basename(file_path)
                destination = os.path.join(album_path, file_name)
                if not os.path.exists(destination):
                    shutil.copy(file_path, destination)
                    print(f"Canción '{file_name}' añadida.")
            
            # Actualizar la lista de canciones en la interfaz
            self.select_album(album_name)  # Recargar el álbum


    def delete_song_from_album(self, album_name, scroll_frame):
        """Eliminar canción y actualizar la lista."""
        selected_song = self.current_song  # Obtener la canción seleccionada
        if selected_song:
            album_path = os.path.join("DataMusic", album_name)
            song_path = os.path.join(album_path, selected_song)
            if os.path.exists(song_path):
                os.remove(song_path)
                print(f"Canción '{selected_song}' eliminada.")
                self.select_album(album_name)  # Recargar el álbum
        else:
            messagebox.showwarning("Advertencia", "Selecciona una canción para eliminar.")

print("Inicializando programa...")
pygame.mixer.init()
print("Pygame.mixer inicializado.")

default_cover_path = os.path.join(os.path.dirname(__file__), 'default_cover.png')
if not os.path.exists(default_cover_path):
    print(f"Warning: Default cover image not found at {default_cover_path}")


if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.mainloop()
