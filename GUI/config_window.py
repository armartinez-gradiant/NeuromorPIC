"""
Ventana de configuración de parámetros de simulación
"""

import customtkinter as ctk
from tkinter import messagebox


class ConfigurationWindow:
    """Ventana para configurar parámetros de simulación"""
    
    def __init__(self, parent, defaults, callback):
        """
        Args:
            parent: Ventana padre
            defaults: Diccionario con valores por defecto
            callback: Función a llamar cuando se confirme la configuración
        """
        self.defaults = defaults
        self.callback = callback
        self.params = {}
        
        # Crear ventana toplevel (ventana secundaria)
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Configuración de Simulación")
        self.window.geometry("700x650")
        
        # Hacer que la ventana sea modal (bloquea la ventana principal)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Configurar la interfaz
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar todos los elementos de la interfaz"""
        
        # ========== TÍTULO ==========
        title_label = ctk.CTkLabel(
            self.window,
            text="⚙️ Configuración de Parámetros",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=15)
        
        # ========== FRAME CON SCROLL ==========
        # Para manejar muchos parámetros sin que se salga de la ventana
        main_frame = ctk.CTkScrollableFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # ========== SECCIÓN 1: LONGITUD DE ONDA ==========
        self.create_section_header(main_frame, "📡 Parámetros del Láser")
        
        self.wavelength_entry = self.create_parameter_field(
            main_frame,
            "Longitud de onda (m):",
            self.defaults.get('source_wavelength', '1.55e-6'),
            "Ejemplo: 1.55e-6 (1550nm)"
        )
        
        # ========== SECCIÓN 2: VOLTAJE ==========
        self.create_section_header(main_frame, "⚡ Rango de Voltaje")
        
        self.min_voltage_entry = self.create_parameter_field(
            main_frame,
            "Voltaje mínimo (V):",
            self.defaults.get('min_v', '0.0'),
            "Voltaje mínimo a simular"
        )
        
        self.max_voltage_entry = self.create_parameter_field(
            main_frame,
            "Voltaje máximo (V):",
            self.defaults.get('max_v', '20.0'),
            "Voltaje máximo a simular"
        )
        
        self.voltage_interval_entry = self.create_parameter_field(
            main_frame,
            "Intervalo de voltaje (V):",
            self.defaults.get('interval_v', '0.2'),
            "Paso entre valores de voltaje"
        )
        
        # ========== SECCIÓN 3: TIEMPO ==========
        self.create_section_header(main_frame, "⏱️ Parámetros Temporales")
        
        self.time_window_entry = self.create_parameter_field(
            main_frame,
            "Ventana de tiempo (s):",
            self.defaults.get('time_window', '5.12e-9'),
            "Ejemplo: 5.12e-9 (nanosegundos)"
        )
        
        self.n_samples_entry = self.create_parameter_field(
            main_frame,
            "Número de muestras:",
            self.defaults.get('n_samples', '15360'),
            "Cantidad de puntos a muestrear"
        )
        
        # ========== SECCIÓN 4: SALIDA ==========
        self.create_section_header(main_frame, "💾 Configuración de Salida")
        
        self.output_dir_entry = self.create_parameter_field(
            main_frame,
            "Directorio de salida:",
            self.defaults.get('output_dir', './results'),
            "Carpeta donde guardar resultados"
        )
        
        # ========== BOTONES DE ACCIÓN ==========
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(fill="x", padx=20, pady=15)
        
        # Botón Cancelar
        cancel_button = ctk.CTkButton(
            button_frame,
            text="✖ Cancelar",
            command=self.cancel,
            fg_color="gray",
            hover_color="darkgray",
            width=150
        )
        cancel_button.pack(side="left", padx=10)
        
        # Botón Confirmar
        confirm_button = ctk.CTkButton(
            button_frame,
            text="✓ Confirmar y Continuar",
            command=self.confirm,
            width=200
        )
        confirm_button.pack(side="right", padx=10)
        
    def create_section_header(self, parent, text):
        """Crear un encabezado de sección"""
        header = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        header.pack(fill="x", pady=(15, 5))
        
        # Línea separadora
        separator = ctk.CTkFrame(parent, height=2)
        separator.pack(fill="x", pady=5)
        
    def create_parameter_field(self, parent, label_text, default_value, help_text):
        """
        Crear un campo de entrada de parámetro con etiqueta y ayuda
        
        Returns:
            CTkEntry: El widget de entrada creado
        """
        # Frame contenedor
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)
        
        # Etiqueta
        label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=200
        )
        label.pack(side="left", padx=(0, 10))
        
        # Campo de entrada
        entry = ctk.CTkEntry(
            field_frame,
            placeholder_text=str(default_value),
            width=250
        )
        entry.pack(side="left")
        entry.insert(0, str(default_value))
        
        # Texto de ayuda
        help_label = ctk.CTkLabel(
            field_frame,
            text=f"ℹ️ {help_text}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        help_label.pack(side="left", padx=10)
        
        return entry
    
    def validate_inputs(self):
        """Validar que todos los inputs sean correctos"""
        try:
            # Validar longitud de onda
            wavelength = float(self.wavelength_entry.get())
            if wavelength <= 0:
                raise ValueError("La longitud de onda debe ser positiva")
            
            # Validar voltajes
            min_v = float(self.min_voltage_entry.get())
            max_v = float(self.max_voltage_entry.get())
            interval_v = float(self.voltage_interval_entry.get())
            
            if min_v >= max_v:
                raise ValueError("El voltaje mínimo debe ser menor que el máximo")
            if interval_v <= 0:
                raise ValueError("El intervalo de voltaje debe ser positivo")
            
            # Validar tiempo
            time_window = float(self.time_window_entry.get())
            n_samples = int(self.n_samples_entry.get())
            
            if time_window <= 0:
                raise ValueError("La ventana de tiempo debe ser positiva")
            if n_samples <= 0:
                raise ValueError("El número de muestras debe ser positivo")
            
            # Validar directorio
            output_dir = self.output_dir_entry.get().strip()
            if not output_dir:
                raise ValueError("Debe especificar un directorio de salida")
            
            # Si todo es válido, guardar parámetros
            self.params = {
                'source_wavelength': wavelength,
                'min_v': min_v,
                'max_v': max_v,
                'interval_v': interval_v,
                'time_window': time_window,
                'n_samples': n_samples,
                'output_dir': output_dir
            }
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
            return False
    
    def confirm(self):
        """Confirmar la configuración"""
        if self.validate_inputs():
            print("✅ Configuración validada correctamente")
            print("Parámetros:", self.params)
            
            # Llamar al callback con los parámetros
            self.callback(self.params)
            
            # Cerrar la ventana
            self.window.destroy()
    
    def cancel(self):
        """Cancelar la configuración"""
        print("❌ Configuración cancelada")
        self.window.destroy()