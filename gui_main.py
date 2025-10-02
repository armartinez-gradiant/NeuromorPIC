"""
Main GUI for Silicon Photonic Neuromorphic Chip Simulation
Modern graphical interface with Sidebar using CustomTkinter
"""

import customtkinter as ctk
from API.main import API
from PIL import Image
import os
import sys

# ========== CUSTOM THEME CONFIGURATION ==========
THEME_COLOR = "#E31E24"  # Gradiant Red
THEME_COLOR_HOVER = "#C01018"  # Darker red
HEADER_BG = "#f8f8f8"  # Very light gray for logo visibility
HEADER_TEXT = "#2d2d2d"  # Dark text on header
DARK_BG = "#1a1a1a"  # Main dark background
SIDEBAR_BG = "#2d2d2d"  # Sidebar background
CARD_BG = "#252525"  # Card background
TEXT_PRIMARY = "#ffffff"  # Primary text
TEXT_SECONDARY = "#999999"  # Secondary text
TEXT_DISABLED = "#555555"  # Disabled text

# Theme configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LumericalGUI:
    """Main GUI class"""
    
    def __init__(self):
        # Create main window
        self.root = ctk.CTk()
        self.root.title("NeuromorPIC Simulation Platform - Gradiant")
        self.root.geometry("1200x800")
        
        # Custom background color
        self.root.configure(fg_color=DARK_BG)
        
        # Initialize API
        self.api = API()
        
        # Default platform
        self.selected_platform = "sipho"
        self.api.set_platform(self.selected_platform)
        self.api.load_cache()
        self.defaults = self.api.get_param_suggestions()
        
        # Variable to store last configuration
        self.last_config = None
        
        # Current section
        self.current_section = "home"
        
        # Variables for configuration form
        self.config_widgets = {}
        
        # Load logo
        self.load_logo()
        
        # Configure interface
        self.setup_ui()
        
    def load_logo(self):
        """Load Gradiant logo"""
        try:
            logo_path = os.path.join("GUI", "assets", "images", "gradiant_logo.png")
            logo_image = Image.open(logo_path)
            self.logo = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(150, 50)
            )
            print(f"✓ Logo loaded from: {logo_path}")
        except Exception as e:
            print(f"⚠️  Could not load logo: {e}")
            self.logo = None
        
    def setup_ui(self):
        """Configure all interface elements"""
        
        # ========== TOP BAR WITH LOGO ==========
        header_frame = ctk.CTkFrame(self.root, fg_color=HEADER_BG, height=80, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Gradiant Logo
        if self.logo:
            logo_label = ctk.CTkLabel(
                header_frame,
                image=self.logo,
                text=""
            )
            logo_label.pack(side="left", padx=30, pady=15)
        
        # Vertical separator
        separator = ctk.CTkFrame(header_frame, fg_color=HEADER_TEXT, width=2)
        separator.pack(side="left", fill="y", padx=(0, 20), pady=15)
        
        # Titles
        titles_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        titles_frame.pack(side="left", fill="y", pady=15)
        
        title_label = ctk.CTkLabel(
            titles_frame,
            text="NeuromorPIC",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=HEADER_TEXT,
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            titles_frame,
            text="Photonic Neuromorphic Chip Simulation Platform",
            font=ctk.CTkFont(size=13),
            text_color=HEADER_TEXT,
            anchor="w"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # ========== MAIN CONTAINER (SIDEBAR + CONTENT) ==========
        main_container = ctk.CTkFrame(self.root, fg_color=DARK_BG)
        main_container.pack(fill="both", expand=True)
        
        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(main_container, fg_color=SIDEBAR_BG, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        sidebar_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=15, pady=20)
        
        # Sidebar title
        sidebar_title = ctk.CTkLabel(
            sidebar_content,
            text="NAVIGATION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        sidebar_title.pack(fill="x", pady=(0, 15))
        
        # Navigation buttons
        self.nav_buttons = {}
        
        self.nav_buttons['home'] = self.create_nav_button(sidebar_content, "🏠  Home", "home", enabled=True)
        self.nav_buttons['simulate'] = self.create_nav_button(sidebar_content, "🔬  Simulate", "simulate", enabled=True)
        self.nav_buttons['results'] = self.create_nav_button(sidebar_content, "📊  Results", "results", enabled=False)
        self.nav_buttons['history'] = self.create_nav_button(sidebar_content, "📝  History", "history", enabled=False)
        self.nav_buttons['settings'] = self.create_nav_button(sidebar_content, "⚙️  Settings", "settings", enabled=False)
        
        # Separator
        separator = ctk.CTkFrame(sidebar_content, fg_color=TEXT_DISABLED, height=1)
        separator.pack(fill="x", pady=20)
        
        # ========== PLATFORM SELECTOR IN SIDEBAR ==========
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
        
        # Separator
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
            text=f"SiPho: {len(self.api.wgT)} sims",
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
        
        # ========== MAIN CONTENT ==========
        self.content_frame = ctk.CTkFrame(main_container, fg_color=DARK_BG)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=30, pady=30)
        
        # Show Home by default
        self.show_home()
        
    def create_nav_button(self, parent, text, section, enabled=True):
        """Create navigation button"""
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
        """Navigate to a section"""
        self.current_section = section
        
        # Update button colors
        for key, btn in self.nav_buttons.items():
            if key == section:
                btn.configure(fg_color=THEME_COLOR, text_color=TEXT_PRIMARY)
            else:
                if btn.cget("state") != "disabled":
                    btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY)
        
        # Show corresponding content
        if section == "home":
            self.show_home()
        elif section == "simulate":
            self.show_simulate()
        elif section == "results":
            self.show_results()
        elif section == "history":
            self.show_history()
        elif section == "settings":
            self.show_settings()
    
    def clear_content(self):
        """Clear current content"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_home(self):
        """Show Home screen"""
        self.clear_content()
        
        # Welcome card
        welcome_card = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=15)
        welcome_card.pack(fill="x", pady=(0, 20))
        
        welcome_title = ctk.CTkLabel(
            welcome_card,
            text="Welcome",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        welcome_title.pack(fill="x", padx=30, pady=(25, 10))
        
        welcome_text = ctk.CTkLabel(
            welcome_card,
            text="This platform allows you to configure and run advanced simulations\n"
                 "of photonic neuromorphic chips using Lumerical INTERCONNECT.",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY,
            anchor="w",
            justify="left"
        )
        welcome_text.pack(fill="x", padx=30, pady=(0, 25))
        
        # Current platform card
        platform_card = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=15)
        platform_card.pack(fill="x", pady=(0, 20))
        
        platform_title = ctk.CTkLabel(
            platform_card,
            text="📡 Current Platform",
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
        
        # Last configuration card
        info_card = ctk.CTkFrame(self.content_frame, fg_color=CARD_BG, corner_radius=15)
        info_card.pack(fill="x", pady=(0, 25))
        
        self.info_title = ctk.CTkLabel(
            info_card,
            text="📊 Last Simulation Parameters",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        self.info_title.pack(fill="x", padx=30, pady=(20, 5))
        
        self.info_subtitle = ctk.CTkLabel(
            info_card,
            text="No simulation has been configured yet",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.info_subtitle.pack(fill="x", padx=30, pady=(0, 15))
        
        self.info_grid = ctk.CTkFrame(info_card, fg_color=CARD_BG)
        self.info_grid.pack(fill="x", padx=30, pady=(0, 20))
        
        self.update_info_display()
        
        # Main button
        button_frame = ctk.CTkFrame(self.content_frame, fg_color=DARK_BG)
        button_frame.pack(expand=True)
        
        start_button = ctk.CTkButton(
            button_frame,
            text="▶  Start New Simulation",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            width=350,
            command=lambda: self.navigate_to("simulate"),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        start_button.pack(pady=20)
    
    def show_simulate(self):
        """Show simulation configuration form"""
        self.clear_content()
        
        # Scrollable frame for the form
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=DARK_BG,
            scrollbar_button_color=CARD_BG,
            scrollbar_button_hover_color=SIDEBAR_BG
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(
            scroll_frame,
            text="⚙️ Simulation Configuration",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title.pack(fill="x", pady=(0, 20))
        
        # SECTION 1: Simulation type
        sim_type_card = self.create_section_card(scroll_frame, "🔬 Simulation Type")
        
        self.sim_type_var = ctk.StringVar(value="single laser")
        
        single_laser_radio = ctk.CTkRadioButton(
            sim_type_card,
            text="Single Laser",
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
            text="Wavelength Sweep",
            variable=self.sim_type_var,
            value="wavelength sweep",
            command=self.on_sim_type_changed,
            font=ctk.CTkFont(size=14),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        wavelength_sweep_radio.pack(anchor="w", pady=8, padx=30)
        
        # SECTION 2: Laser parameters
        laser_card = self.create_section_card(scroll_frame, "💡 Laser Parameters")
        
        self.source_wavelength_entry = self.create_input_field(
            laser_card,
            "Laser wavelength (m)",
            self.defaults.get('laser_wavelength', '1.545e-9')
        )
        
        self.wavelength_window_frame = ctk.CTkFrame(laser_card, fg_color="transparent")
        self.wavelength_window_frame.pack(fill="x", pady=(5, 0), padx=30)
        
        self.wavelength_window_entry = self.create_input_field(
            self.wavelength_window_frame,
            "Wavelength window (m)",
            self.defaults.get('wavelength_window', '2.5e-8')
        )
        
        # SECTION 3: Heater
        heater_card = self.create_section_card(scroll_frame, "🔥 N-Doped Heater")
        
        self.heater_type_var = ctk.StringVar(value="constant voltage")
        
        constant_v_radio = ctk.CTkRadioButton(
            heater_card,
            text="Constant Voltage",
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
            text="Voltage Sweep",
            variable=self.heater_type_var,
            value="sweep",
            command=self.on_heater_type_changed,
            font=ctk.CTkFont(size=14),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        sweep_radio.pack(anchor="w", pady=8, padx=30)
        
        # Constant voltage
        self.constant_voltage_frame = ctk.CTkFrame(heater_card, fg_color="transparent")
        self.constant_voltage_frame.pack(fill="x", pady=(5, 0), padx=30)
        
        self.constant_v_entry = self.create_input_field(
            self.constant_voltage_frame,
            "Fixed voltage (V)",
            self.defaults.get('constant_v', '10.0')
        )
        
        # Voltage sweep
        self.sweep_container = ctk.CTkFrame(heater_card, fg_color="transparent")
        self.sweep_container.pack(fill="x", pady=(5, 0), padx=30)
        
        self.min_voltage_entry = self.create_input_field(
            self.sweep_container,
            "Minimum voltage (V)",
            self.defaults.get('min_v', '0.0')
        )
        
        self.max_voltage_entry = self.create_input_field(
            self.sweep_container,
            "Maximum voltage (V)",
            self.defaults.get('max_v', '20.0')
        )
        
        self.voltage_interval_entry = self.create_input_field(
            self.sweep_container,
            "Voltage interval (V)",
            self.defaults.get('interval_v', '0.2')
        )
        
        # SECTION 4: Time parameters
        time_card = self.create_section_card(scroll_frame, "⏱️ Time Parameters")
        
        self.time_window_entry = self.create_input_field(
            time_card,
            "Time window (s)",
            '5.12e-9'
        )
        
        self.n_samples_entry = self.create_input_field(
            time_card,
            "Number of samples",
            '15360'
        )
        
        # SECTION 5: Output
        output_card = self.create_section_card(scroll_frame, "💾 Output Configuration")
        
        self.output_dir_entry = self.create_input_field(
            output_card,
            "Output directory",
            './results'
        )
        
        # Action buttons
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", height=80)
        button_frame.pack(fill="x", pady=30)
        
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True)
        
        cancel_button = ctk.CTkButton(
            button_container,
            text="✖  Cancel",
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
            text="✓  Confirm and Continue",
            command=self.confirm_simulation,
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            width=220,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        confirm_button.pack(side="left", padx=10)
        
        # Initialize visibility
        self.on_sim_type_changed()
        self.on_heater_type_changed()
    
    def create_section_card(self, parent, title):
        """Create a section card"""
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
        """Create input field"""
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
        """Callback when simulation type changes"""
        sim_type = self.sim_type_var.get()
        
        if sim_type == "single laser":
            self.wavelength_window_frame.pack_forget()
        else:
            self.wavelength_window_frame.pack(fill="x", pady=(5, 0), padx=30)
    
    def on_heater_type_changed(self):
        """Callback when heater type changes"""
        heater_type = self.heater_type_var.get()
        
        if heater_type == "constant voltage":
            self.sweep_container.pack_forget()
            self.constant_voltage_frame.pack(fill="x", pady=(5, 0), padx=30)
        else:
            self.constant_voltage_frame.pack_forget()
            self.sweep_container.pack(fill="x", pady=(5, 0), padx=30)
    
    def confirm_simulation(self):
        """Confirm and run simulation"""
        # Collect parameters
        params = {
            'sim_type': self.sim_type_var.get(),
            'heater_sim_type': self.heater_type_var.get(),
            'source_wavelength': float(self.source_wavelength_entry.get()),
            'time_window': float(self.time_window_entry.get()),
            'n_samples': int(self.n_samples_entry.get()),
            'output_dir': self.output_dir_entry.get(),
            'platform': self.selected_platform
        }
        
        # Parameters according to simulation type
        if params['sim_type'] == "single laser":
            params['start_wavelength'] = params['source_wavelength']
            params['end_wavelength'] = params['source_wavelength']
        else:
            wavelength_window = float(self.wavelength_window_entry.get())
            half_window = wavelength_window / 2
            params['start_wavelength'] = params['source_wavelength'] - half_window
            params['end_wavelength'] = params['source_wavelength'] + half_window
        
        # Parameters according to heater type
        if params['heater_sim_type'] == "constant voltage":
            params['constant_v'] = float(self.constant_v_entry.get())
            params['min_v'] = params['constant_v']
            params['max_v'] = params['constant_v']
            params['interval_v'] = 1
        else:
            params['min_v'] = float(self.min_voltage_entry.get())
            params['max_v'] = float(self.max_voltage_entry.get())
            params['interval_v'] = float(self.voltage_interval_entry.get())
        
        # Execute callback
        self.on_configuration_complete(params)
    
    def show_results(self):
        """Show Results screen"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="📊 Results\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def show_history(self):
        """Show History screen"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="📝 History\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def show_settings(self):
        """Show Settings screen"""
        self.clear_content()
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="⚙️ Settings\n\nComing soon...",
            font=ctk.CTkFont(size=24),
            text_color=TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def on_platform_changed(self):
        """Callback when platform changes"""
        new_platform = self.platform_var.get()
        print(f"\n🔄 Switching platform to: {new_platform.upper()}")
        
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
        
        print(f"✓ Platform successfully switched to {new_platform.upper()}\n")
    
    def update_cache_info(self):
        """Update cache information"""
        current_platform = self.selected_platform
        current_count = len(self.api.wgT)
        
        other_platform = "sin" if current_platform == "sipho" else "sipho"
        self.api.set_platform(other_platform)
        self.api.load_cache()
        other_count = len(self.api.wgT)
        
        self.api.set_platform(current_platform)
        self.api.load_cache()
        
        if current_platform == "sipho":
            self.cache_sipho_label.configure(text=f"SiPho: {current_count} sims", text_color=TEXT_PRIMARY)
            self.cache_sin_label.configure(text=f"SiN: {other_count} sims", text_color=TEXT_SECONDARY)
        else:
            self.cache_sin_label.configure(text=f"SiN: {current_count} sims", text_color=TEXT_PRIMARY)
            self.cache_sipho_label.configure(text=f"SiPho: {other_count} sims", text_color=TEXT_SECONDARY)
    
    def update_info_display(self):
        """Update last simulation information"""
        for widget in self.info_grid.winfo_children():
            widget.destroy()
        
        if self.last_config is None:
            no_config_label = ctk.CTkLabel(
                self.info_grid,
                text="No simulation has been run yet",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_SECONDARY
            )
            no_config_label.pack(pady=20)
            return
        
        params = self.last_config
        wavelength_nm = float(params.get('source_wavelength', 0)) * 1e9
        
        if params.get('heater_sim_type') == 'constant voltage':
            voltage_display = f"{params.get('constant_v', 'N/A')} V (constant)"
        else:
            voltage_display = f"{params.get('min_v', 'N/A')}-{params.get('max_v', 'N/A')} V"
        
        display_data = [
            ("Simulation Type", self.format_sim_type(params.get('sim_type', ''))),
            ("Wavelength", f"{wavelength_nm:.2f} nm"),
            ("Heater Mode", self.format_heater_type(params.get('heater_sim_type', ''))),
            ("Voltage", voltage_display),
            ("Time Window", params.get('time_window', 'N/A')),
            ("Samples", params.get('n_samples', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(display_data):
            row = i // 2
            col = i % 2
            self.create_info_item(self.info_grid, label, value, row, col)
    
    def format_sim_type(self, sim_type):
        """Format simulation type"""
        if sim_type == "single laser":
            return "Single Laser"
        elif sim_type == "wavelength sweep":
            return "Wavelength Sweep"
        return sim_type
    
    def format_heater_type(self, heater_type):
        """Format heater type"""
        if heater_type == "constant voltage":
            return "Constant Voltage"
        elif heater_type == "sweep":
            return "Sweep"
        return heater_type
    
    def create_info_item(self, parent, label, value, row, column):
        """Create information item"""
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
        """Callback when configuration is complete"""
        print("\n" + "="*50)
        print("🎉 Configuration completed!")
        print("="*50)
        print("\nReceived parameters:")
        for key, value in params.items():
            print(f"  • {key}: {value}")
        print("\n" + "="*50)
        
        self.last_config = params
        
        self.info_subtitle.configure(
            text=f"Last configuration: {self.format_sim_type(params.get('sim_type', ''))} | "
                 f"{self.format_heater_type(params.get('heater_sim_type', ''))} | "
                 f"Platform: {self.selected_platform.upper()}"
        )
        
        self.update_info_display()
        
        # Go back to Home
        self.navigate_to("home")
        
        # Run simulation
        from GUI.simulation_window import SimulationWindow
        SimulationWindow(
            parent=self.root,
            api=self.api,
            params=params,
            callback=self.on_simulation_complete
        )
    
    def on_simulation_complete(self, success, params=None, error=None):
        """Callback when simulation finishes"""
        if success:
            print("\n✓ Simulation completed successfully")
            self.update_cache_info()
        else:
            print(f"\n✗ Simulation failed: {error}")
        
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print("=" * 50)
    print("Starting NeuromorPIC Simulation GUI")
    print("=" * 50)
    
    app = LumericalGUI()
    app.run()


if __name__ == '__main__':
    main()