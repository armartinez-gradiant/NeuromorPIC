"""
GUI Principal para Silicon Photonic Neuromorphic Chip Simulation
Interfaz gráfica moderna usando CustomTkinter
"""

import customtkinter as ctk
from API.main import API
from GUI.config_window import ConfigurationWindow
import sys

# ========== CONFIGURACIÓN DE TEMA PERSONALIZADO ==========
# Color rojo corporativo personalizado
THEME_COLOR = "#E31E24"  # Rojo intenso
THEME_COLOR_HOVER = "#B01419"  # Rojo más oscuro para hover
DARK_BG = "#1a1a1a"  # Fondo oscuro principal
CARD_BG = "#2b2b2b"  # Fondo de tarjetas
TEXT_PRIMARY = "#ffffff"  # Texto principal
TEXT_SECONDARY = "#b0b0b0"  # Texto secundario

# Configuración del tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # Base theme


class LumericalGUI:
    """Clase principal de la interfaz gráfica"""
    
    def __init__(self):
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("Lumerical Simulation Platform")
        self.root.geometry("1000x800")
        
        # Color de fondo personalizado
        self.root.configure(fg_color=DARK_BG)
        
        # Inicializar API
        self.api = API()
        
        # Platform por defecto
        self.selected_platform = "sipho"
        self.api.set_platform(self.selected_platform)
        self.api.load_cache()
        self.defaults = self.api.get_param_suggestions()
        
        # Variable para almacenar última configuración
        self.last_config = None
        
        # Configurar la interfaz
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar todos los elementos de la interfaz"""
        
        # ========== BARRA SUPERIOR CON LOGO ==========
        header_frame = ctk.CTkFrame(self.root, fg_color=THEME_COLOR, height=80, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo/Icono (emoji como placeholder)
        logo_label = ctk.CTkLabel(
            header_frame,
            text="🔬",
            font=ctk.CTkFont(size=40),
            text_color=TEXT_PRIMARY
        )
        logo_label.pack(side="left", padx=30, pady=10)
        
        # Título en header
        title_label = ctk.CTkLabel(
            header_frame,
            text="Lumerical Simulation Platform",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Silicon Photonic Neuromorphic Chip",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY
        )
        subtitle_label.pack(side="left", padx=10, pady=10)
        
        # ========== CONTENIDO PRINCIPAL ==========
        content_frame = ctk.CTkFrame(self.root, fg_color=DARK_BG)
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # ========== CARD DE BIENVENIDA ==========
        welcome_card = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15)
        welcome_card.pack(fill="x", pady=(0, 20))
        
        welcome_title = ctk.CTkLabel(
            welcome_card,
            text="Bienvenido",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        welcome_title.pack(fill="x", padx=30, pady=(25, 10))
        
        welcome_text = ctk.CTkLabel(
            welcome_card,
            text="Esta plataforma permite configurar y ejecutar simulaciones avanzadas\n"
                 "de chips neuromórficos fotónicos usando Lumerical INTERCONNECT.",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY,
            anchor="w",
            justify="left"
        )
        welcome_text.pack(fill="x", padx=30, pady=(0, 25))
        
        # ========== CARD DE SELECCIÓN DE PLATAFORMA ==========
        platform_card = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15)
        platform_card.pack(fill="x", pady=(0, 20))
        
        platform_title = ctk.CTkLabel(
            platform_card,
            text="🔧 Seleccionar Plataforma",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        platform_title.pack(fill="x", padx=30, pady=(20, 10))
        
        platform_subtitle = ctk.CTkLabel(
            platform_card,
            text="Selecciona la tecnología fotónica para las simulaciones",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        platform_subtitle.pack(fill="x", padx=30, pady=(0, 15))
        
        # Container para los botones de plataforma
        platform_buttons_frame = ctk.CTkFrame(platform_card, fg_color="transparent")
        platform_buttons_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Crear variable para el selector
        self.platform_var = ctk.StringVar(value="sipho")
        
        # Radio buttons para plataformas
        sipho_radio = ctk.CTkRadioButton(
            platform_buttons_frame,
            text="Silicon Photonics (SiPho)",
            variable=self.platform_var,
            value="sipho",
            command=self.on_platform_changed,
            font=ctk.CTkFont(size=14),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        sipho_radio.pack(side="left", padx=(0, 30))
        
        sin_radio = ctk.CTkRadioButton(
            platform_buttons_frame,
            text="Silicon Nitride (SiN)",
            variable=self.platform_var,
            value="sin",
            command=self.on_platform_changed,
            font=ctk.CTkFont(size=14),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        sin_radio.pack(side="left")
        
        # Label para mostrar la plataforma actual
        self.platform_status_label = ctk.CTkLabel(
            platform_card,
            text=f"✓ Plataforma actual: Silicon Photonics (SiPho)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLOR,
            anchor="w"
        )
        self.platform_status_label.pack(fill="x", padx=30, pady=(0, 20))
        
        # ========== CARD DE ÚLTIMA CONFIGURACIÓN ==========
        info_card = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=15)
        info_card.pack(fill="x", pady=(0, 25))
        
        self.info_title = ctk.CTkLabel(
            info_card,
            text="📊 Parámetros de la Última Simulación",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        self.info_title.pack(fill="x", padx=30, pady=(20, 5))
        
        self.info_subtitle = ctk.CTkLabel(
            info_card,
            text="Aún no se ha configurado ninguna simulación",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.info_subtitle.pack(fill="x", padx=30, pady=(0, 15))
        
        # Grid para información - guardar referencia
        self.info_grid = ctk.CTkFrame(info_card, fg_color=CARD_BG)
        self.info_grid.pack(fill="x", padx=30, pady=(0, 20))
        
        # Crear items iniciales con valores por defecto
        self.info_items = {}
        self.update_info_display()
        
        # ========== BOTÓN PRINCIPAL ==========
        button_frame = ctk.CTkFrame(content_frame, fg_color=DARK_BG)
        button_frame.pack(expand=True)
        
        start_button = ctk.CTkButton(
            button_frame,
            text="▶  Iniciar Nueva Simulación",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            width=350,
            command=self.start_configuration,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        start_button.pack(pady=20)
    
    def on_platform_changed(self):
        """Callback cuando cambia la plataforma seleccionada"""
        new_platform = self.platform_var.get()
        print(f"\n🔄 Cambiando plataforma a: {new_platform.upper()}")
        
        # Actualizar API con nueva plataforma
        self.selected_platform = new_platform
        self.api.set_platform(new_platform)
        
        # Recargar cache de la nueva plataforma
        self.api.load_cache()
        self.defaults = self.api.get_param_suggestions()
        
        # Actualizar label de estado
        platform_names = {
            "sipho": "Silicon Photonics (SiPho)",
            "sin": "Silicon Nitride (SiN)"
        }
        self.platform_status_label.configure(
            text=f"✓ Plataforma actual: {platform_names[new_platform]}"
        )
        
        print(f"✓ Plataforma cambiada exitosamente a {new_platform.upper()}\n")
    
    def update_info_display(self):
        """Actualizar la visualización de información de la última simulación"""
        # Limpiar grid anterior
        for widget in self.info_grid.winfo_children():
            widget.destroy()
        
        if self.last_config is None:
            # Mostrar mensaje de que no hay configuración
            no_config_label = ctk.CTkLabel(
                self.info_grid,
                text="Ninguna simulación ejecutada aún",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_SECONDARY
            )
            no_config_label.pack(pady=20)
            return
        
        # Preparar datos para mostrar
        params = self.last_config
        
        # Formatear wavelength
        wavelength_nm = float(params.get('source_wavelength', 0)) * 1e9
        
        # Determinar voltaje a mostrar
        if params.get('heater_sim_type') == 'constant voltage':
            voltage_display = f"{params.get('constant_v', 'N/A')} V (constante)"
        else:
            voltage_display = f"{params.get('min_v', 'N/A')}-{params.get('max_v', 'N/A')} V"
        
        # Datos a mostrar en grid 2x3
        display_data = [
            ("Tipo de Simulación", self.format_sim_type(params.get('sim_type', ''))),
            ("Longitud de Onda", f"{wavelength_nm:.2f} nm"),
            ("Modo Heater", self.format_heater_type(params.get('heater_sim_type', ''))),
            ("Voltaje", voltage_display),
            ("Ventana Temporal", params.get('time_window', 'N/A')),
            ("Muestras", params.get('n_samples', 'N/A'))
        ]
        
        # Crear grid
        for i, (label, value) in enumerate(display_data):
            row = i // 2
            col = i % 2
            self.create_info_item(self.info_grid, label, value, row, col)
    
    def format_sim_type(self, sim_type):
        """Formatear tipo de simulación para mostrar"""
        if sim_type == "single laser":
            return "Láser Único"
        elif sim_type == "wavelength sweep":
            return "Barrido de Longitud de Onda"
        return sim_type
    
    def format_heater_type(self, heater_type):
        """Formatear tipo de heater para mostrar"""
        if heater_type == "constant voltage":
            return "Voltaje Constante"
        elif heater_type == "sweep":
            return "Barrido (Sweep)"
        return heater_type
    
    def create_info_item(self, parent, label, value, row, column):
        """Crear un item de información en grid"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.grid(row=row, column=column, padx=20, pady=12, sticky="w")
        
        label_widget = ctk.CTkLabel(
            item_frame,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        label_widget.pack(anchor="w")
        
        value_widget = ctk.CTkLabel(
            item_frame,
            text=value,
            font=ctk.CTkFont(size=16),
            text_color=THEME_COLOR,
            anchor="w"
        )
        value_widget.pack(anchor="w", pady=(3, 0))
        
    def start_configuration(self):
        """Iniciar la ventana de configuración"""
        print("🚀 Iniciando configuración...")
        print(f"Plataforma seleccionada: {self.selected_platform.upper()}")
        
        # Crear y mostrar la ventana de configuración
        ConfigurationWindow(
            parent=self.root,
            defaults=self.defaults,
            callback=self.on_configuration_complete
        )
    
    def on_configuration_complete(self, params):
        """
        Callback que se ejecuta cuando se completa la configuración
        
        Args:
            params: Diccionario con los parámetros configurados
        """
        print("\n" + "="*50)
        print("🎉 Configuración completada!")
        print("="*50)
        print("\nParámetros recibidos:")
        for key, value in params.items():
            print(f"  • {key}: {value}")
        
        # IMPORTANTE: Añadir la plataforma a los parámetros
        params['platform'] = self.selected_platform
        print(f"  • platform: {self.selected_platform}")
        print("\n" + "="*50)
        
        # Guardar última configuración
        self.last_config = params
        
        # Actualizar subtítulo
        self.info_subtitle.configure(
            text=f"Última configuración: {self.format_sim_type(params.get('sim_type', ''))} | "
                 f"{self.format_heater_type(params.get('heater_sim_type', ''))} | "
                 f"Plataforma: {self.selected_platform.upper()}"
        )
        
        # Actualizar visualización de información
        self.update_info_display()
        
        # NUEVO: Ejecutar simulación
        from GUI.simulation_window import SimulationWindow
        SimulationWindow(
            parent=self.root,
            api=self.api,
            params=params,
            callback=self.on_simulation_complete
        )
    
    def on_simulation_complete(self, success, params=None, error=None):
        """
        Callback cuando termina la simulación
        
        Args:
            success: Si la simulación fue exitosa
            params: Parámetros usados
            error: Mensaje de error si hubo fallo
        """
        if success:
            print("\n✓ Simulación completada exitosamente")
            # Aquí más adelante mostraremos resultados
        else:
            print(f"\n✗ Simulación falló: {error}")
        
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()


def main():
    """Punto de entrada principal"""
    print("=" * 50)
    print("Iniciando GUI de Lumerical Simulation")
    print("=" * 50)
    
    app = LumericalGUI()
    app.run()


if __name__ == '__main__':
    main()