"""
GUI Principal para Silicon Photonic Neuromorphic Chip Simulation
Interfaz gráfica moderna con Sidebar usando CustomTkinter

ARCHIVO: gui_main.py
PARTE 1 DE 2
"""

import customtkinter as ctk
from API.main import API
from PIL import Image
import os
import sys
import warnings
import atexit
import numpy as np
from scipy.stats import unitary_group

# Suprimir warnings de threading de tkinter
warnings.filterwarnings('ignore', category=RuntimeWarning)

# Redirigir stderr para suprimir errores específicos de Image
class SuppressImageErrors:
    def __init__(self):
        self.stderr = sys.stderr
        self.suppress_patterns = [
            'Image.__del__',
            'Tcl_AsyncDelete',
            'main thread is not in main loop',
            'async handler deleted by the wrong thread',
            'RuntimeError: main thread is not in main loop'
        ]
        
    def write(self, msg):
        if not any(pattern in msg for pattern in self.suppress_patterns):
            self.stderr.write(msg)
    
    def flush(self):
        self.stderr.flush()

sys.stderr = SuppressImageErrors()

# Registrar limpieza al salir
def cleanup_on_exit():
    """Limpieza final al salir del programa"""
    try:
        import gc
        gc.collect()
    except:
        pass

atexit.register(cleanup_on_exit)

# ========== CONFIGURACIÓN DE TEMA PERSONALIZADO ==========
THEME_COLOR = "#E31E24"  # Rojo Gradiant
THEME_COLOR_HOVER = "#C01018"
HEADER_BG = "#f8f8f8"
HEADER_TEXT = "#2d2d2d"
DARK_BG = "#1a1a1a"
SIDEBAR_BG = "#2d2d2d"
CARD_BG = "#252525"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#999999"
TEXT_DISABLED = "#555555"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LumericalGUI:
    """Clase principal de la interfaz gráfica"""
    
    def __init__(self):
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("Lumerical Simulation Platform - Gradiant")
        self.root.geometry("1200x800")
        self.root.state('zoomed')
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
        
        # Sección actual
        self.current_section = "home"
        
        # Variables para el formulario de configuración
        self.config_widgets = {}
        
        # Variables para MZI Mesh
        self.mesh_dimension_var = None
        self.matrix_type_var = None
        self.vector_type_var = None
        self.visualize_mesh_var = None
        self.show_interconnect_var = None
        self.normalize_vector_var = None
        
        # Cargar logo
        self.load_logo()
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Configurar protocolo de cierre para limpiar recursos
        self.root.protocol("WM_DELETE_WINDOW", self.on_app_closing)

    def load_logo(self):
        """Cargar el logo de Gradiant con proporción correcta"""
        try:
            logo_path = os.path.join("GUI", "assets", "images", "gradiant_logo.png")
            logo_image = Image.open(logo_path)
            
            original_width, original_height = logo_image.size
            target_height = 40
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)
            
            self.logo = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(target_width, target_height)
            )
            
            self._logo_pil_reference = logo_image
            
            print(f"✓ Logo cargado desde: {logo_path}")
        except Exception as e:
            print(f"⚠ No se pudo cargar el logo: {e}")
            self.logo = None
            self._logo_pil_reference = None

    def on_app_closing(self):
        """Manejar el cierre de la aplicación"""
        try:
            print("\n🧹 Limpiando recursos...")
            
            # Limpiar simulador activo
            if hasattr(self, 'api') and hasattr(self.api, '_active_simulator'):
                if self.api._active_simulator is not None:
                    try:
                        self.api._active_simulator.close()
                        print("   ✓ INTERCONNECT cerrado")
                    except:
                        pass
                    self.api._active_simulator = None
            
            # Limpiar imágenes
            if hasattr(self, 'logo'):
                self.logo = None
            if hasattr(self, '_logo_pil_reference'):
                self._logo_pil_reference = None
            
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"⚠ Error durante limpieza: {e}")
        finally:
            print("🔚 Cerrando aplicación...")
            try:
                self.root.quit()
                import time
                time.sleep(0.05)
                self.root.destroy()
            except:
                pass
        
    def setup_ui(self):
        """Configurar todos los elementos de la interfaz"""
        
        # ========== BARRA SUPERIOR CON LOGO ==========
        header_frame = ctk.CTkFrame(self.root, fg_color=HEADER_BG, height=80, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        if self.logo:
            logo_label = ctk.CTkLabel(header_frame, image=self.logo, text="")
            logo_label.pack(side="left", padx=30, pady=15)
        
        separator = ctk.CTkFrame(header_frame, fg_color=HEADER_TEXT, width=2)
        separator.pack(side="left", fill="y", padx=(0, 20), pady=15)
        
        titles_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        titles_frame.pack(side="left", fill="y", pady=15)
        
        title_label = ctk.CTkLabel(
            titles_frame,
            text="Lumerical Simulation Platform",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=HEADER_TEXT,
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            titles_frame,
            text="Silicon Photonic Neuromorphic Chip",
            font=ctk.CTkFont(size=13),
            text_color=HEADER_TEXT,
            anchor="w"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # ========== CONTENEDOR PRINCIPAL ==========
        main_container = ctk.CTkFrame(self.root, fg_color=DARK_BG)
        main_container.pack(fill="both", expand=True)
        
        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(main_container, fg_color=SIDEBAR_BG, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        sidebar_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=15, pady=20)
        
        sidebar_title = ctk.CTkLabel(
            sidebar_content,
            text="NAVIGATION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        sidebar_title.pack(fill="x", pady=(0, 15))
        
        # Botones de navegación
        self.nav_buttons = {}
        self.nav_buttons['home'] = self.create_nav_button(sidebar_content, "🏠  Home", "home", enabled=True)
        self.nav_buttons['simulate'] = self.create_nav_button(sidebar_content, "🔬  Simulate", "simulate", enabled=True)
        self.nav_buttons['mzi_mesh'] = self.create_nav_button(sidebar_content, "🔷  MZI Mesh", "mzi_mesh", enabled=True)
        self.nav_buttons['results'] = self.create_nav_button(sidebar_content, "📊  Results", "results", enabled=False)
        self.nav_buttons['history'] = self.create_nav_button(sidebar_content, "📝  History", "history", enabled=False)
        self.nav_buttons['settings'] = self.create_nav_button(sidebar_content, "⚙️  Settings", "settings", enabled=False)
        
        separator = ctk.CTkFrame(sidebar_content, fg_color=TEXT_DISABLED, height=1)
        separator.pack(fill="x", pady=20)
        
        # Selector de plataforma
        platform_label = ctk.CTkLabel(
            sidebar_content,
            text="PLATFORM",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        platform_label.pack(fill="x", pady=(0, 10))
        
        self.platform_var = ctk.StringVar(value="sipho")
        platform_menu = ctk.CTkOptionMenu(
            sidebar_content,
            variable=self.platform_var,
            values=["sipho", "sin"],
            command=lambda x: self.on_platform_changed(),
            fg_color=CARD_BG,
            button_color=THEME_COLOR,
            button_hover_color=THEME_COLOR_HOVER,
            dropdown_fg_color=CARD_BG
        )
        platform_menu.pack(fill="x", pady=(0, 15))
        
        # Info de cache
        cache_info_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        cache_info_frame.pack(fill="x", pady=(10, 0))
        
        cache_title = ctk.CTkLabel(
            cache_info_frame,
            text="CACHE INFO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        cache_title.pack(fill="x", pady=(0, 10))
        
        self.cache_sipho_label = ctk.CTkLabel(
            cache_info_frame,
            text="SiPho: 0 sims",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        self.cache_sipho_label.pack(fill="x", pady=2)
        
        self.cache_sin_label = ctk.CTkLabel(
            cache_info_frame,
            text="SiN: 0 sims",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.cache_sin_label.pack(fill="x", pady=2)
        
        self.update_cache_info()
        
        # ========== ÁREA DE CONTENIDO ==========
        self.content_frame = ctk.CTkFrame(main_container, fg_color=DARK_BG, corner_radius=0)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=25, pady=25)
        
        self.show_home()
    
    def create_nav_button(self, parent, text, section, enabled=True):
        """Crear un botón de navegación"""
        state = "normal" if enabled else "disabled"
        text_color = TEXT_PRIMARY if enabled else TEXT_DISABLED
        
        if enabled:
            btn = ctk.CTkButton(
                parent,
                text=text,
                command=lambda: self.navigate_to(section),
                fg_color="transparent",
                hover_color=CARD_BG,
                text_color=text_color,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=14),
                state=state
            )
        else:
            btn = ctk.CTkButton(
                parent,
                text=text,
                command=None,
                fg_color="transparent",
                hover_color=SIDEBAR_BG,  # ← CAMBIO AQUÍ
                text_color=text_color,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=14),
                state=state
            )
        
        btn.pack(fill="x", pady=2)
        return btn
    
    def navigate_to(self, section):
        """Navegar a una sección"""
        self.current_section = section
        
        for key, btn in self.nav_buttons.items():
            if key == section:
                btn.configure(fg_color=THEME_COLOR, text_color=TEXT_PRIMARY)
            else:
                if btn.cget("state") != "disabled":
                    btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY)
        
        if section == "home":
            self.show_home()
        elif section == "simulate":
            self.show_simulate()
        elif section == "mzi_mesh":
            self.show_mzi_mesh()   
        elif section == "results":
            self.show_results()
        elif section == "history":
            self.show_history()
        elif section == "settings":
            self.show_settings()
    
    def clear_content(self):
        """Limpiar el contenido actual"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def create_section_card(self, parent, title):
        """Crear una tarjeta de sección con título"""
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        card.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(fill="x", padx=20, pady=(15, 10))
        
        return card
    
    def format_sim_type(self, sim_type):
        """Formatear tipo de simulación"""
        types = {
            "single laser": "Single Laser",
            "scatter": "Multi-Wavelength Scatter"
        }
        return types.get(sim_type, sim_type)
    
    def format_heater_type(self, heater_type):
        """Formatear tipo de heater"""
        types = {
            "constant voltage": "Constant Voltage",
            "sweep": "Voltage Sweep"
        }
        return types.get(heater_type, heater_type)
    
    def on_platform_changed(self):
        """Callback cuando cambia la plataforma"""
        new_platform = self.platform_var.get()
        print(f"\n🔄 Cambiando plataforma a: {new_platform.upper()}")
        
        self.selected_platform = new_platform
        self.api.set_platform(new_platform)
        self.api.load_cache()
        self.defaults = self.api.get_param_suggestions()
        
        self.update_cache_info()
        
        if self.current_section == "home" and hasattr(self, 'platform_display_label'):
            platform_names = {
                "sipho": "Silicon Photonics (SiPho)",
                "sin": "Silicon Nitride (SiN)"
            }
            self.platform_display_label.configure(text=f"✓ {platform_names[new_platform]}")
        
        print(f"✓ Plataforma cambiada a {new_platform.upper()}\n")
    
    def update_cache_info(self):
        """Actualizar información de cache"""
        current_platform = self.selected_platform
        current_count = self.api.get_total_simulations()
        
        other_platform = "sin" if current_platform == "sipho" else "sipho"
        self.api.set_platform(other_platform)
        self.api.load_cache()
        other_count = self.api.get_total_simulations()
        
        self.api.set_platform(current_platform)
        self.api.load_cache()
        
        if current_platform == "sipho":
            self.cache_sipho_label.configure(text=f"SiPho: {current_count} sims", text_color=TEXT_PRIMARY)
            self.cache_sin_label.configure(text=f"SiN: {other_count} sims", text_color=TEXT_SECONDARY)
        else:
            self.cache_sin_label.configure(text=f"SiN: {current_count} sims", text_color=TEXT_PRIMARY)
            self.cache_sipho_label.configure(text=f"SiPho: {other_count} sims", text_color=TEXT_SECONDARY)
    
    def show_home(self):
        """Mostrar pantalla de Home"""
        self.clear_content()
        
        # Card de bienvenida
        welcome_card = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=15)
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
        
        # Información de la plataforma actual
        platform_card = self.create_section_card(self.content_frame, "🔧 Configuración Actual")
        
        platform_names = {
            "sipho": "Silicon Photonics (SiPho)",
            "sin": "Silicon Nitride (SiN)"
        }
        
        self.platform_display_label = ctk.CTkLabel(
            platform_card,
            text=f"✓ {platform_names[self.selected_platform]}",
            font=ctk.CTkFont(size=15),
            text_color=THEME_COLOR,
            anchor="w"
        )
        self.platform_display_label.pack(fill="x", padx=30, pady=(5, 20))
        
        # Información de última simulación
        info_card = self.create_section_card(self.content_frame, "📊 Última Simulación")
        
        self.info_subtitle = ctk.CTkLabel(
            info_card,
            text="No se ha ejecutado ninguna simulación aún",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.info_subtitle.pack(fill="x", padx=30, pady=(0, 15))
        
        self.info_grid = ctk.CTkFrame(info_card, fg_color="transparent")
        self.info_grid.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        self.update_info_display()
        
        # Botones de acción rápida
        action_card = self.create_section_card(self.content_frame, "🚀 Acciones Rápidas")
        
        buttons_frame = ctk.CTkFrame(action_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=30, pady=(5, 20))
        
        simulate_btn = ctk.CTkButton(
            buttons_frame,
            text="🔬 Nueva Simulación",
            command=lambda: self.navigate_to("simulate"),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        simulate_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        mzi_btn = ctk.CTkButton(
            buttons_frame,
            text="🔷 MZI Mesh",
            command=lambda: self.navigate_to("mzi_mesh"),
            fg_color=CARD_BG,
            hover_color=SIDEBAR_BG,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            border_width=2,
            border_color=THEME_COLOR
        )
        mzi_btn.pack(side="left", expand=True, fill="x")
    
    def update_info_display(self):
        """Actualizar información de última simulación"""
        for widget in self.info_grid.winfo_children():
            widget.destroy()
        
        if self.last_config is None:
            no_config_label = ctk.CTkLabel(
                self.info_grid,
                text="Ninguna simulación ejecutada aún",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_SECONDARY
            )
            no_config_label.pack(pady=20)
            return
        
        params = self.last_config
        wavelength_nm = float(params.get('source_wavelength', 0)) * 1e9
        
        # Grid de parámetros
        info_items = [
            ("Tipo de Simulación:", self.format_sim_type(params.get('sim_type', 'N/A'))),
            ("Longitud de Onda:", f"{wavelength_nm:.2f} nm"),
            ("Tipo de Heater:", self.format_heater_type(params.get('heater_sim_type', 'N/A'))),
            ("Plataforma:", params.get('platform', 'N/A').upper())
        ]
        
        for i, (label, value) in enumerate(info_items):
            row_frame = ctk.CTkFrame(self.info_grid, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            label_widget = ctk.CTkLabel(
                row_frame,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=TEXT_SECONDARY,
                anchor="w",
                width=200
            )
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=13),
                text_color=TEXT_PRIMARY,
                anchor="w"
            )
            value_widget.pack(side="left", padx=(10, 0))
    
    def on_simulation_complete(self, success, error=None):
        """Callback cuando termina la simulación"""
        if success:
            print("\n✓ Simulación completada exitosamente")
            self.update_info_display()
            self.navigate_to("home")
            self.show_success_dialog("Éxito", "Simulación completada exitosamente")
        else:
            print(f"\n✗ Error en simulación: {error}")
            self.show_error_dialog("Error", f"Error durante la simulación:\n{error}")

    def show_simulate(self):
        """Mostrar pantalla de configuración de simulación"""
        self.clear_content()
        
        # Importar el componente de formulario
        from GUI.simulation_config_form import SimulationConfigForm
        
        # Crear y mostrar el formulario
        form = SimulationConfigForm(
            parent=self.content_frame,
            defaults=self.defaults,
            on_submit_callback=self.on_simulation_config_submit,
            on_cancel_callback=lambda: self.navigate_to("home")
        )
        form.pack(fill="both", expand=True)
    
    def on_simulation_config_submit(self, params):
        """Callback cuando se confirma la configuración del formulario"""
        try:
            # Agregar plataforma actual
            params['platform'] = self.selected_platform
            
            # Guardar configuración
            self.last_config = params
            
            # Log de confirmación
            print("\n" + "="*70)
            print("✓ CONFIGURACIÓN COMPLETADA")
            print("="*70)
            print("Parámetros:")
            for key, value in params.items():
                print(f"  • {key}: {value}")
            print("="*70 + "\n")
            
            # Abrir ventana de simulación
            from GUI.simulation_window import SimulationWindow
            SimulationWindow(
                parent=self.root,
                api=self.api,
                params=params,
                callback=self.on_simulation_complete
            )
            
        except Exception as e:
            self.show_error_dialog("Error", f"Error al procesar configuración:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def show_results(self):
        """Mostrar pantalla de Results (placeholder)"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="📊 Results\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def show_history(self):
        """Mostrar pantalla de History (placeholder)"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="📝 History\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def show_settings(self):
        """Mostrar pantalla de Settings (placeholder)"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="⚙️ Settings\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)


    def show_mzi_mesh(self):
        """Mostrar interfaz de MZI Mesh - Multiplicación Matricial Óptica"""
        self.clear_content()
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=DARK_BG,
            scrollbar_button_color=CARD_BG,
            scrollbar_button_hover_color=SIDEBAR_BG
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # Título principal
        title = ctk.CTkLabel(
            scroll_frame,
            text="🔷 MZI Mesh - Multiplicación Matricial Óptica",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title.pack(fill="x", pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            scroll_frame,
            text="Simula un mesh de Mach-Zehnder para realizar multiplicación matricial óptica (U @ v)",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        subtitle.pack(fill="x", pady=(0, 25))
        
        # ========== SECCIÓN 1: DIMENSIÓN ==========
        dimension_card = self.create_section_card(scroll_frame, "📐 Dimensión del Sistema")

        dim_frame = ctk.CTkFrame(dimension_card, fg_color="transparent")
        dim_frame.pack(fill="x", pady=(10, 20), padx=30)

        dim_label = ctk.CTkLabel(
            dim_frame,
            text="Dimensión de la matriz (N×N):",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY
        )
        dim_label.pack(side="left", padx=(0, 10))

        # Campo de entrada de texto para dimensión
        self.mesh_dimension_var = ctk.StringVar(value="4")
        dimension_entry = ctk.CTkEntry(
            dim_frame,
            textvariable=self.mesh_dimension_var,
            width=100,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        dimension_entry.pack(side="left")
        
        dim_info = ctk.CTkLabel(
            dim_frame,
            text="(Ingresa cualquier valor ≥ 2)",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY
        )
        dim_info.pack(side="left", padx=(10, 0))
        
        # ========== SECCIÓN 2: MATRIZ UNITARIA ==========
        matrix_card = self.create_section_card(scroll_frame, "🔢 Matriz Unitaria (U)")
        
        matrix_type_label = ctk.CTkLabel(
            matrix_card,
            text="Tipo de matriz:",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        matrix_type_label.pack(fill="x", pady=(10, 10), padx=30)
        
        # Radio buttons para tipo de matriz
        self.matrix_type_var = ctk.StringVar(value="random")
        
        matrix_options_frame = ctk.CTkFrame(matrix_card, fg_color="transparent")
        matrix_options_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        random_radio = ctk.CTkRadioButton(
            matrix_options_frame,
            text="Matriz Unitaria Aleatoria",
            variable=self.matrix_type_var,
            value="random",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            command=self.on_matrix_type_changed
        )
        random_radio.pack(anchor="w", pady=5)
        
        identity_radio = ctk.CTkRadioButton(
            matrix_options_frame,
            text="Matriz Identidad",
            variable=self.matrix_type_var,
            value="identity",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            command=self.on_matrix_type_changed
        )
        identity_radio.pack(anchor="w", pady=5)
        
        custom_radio = ctk.CTkRadioButton(
            matrix_options_frame,
            text="Matriz Personalizada",
            variable=self.matrix_type_var,
            value="custom",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            command=self.on_matrix_type_changed
        )
        custom_radio.pack(anchor="w", pady=5)
        
        # Frame para entrada de matriz personalizada (inicialmente oculto)
        self.matrix_input_frame = ctk.CTkFrame(matrix_card, fg_color=DARK_BG, corner_radius=8)
        
        matrix_input_label = ctk.CTkLabel(
            self.matrix_input_frame,
            text="Ingresa la matriz en formato NumPy (ejemplo: [[1,0],[0,1]]):",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        matrix_input_label.pack(fill="x", pady=(10, 5), padx=15)
        
        self.matrix_entry = ctk.CTkTextbox(
            self.matrix_input_frame,
            height=100,
            font=ctk.CTkFont(family="Courier", size=12),
            fg_color=CARD_BG
        )
        self.matrix_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # ========== SECCIÓN 3: VECTOR DE ENTRADA ==========
        vector_card = self.create_section_card(scroll_frame, "📊 Vector de Entrada (v)")
        
        vector_type_label = ctk.CTkLabel(
            vector_card,
            text="Tipo de vector:",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        vector_type_label.pack(fill="x", pady=(10, 10), padx=30)
        
        # Radio buttons para tipo de vector
        self.vector_type_var = ctk.StringVar(value="random")
        
        vector_options_frame = ctk.CTkFrame(vector_card, fg_color="transparent")
        vector_options_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        random_vector_radio = ctk.CTkRadioButton(
            vector_options_frame,
            text="Vector Aleatorio Normalizado",
            variable=self.vector_type_var,
            value="random",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            command=self.on_vector_type_changed
        )
        random_vector_radio.pack(anchor="w", pady=5)
        
        custom_vector_radio = ctk.CTkRadioButton(
            vector_options_frame,
            text="Vector Personalizado",
            variable=self.vector_type_var,
            value="custom",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            command=self.on_vector_type_changed
        )
        custom_vector_radio.pack(anchor="w", pady=5)
        
        # Frame para entrada de vector personalizado (inicialmente oculto)
        self.vector_input_frame = ctk.CTkFrame(vector_card, fg_color=DARK_BG, corner_radius=8)
        
        vector_input_label = ctk.CTkLabel(
            self.vector_input_frame,
            text="Ingresa el vector (ejemplo: 1, 2, 3, 4):",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        vector_input_label.pack(fill="x", pady=(10, 5), padx=15)
        
        self.vector_entry = ctk.CTkEntry(
            self.vector_input_frame,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=CARD_BG
        )
        self.vector_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Checkbox para normalizar
        self.normalize_vector_var = ctk.BooleanVar(value=True)
        normalize_checkbox = ctk.CTkCheckBox(
            self.vector_input_frame,
            text="Normalizar vector",
            variable=self.normalize_vector_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_PRIMARY,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        normalize_checkbox.pack(anchor="w", padx=15, pady=(0, 10))
        
        # ========== SECCIÓN 4: OPCIONES DE VISUALIZACIÓN ==========
        viz_card = self.create_section_card(scroll_frame, "👁️ Opciones de Visualización")
        
        viz_options_frame = ctk.CTkFrame(viz_card, fg_color="transparent")
        viz_options_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        self.visualize_mesh_var = ctk.CTkVariable(value=False)
        visualize_checkbox = ctk.CTkCheckBox(
            viz_options_frame,
            text="Mostrar diagrama del mesh (matplotlib)",
            variable=self.visualize_mesh_var,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        visualize_checkbox.pack(anchor="w", pady=5)
        
        self.show_interconnect_var = ctk.CTkVariable(value=False)
        show_ic_checkbox = ctk.CTkCheckBox(
            viz_options_frame,
            text="Mantener INTERCONNECT abierto después de la simulación",
            variable=self.show_interconnect_var,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        show_ic_checkbox.pack(anchor="w", pady=5)

        # ========== BOTONES ==========
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        run_button = ctk.CTkButton(
            button_frame,
            text="▶  Ejecutar Simulación MZI Mesh",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            command=self.run_mzi_mesh_simulation,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        run_button.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            font=ctk.CTkFont(size=16),
            height=50,
            command=lambda: self.navigate_to("home"),
            fg_color=CARD_BG,
            hover_color=SIDEBAR_BG,
            border_width=2,
            border_color=TEXT_DISABLED
        )
        cancel_button.pack(side="left", expand=True, fill="x")

    def on_matrix_type_changed(self):
        """Callback cuando cambia el tipo de matriz"""
        if self.matrix_type_var.get() == "custom":
            self.matrix_input_frame.pack(fill="x", pady=(0, 20), padx=30)
        else:
            self.matrix_input_frame.pack_forget()

    def on_vector_type_changed(self):
        """Callback cuando cambia el tipo de vector"""
        if self.vector_type_var.get() == "custom":
            self.vector_input_frame.pack(fill="x", pady=(0, 20), padx=30)
        else:
            self.vector_input_frame.pack_forget()

    def run_mzi_mesh_simulation(self):
        """Ejecutar la simulación de MZI Mesh"""
        try:
            # ✅ VALIDACIÓN: Obtener y validar dimensión
            dim_text = self.mesh_dimension_var.get().strip()
            
            try:
                dim = int(dim_text)
            except ValueError:
                self.show_error_dialog(
                    "Error de Dimensión", 
                    f"'{dim_text}' no es un número válido.\n\nPor favor ingresa un número entero."
                )
                return
            
            if dim < 2:
                self.show_error_dialog(
                    "Error de Dimensión",
                    f"La dimensión debe ser al menos 2.\n\nDimensión ingresada: {dim}"
                )
                return
            
            if dim > 100:
                self.show_error_dialog(
                    "Error de Dimensión",
                    f"La dimensión {dim} es demasiado grande.\n\nPor razones de rendimiento, el límite es 100."
                )
                return
            
            print(f"✓ Dimensión validada: {dim}×{dim}")
            
            # Generar o cargar matriz unitaria
            matrix_type = self.matrix_type_var.get()
            
            if matrix_type == "random":
                unitary_matrix = unitary_group.rvs(dim)
                print(f"✓ Matriz unitaria aleatoria {dim}×{dim} generada")
            elif matrix_type == "identity":
                unitary_matrix = np.identity(dim)
                print(f"✓ Matriz identidad {dim}×{dim} cargada")
            else:  # custom
                matrix_text = self.matrix_entry.get("1.0", "end").strip()
                if not matrix_text:
                    self.show_error_dialog("Error", "Por favor ingresa una matriz válida")
                    return
                
                try:
                    unitary_matrix = np.array(eval(matrix_text))
                    if unitary_matrix.shape != (dim, dim):
                        self.show_error_dialog(
                            "Error", 
                            f"La matriz debe ser {dim}×{dim}\n\nDimensión ingresada: {unitary_matrix.shape}"
                        )
                        return
                    print(f"✓ Matriz personalizada de dimensión {dim}×{dim} cargada")
                except Exception as e:
                    self.show_error_dialog("Error", f"Formato de matriz inválido: {str(e)}")
                    return
            
            # Generar o cargar vector de entrada
            vector_type = self.vector_type_var.get()
            
            if vector_type == "random":
                input_vector = np.random.randn(dim)
                input_vector = input_vector / np.linalg.norm(input_vector)
                print(f"✓ Vector aleatorio normalizado de dimensión {dim} generado")
            else:  # custom
                vector_text = self.vector_entry.get().strip()
                if not vector_text:
                    self.show_error_dialog("Error", "Por favor ingresa un vector válido")
                    return
                
                try:
                    vector_text = vector_text.replace(',', ' ')
                    input_vector = np.array([float(x) for x in vector_text.split()])
                    
                    if len(input_vector) != dim:
                        self.show_error_dialog("Error", f"El vector debe tener {dim} elementos")
                        return
                    
                    if self.normalize_vector_var.get():
                        input_vector = input_vector / np.linalg.norm(input_vector)
                    
                    print(f"✓ Vector personalizado de dimensión {dim} cargado")
                except Exception as e:
                    self.show_error_dialog("Error", f"Formato de vector inválido: {str(e)}")
                    return
            
            # Preparar parámetros
            params = {
                'unitary_matrix': unitary_matrix,
                'input_vector': input_vector,
                'visualize': self.visualize_mesh_var.get(),
                'show_interconnect': self.show_interconnect_var.get(), 
                'platform': self.selected_platform
            }
            
            print("\n" + "="*50)
            print("🔷 EJECUTANDO SIMULACIÓN MZI MESH")
            print("="*50)
            print(f"Plataforma: {self.selected_platform.upper()}")
            print(f"Dimensión: {dim}×{dim}")
            print(f"Matriz: {matrix_type}")
            print(f"Vector: {vector_type}")
            print(f"Visualizar: {params['visualize']}")
            print("="*50 + "\n")
            
            # Ejecutar simulación
            from GUI.mzi_mesh_simulation_window import MZIMeshSimulationWindow
            MZIMeshSimulationWindow(
                parent=self.root,
                api=self.api,
                params=params,
                callback=self.on_mzi_mesh_complete
            )
            
        except Exception as e:
            self.show_error_dialog("Error", f"Error al configurar simulación: {str(e)}")
            import traceback
            traceback.print_exc()

    def on_mzi_mesh_complete(self, success, results=None, error=None):
        """Callback cuando termina la simulación MZI Mesh"""
        if success:
            print("\n✓ Simulación MZI Mesh completada exitosamente")
            if results:
                print("Resultados:")
                print(f"  Error promedio: {results.get('avg_error', 'N/A')}")
                print(f"  Error máximo: {results.get('max_error', 'N/A')}")
        else:
            print(f"\n✗ Simulación MZI Mesh falló: {error}")

    def show_error_dialog(self, title, message):
        """Mostrar diálogo de error"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("450x180")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=DARK_BG)
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (180 // 2)
        dialog.geometry(f"450x180+{x}+{y}")
        
        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=TEXT_PRIMARY,
            wraplength=400
        )
        label.pack(pady=30, padx=20)
        
        button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            width=100
        )
        button.pack(pady=10)

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