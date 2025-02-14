import tkinter as tk

class Perfil:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.frame_principal = tk.Frame(self.parent, bg="#1a1a1d")
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.frame_principal, 
                text="Perfil del usuario",
                font=("Helvetica", 16, "bold"),
                bg="#1a1a1d",
                fg="white").pack(pady=20)
        
        # Aquí puedes añadir más elementos del perfil