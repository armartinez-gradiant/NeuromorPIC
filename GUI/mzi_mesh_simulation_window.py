"""
Ventana para ejecutar simulación de MZI Mesh
Muestra el progreso de la simulación en una ventana modal
CORREGIDO: Thread-safe para Tkinter y gestión de cierre mejorada
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
        self.geometry("700x550")
        self.transient(parent)
        self.grab_set()
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"700x550+{x}+{y}")
        
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
            width=600,
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
            wraplength=600
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
            height=180,
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
            text="Cerrar Ventana (INTERCONNECT seguirá abierto)",
            command=self.close_window_only,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        # NO hacer pack() aquí - se mostrará solo si show_interconnect=True
    
    def add_detail(self, message):
        """
        Añadir mensaje al log de detalles (THREAD-SAFE)
        Programa la actualización en el thread principal
        """
        def _add():
            try:
                self.details_text.configure(state="normal")
                self.details_text.insert("end", message + "\n")
                self.details_text.see("end")
                self.details_text.configure(state="disabled")
            except Exception as e:
                print(f"Error añadiendo detalle: {e}")
        
        # Programar actualización en el thread principal
        self.after(0, _add)
    
    def update_status(self, message, progress_value=None):
        """
        Actualizar el label de status (THREAD-SAFE)
        """
        def _update():
            try:
                self.status_label.configure(text=message)
                if progress_value is not None:
                    self.progress.set(progress_value)
            except Exception as e:
                print(f"Error actualizando status: {e}")
        
        # Programar actualización en el thread principal
        self.after(0, _update)
    
    def update_progress(self, value):
        """
        Actualizar la barra de progreso (THREAD-SAFE)
        Args:
            value: float entre 0.0 y 1.0
        """
        def _update():
            try:
                self.progress.set(value)
            except Exception as e:
                print(f"Error actualizando progreso: {e}")
        
        # Programar actualización en el thread principal
        self.after(0, _update)
    
    def run_simulation(self):
        """Ejecutar la simulación MZI Mesh"""
        try:
            # Fase 1: Descomposición
            self.update_status("Descomponiendo matriz unitaria...", 0.1)
            self.add_detail("="*50)
            self.add_detail("FASE 1: Descomposición de Matriz")
            self.add_detail("="*50)
            
            # Fase 2: Configuración
            self.update_status("Configurando INTERCONNECT...", 0.3)
            self.add_detail("\n" + "="*50)
            self.add_detail("FASE 2: Configuración de INTERCONNECT")
            self.add_detail("="*50)
            
            # Fase 3: Ejecución
            self.update_status("Ejecutando simulación en INTERCONNECT...", 0.5)
            self.add_detail("\n" + "="*50)
            self.add_detail("FASE 3: Ejecución de Simulación")
            self.add_detail("="*50)
            
            # EJECUTAR SIMULACIÓN REAL
            self.results = self.api.run_mzi_mesh(
                unitary_matrix=self.params['unitary_matrix'],
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
                self.add_detail(f"\nError promedio: {self.results.get('avg_error', 'N/A')}")
                self.add_detail(f"Error máximo: {self.results.get('max_error', 'N/A')}")
            
            # Programar cierre (en el main thread)
            self.after(3000, self.finish_success)
            
        except Exception as e:
            # Error durante simulación
            self.error = str(e)
            self.update_status(f"✗ Error: {self.error}", 0.0)
            self.add_detail("\n" + "="*50)
            self.add_detail("✗ ERROR EN SIMULACIÓN")
            self.add_detail("="*50)
            self.add_detail(f"\n{self.error}\n")
            
            # Programar cerrar (en el main thread)
            self.after(8000, self.finish_error)
    
    def finish_success(self):
        """Finalizar con éxito"""
        show_ic = self.params.get('show_interconnect', False)
        
        def _finish():
            try:
                if self.callback:
                    self.callback(success=True, results=self.results, error=None)
                
                # Solo destruir si INTERCONNECT NO debe permanecer abierto
                if not show_ic:
                    self.destroy()
                else:
                    # Mostrar mensaje e informar
                    self.update_status("✓ Completado - INTERCONNECT permanece abierto", 1.0)
                    self.add_detail("\n" + "="*50)
                    self.add_detail("✅ PUEDES CERRAR ESTA VENTANA")
                    self.add_detail("="*50)
                    self.add_detail("\n⚠ INTERCONNECT sigue abierto para inspección")
                    self.add_detail("Cierra INTERCONNECT manualmente cuando termines.\n")
                    
                    # Mostrar botón de cerrar
                    self.close_btn.pack(pady=15)
                    
                    # Liberar el grab para que el usuario pueda interactuar con INTERCONNECT
                    self.grab_release()
            except Exception:
                pass  # La ventana podría haberse cerrado
        
        # Ejecutar en el main thread de Tkinter
        self.after(0, _finish)
    
    def finish_error(self):
        """Finalizar con error"""
        def _finish():
            try:
                if self.callback:
                    self.callback(success=False, results=None, error=self.error)
                self.destroy()
            except Exception:
                pass  # La ventana podría haberse cerrado
        
        self.after(0, _finish)
    
    def close_window_only(self):
        """Cerrar solo la ventana de progreso, mantener INTERCONNECT abierto"""
        self.destroy()
    
    def on_closing(self):
        """Prevenir cierre durante simulación"""
        # Si la simulación terminó y show_interconnect=True, permitir cerrar
        if self.progress.get() >= 1.0 or self.error is not None:
            self.destroy()