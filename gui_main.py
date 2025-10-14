"""
GUI Principal para Silicon Photonic Neuromorphic Chip Simulation
Interfaz gráfica moderna con Sidebar usando CustomTkinter
"""

import customtkinter as ctk
from API.main import API
from PIL import Image
import os
import sys
import warnings
import atexit

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
        # Suprimir errores relacionados con threading de Tkinter
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
THEME_COLOR_HOVER = "#C01018"  # Rojo más oscuro
HEADER_BG = "#f8f8f8"  # Gris muy claro para que logo se vea
HEADER_TEXT = "#2d2d2d"  # Texto oscuro en header
DARK_BG = "#1a1a1a"  # Fondo oscuro principal
SIDEBAR_BG = "#2d2d2d"  # Fondo del sidebar
CARD_BG = "#252525"  # Fondo de tarjetas
TEXT_PRIMARY = "#ffffff"  # Texto principal
TEXT_SECONDARY = "#999999"  # Texto secundario
TEXT_DISABLED = "#555555"  # Texto deshabilitado

# Configuración del tema
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
        
        # Sección actual
        self.current_section = "home"
        
        # Variables para el formulario de configuración
        self.config_widgets = {}
        
        # Cargar logo
        self.load_logo()
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Configurar protocolo de cierre para limpiar recursos
        self.root.protocol("WM_DELETE_WINDOW", self.on_app_closing)

    def on_app_closing(self):
        """
        Manejar el cierre de la aplicación
        Limpia todos los recursos antes de cerrar
        """
        try:
            # 1. Limpiar imágenes de Tkinter
            print("\n Limpiando recursos de la GUI...")
            if hasattr(self, 'logo') and self.logo is not None:
                try:
                    self.logo = None
                    self._logo_pil = None
                    print("✓ Logo limpiado")
                except Exception as e:
                    print(f"⚠ Error al limpiar logo: {e}")
            
            # 2. Limpiar simulador activo de MZI si existe
            if hasattr(self.api, '_active_simulator') and self.api._active_simulator is not None:
                print("🧹 Limpiando recursos de INTERCONNECT...")
                try:
                    self.api._active_simulator.ic.close()
                    print("✓ INTERCONNECT cerrado correctamente")
                except Exception as e:
                    print(f"⚠ No se pudo cerrar INTERCONNECT: {e}")
                finally:
                    self.api._active_simulator = None
            
            # 3. Forzar garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"⚠ Error durante limpieza: {e}")
        finally:
            # 4. Cerrar ventana
            print("👋 Cerrando aplicación...")
            try:
                self.root.quit()
            except:
                pass
            try:
                self.root.destroy()
            except:
                pass    

    def on_app_closing(self):
        """
        Manejar el cierre de la aplicación
        Limpia todos los recursos activos de INTERCONNECT antes de cerrar
        """
        try:
            # Limpiar simulador activo de MZI si existe
            if hasattr(self.api, '_active_simulator') and self.api._active_simulator is not None:
                print("\n🧹 Limpiando recursos de INTERCONNECT...")
                try:
                    # Intentar cerrar INTERCONNECT de forma limpia
                    self.api._active_simulator.ic.close()
                    print("✓ INTERCONNECT cerrado correctamente")
                except Exception as e:
                    print(f"⚠ No se pudo cerrar INTERCONNECT limpiamente: {e}")
                finally:
                    self.api._active_simulator = None
        except Exception as e:
            print(f"⚠ Error durante limpieza: {e}")
        finally:
            # Cerrar la ventana principal
            print("👋 Cerrando aplicación...")
            self.root.quit()
            self.root.destroy()

    def load_logo(self):
        """Cargar el logo de Gradiant con proporción correcta"""
        try:
            logo_path = os.path.join("GUI", "assets", "images", "gradiant_logo.png")
            logo_image = Image.open(logo_path)
            
            # Obtener tamaño original y calcular proporción
            original_width, original_height = logo_image.size
            target_height = 40
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)
            
            self.logo = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(target_width, target_height)
            )
            
            # ✅ CRÍTICO: Mantener referencia fuerte a la imagen PIL
            # Esto evita que el garbage collector libere la imagen prematuramente
            # y causa el error "RuntimeError: Tcl_AsyncDelete: async handler deleted by the wrong thread"
            self._logo_pil_reference = logo_image
            
            print(f"✓ Logo cargado desde: {logo_path}")
            print(f"✓ Tamaño ajustado: {target_width}x{target_height}")
        except Exception as e:
            print(f"⚠ No se pudo cargar el logo: {e}")
            self.logo = None
            self._logo_pil_reference = None
        
    def setup_ui(self):
        """Configurar todos los elementos de la interfaz"""
        
        # ========== BARRA SUPERIOR CON LOGO ==========
        header_frame = ctk.CTkFrame(self.root, fg_color=HEADER_BG, height=80, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo de Gradiant
        if self.logo:
            logo_label = ctk.CTkLabel(
                header_frame,
                image=self.logo,
                text=""
            )
            logo_label.pack(side="left", padx=30, pady=15)
        
        # Separador vertical
        separator = ctk.CTkFrame(header_frame, fg_color=HEADER_TEXT, width=2)
        separator.pack(side="left", fill="y", padx=(0, 20), pady=15)
        
        # Títulos
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
        
        # ========== CONTENEDOR PRINCIPAL (SIDEBAR + CONTENIDO) ==========
        main_container = ctk.CTkFrame(self.root, fg_color=DARK_BG)
        main_container.pack(fill="both", expand=True)
        
        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(main_container, fg_color=SIDEBAR_BG, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        sidebar_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=15, pady=20)
        
        # Título del sidebar
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
        
        # Separador
        separator = ctk.CTkFrame(sidebar_content, fg_color=TEXT_DISABLED, height=1)
        separator.pack(fill="x", pady=20)
        
        # ========== SELECTOR DE PLATAFORMA EN SIDEBAR ==========
        platform_section_title = ctk.CTkLabel(
            sidebar_content,
            text="PLATFORM",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        platform_section_title.pack(fill="x", pady=(0, 10))
        
        self.platform_var = ctk.StringVar(value="sipho")
        
        sipho_radio = ctk.CTkRadioButton(
            sidebar_content,
            text="Silicon Photonics",
            variable=self.platform_var,
            value="sipho",
            command=self.on_platform_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        sipho_radio.pack(anchor="w", pady=5)
        
        sin_radio = ctk.CTkRadioButton(
            sidebar_content,
            text="Silicon Nitride",
            variable=self.platform_var,
            value="sin",
            command=self.on_platform_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        sin_radio.pack(anchor="w", pady=5)
        
        # Separador
        separator2 = ctk.CTkFrame(sidebar_content, fg_color=TEXT_DISABLED, height=1)
        separator2.pack(fill="x", pady=20)
        
        # ========== CACHE INFO ==========
        cache_title = ctk.CTkLabel(
            sidebar_content,
            text="CACHE INFO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        cache_title.pack(fill="x", pady=(0, 10))
        
        cache_info_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        cache_info_frame.pack(fill="x")
        
        self.cache_sipho_label = ctk.CTkLabel(
            cache_info_frame,
            text=f"SiPho: {self.api.get_total_simulations()} sims",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        self.cache_sipho_label.pack(anchor="w", pady=2)
        
        self.cache_sin_label = ctk.CTkLabel(
            cache_info_frame,
            text="SiN: - sims",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.cache_sin_label.pack(anchor="w", pady=2)
        
        # ========== CONTENIDO PRINCIPAL ==========
        self.content_frame = ctk.CTkFrame(main_container, fg_color=DARK_BG)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=30, pady=30)
        
        # Mostrar Home por defecto
        self.show_home()
        
    def create_nav_button(self, parent, text, section, enabled=True):
        """Crear botón de navegación"""
        if enabled:
            btn = ctk.CTkButton(
                parent,
                text=text,
                command=lambda: self.navigate_to(section),
                fg_color="transparent",
                text_color=TEXT_PRIMARY,
                hover_color=CARD_BG,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=13)
            )
        else:
            btn = ctk.CTkButton(
                parent,
                text=text,
                fg_color="transparent",
                text_color=TEXT_DISABLED,
                hover_color=SIDEBAR_BG,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=13),
                state="disabled"
            )
        
        btn.pack(fill="x", pady=2)
        return btn
    
    def navigate_to(self, section):
        """Navegar a una sección"""
        self.current_section = section
        
        # Actualizar colores de botones
        for key, btn in self.nav_buttons.items():
            if key == section:
                btn.configure(fg_color=THEME_COLOR, text_color=TEXT_PRIMARY)
            else:
                if btn.cget("state") != "disabled":
                    btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY)
        
        # Mostrar contenido correspondiente
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
        
        # Card de plataforma actual
        platform_card = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=15)
        platform_card.pack(fill="x", pady=(0, 20))
        
        platform_title = ctk.CTkLabel(
            platform_card,
            text="📡 Plataforma Actual",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        platform_title.pack(fill="x", padx=30, pady=(20, 10))
        
        platform_names = {
            "sipho": "Silicon Photonics (SiPho)",
            "sin": "Silicon Nitride (SiN)"
        }
        
        self.platform_display_label = ctk.CTkLabel(
            platform_card,
            text=f"✓ {platform_names[self.selected_platform]}",
            font=ctk.CTkFont(size=16),
            text_color=THEME_COLOR,
            anchor="w"
        )
        self.platform_display_label.pack(fill="x", padx=30, pady=(0, 20))
        
        # Card de última configuración
        info_card = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=15)
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
        
        self.info_grid = ctk.CTkFrame(info_card, fg_color=CARD_BG)
        self.info_grid.pack(fill="x", padx=30, pady=(0, 20))
        
        self.update_info_display()
        
        # Botón principal
        button_frame = ctk.CTkFrame(self.content_frame, fg_color=DARK_BG)
        button_frame.pack(expand=True)
        
        start_button = ctk.CTkButton(
            button_frame,
            text="▶  Iniciar Nueva Simulación",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            width=350,
            command=lambda: self.navigate_to("simulate"),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        start_button.pack(pady=20)
    
    def show_simulate(self):
        """Mostrar formulario de configuración de simulación"""
        self.clear_content()
        
        # Scrollable frame para el formulario
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=DARK_BG,
            scrollbar_button_color=CARD_BG,
            scrollbar_button_hover_color=SIDEBAR_BG
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # Título
        title = ctk.CTkLabel(
            scroll_frame,
            text="⚙️ Configuración de Simulación",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title.pack(fill="x", pady=(0, 20))
        
        # SECCIÓN 1: Tipo de simulación
        sim_type_card = self.create_section_card(scroll_frame, "🔬 Tipo de Simulación")
        
        self.sim_type_var = ctk.StringVar(value="single laser")
        
        single_laser_radio = ctk.CTkRadioButton(
            sim_type_card,
            text="Láser Único",
            variable=self.sim_type_var,
            value="single laser",
            command=self.on_sim_type_changed,
            font=ctk.CTkFont(size=14),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        single_laser_radio.pack(anchor="w", pady=8, padx=30)
        
        wavelength_sweep_radio = ctk.CTkRadioButton(
            sim_type_card,
            text="Barrido de Longitud de Onda",
            variable=self.sim_type_var,
            value="wavelength sweep",
            command=self.on_sim_type_changed,
            font=ctk.CTkFont(size=14),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        wavelength_sweep_radio.pack(anchor="w", pady=8, padx=30)
        
        # SECCIÓN 2: Parámetros del láser
        laser_card = self.create_section_card(scroll_frame, "💡 Parámetros del Láser")
        
        self.source_wavelength_entry = self.create_input_field(
            laser_card,
            "Longitud de onda del láser (m)",
            self.defaults.get('laser_wavelength', '1.545e-9')
        )
        
        self.wavelength_window_frame = ctk.CTkFrame(laser_card, fg_color="transparent")
        self.wavelength_window_frame.pack(fill="x", pady=(5, 0), padx=30)
        
        self.wavelength_window_entry = self.create_input_field(
            self.wavelength_window_frame,
            "Ventana de longitud de onda (m)",
            self.defaults.get('wavelength_window', '2.5e-8')
        )
        
        # SECCIÓN 3: Heater
        heater_card = self.create_section_card(scroll_frame, "🔥 N-Doped Heater")
        
        self.heater_type_var = ctk.StringVar(value="constant voltage")
        
        constant_v_radio = ctk.CTkRadioButton(
            heater_card,
            text="Voltaje Constante",
            variable=self.heater_type_var,
            value="constant voltage",
            command=self.on_heater_type_changed,
            font=ctk.CTkFont(size=14),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        constant_v_radio.pack(anchor="w", pady=8, padx=30)
        
        sweep_radio = ctk.CTkRadioButton(
            heater_card,
            text="Barrido de Voltaje",
            variable=self.heater_type_var,
            value="sweep",
            command=self.on_heater_type_changed,
            font=ctk.CTkFont(size=14),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        sweep_radio.pack(anchor="w", pady=8, padx=30)
        
        # Voltaje constante
        self.constant_voltage_frame = ctk.CTkFrame(heater_card, fg_color="transparent")
        self.constant_voltage_frame.pack(fill="x", pady=(5, 0), padx=30)
        
        self.constant_v_entry = self.create_input_field(
            self.constant_voltage_frame,
            "Voltaje fijo (V)",
            self.defaults.get('constant_v', '10.0')
        )
        
        # Barrido de voltaje
        self.sweep_container = ctk.CTkFrame(heater_card, fg_color="transparent")
        self.sweep_container.pack(fill="x", pady=(5, 0), padx=30)
        
        self.min_voltage_entry = self.create_input_field(
            self.sweep_container,
            "Voltaje mínimo (V)",
            self.defaults.get('min_v', '0.0')
        )
        
        self.max_voltage_entry = self.create_input_field(
            self.sweep_container,
            "Voltaje máximo (V)",
            self.defaults.get('max_v', '20.0')
        )
        
        self.voltage_interval_entry = self.create_input_field(
            self.sweep_container,
            "Intervalo de voltaje (V)",
            self.defaults.get('interval_v', '0.2')
        )
        
        # SECCIÓN 4: Parámetros temporales
        time_card = self.create_section_card(scroll_frame, "⏱️ Parámetros Temporales")
        
        self.time_window_entry = self.create_input_field(
            time_card,
            "Ventana de tiempo (s)",
            '5.12e-9'
        )
        
        self.n_samples_entry = self.create_input_field(
            time_card,
            "Número de muestras",
            '15360'
        )
        
        # SECCIÓN 5: Salida
        output_card = self.create_section_card(scroll_frame, "💾 Configuración de Salida")
        
        self.output_dir_entry = self.create_input_field(
            output_card,
            "Directorio de salida",
            './results'
        )
        
        # Botones de acción
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", height=80)
        button_frame.pack(fill="x", pady=30)
        
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True)
        
        cancel_button = ctk.CTkButton(
            button_container,
            text="✖  Cancelar",
            command=lambda: self.navigate_to("home"),
            fg_color="transparent",
            border_width=2,
            border_color=TEXT_SECONDARY,
            hover_color=CARD_BG,
            width=180,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cancel_button.pack(side="left", padx=10)
        
        confirm_button = ctk.CTkButton(
            button_container,
            text="✓  Confirmar y Continuar",
            command=self.confirm_simulation,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            width=220,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        confirm_button.pack(side="left", padx=10)
        
        # Inicializar visibilidad
        self.on_sim_type_changed()
        self.on_heater_type_changed()
    
    def create_section_card(self, parent, title):
        """Crear una tarjeta de sección"""
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        card.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(fill="x", padx=30, pady=(20, 10))
        
        return card
    
    def create_input_field(self, parent, label_text, default_value):
        """Crear campo de entrada"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=8)
        
        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        label.pack(fill="x", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            container,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=SIDEBAR_BG,
            border_color=CARD_BG,
            text_color=TEXT_PRIMARY
        )
        entry.pack(fill="x")
        entry.insert(0, default_value)
        
        return entry
    
    def on_sim_type_changed(self):
        """Callback cuando cambia el tipo de simulación"""
        sim_type = self.sim_type_var.get()
        
        if sim_type == "single laser":
            self.wavelength_window_frame.pack_forget()
        else:
            self.wavelength_window_frame.pack(fill="x", pady=(5, 0), padx=30)
    
    def on_heater_type_changed(self):
        """Callback cuando cambia el tipo de heater"""
        heater_type = self.heater_type_var.get()
        
        if heater_type == "constant voltage":
            self.sweep_container.pack_forget()
            self.constant_voltage_frame.pack(fill="x", pady=(5, 0), padx=30)
        else:
            self.constant_voltage_frame.pack_forget()
            self.sweep_container.pack(fill="x", pady=(5, 0), padx=30)
    
    def confirm_simulation(self):
        """Confirmar y ejecutar simulación"""
        # Recopilar parámetros
        params = {
            'sim_type': self.sim_type_var.get(),
            'heater_sim_type': self.heater_type_var.get(),
            'source_wavelength': float(self.source_wavelength_entry.get()),
            'time_window': float(self.time_window_entry.get()),
            'n_samples': int(self.n_samples_entry.get()),
            'output_dir': self.output_dir_entry.get(),
            'platform': self.selected_platform
        }
        
        # Parámetros según tipo de simulación
        if params['sim_type'] == "single laser":
            params['start_wavelength'] = params['source_wavelength']
            params['end_wavelength'] = params['source_wavelength']
        else:
            wavelength_window = float(self.wavelength_window_entry.get())
            half_window = wavelength_window / 2
            params['start_wavelength'] = params['source_wavelength'] - half_window
            params['end_wavelength'] = params['source_wavelength'] + half_window
        
        # Parámetros según tipo de heater
        if params['heater_sim_type'] == "constant voltage":
            params['constant_v'] = float(self.constant_v_entry.get())
            params['min_v'] = params['constant_v']
            params['max_v'] = params['constant_v']
            params['interval_v'] = 1
        else:
            params['min_v'] = float(self.min_voltage_entry.get())
            params['max_v'] = float(self.max_voltage_entry.get())
            params['interval_v'] = float(self.voltage_interval_entry.get())
        
        # Ejecutar callback
        self.on_configuration_complete(params)
    
    def show_results(self):
        """Mostrar pantalla de Results"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="📊 Results\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def show_history(self):
        """Mostrar pantalla de History"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="📝 History\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def show_settings(self):
        """Mostrar pantalla de Settings"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="⚙️ Settings\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
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
        
        print(f"✓ Plataforma cambiada exitosamente a {new_platform.upper()}\n")
    
    def update_cache_info(self):
        """Actualizar información de cache"""
        current_platform = self.selected_platform
        current_count = self.api.get_total_simulations()  # ← CORREGIDO
        
        other_platform = "sin" if current_platform == "sipho" else "sipho"
        self.api.set_platform(other_platform)
        self.api.load_cache()
        other_count = self.api.get_total_simulations()  # ← CORREGIDO
        
        self.api.set_platform(current_platform)
        self.api.load_cache()
        
        if current_platform == "sipho":
            self.cache_sipho_label.configure(text=f"SiPho: {current_count} sims", text_color=TEXT_PRIMARY)
            self.cache_sin_label.configure(text=f"SiN: {other_count} sims", text_color=TEXT_SECONDARY)
        else:
            self.cache_sin_label.configure(text=f"SiN: {current_count} sims", text_color=TEXT_PRIMARY)
            self.cache_sipho_label.configure(text=f"SiPho: {other_count} sims", text_color=TEXT_SECONDARY)
    
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
        
        if params.get('heater_sim_type') == 'constant voltage':
            voltage_display = f"{params.get('constant_v', 'N/A')} V (constante)"
        else:
            voltage_display = f"{params.get('min_v', 'N/A')}-{params.get('max_v', 'N/A')} V"
        
        display_data = [
            ("Tipo de Simulación", self.format_sim_type(params.get('sim_type', ''))),
            ("Longitud de Onda", f"{wavelength_nm:.2f} nm"),
            ("Modo Heater", self.format_heater_type(params.get('heater_sim_type', ''))),
            ("Voltaje", voltage_display),
            ("Ventana Temporal", params.get('time_window', 'N/A')),
            ("Muestras", params.get('n_samples', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(display_data):
            row = i // 2
            col = i % 2
            self.create_info_item(self.info_grid, label, value, row, col)
    
    def format_sim_type(self, sim_type):
        """Formatear tipo de simulación"""
        if sim_type == "single laser":
            return "Láser Único"
        elif sim_type == "wavelength sweep":
            return "Barrido de Longitud de Onda"
        return sim_type
    
    def format_heater_type(self, heater_type):
        """Formatear tipo de heater"""
        if heater_type == "constant voltage":
            return "Voltaje Constante"
        elif heater_type == "sweep":
            return "Barrido (Sweep)"
        return heater_type
    
    def create_info_item(self, parent, label, value, row, column):
        """Crear item de información"""
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
    
    def on_configuration_complete(self, params):
        """Callback cuando se completa la configuración"""
        print("\n" + "="*50)
        print("🎉 Configuración completada!")
        print("="*50)
        print("\nParámetros recibidos:")
        for key, value in params.items():
            print(f"  • {key}: {value}")
        print("\n" + "="*50)
        
        self.last_config = params
        
        self.info_subtitle.configure(
            text=f"Última configuración: {self.format_sim_type(params.get('sim_type', ''))} | "
                 f"{self.format_heater_type(params.get('heater_sim_type', ''))} | "
                 f"Plataforma: {self.selected_platform.upper()}"
        )
        
        self.update_info_display()
        
        # Volver a Home
        self.navigate_to("home")
        
        # Ejecutar simulación
        from GUI.simulation_window import SimulationWindow
        SimulationWindow(
            parent=self.root,
            api=self.api,
            params=params,
            callback=self.on_simulation_complete
        )
    
    def on_simulation_complete(self, success, params=None, error=None):
        """Callback cuando termina la simulación"""
        if success:
            print("\n✓ Simulación completada exitosamente")
            self.update_cache_info()
        else:
            print(f"\n✗ Simulación falló: {error}")

    def show_mzi_mesh(self):
        """Mostrar interfaz de MZI Mesh"""
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

        # ✅ NUEVO: Campo de entrada de texto en lugar de dropdown
        self.mesh_dimension_var = ctk.StringVar(value="4")
        dim_entry = ctk.CTkEntry(
            dim_frame,
            textvariable=self.mesh_dimension_var,
            width=80,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=CARD_BG,
            border_width=2,
            border_color=THEME_COLOR,
            justify="center"
        )
        dim_entry.pack(side="left", padx=(0, 10))

        # Texto de ayuda
        dim_help = ctk.CTkLabel(
            dim_frame,
            text="(min: 2, recomendado: 2-20)",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY
        )
        dim_help.pack(side="left")

        
        # ========== SECCIÓN 2: MATRIZ ==========
        matrix_card = self.create_section_card(scroll_frame, "🔢 Matriz Unitaria (U)")
        
        self.matrix_type_var = ctk.StringVar(value="random")
        
        matrix_options_frame = ctk.CTkFrame(matrix_card, fg_color="transparent")
        matrix_options_frame.pack(fill="x", pady=(10, 15), padx=30)
        
        random_matrix_radio = ctk.CTkRadioButton(
            matrix_options_frame,
            text="Matriz aleatoria (generada automáticamente)",
            variable=self.matrix_type_var,
            value="random",
            command=self.on_matrix_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        random_matrix_radio.pack(anchor="w", pady=5)
        
        identity_matrix_radio = ctk.CTkRadioButton(
            matrix_options_frame,
            text="Matriz identidad",
            variable=self.matrix_type_var,
            value="identity",
            command=self.on_matrix_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        identity_matrix_radio.pack(anchor="w", pady=5)
        
        custom_matrix_radio = ctk.CTkRadioButton(
            matrix_options_frame,
            text="Matriz personalizada (ingresar manualmente)",
            variable=self.matrix_type_var,
            value="custom",
            command=self.on_matrix_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        custom_matrix_radio.pack(anchor="w", pady=5)
        
        # Área para matriz personalizada
        self.matrix_input_frame = ctk.CTkFrame(matrix_card, fg_color=CARD_BG)
        
        matrix_help_label = ctk.CTkLabel(
            self.matrix_input_frame,
            text="Formato: Elementos separados por espacios, una fila por línea\nEjemplo 2×2:\n0.707 0.707\n-0.707 0.707",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
            justify="left"
        )
        matrix_help_label.pack(anchor="w", pady=(10, 5), padx=10)
        
        self.matrix_textbox = ctk.CTkTextbox(
            self.matrix_input_frame,
            height=150,
            font=ctk.CTkFont(family="Courier", size=12),
            fg_color=DARK_BG,
            border_width=1,
            border_color=TEXT_DISABLED
        )
        self.matrix_textbox.pack(fill="x", pady=10, padx=10)
        
        # ========== SECCIÓN 3: VECTOR ==========
        vector_card = self.create_section_card(scroll_frame, "➡️  Vector de Entrada (v)")
        
        self.vector_type_var = ctk.StringVar(value="random")
        
        vector_options_frame = ctk.CTkFrame(vector_card, fg_color="transparent")
        vector_options_frame.pack(fill="x", pady=(10, 15), padx=30)
        
        random_vector_radio = ctk.CTkRadioButton(
            vector_options_frame,
            text="Vector aleatorio normalizado",
            variable=self.vector_type_var,
            value="random",
            command=self.on_vector_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        random_vector_radio.pack(anchor="w", pady=5)
        
        custom_vector_radio = ctk.CTkRadioButton(
            vector_options_frame,
            text="Vector personalizado",
            variable=self.vector_type_var,
            value="custom",
            command=self.on_vector_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        custom_vector_radio.pack(anchor="w", pady=5)
        
        # Campo para vector personalizado
        self.vector_input_frame = ctk.CTkFrame(vector_card, fg_color=CARD_BG)
        
        vector_help_label = ctk.CTkLabel(
            self.vector_input_frame,
            text="Formato: Elementos separados por espacios o comas\nEjemplo: 1 2 -3 4",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
            justify="left"
        )
        vector_help_label.pack(anchor="w", pady=(10, 5), padx=10)
        
        self.vector_entry = ctk.CTkEntry(
            self.vector_input_frame,
            height=40,
            font=ctk.CTkFont(family="Courier", size=13),
            fg_color=DARK_BG,
            border_width=1,
            border_color=TEXT_DISABLED
        )
        self.vector_entry.pack(fill="x", pady=10, padx=10)
        
        # ========== SECCIÓN 4: OPCIONES ==========
        options_card = self.create_section_card(scroll_frame, "⚙️  Opciones de Simulación")
        
        options_frame = ctk.CTkFrame(options_card, fg_color="transparent")
        options_frame.pack(fill="x", pady=(10, 20), padx=30)
        
        self.visualize_mesh_var = ctk.BooleanVar(value=True)
        visualize_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Visualizar diagrama del mesh",
            variable=self.visualize_mesh_var,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        visualize_checkbox.pack(anchor="w", pady=5)
        
        self.normalize_vector_var = ctk.BooleanVar(value=True)
        normalize_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Normalizar vector de entrada",
            variable=self.normalize_vector_var,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        normalize_checkbox.pack(anchor="w", pady=5)
        
        self.show_interconnect_var = ctk.BooleanVar(value=True)
        show_ic_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Mostrar ventana de INTERCONNECT (ver simulación en tiempo real)",
            variable=self.show_interconnect_var,
            font=ctk.CTkFont(size=13),
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
        import numpy as np
        from scipy.stats import unitary_group
        
        try:
            # ✅ VALIDACIÓN MEJORADA: Obtener y validar dimensión
            dim_text = self.mesh_dimension_var.get().strip()
            
            # Verificar que sea un número
            try:
                dim = int(dim_text)
            except ValueError:
                self.show_error_dialog(
                    "Error de Dimensión", 
                    f"'{dim_text}' no es un número válido.\n\nPor favor ingresa un número entero."
                )
                return
            
            # Validar rango
            if dim < 2:
                self.show_error_dialog(
                    "Error de Dimensión", 
                    f"La dimensión debe ser al menos 2.\n\nDimensión ingresada: {dim}"
                )
                return
            
            if dim > 50:
                # Advertencia para dimensiones grandes
                from tkinter import messagebox
                confirm = messagebox.askyesno(
                    "Dimensión Grande",
                    f"Has ingresado una dimensión de {dim}×{dim}.\n\n"
                    f"Esto puede:\n"
                    f"• Tomar mucho tiempo de simulación\n"
                    f"• Consumir mucha memoria\n"
                    f"• Hacer que INTERCONNECT se vuelva lento\n\n"
                    f"¿Deseas continuar de todas formas?",
                    icon='warning'
                )
                if not confirm:
                    return
            
            print(f"✓ Dimensión validada: {dim}×{dim}")
            
            # Generar o leer matriz
            matrix_type = self.matrix_type_var.get()
            

            if matrix_type == "random":
                unitary_matrix = unitary_group.rvs(dim)
                print(f"✓ Matriz aleatoria {dim}×{dim} generada")
            elif matrix_type == "identity":
                unitary_matrix = np.identity(dim)
                print(f"✓ Matriz identidad {dim}×{dim} creada")
            else:  # custom
                matrix_text = self.matrix_textbox.get("1.0", "end-1c")
                if not matrix_text.strip():
                    self.show_error_dialog("Error", "Por favor ingresa una matriz válida")
                    return
                
                try:
                    rows = [line.strip() for line in matrix_text.split('\n') if line.strip()]
                    unitary_matrix = np.array([[float(x) for x in row.split()] for row in rows])
                    
                    if unitary_matrix.shape != (dim, dim):
                        self.show_error_dialog("Error", f"La matriz debe ser {dim}×{dim}")
                        return
                    
                    print(f"✓ Matriz personalizada {dim}×{dim} cargada")
                except Exception as e:
                    self.show_error_dialog("Error", f"Formato de matriz inválido: {str(e)}")
                    return
            
            # Generar o leer vector
            vector_type = self.vector_type_var.get()
            if vector_type == "random":
                input_vector = np.random.randn(dim)
                if self.normalize_vector_var.get():
                    input_vector = input_vector / np.linalg.norm(input_vector)
                print(f"✓ Vector aleatorio de dimensión {dim} generado")
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
            print("Resultados:", results)
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