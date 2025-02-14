import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from pygame import mixer
import pygame  # Asegúrate de importar pygame completo para manejar eventos
import shutil

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("600x400")

        self.albums = {}
        self.current_album = None
        self.current_song = None
        self.is_playing = False
        self.auto_play = False  # Variable para controlar el modo de auto-reproducción

        # Crear widgets
        self.create_widgets()
        mixer.init()

        # Inicializar pygame para manejar eventos
        pygame.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

        # Cargar álbumes y canciones desde el disco
        self.load_albums()

        # Evento de finalización de canción
        self.root.after(100, self.check_song_end)

    def create_widgets(self):
        # Colores
        bg_color = "#282c34"
        fg_color = "#ffffff"
        btn_color = "#61afef"
        listbox_color = "#1e2127"
        
        # Configurar el color de fondo de la ventana
        self.root.configure(bg=bg_color)

        # Crear un marco para la lista de álbumes
        album_frame = tk.Frame(self.root, bg=bg_color)
        album_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=True)

        # Lista de álbumes
        self.album_listbox = tk.Listbox(album_frame, bg=listbox_color, fg=fg_color, selectbackground="#3e4451", selectforeground=fg_color)
        self.album_listbox.pack(fill=tk.BOTH, expand=True)
        self.album_listbox.bind("<<ListboxSelect>>", self.on_album_select)

        # Crear un marco para la lista de canciones
        song_frame = tk.Frame(self.root, bg=bg_color)
        song_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=True)

        # Lista de canciones
        self.song_listbox = tk.Listbox(song_frame, bg=listbox_color, fg=fg_color, selectbackground="#3e4451", selectforeground=fg_color)
        self.song_listbox.pack(fill=tk.BOTH, expand=True)
        self.song_listbox.bind("<<ListboxSelect>>", self.on_song_select)

        # Crear un marco para los botones
        control_frame = tk.Frame(self.root, bg=bg_color)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        # Botones para agregar y eliminar álbumes y canciones
        btn_add_album = tk.Button(control_frame, text="Agregar Álbum", command=self.add_album, bg=btn_color, fg=fg_color)
        btn_add_album.pack(pady=5, fill=tk.X)

        btn_remove_album = tk.Button(control_frame, text="Eliminar Álbum", command=self.remove_album, bg=btn_color, fg=fg_color)
        btn_remove_album.pack(pady=5, fill=tk.X)

        btn_add_song = tk.Button(control_frame, text="Agregar Canción", command=self.add_song, bg=btn_color, fg=fg_color)
        btn_add_song.pack(pady=5, fill=tk.X)

        btn_remove_song = tk.Button(control_frame, text="Eliminar Canción", command=self.remove_song, bg=btn_color, fg=fg_color)
        btn_remove_song.pack(pady=5, fill=tk.X)

        # Botones de control de música
        btn_play = tk.Button(control_frame, text="Reproducir", command=self.play_song, bg=btn_color, fg=fg_color)
        btn_play.pack(pady=5, fill=tk.X)

        btn_pause = tk.Button(control_frame, text="Pausar", command=self.pause_song, bg=btn_color, fg=fg_color)
        btn_pause.pack(pady=5, fill=tk.X)

        btn_stop = tk.Button(control_frame, text="Detener", command=self.stop_song, bg=btn_color, fg=fg_color)
        btn_stop.pack(pady=5, fill=tk.X)

        # Botón de Auto-Reproducir
        self.auto_play_button = tk.Button(control_frame, text="Auto-Reproducir: OFF", command=self.toggle_auto_play, bg=btn_color, fg=fg_color)
        self.auto_play_button.pack(pady=5, fill=tk.X)

        # Barra de volumen
        self.volume_scale = tk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume, bg=bg_color, fg=fg_color, sliderlength=20, length=150)
        self.volume_scale.set(50)  # Volumen inicial al 50%
        self.volume_scale.pack(pady=10)

    def toggle_auto_play(self):
        """Alternar el modo de auto-reproducción."""
        self.auto_play = not self.auto_play
        if self.auto_play:
            self.auto_play_button.config(text="Auto-Reproducir: ON")
        else:
            self.auto_play_button.config(text="Auto-Reproducir: OFF")

    def check_song_end(self):
        """Revisa si la canción ha terminado."""
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT and self.auto_play:
                self.play_next_song()
        self.root.after(100, self.check_song_end)

    def play_next_song(self):
        """Reproduce la siguiente canción automáticamente."""
        if self.current_album:
            current_album_songs = self.albums.get(self.current_album, [])
            if current_album_songs:
                current_index = current_album_songs.index(self.current_song)
                next_index = (current_index + 1) % len(current_album_songs)  # Avanza al siguiente o vuelve al inicio
                self.current_song = current_album_songs[next_index]
                self.play_song()

    def add_album(self):
        album_name = simpledialog.askstring("Nombre del Álbum", "Ingrese el nombre del álbum:")
        if album_name:
            album_path = os.path.join("DataMusic", album_name)
            if not os.path.exists(album_path):
                os.makedirs(album_path)
                self.albums[album_name] = []
                self.album_listbox.insert(tk.END, album_name)
                print(f"Álbum '{album_name}' creado en {album_path}")

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
                for file_name in os.listdir(album_path):
                    file_path = os.path.join(album_path, file_name)
                    try:
                        os.remove(file_path)
                    except PermissionError:
                        messagebox.showerror("Error", f"No se puede eliminar el archivo '{file_name}' porque está en uso.")
                        return
                os.rmdir(album_path)
                self.album_listbox.delete(self.album_listbox.curselection())
                del self.albums[self.current_album]
                self.current_album = None
                self.song_listbox.delete(0, tk.END)
                print(f"Álbum '{self.current_album}' eliminado.")
            else:
                messagebox.showerror("Error", "No se pudo encontrar la carpeta del álbum.")

    def add_song(self):
        if self.current_album is None:
            messagebox.showerror("Error", "Por favor, selecciona un álbum.")
            return

        song_paths = filedialog.askopenfilenames(title="Seleccionar Canciones", filetypes=(("MP3 Files", "*.mp3"),))
        if song_paths:
            album_path = os.path.join("DataMusic", self.current_album)
            for song_path in song_paths:
                song_name = os.path.basename(song_path)
                destination = os.path.join(album_path, song_name)
                if not os.path.exists(destination):
                    shutil.copy(song_path, destination)  # Copia el archivo en lugar de moverlo
                    self.albums[self.current_album].append(song_name)
                    self.song_listbox.insert(tk.END, song_name)
                    print(f"Canción '{song_name}' copiada al álbum '{self.current_album}' en {destination}")
                else:
                    messagebox.showwarning("Advertencia", f"La canción '{song_name}' ya existe en el álbum '{self.current_album}'")

    def remove_song(self):
        if self.current_album is None:
            messagebox.showerror("Error", "Por favor, selecciona un álbum.")
            return
        if self.current_song is None:
            messagebox.showerror("Error", "Por favor, selecciona una canción.")
            return

        confirmation = messagebox.askyesno("Confirmación", f"¿Estás seguro de que quieres eliminar la canción '{self.current_song}'?")
        if confirmation:
            song_path = os.path.join("DataMusic", self.current_album, self.current_song)
            if os.path.exists(song_path):
                try:
                    os.remove(song_path)
                    self.albums[self.current_album].remove(self.current_song)
                    self.song_listbox.delete(self.song_listbox.curselection())
                    if self.current_song == self.song_listbox.get(0):  # Si la canción eliminada es la actual
                        self.stop_song()
                        self.current_song = None
                    print(f"Canción '{self.current_song}' eliminada.")
                except PermissionError:
                    messagebox.showerror("Error", f"No se puede eliminar la canción '{self.current_song}' porque está en uso.")
            else:
                messagebox.showerror("Error", "No se pudo encontrar el archivo de la canción.")

    def on_album_select(self, event):
        selection = self.album_listbox.curselection()
        if selection:
            album_index = selection[0]
            self.current_album = self.album_listbox.get(album_index)
            print(f"Álbum seleccionado: {self.current_album}")
            self.update_song_list()

    def update_song_list(self):
        self.song_listbox.delete(0, tk.END)
        for song in self.albums.get(self.current_album, []):
            self.song_listbox.insert(tk.END, song)

    def on_song_select(self, event):
        selection = self.song_listbox.curselection()
        if selection:
            song_index = selection[0]
            self.current_song = self.song_listbox.get(song_index)
            print(f"Canción seleccionada: {self.current_song}")

    def play_song(self):
        if self.current_song:
            song_path = os.path.join("DataMusic", self.current_album, self.current_song)
            mixer.music.load(song_path)
            mixer.music.play()
            self.is_playing = True
            print(f"Reproduciendo: {self.current_song}")

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
        mixer.music.stop()
        self.is_playing = False
        print("Canción detenida")

    def set_volume(self, volume):
        mixer.music.set_volume(int(volume) / 100)

    def load_albums(self):
        data_folder = "DataMusic"
        if os.path.exists(data_folder):
            for album_name in os.listdir(data_folder):
                album_path = os.path.join(data_folder, album_name)
                if os.path.isdir(album_path):
                    self.albums[album_name] = []
                    self.album_listbox.insert(tk.END, album_name)
                    for song_name in os.listdir(album_path):
                        self.albums[album_name].append(song_name)
        print("Álbumes y canciones cargados desde el disco.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
