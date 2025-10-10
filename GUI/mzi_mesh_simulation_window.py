"""
Ventana para ejecutar simulación de MZI Mesh
Muestra el progreso de la simulación en una ventana modal
"""

import customtkinter as ctk
import threading

# Colores del tema
THEME_COLOR = "#E31E24"
DARK_BG = "#1a1a1a"
CARD_BG = "#252525"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#999999"


class MZIMeshSimulationWindow(ctk.CTkToplevel):
    """Ventana modal para mostrar progreso de simulación MZI Mesh"""
    
    def __init__(self, parent, api, params, callback):
        super().__init__(parent)
        
        self.api = api
        self.params = params
        self.callback = callback
        self.results = None
        self.error = None
        
        self.title("Simulación MZI Mesh en progreso...")
        self.geometry("600x350")
        self.transient(parent)
        self.grab_set()
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (350 // 2)
        self.geometry(f"600x350+{x}+{y}")
        
        # Configurar estilo
        self.configure(fg_color=DARK_BG)
        
        # Configurar contenido
        self.setup_ui()
        
        # Ejecutar simulación en thread separado
        self.thread = threading.Thread(target=self.run_simulation, daemon=True)
        self.thread.start()
        
        # Prevenir cierre manual durante simulación
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=DARK_BG)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="🔷 Ejecutando Simulación MZI Mesh",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title.pack(pady=(0, 10))
        
        # Subtítulo con info de la simulación
        dim = self.params['unitary_matrix'].shape[0]
        subtitle = ctk.CTkLabel(
            main_frame,
            text=f"Matriz {dim}×{dim} | Plataforma: {self.params['platform'].upper()}",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 30))
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(
            main_frame, 
            width=500,
            height=20,
            fg_color=CARD_BG,
            progress_color=THEME_COLOR
        )
        self.progress.pack(pady=20)
        self.progress.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Inicializando simulación...",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_PRIMARY,
            wraplength=500
        )
        self.status_label.pack(pady=10)
        
        # Frame para detalles (log)
        details_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG)
        details_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        details_title = ctk.CTkLabel(
            details_frame,
            text="Detalles de la simulación:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        details_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.details_text = ctk.CTkTextbox(
            details_frame,
            height=100,
            font=ctk.CTkFont(family="Courier", size=11),
            fg_color=DARK_BG,
            text_color=TEXT_SECONDARY,
            wrap="word"
        )
        self.details_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.details_text.configure(state="disabled")
    
    def add_detail(self, message):
        """Añadir mensaje al log de detalles"""
        self.details_text.configure(state="normal")
        self.details_text.insert("end", message + "\n")
        self.details_text.see("end")
        self.details_text.configure(state="disabled")
    
    def update_status(self, message, progress):
        """Actualizar estado de la simulación"""
        self.status_label.configure(text=message)
        self.progress.set(progress)
        self.add_detail(f"[{int(progress*100)}%] {message}")
    
    def run_simulation(self):
        """Ejecutar la simulación en thread separado"""
        try:
            # Fase 1: Inicialización
            self.update_status("Inicializando MZI Mesh Simulator...", 0.1)
            
            # Fase 2: Construcción del mesh
            self.update_status("Construyendo mesh de Mach-Zehnder...", 0.3)
            
            # Fase 3: Ejecutar simulación
            self.update_status("Ejecutando simulación INTERCONNECT...", 0.5)
            
            # Llamar a la API
            self.results = self.api.run_mzi_mesh(
                self.params['unitary_matrix'],
                self.params['input_vector'],
                visualize=self.params.get('visualize', False)
            )
            
            # Fase 4: Procesando resultados
            self.update_status("Procesando resultados...", 0.9)
            
            # Fase 5: Completado
            self.update_status("✓ Simulación completada exitosamente", 1.0)
            
            # Esperar un momento antes de cerrar
            self.after(1500, lambda: self.finish(True))
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            traceback_msg = traceback.format_exc()
            
            self.error = error_msg
            self.update_status(f"✗ Error: {error_msg}", 1.0)
            self.add_detail(f"\nTraceback completo:\n{traceback_msg}")
            
            # Esperar antes de cerrar
            self.after(3000, lambda: self.finish(False))
    
    def finish(self, success):
        """Finalizar y cerrar ventana"""
        if self.callback:
            self.callback(success, self.results, self.error)
        self.destroy()
    
    def on_closing(self):
        """Prevenir cierre durante simulación"""
        # Solo permitir cerrar si la simulación terminó
        if self.progress.get() >= 1.0:
            self.destroy()
        else:
            # Mostrar mensaje
            pass  # Ignorar intento de cierre