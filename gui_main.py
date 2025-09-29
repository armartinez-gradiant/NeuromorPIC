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
        self.root.geometry("1000x750")
        
        # Color de fondo personalizado
        self.root.configure(fg_color=DARK_BG)
        
        # Inicializar API
        self.api = API()
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
            corner_radius=10,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            command=self.start_configuration
        )
        start_button.pack(pady=20)
        
        # ========== FOOTER ==========
        footer_frame = ctk.CTkFrame(self.root, fg_color=CARD_BG, height=50, corner_radius=0)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        footer_text = ctk.CTkLabel(
            footer_frame,
            text="© 2025 Lumerical Simulation Platform  |  Powered by Python & CustomTkinter",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY
        )
        footer_text.pack(pady=15)
    
    def update_info_display(self):
        """Actualizar la visualización de información"""
        # Limpiar grid actual
        for widget in self.info_grid.winfo_children():
            widget.destroy()
        
        if self.last_config is None:
            # Mostrar mensaje de "sin configuración"
            no_config_label = ctk.CTkLabel(
                self.info_grid,
                text="Haz clic en 'Iniciar Nueva Simulación' para configurar parámetros",
                font=ctk.CTkFont(size=13),
                text_color=TEXT_SECONDARY
            )
            no_config_label.pack(pady=20)
        else:
            # Mostrar configuración actual
            config = self.last_config
            
            # Fila 1
            self.create_info_item(
                self.info_grid,
                "Tipo de simulación",
                self.format_sim_type(config.get('sim_type', 'N/A')),
                0, 0
            )
            
            self.create_info_item(
                self.info_grid,
                "Modo del heater",
                self.format_heater_type(config.get('heater_sim_type', 'N/A')),
                0, 1
            )
            
            # Fila 2
            if config.get('sim_type') == 'scatter':
                wavelength_text = f"{config.get('start_wavelength', 0)*1e9:.2f} - {config.get('end_wavelength', 0)*1e9:.2f} nm"
            else:
                wavelength_text = f"{config.get('source_wavelength', 0)*1e9:.2f} nm"
            
            self.create_info_item(
                self.info_grid,
                "Longitud de onda",
                wavelength_text,
                1, 0
            )
            
            if config.get('heater_sim_type') == 'sweep':
                voltage_text = f"{config.get('min_v', 0):.1f} - {config.get('max_v', 0):.1f} V"
            else:
                voltage_text = f"{config.get('constant_v', 0):.1f} V"
            
            self.create_info_item(
                self.info_grid,
                "Voltaje",
                voltage_text,
                1, 1
            )
            
            # Fila 3
            self.create_info_item(
                self.info_grid,
                "Ventana temporal",
                f"{config.get('time_window', 0)*1e9:.2f} ns",
                2, 0
            )
            
            self.create_info_item(
                self.info_grid,
                "Muestras",
                str(config.get('n_samples', 0)),
                2, 1
            )
    
    def format_sim_type(self, sim_type):
        """Formatear tipo de simulación para mostrar"""
        if sim_type == "scatter":
            return "Scatter"
        elif sim_type == "single laser":
            return "Single Laser"
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
        print("\n" + "="*50)
        
        # Guardar última configuración
        self.last_config = params
        
        # Actualizar subtítulo
        self.info_subtitle.configure(
            text=f"Última configuración: {self.format_sim_type(params.get('sim_type', ''))} | "
                 f"{self.format_heater_type(params.get('heater_sim_type', ''))}"
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