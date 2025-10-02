"""
Configuration window for simulation parameters
"""

import customtkinter as ctk
from tkinter import messagebox

# Custom theme (same as gui_main.py)
THEME_COLOR = "#E31E24"
THEME_COLOR_HOVER = "#B01419"
DARK_BG = "#1a1a1a"
CARD_BG = "#2b2b2b"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#b0b0b0"
DIVIDER_COLOR = "#3a3a3a"


class ConfigurationWindow:
    """Window to configure simulation parameters"""
    
    def __init__(self, parent, defaults, callback):
        """
        Args:
            parent: Parent window
            defaults: Dictionary with default values
            callback: Function to call when configuration is confirmed
        """
        self.defaults = defaults
        self.callback = callback
        self.params = {}
        
        # Create toplevel window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Simulation Configuration")
        self.window.geometry("900x800")
        self.window.configure(fg_color=DARK_BG)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Configure interface
        self.setup_ui()
        
    def setup_ui(self):
        """Configure all interface elements"""
        
        # ========== HEADER ==========
        header_frame = ctk.CTkFrame(self.window, fg_color=THEME_COLOR, height=70, corner_radius=0)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️  Parameter Configuration",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title_label.pack(pady=20, padx=30, anchor="w")
        
        # ========== SCROLLABLE FRAME ==========
        main_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color=DARK_BG,
            scrollbar_button_color=THEME_COLOR,
            scrollbar_button_hover_color=THEME_COLOR_HOVER
        )
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # ========== SECTION 1: LASER SIMULATION TYPE ==========
        self.laser_section = self.create_section_card(main_frame, "🔬  Laser Simulation Type")
        
        # Radio buttons for simulation type
        self.sim_type_var = ctk.StringVar(value="scatter")
        
        radio_frame = ctk.CTkFrame(self.laser_section, fg_color="transparent")
        radio_frame.pack(fill="x", pady=(10, 15))
        
        radio_scatter = ctk.CTkRadioButton(
            radio_frame,
            text="Scatter (wavelength range)",
            variable=self.sim_type_var,
            value="scatter",
            command=self.on_sim_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        radio_scatter.pack(side="left", padx=(0, 20))
        
        radio_single = ctk.CTkRadioButton(
            radio_frame,
            text="Single laser (single wavelength)",
            variable=self.sim_type_var,
            value="single laser",
            command=self.on_sim_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        radio_single.pack(side="left")
        
        # ========== SECTION 2: LASER PARAMETERS ==========
        self.wavelength_section = self.create_section_card(main_frame, "📡  Laser Parameters")
        
        # Wavelength field
        self.wavelength_field_frame = self.create_input_field(
            self.wavelength_section,
            "Central wavelength (m)",
            self.defaults.get('source_wavelength', '1.55e-6'),
            "For scatter: center of range. Single: unique wavelength"
        )
        self.wavelength_entry = self.wavelength_field_frame["entry"]
        
        # Wavelength window field
        self.wavelength_window_frame_container = self.create_input_field(
            self.wavelength_section,
            "Wavelength window (m)",
            self.defaults.get('wavelength_window', '20e-9'),
            "Total wavelength range to simulate"
        )
        self.wavelength_window_frame = self.wavelength_window_frame_container["frame"]
        self.wavelength_window_entry = self.wavelength_window_frame_container["entry"]
        
        # ========== SECTION 3: HEATER TYPE ==========
        self.heater_section = self.create_section_card(main_frame, "⚡  Heater Simulation Type")
        
        # Radio buttons for heater type
        self.heater_sim_type_var = ctk.StringVar(value="sweep")
        
        heater_radio_frame = ctk.CTkFrame(self.heater_section, fg_color="transparent")
        heater_radio_frame.pack(fill="x", pady=(10, 15))
        
        radio_constant = ctk.CTkRadioButton(
            heater_radio_frame,
            text="Constant voltage",
            variable=self.heater_sim_type_var,
            value="constant voltage",
            command=self.on_heater_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        radio_constant.pack(side="left", padx=(0, 20))
        
        radio_sweep = ctk.CTkRadioButton(
            heater_radio_frame,
            text="Voltage sweep",
            variable=self.heater_sim_type_var,
            value="sweep",
            command=self.on_heater_type_changed,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER
        )
        radio_sweep.pack(side="left")
        
        # ========== CONSTANT VOLTAGE ==========
        constant_v_container = self.create_input_field(
            self.heater_section,
            "Constant voltage (V)",
            self.defaults.get('constant_v', '10.0'),
            "Fixed voltage applied to heater"
        )
        self.constant_voltage_frame = constant_v_container["frame"]
        self.constant_v_entry = constant_v_container["entry"]
        
        # ========== VOLTAGE SWEEP ==========
        # Container for the 3 sweep fields
        self.sweep_container = ctk.CTkFrame(self.heater_section, fg_color="transparent")
        self.sweep_container.pack(fill="x", pady=(5, 0))
        
        min_v_container = self.create_input_field(
            self.sweep_container,
            "Minimum voltage (V)",
            self.defaults.get('min_v', '0.0'),
            "Minimum sweep voltage"
        )
        self.sweep_voltage_frame = self.sweep_container  # Reference to container
        self.min_voltage_entry = min_v_container["entry"]
        
        max_v_container = self.create_input_field(
            self.sweep_container,
            "Maximum voltage (V)",
            self.defaults.get('max_v', '20.0'),
            "Maximum sweep voltage"
        )
        self.max_voltage_entry = max_v_container["entry"]
        
        interval_v_container = self.create_input_field(
            self.sweep_container,
            "Voltage interval (V)",
            self.defaults.get('interval_v', '0.2'),
            "Step between voltage values"
        )
        self.voltage_interval_entry = interval_v_container["entry"]
        
        # ========== SECTION 4: TIME PARAMETERS ==========
        time_section = self.create_section_card(main_frame, "⏱️  Time Parameters")
        
        time_window_container = self.create_input_field(
            time_section,
            "Time window (s)",
            self.defaults.get('time_window', '5.12e-9'),
            "Temporal duration of simulation"
        )
        self.time_window_entry = time_window_container["entry"]
        
        n_samples_container = self.create_input_field(
            time_section,
            "Number of samples",
            self.defaults.get('n_samples', '15360'),
            "Number of points to sample"
        )
        self.n_samples_entry = n_samples_container["entry"]
        
        # ========== SECTION 5: OUTPUT ==========
        output_section = self.create_section_card(main_frame, "💾  Output Configuration")
        
        output_container = self.create_input_field(
            output_section,
            "Output directory",
            self.defaults.get('output_dir', './results'),
            "Folder to save results"
        )
        self.output_dir_entry = output_container["entry"]
        
        # Checkbox to keep INTERCONNECT open
        checkbox_frame = ctk.CTkFrame(output_section, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=25, pady=15)
        
        self.keep_interconnect_open_var = ctk.BooleanVar(value=False)
        
        self.keep_interconnect_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Keep INTERCONNECT window open after simulation",
            variable=self.keep_interconnect_open_var,
            font=ctk.CTkFont(size=13),
            fg_color=THEME_COLOR,
            hover_color=THEME_COLOR_HOVER,
            text_color=TEXT_PRIMARY
        )
        self.keep_interconnect_checkbox.pack(anchor="w")
        
        help_label = ctk.CTkLabel(
            checkbox_frame,
            text="ℹ️  Useful for debugging or manual inspection of results",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        help_label.pack(anchor="w", pady=(5, 0))
        
        # ========== ACTION BUTTONS ==========
        button_frame = ctk.CTkFrame(self.window, fg_color=CARD_BG, height=80, corner_radius=0)
        button_frame.pack(fill="x", side="bottom")
        button_frame.pack_propagate(False)
        
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True)
        
        cancel_button = ctk.CTkButton(
            button_container,
            text="✖  Cancel",
            command=self.cancel,
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
            command=self.confirm,
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
        title_label.pack(fill="x", padx=25, pady=(20, 10))
        
        # Divider line
        divider = ctk.CTkFrame(card, height=1, fg_color=DIVIDER_COLOR)
        divider.pack(fill="x", padx=25, pady=(0, 15))
        
        return card
    
    def create_input_field(self, parent, label_text, default_value, help_text):
        """Create an improved input field"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", padx=25, pady=8)
        
        # Label
        label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        label.pack(anchor="w", pady=(0, 5))
        
        # Entry
        entry = ctk.CTkEntry(
            field_frame,
            placeholder_text=str(default_value),
            height=40,
            font=ctk.CTkFont(size=13),
            border_color=DIVIDER_COLOR,
            fg_color=DARK_BG
        )
        entry.pack(fill="x", pady=(0, 5))
        entry.insert(0, str(default_value))
        
        # Help text
        help_label = ctk.CTkLabel(
            field_frame,
            text=f"ℹ️  {help_text}",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        help_label.pack(anchor="w")
        
        return {"frame": field_frame, "entry": entry}
    
    def on_sim_type_changed(self):
        """Callback when laser simulation type changes"""
        sim_type = self.sim_type_var.get()
        
        if sim_type == "scatter":
            self.wavelength_window_frame.pack(fill="x", padx=25, pady=8)
        else:
            self.wavelength_window_frame.pack_forget()
    
    def on_heater_type_changed(self):
        """Callback when heater simulation type changes"""
        heater_type = self.heater_sim_type_var.get()
        
        if heater_type == "constant voltage":
            self.constant_voltage_frame.pack(fill="x", padx=25, pady=8)
            self.sweep_voltage_frame.pack_forget()
        else:
            self.sweep_voltage_frame.pack(fill="x", pady=(5, 0))
            self.constant_voltage_frame.pack_forget()
    
    def validate_inputs(self):
        """Validate that all inputs are correct"""
        try:
            sim_type = self.sim_type_var.get()
            heater_sim_type = self.heater_sim_type_var.get()
            
            wavelength = float(self.wavelength_entry.get())
            if wavelength <= 0:
                raise ValueError("Wavelength must be positive")
            
            if sim_type == "scatter":
                wavelength_window = float(self.wavelength_window_entry.get())
                if wavelength_window <= 0:
                    raise ValueError("Wavelength window must be positive")
            
            if heater_sim_type == "constant voltage":
                constant_v = float(self.constant_v_entry.get())
                if constant_v < 0:
                    raise ValueError("Constant voltage cannot be negative")
            else:
                min_v = float(self.min_voltage_entry.get())
                max_v = float(self.max_voltage_entry.get())
                interval_v = float(self.voltage_interval_entry.get())
                
                if min_v >= max_v:
                    raise ValueError("Minimum voltage must be less than maximum")
                if interval_v <= 0:
                    raise ValueError("Voltage interval must be positive")
            
            time_window = float(self.time_window_entry.get())
            n_samples = int(self.n_samples_entry.get())
            
            if time_window <= 0:
                raise ValueError("Time window must be positive")
            if n_samples <= 0:
                raise ValueError("Number of samples must be positive")
            
            output_dir = self.output_dir_entry.get().strip()
            if not output_dir:
                raise ValueError("Must specify an output directory")
            
            self.params = {
                'sim_type': sim_type,
                'source_wavelength': wavelength,
                'heater_sim_type': heater_sim_type,
                'time_window': time_window,
                'n_samples': n_samples,
                'output_dir': output_dir,
                'keep_interconnect_open': self.keep_interconnect_open_var.get()
            }
            
            if sim_type == "scatter":
                wavelength_window = float(self.wavelength_window_entry.get())
                self.params['wavelength_window'] = wavelength_window
                
                half_window = wavelength_window / 2
                self.params['start_wavelength'] = wavelength - half_window
                self.params['end_wavelength'] = wavelength + half_window
            else:
                self.params['start_wavelength'] = wavelength
                self.params['end_wavelength'] = wavelength
            
            if heater_sim_type == "constant voltage":
                constant_v = float(self.constant_v_entry.get())
                self.params['constant_v'] = constant_v
                self.params['min_v'] = constant_v
                self.params['max_v'] = constant_v
                self.params['interval_v'] = 1
            else:
                self.params['min_v'] = float(self.min_voltage_entry.get())
                self.params['max_v'] = float(self.max_voltage_entry.get())
                self.params['interval_v'] = float(self.voltage_interval_entry.get())
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return False
    
    def confirm(self):
        """Confirm configuration"""
        if self.validate_inputs():
            print("✅ Configuration validated successfully")
            print("Parameters:", self.params)
            
            self.callback(self.params)
            self.window.destroy()
    
    def cancel(self):
        """Cancel configuration"""
        print("❌ Configuration cancelled")
        self.window.destroy()