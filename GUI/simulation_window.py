"""
Simulation execution and progress window
"""

import customtkinter as ctk
import threading
from tkinter import messagebox
import sys
from io import StringIO

# Custom theme
THEME_COLOR = "#E31E24"
THEME_COLOR_HOVER = "#B01419"
DARK_BG = "#1a1a1a"
CARD_BG = "#2b2b2b"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#b0b0b0"


class SimulationWindow:
    """Window to execute and monitor simulation"""
    
    def __init__(self, parent, api, params, callback=None):
        """
        Args:
            parent: Parent window
            api: API instance
            params: Simulation parameters
            callback: Function to call when finished
        """
        self.api = api
        self.params = params
        self.callback = callback
        self.is_running = False
        
        # Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Running Simulation")
        self.window.geometry("800x600")
        self.window.configure(fg_color=DARK_BG)
        
        # Make modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Prevent closing during simulation
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
        # Start simulation automatically
        self.start_simulation()
        
    def setup_ui(self):
        """Configure interface"""
        
        # Header
        header_frame = ctk.CTkFrame(self.window, fg_color=THEME_COLOR, height=70, corner_radius=0)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="⚙️  Running Simulation",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title.pack(pady=20, padx=30, anchor="w")
        
        # Main content
        content_frame = ctk.CTkFrame(self.window, fg_color=DARK_BG)
        content_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Current status
        self.status_label = ctk.CTkLabel(
            content_frame,
            text="Initializing simulation...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME_COLOR
        )
        self.status_label.pack(pady=(10, 20))
        
        # Indeterminate progress bar
        self.progress_bar = ctk.CTkProgressBar(
            content_frame,
            width=700,
            height=20,
            progress_color=THEME_COLOR
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        self.progress_bar.start()
        
        # Log area
        log_label = ctk.CTkLabel(
            content_frame,
            text="Execution Log:",
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
        
        # Close button (initially disabled)
        self.close_button = ctk.CTkButton(
            content_frame,
            text="Close",
            command=self.close_window,
            state="disabled",
            fg_color=TEXT_SECONDARY,
            width=150,
            height=40
        )
        self.close_button.pack(pady=10)
        
    def log(self, message):
        """Add message to log"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.window.update()
        
    def update_status(self, status):
        """Update current status"""
        self.status_label.configure(text=status)
        self.window.update()
        
    def start_simulation(self):
        """Start simulation in separate thread"""
        self.is_running = True
        self.log("="*70)
        self.log("SIMULATION START")
        self.log("="*70)
        
        # Show parameters
        self.log("\nSimulation parameters:")
        for key, value in self.params.items():
            self.log(f"  • {key}: {value}")
        self.log("\n" + "="*70)
        
        # Execute in separate thread to avoid blocking UI
        thread = threading.Thread(target=self.run_simulation)
        thread.daemon = True
        thread.start()
        
    def run_simulation(self):
        """Execute the simulation"""
        try:
            # Capture stdout to show in log
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            self.update_status("Running Lumerical simulations...")
            self.log("\n▶ Starting simulations...\n")
            
            # EXECUTE SIMULATION
            self.api.run(self.params)
            
            # Retrieve output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Show output in log
            if output:
                self.log(output)
            
            # Simulation completed successfully
            self.log("\n" + "="*70)
            self.log("✓ SIMULATION COMPLETED SUCCESSFULLY")
            self.log("="*70)
            
            self.update_status("Simulation completed successfully")
            self.progress_bar.stop()
            self.progress_bar.set(1.0)
            
            self.is_running = False
            self.close_button.configure(
                state="normal",
                fg_color=THEME_COLOR,
                hover_color=THEME_COLOR_HOVER
            )
            
            # Call callback if exists
            if self.callback:
                self.callback(success=True, params=self.params)
            
        except Exception as e:
            # Restore stdout
            sys.stdout = old_stdout
            
            # Error during simulation
            error_msg = str(e)
            self.log("\n" + "="*70)
            self.log("✗ SIMULATION ERROR")
            self.log("="*70)
            self.log(f"\nError: {error_msg}\n")
            
            self.update_status("Error during simulation")
            self.progress_bar.stop()
            self.progress_bar.set(0)
            
            self.is_running = False
            self.close_button.configure(
                state="normal",
                fg_color="darkred",
                hover_color="red"
            )
            
            messagebox.showerror(
                "Simulation Error",
                f"An error occurred during simulation:\n\n{error_msg}"
            )
            
            # Call callback with error
            if self.callback:
                self.callback(success=False, error=error_msg)
    
    def on_closing(self):
        """Handle window close attempt"""
        if self.is_running:
            response = messagebox.askyesno(
                "Simulation in progress",
                "The simulation is in progress. Do you want to cancel it and close?"
            )
            if response:
                self.is_running = False
                self.window.destroy()
        else:
            self.close_window()
    
    def close_window(self):
        """Close window"""
        self.window.destroy()