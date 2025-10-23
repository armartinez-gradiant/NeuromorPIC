"""
Formulario de configuración de simulación como componente reutilizable
Archivo: GUI/simulation_config_form.py
"""

import customtkinter as ctk

# Tema personalizado
THEME_COLOR = "#E31E24"
THEME_COLOR_HOVER = "#C01018"
DARK_BG = "#1a1a1a"
CARD_BG = "#252525"
INPUT_BG = "#2d2d2d"  # Fondo más claro para inputs
INPUT_BORDER = "#404040"  # Borde visible para inputs
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#999999"
TEXT_DISABLED = "#555555"


class SimulationConfigForm(ctk.CTkFrame):
    """Formulario de configuración de simulación integrado"""
    
    def __init__(self, parent, defaults, on_submit_callback, on_cancel_callback):
        """
        Args:
            parent: Widget padre
            defaults: Diccionario con valores por defecto
            on_submit_callback: Función a llamar al confirmar (recibe params dict)
            on_cancel_callback: Función a llamar al cancelar
        """
        super().__init__(parent, fg_color=DARK_BG)
        
        self.defaults = defaults
        self.on_submit = on_submit_callback
        self.on_cancel = on_cancel_callback
        
        # Variables para los widgets
        self.sim_type_var = ctk.StringVar(value="scatter")
        self.heater_sim_type_var = ctk.StringVar(value="sweep")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del formulario"""
        
        # Frame con scroll
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=DARK_BG,
            scrollbar_button_color=THEME_COLOR,
            scrollbar_button_hover_color=THEME_COLOR_HOVER
        )
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # ========== HEADER ==========
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20), padx=30)
        
        title = ctk.CTkLabel(
            header_frame,
            text="⚙️  Configuración de Simulación",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Configure los parámetros de simulación para Lumerical INTERCONNECT",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # ========== SECCIÓN 1: TIPO DE SIMULACIÓN LÁSER ==========
        laser_card = self.create_section_card(scroll_frame, "🔬  Tipo de Simulación Láser")
        
        radio_frame = ctk.CTkFrame(laser_card, fg_color="transparent")
        radio_frame.pack(fill="x", padx=30, pady=(10, 15))
        
        radio_scatter = ctk.CTkRadioButton(
            radio_frame,
            text="Multi-Wavelength Scatter",
            variable=self.sim_type_var,
            value="scatter",
            command=self.on_sim_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        radio_scatter.pack(side="left", padx=(0, 30))
        
        radio_single = ctk.CTkRadioButton(
            radio_frame,
            text="Single Laser",
            variable=self.sim_type_var,
            value="single laser",
            command=self.on_sim_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        radio_single.pack(side="left")
        
        # ========== SECCIÓN 2: LONGITUD DE ONDA ==========
        wavelength_card = self.create_section_card(scroll_frame, "📏  Parámetros de Longitud de Onda")
        
        self.wavelength_entry = self.create_input_field(
            wavelength_card,
            "Longitud de onda fuente (m)",
            self.defaults.get('laser_wavelength', '1.545e-6'),
            "Para Scatter: centro del rango | Para Single: longitud única"
        )
        
        self.wavelength_window_entry, self.wavelength_window_frame = self.create_input_field(
            wavelength_card,
            "Ventana de longitud de onda (m)",
            self.defaults.get('wavelength_window', '20e-9'),
            "Rango total de longitudes de onda a simular",
            return_frame=True
        )
        
        # ========== SECCIÓN 3: HEATER ==========
        heater_card = self.create_section_card(scroll_frame, "⚡  Configuración del Heater")
        
        heater_radio_frame = ctk.CTkFrame(heater_card, fg_color="transparent")
        heater_radio_frame.pack(fill="x", padx=30, pady=(10, 15))
        
        radio_constant = ctk.CTkRadioButton(
            heater_radio_frame,
            text="Voltaje constante",
            variable=self.heater_sim_type_var,
            value="constant voltage",
            command=self.on_heater_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        radio_constant.pack(side="left", padx=(0, 30))
        
        radio_sweep = ctk.CTkRadioButton(
            heater_radio_frame,
            text="Barrido de voltaje (sweep)",
            variable=self.heater_sim_type_var,
            value="sweep",
            command=self.on_heater_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        radio_sweep.pack(side="left")
        
        # Voltaje constante
        self.constant_v_entry, self.constant_voltage_frame = self.create_input_field(
            heater_card,
            "Voltaje constante (V)",
            self.defaults.get('constant_v', '10.0'),
            "Voltaje fijo aplicado al heater",
            return_frame=True
        )
        
        # Barrido de voltaje
        self.sweep_container = ctk.CTkFrame(heater_card, fg_color="transparent")
        self.sweep_container.pack(fill="x", pady=(5, 0))
        
        self.min_voltage_entry = self.create_input_field(
            self.sweep_container,
            "Voltaje mínimo (V)",
            self.defaults.get('min_v', '0.0'),
            "Voltaje mínimo del barrido"
        )
        
        self.max_voltage_entry = self.create_input_field(
            self.sweep_container,
            "Voltaje máximo (V)",
            self.defaults.get('max_v', '20.0'),
            "Voltaje máximo del barrido"
        )
        
        self.voltage_interval_entry = self.create_input_field(
            self.sweep_container,
            "Intervalo de voltaje (V)",
            self.defaults.get('interval_v', '0.2'),
            "Paso entre valores de voltaje"
        )
        
        # ========== SECCIÓN 4: PARÁMETROS TEMPORALES ==========
        time_card = self.create_section_card(scroll_frame, "⏱️  Parámetros Temporales")
        
        self.time_window_entry = self.create_input_field(
            time_card,
            "Ventana de tiempo (s)",
            '5.12e-9',
            "Duración temporal de la simulación"
        )
        
        self.n_samples_entry = self.create_input_field(
            time_card,
            "Número de muestras",
            '15360',
            "Cantidad de puntos a muestrear"
        )
        
        # ========== BOTONES ==========
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(30, 20), padx=30)
        
        run_button = ctk.CTkButton(
            button_frame,
            text="▶  Ejecutar Simulación",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            command=self.submit_form,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            corner_radius=8
        )
        run_button.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            font=ctk.CTkFont(size=16),
            height=50,
            command=self.on_cancel,
            fg_color=CARD_BG,
            hover_color="#333333",
            border_width=2,
            border_color=INPUT_BORDER,
            corner_radius=8
        )
        cancel_button.pack(side="left", expand=True, fill="x")
        
        # Inicializar visibilidad
        self.on_sim_type_changed()
        self.on_heater_type_changed()
    
    def create_section_card(self, parent, title):
        """Crear tarjeta de sección"""
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        card.pack(fill="x", pady=(0, 15), padx=20)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(fill="x", padx=25, pady=(20, 10))
        
        # Línea divisora
        divider = ctk.CTkFrame(card, height=2, fg_color=INPUT_BORDER)
        divider.pack(fill="x", padx=25, pady=(0, 15))
        
        return card
    
    def create_input_field(self, parent, label_text, default_value, help_text, return_frame=False):
        """Crear campo de entrada con mejor estilo visual"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", padx=30, pady=10)
        
        # Label
        label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        label.pack(anchor="w", pady=(0, 8))
        
        # Entry con mejor estilo visual
        entry = ctk.CTkEntry(
            field_frame,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            border_width=2,
            corner_radius=6,
            text_color=TEXT_PRIMARY,
            placeholder_text=str(default_value),
            placeholder_text_color=TEXT_DISABLED
        )
        entry.pack(fill="x", pady=(0, 8))
        entry.insert(0, str(default_value))
        
        # Texto de ayuda
        help_label = ctk.CTkLabel(
            field_frame,
            text=f"ℹ️  {help_text}",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        help_label.pack(anchor="w")
        
        if return_frame:
            return entry, field_frame
        return entry
    
    def on_sim_type_changed(self):
        """Callback cuando cambia tipo de simulación"""
        if self.sim_type_var.get() == "scatter":
            self.wavelength_window_frame.pack(fill="x", padx=30, pady=10)
        else:
            self.wavelength_window_frame.pack_forget()
    
    def on_heater_type_changed(self):
        """Callback cuando cambia tipo de heater"""
        if self.heater_sim_type_var.get() == "constant voltage":
            self.constant_voltage_frame.pack(fill="x", padx=30, pady=10)
            self.sweep_container.pack_forget()
        else:
            self.sweep_container.pack(fill="x", pady=(5, 0))
            self.constant_voltage_frame.pack_forget()
    
    def validate_and_get_params(self):
        """Validar campos y retornar parámetros"""
        try:
            sim_type = self.sim_type_var.get()
            heater_sim_type = self.heater_sim_type_var.get()
            
            # Validar longitud de onda
            wavelength = float(self.wavelength_entry.get())
            if wavelength <= 0:
                return None, "La longitud de onda debe ser positiva"
            
            # Parámetros básicos
            params = {
                'sim_type': sim_type,
                'source_wavelength': wavelength,
                'heater_sim_type': heater_sim_type,
                'time_window': float(self.time_window_entry.get()),
                'n_samples': int(self.n_samples_entry.get())
            }
            
            # Validar parámetros temporales
            if params['time_window'] <= 0:
                return None, "La ventana de tiempo debe ser positiva"
            if params['n_samples'] <= 0:
                return None, "El número de muestras debe ser positivo"
            
            # Parámetros según tipo de simulación
            if sim_type == "scatter":
                wavelength_window = float(self.wavelength_window_entry.get())
                if wavelength_window <= 0:
                    return None, "La ventana de longitud de onda debe ser positiva"
                params['wavelength_window'] = wavelength_window
                half_window = wavelength_window / 2
                params['start_wavelength'] = wavelength - half_window
                params['end_wavelength'] = wavelength + half_window
            else:
                params['start_wavelength'] = wavelength
                params['end_wavelength'] = wavelength
            
            # Parámetros de voltaje
            if heater_sim_type == "constant voltage":
                constant_v = float(self.constant_v_entry.get())
                if constant_v < 0:
                    return None, "El voltaje constante no puede ser negativo"
                params['constant_v'] = constant_v
                params['min_v'] = constant_v
                params['max_v'] = constant_v
                params['interval_v'] = 1
            else:
                min_v = float(self.min_voltage_entry.get())
                max_v = float(self.max_voltage_entry.get())
                interval_v = float(self.voltage_interval_entry.get())
                
                if min_v >= max_v:
                    return None, "El voltaje mínimo debe ser menor que el máximo"
                if interval_v <= 0:
                    return None, "El intervalo de voltaje debe ser positivo"
                
                params['min_v'] = min_v
                params['max_v'] = max_v
                params['interval_v'] = interval_v
            
            return params, None
            
        except ValueError as e:
            return None, f"Valor inválido: {str(e)}"
        except Exception as e:
            return None, f"Error al validar: {str(e)}"
    
    def submit_form(self):
        """Validar y enviar formulario"""
        params, error = self.validate_and_get_params()
        
        if error:
            # Mostrar error
            from tkinter import messagebox
            messagebox.showerror("Error de Validación", error)
        else:
            # Llamar callback con parámetros validados
            self.on_submit(params)