"""
Ventana de ejecución y progreso de simulación
"""

import customtkinter as ctk
import threading
from tkinter import messagebox
import sys
from io import StringIO

# Tema personalizado
THEME_COLOR = "#E31E24"
THEME_COLOR_HOVER = "#B01419"
DARK_BG = "#1a1a1a"
CARD_BG = "#2b2b2b"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#b0b0b0"


class SimulationWindow:
    """Ventana para ejecutar y monitorear simulación"""
    
    def __init__(self, parent, api, params, callback=None):
        """
        Args:
            parent: Ventana padre
            api: Instancia de API
            params: Parámetros de simulación
            callback: Función a llamar al finalizar
        """
        self.api = api
        self.params = params
        self.callback = callback
        self.is_running = False
        
        # Crear ventana
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Ejecutando Simulación")
        self.window.geometry("800x600")
        self.window.configure(fg_color=DARK_BG)
        
        # Hacer modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Prevenir cierre durante simulación
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
        # Iniciar simulación automáticamente
        self.start_simulation()
        
    def setup_ui(self):
        """Configurar interfaz"""
        
        # Header
        header_frame = ctk.CTkFrame(self.window, fg_color=THEME_COLOR, height=70, corner_radius=0)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="⚙️  Ejecutando Simulación",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title.pack(pady=20, padx=30, anchor="w")
        
        # Contenido principal
        content_frame = ctk.CTkFrame(self.window, fg_color=DARK_BG)
        content_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Estado actual
        self.status_label = ctk.CTkLabel(
            content_frame,
            text="Inicializando simulación...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME_COLOR
        )
        self.status_label.pack(pady=(10, 20))
        
        # Barra de progreso indeterminada
        self.progress_bar = ctk.CTkProgressBar(
            content_frame,
            width=700,
            height=20,
            progress_color=THEME_COLOR
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        self.progress_bar.start()
        
        # Área de logs
        log_label = ctk.CTkLabel(
            content_frame,
            text="Log de Ejecución:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        log_label.pack(fill="x", pady=(20, 5))
        
        self.log_text = ctk.CTkTextbox(
            content_frame,
            font=ctk.CTkFont(family="Courier", size=11),
            fg_color=CARD_BG,
            text_color=TEXT_SECONDARY,
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Botón de cerrar (inicialmente deshabilitado)
        self.close_button = ctk.CTkButton(
            content_frame,
            text="Cerrar",
            command=self.close_window,
            state="disabled",
            fg_color=TEXT_SECONDARY,
            width=150,
            height=40
        )
        self.close_button.pack(pady=10)
        
    def log(self, message):
        """Añadir mensaje al log"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.window.update()
        
    def update_status(self, status):
        """Actualizar estado actual"""
        self.status_label.configure(text=status)
        self.window.update()
        
    def start_simulation(self):
        """Iniciar simulación en thread separado"""
        self.is_running = True
        self.log("="*70)
        self.log("INICIO DE SIMULACIÓN")
        self.log("="*70)
        
        # Mostrar parámetros
        self.log("\nParámetros de simulación:")
        for key, value in self.params.items():
            self.log(f"  • {key}: {value}")
        self.log("\n" + "="*70)
        
        # Ejecutar en thread separado para no bloquear UI
        thread = threading.Thread(target=self.run_simulation)
        thread.daemon = True
        thread.start()
        
    def run_simulation(self):
        """Ejecutar la simulación"""
        try:
            # Capturar stdout para mostrar en log
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            self.update_status("Ejecutando simulaciones de Lumerical...")
            self.log("\n▶ Iniciando simulaciones...\n")
            
            # EJECUTAR LA SIMULACIÓN
            self.api.run(self.params)
            
            # Recuperar output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Mostrar output en log
            if output:
                self.log(output)
            
            # Simulación completada exitosamente
            self.log("\n" + "="*70)
            self.log("✓ SIMULACIÓN COMPLETADA EXITOSAMENTE")
            self.log("="*70)
            
            self.update_status("Simulación completada exitosamente")
            self.progress_bar.stop()
            self.progress_bar.set(1.0)
            
            self.is_running = False
            self.close_button.configure(
                state="normal",
                fg_color=THEME_COLOR,
                hover_color=THEME_COLOR_HOVER
            )
            
            # Llamar callback si existe
            if self.callback:
                self.callback(success=True, params=self.params)
            
        except Exception as e:
            # Restaurar stdout
            sys.stdout = old_stdout
            
            # Error durante simulación
            error_msg = str(e)
            self.log("\n" + "="*70)
            self.log("✗ ERROR EN SIMULACIÓN")
            self.log("="*70)
            self.log(f"\nError: {error_msg}\n")
            
            self.update_status("Error durante la simulación")
            self.progress_bar.stop()
            self.progress_bar.set(0)
            
            self.is_running = False
            self.close_button.configure(
                state="normal",
                fg_color="darkred",
                hover_color="red"
            )
            
            messagebox.showerror(
                "Error de Simulación",
                f"Ocurrió un error durante la simulación:\n\n{error_msg}"
            )
            
            # Llamar callback con error
            if self.callback:
                self.callback(success=False, error=error_msg)
    
    def on_closing(self):
        """Manejar intento de cerrar ventana"""
        if self.is_running:
            response = messagebox.askyesno(
                "Simulación en progreso",
                "La simulación está en progreso. ¿Desea cancelarla y cerrar?"
            )
            if response:
                self.is_running = False
                self.window.destroy()
        else:
            self.close_window()
    
    def close_window(self):
        """Cerrar ventana"""
        self.window.destroy()