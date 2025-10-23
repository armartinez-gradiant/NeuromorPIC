"""
Ventana para ejecutar simulación de Multiplicación Matricial
Soporta matrices unitarias y no unitarias (con SVD)
"""

import customtkinter as ctk
import threading

# Colores del tema
THEME_COLOR = "#E31E24"
THEME_COLOR_HOVER = "#C41A1F"
DARK_BG = "#1a1a1a"
CARD_BG = "#252525"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#999999"


class MatrixMultSimulationWindow(ctk.CTkToplevel):
    """Ventana modal para mostrar progreso de simulación"""
    
    def __init__(self, parent, api, params, callback):
        super().__init__(parent)
        
        self.api = api
        self.params = params
        self.callback = callback
        self.results = None
        self.error = None
        
        self.title("Simulación de Multiplicación Matricial...")
        self.geometry("750x600")
        self.transient(parent)
        self.grab_set()
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"750x600+{x}+{y}")
        
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
            text="🔷 Multiplicación Matricial Óptica",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title.pack(pady=(0, 10))
        
        # Subtítulo con info de la simulación
        dim = self.params['unitary_matrix'].shape[0]
        matrix_info = "Unitaria" if self.params['is_unitary'] else "No Unitaria (SVD)"
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text=f"Matriz {dim}×{dim} ({matrix_info}) | Plataforma: {self.params['platform'].upper()}",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 30))
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(
            main_frame, 
            width=650,
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
            wraplength=650
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
            height=200,
            font=ctk.CTkFont(family="Courier", size=11),
            fg_color=DARK_BG,
            text_color=TEXT_SECONDARY,
            wrap="word"
        )
        self.details_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.details_text.configure(state="disabled")
        
        # Botón de cerrar (inicialmente oculto)
        self.close_btn = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.close_window_only,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            width=200,
            height=40
        )
        # No lo mostramos hasta que termine
    
    def update_status(self, message, progress):
        """Actualizar status y barra de progreso (thread-safe)"""
        self.after(0, lambda: self.status_label.configure(text=message))
        self.after(0, lambda: self.progress.set(progress))
    
    def add_detail(self, message):
        """Añadir mensaje al log de detalles (thread-safe)"""
        def _add():
            self.details_text.configure(state="normal")
            self.details_text.insert("end", message + "\n")
            self.details_text.see("end")
            self.details_text.configure(state="disabled")
        self.after(0, _add)
    
    def run_simulation(self):
        """Ejecutar simulación en thread separado"""
        try:
            # Fase 1: Validación
            self.update_status("Validando parámetros...", 0.1)
            self.add_detail("="*50)
            self.add_detail("FASE 1: Validación de Parámetros")
            self.add_detail("="*50)
            self.add_detail(f"Dimensión: {self.params['unitary_matrix'].shape}")
            self.add_detail(f"Tipo: {'Unitaria' if self.params['is_unitary'] else 'No Unitaria (SVD)'}")
            self.add_detail(f"Plataforma: {self.params['platform'].upper()}")
            
            # Fase 2: Construcción del circuito
            self.update_status("Construyendo circuito fotónico...", 0.3)
            self.add_detail("\n" + "="*50)
            self.add_detail("FASE 2: Construcción del Circuito")
            self.add_detail("="*50)
            
            # Fase 3: Ejecución
            self.update_status("Ejecutando simulación en INTERCONNECT...", 0.5)
            self.add_detail("\n" + "="*50)
            self.add_detail("FASE 3: Simulación")
            self.add_detail("="*50)
            
            # EJECUTAR SIMULACIÓN REAL
            if self.params['is_unitary']:
                self.add_detail("Usando método de matriz unitaria (MZI Mesh estándar)")
                self.results = self.api.run_matrix_multiplication(
                    unitary_matrix=self.params['unitary_matrix'],
                    input_vector=self.params['input_vector'],
                    visualize=self.params.get('visualize', False),
                    show_interconnect=self.params.get('show_interconnect', False)
                )
            else:
                self.add_detail("Usando método general con descomposición SVD")
                self.results = self.api.run_general_matrix_multiplication(
                    matrix=self.params['unitary_matrix'],
                    input_vector=self.params['input_vector'],
                    visualize=self.params.get('visualize', False),
                    show_interconnect=self.params.get('show_interconnect', False)
                )
            
            # Fase 4: Completado
            self.update_status("✓ Simulación completada exitosamente", 1.0)
            self.add_detail("\n" + "="*50)
            self.add_detail("✓ SIMULACIÓN COMPLETADA")
            self.add_detail("="*50)
            
            if self.results:
                self.add_detail(f"\nError promedio: {self.results.get('avg_error', 'N/A'):.6e}")
                self.add_detail(f"Error máximo: {self.results.get('max_error', 'N/A'):.6e}")
            
            # Mostrar botón de cerrar
            self.after(0, lambda: self.close_btn.pack(pady=20))
            
            # Programar callback (en el main thread)
            self.after(100, self.finish_success)
            
        except Exception as e:
            # Error durante simulación
            self.error = str(e)
            self.update_status(f"✗ Error: {self.error}", 0.0)
            self.add_detail("\n" + "="*50)
            self.add_detail("✗ ERROR EN SIMULACIÓN")
            self.add_detail("="*50)
            self.add_detail(f"\n{self.error}\n")
            
            import traceback
            self.add_detail("\nTraceback:")
            self.add_detail(traceback.format_exc())
            
            # Mostrar botón de cerrar
            self.after(0, lambda: self.close_btn.pack(pady=20))
            
            # Programar callback de error
            self.after(100, self.finish_error)
    
    def finish_success(self):
        """Finalizar con éxito"""
        if self.callback:
            self.callback(success=True, results=self.results)
    
    def finish_error(self):
        """Finalizar con error"""
        if self.callback:
            self.callback(success=False, error=self.error)
    
    def close_window_only(self):
        """Cerrar solo la ventana (INTERCONNECT puede seguir abierto)"""
        # Llamar al callback si no se ha llamado aún
        if self.results:
            self.finish_success()
        elif self.error:
            self.finish_error()
        
        self.destroy()
    
    def on_closing(self):
        """Manejar intento de cerrar ventana durante simulación"""
        # Si aún está corriendo la simulación, no permitir cerrar
        if self.thread.is_alive():
            return
        
        self.close_window_only()