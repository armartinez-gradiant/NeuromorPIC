"""
GUI Principal para Silicon Photonic Neuromorphic Chip Simulation
Interfaz gráfica moderna usando CustomTkinter
"""

import customtkinter as ctk
from API.main import API
from GUI.config_window import ConfigurationWindow
import sys

# Configuración del tema y apariencia
ctk.set_appearance_mode("dark")  # Opciones: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"


class LumericalGUI:
    """Clase principal de la interfaz gráfica"""
    
    def __init__(self):
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("Lumerical Simulation - Photonic Neuromorphic Chip")
        self.root.geometry("900x700")
        
        # Inicializar API
        self.api = API()
        self.api.load_cache()
        self.defaults = self.api.get_param_suggestions()
        
        # Configurar la interfaz
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar todos los elementos de la interfaz"""
        
        # ========== TÍTULO ==========
        title_label = ctk.CTkLabel(
            self.root,
            text="🔬 Lumerical Simulation Platform",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # ========== MARCO PRINCIPAL ==========
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Texto de bienvenida
        welcome_text = ctk.CTkTextbox(
            main_frame,
            height=100,
            font=ctk.CTkFont(size=13)
        )
        welcome_text.pack(fill="x", padx=20, pady=20)
        welcome_text.insert("1.0", 
            "Bienvenido a la plataforma de simulación de chips neuromórficos fotónicos.\n\n"
            "Esta interfaz te permitirá configurar y ejecutar simulaciones de Lumerical "
            "de manera visual e intuitiva."
        )
        welcome_text.configure(state="disabled")  # Solo lectura
        
        # ========== BOTÓN DE INICIO ==========
        start_button = ctk.CTkButton(
            main_frame,
            text="▶ Iniciar Configuración",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            command=self.start_configuration
        )
        start_button.pack(pady=30)
        
        # ========== INFORMACIÓN DEL SISTEMA ==========
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="ℹ️ Información del Sistema",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.pack(pady=10)
        
        # Mostrar valores por defecto cargados
        defaults_text = f"Valores predeterminados cargados:\n"
        defaults_text += f"• Longitud de onda: {self.defaults.get('source_wavelength', 'N/A')}\n"
        defaults_text += f"• Voltaje mín: {self.defaults.get('min_v', 'N/A')}\n"
        defaults_text += f"• Voltaje máx: {self.defaults.get('max_v', 'N/A')}"
        
        defaults_label = ctk.CTkLabel(
            info_frame,
            text=defaults_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        defaults_label.pack(pady=5)
        
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
        
        # Aquí más adelante ejecutaremos la simulación
        # Por ahora solo mostramos los parámetros
        
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