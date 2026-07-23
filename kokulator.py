"""
Kokulator - An Advanced Scientific Calculator with Graphing
A graphical calculator application with equation plotting built with Tkinter and Matplotlib
"""

import tkinter as tk
from tkinter import font, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Kokulator - Advanced Scientific Calculator")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Solarized Dark color scheme
        self.bg_color = "#002b36"          # base03
        self.surface_color = "#073642"     # base02
        self.btn_color = "#eee8d5"         # base2
        self.btn_hover = "#fdf6e3"         # base3
        self.display_color = "#eee8d5"     # base2
        self.operation_color = "#cb4b16"   # orange
        self.equals_color = "#859900"      # green
        self.text_color = "#fdf6e3"        # base3
        self.key_text_color = "#002b36"    # dark text on light keys
        self.scientific_color = "#6c71c4"  # violet
        self.mode_color = "#2aa198"        # cyan
        self.grid_color = "#586e75"        # base01
        
        self.root.configure(bg=self.bg_color)
        
        # Display variable
        self.display_var = tk.StringVar(value="0")
        self.current_number = ""
        self.previous_number = ""
        self.operation = None
        self.should_reset_display = False
        self.scientific_mode = False
        self.angle_mode = "deg"  # deg or rad
        self.view_mode = "standard"  # standard or graphical
        self.last_was_calculation = False  # Track if last action was a calculation
        
        # Bind keyboard events
        self.root.bind('<Key>', self.on_key_press)
        
        # Create main frame
        self.create_ui()
    
    def on_key_press(self, event):
        """Handle keyboard input"""
        char = event.char
        
        # Handle number keys and decimal point
        if char.isdigit() or char == '.':
            self.append_number(char)
        # Handle operators
        elif char in ['+', '-', '*', '/']:
            self.append_number(char)
        # Handle parentheses
        elif char == '(':
            self.append_number('(')
        elif char == ')':
            self.append_number(')')
        # Handle Enter/Return for calculation
        elif event.keysym == 'Return':
            self.calculate()
        # Handle Backspace for deletion
        elif event.keysym == 'BackSpace':
            self.delete()
        # Handle Escape for clear
        elif event.keysym == 'Escape':
            self.clear()
    
    def create_ui(self):
        """Create the main UI with mode toggle"""
        # Top bar with mode toggle
        top_bar = tk.Frame(self.root, bg=self.bg_color)
        top_bar.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        title = tk.Label(top_bar, text="Kokulator", font=("Arial", 16, "bold"),
                        bg=self.bg_color, fg=self.display_color)
        title.pack(side=tk.LEFT)
        
        self.view_mode_btn = tk.Button(top_bar, text="📊 Graphical Mode", font=("Arial", 10, "bold"),
                                       bg=self.mode_color, fg=self.text_color,
                                       command=self.toggle_view_mode, cursor="hand2")
        self.view_mode_btn.pack(side=tk.RIGHT)
        
        # Main container with two sections
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Calculator
        self.left_frame = tk.Frame(self.main_container, bg=self.bg_color)
        
        # Right side - Graph
        self.right_frame = tk.Frame(self.main_container, bg=self.bg_color)
        
        # Create calculator in left frame
        self.create_calculator(self.left_frame)
        
        # Create graph area in right frame
        self.create_graph_area(self.right_frame)
        
        # Initial layout - standard mode (show calculator)
        self.update_view_mode()
    
    def toggle_view_mode(self):
        """Toggle between standard and graphical modes"""
        if self.view_mode == "standard":
            self.view_mode = "graphical"
            self.view_mode_btn.config(text="🧮 Standard Mode")
        else:
            self.view_mode = "standard"
            self.view_mode_btn.config(text="📊 Graphical Mode")
        
        self.update_view_mode()
    
    def update_view_mode(self):
        """Update the layout based on current view mode"""
        # Clear previous layout
        for widget in self.main_container.winfo_children():
            widget.pack_forget()
        
        if self.view_mode == "standard":
            # Show only calculator with full width
            self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0))
            self.right_frame.pack_forget()
        else:  # graphical
            # Show only graph
            self.left_frame.pack_forget()
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 0))
    
    def create_calculator(self, parent):
        """Create the calculator interface"""
        calc_frame = tk.Frame(parent, bg=self.bg_color)
        calc_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and mode toggle
        title_frame = tk.Frame(calc_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(title_frame, text="Calculator", font=("Arial", 14, "bold"), 
                         bg=self.bg_color, fg=self.display_color)
        title.pack(side=tk.LEFT)
        
        self.mode_btn = tk.Button(title_frame, text="Scientific Mode", font=("Arial", 9, "bold"),
                                  bg=self.scientific_color, fg=self.text_color, 
                                  command=self.toggle_scientific_mode, cursor="hand2")
        self.mode_btn.pack(side=tk.RIGHT)
        
        # Display
        self.create_display(calc_frame)
        
        # Basic buttons
        self.create_buttons(calc_frame)
        
        # Scientific buttons (initially hidden)
        self.scientific_frame = tk.Frame(calc_frame, bg=self.bg_color)
        self.create_scientific_buttons(self.scientific_frame)
    
    def toggle_scientific_mode(self):
        """Toggle scientific mode on/off"""
        self.scientific_mode = not self.scientific_mode
        if self.scientific_mode:
            self.scientific_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
            self.mode_btn.config(relief=tk.SUNKEN, bg="#d33682")
        else:
            self.scientific_frame.pack_forget()
            self.mode_btn.config(relief=tk.RAISED, bg=self.scientific_color)
    
    def create_display(self, parent):
        """Create the display area"""
        display_frame = tk.Frame(parent, bg=self.bg_color)
        display_frame.pack(pady=10, padx=10, fill=tk.BOTH)
        
        # Display label
        display = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=("Arial", 28, "bold"),
            bg=self.display_color,
            fg=self.bg_color,
            anchor="e",
            padx=10,
            pady=15
        )
        display.pack(fill=tk.BOTH, expand=True)
    
    def create_buttons(self, parent):
        """Create the basic button grid"""
        button_frame = tk.Frame(parent, bg=self.bg_color)
        button_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Button layout
        buttons = [
            ["C", "DEL", "/", "*"],
            ["7", "8", "9", "-"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "="],
            ["0", ".", "(", ")"]
        ]
        
        for row_idx, row in enumerate(buttons):
            for col_idx, btn_text in enumerate(row):
                self.create_button(button_frame, btn_text, row_idx, col_idx, self.btn_color)
        
        # Configure grid weights
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)
    
    def create_scientific_buttons(self, parent):
        """Create scientific function buttons"""
        sci_frame = tk.Frame(parent, bg=self.bg_color)
        sci_frame.pack(fill=tk.BOTH, expand=True)
        
        # Trigonometric functions
        trig_label = tk.Label(sci_frame, text="Trigonometric", font=("Arial", 10, "bold"),
                             bg=self.bg_color, fg=self.display_color)
        trig_label.pack(pady=(5, 0))
        
        trig_frame = tk.Frame(sci_frame, bg=self.bg_color)
        trig_frame.pack(fill=tk.X, padx=5, pady=5)
        
        trig_buttons = [
            ("sin", lambda: self.apply_function("sin")),
            ("cos", lambda: self.apply_function("cos")),
            ("tan", lambda: self.apply_function("tan")),
            ("asin", lambda: self.apply_function("asin")),
            ("acos", lambda: self.apply_function("acos")),
            ("atan", lambda: self.apply_function("atan")),
        ]
        
        for i, (text, cmd) in enumerate(trig_buttons):
            btn = tk.Button(trig_frame, text=text, font=("Arial", 9, "bold"),
                           bg=self.btn_color, fg=self.key_text_color,
                           command=cmd, cursor="hand2", width=8)
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
        
        for i in range(6):
            trig_frame.grid_columnconfigure(i, weight=1)
        
        # Logarithmic functions
        log_label = tk.Label(sci_frame, text="Logarithmic", font=("Arial", 10, "bold"),
                            bg=self.bg_color, fg=self.display_color)
        log_label.pack(pady=(5, 0))
        
        log_frame = tk.Frame(sci_frame, bg=self.bg_color)
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        log_buttons = [
            ("log₁₀", lambda: self.apply_function("log10")),
            ("ln", lambda: self.apply_function("log")),
            ("e^x", lambda: self.apply_function("exp")),
            ("2^x", lambda: self.append_number("2**")),
        ]
        
        for i, (text, cmd) in enumerate(log_buttons):
            btn = tk.Button(log_frame, text=text, font=("Arial", 9, "bold"),
                           bg=self.btn_color, fg=self.key_text_color,
                           command=cmd, cursor="hand2", width=8)
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
        
        for i in range(4):
            log_frame.grid_columnconfigure(i, weight=1)
        
        # Power and root functions
        power_label = tk.Label(sci_frame, text="Powers & Roots", font=("Arial", 10, "bold"),
                              bg=self.bg_color, fg=self.display_color)
        power_label.pack(pady=(5, 0))
        
        power_frame = tk.Frame(sci_frame, bg=self.bg_color)
        power_frame.pack(fill=tk.X, padx=5, pady=5)
        
        power_buttons = [
            ("x²", lambda: self.append_number("**2")),
            ("x³", lambda: self.append_number("**3")),
            ("√x", lambda: self.apply_function("sqrt")),
            ("ʸ√x", lambda: self.append_number("**(1/")),
            ("1/x", lambda: self.apply_function("reciprocal")),
        ]
        
        for i, (text, cmd) in enumerate(power_buttons):
            btn = tk.Button(power_frame, text=text, font=("Arial", 9, "bold"),
                           bg=self.btn_color, fg=self.key_text_color,
                           command=cmd, cursor="hand2", width=8)
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
        
        for i in range(5):
            power_frame.grid_columnconfigure(i, weight=1)
        
        # Other functions
        other_label = tk.Label(sci_frame, text="Other Functions", font=("Arial", 10, "bold"),
                              bg=self.bg_color, fg=self.display_color)
        other_label.pack(pady=(5, 0))
        
        other_frame = tk.Frame(sci_frame, bg=self.bg_color)
        other_frame.pack(fill=tk.X, padx=5, pady=5)
        
        other_buttons = [
            ("n!", lambda: self.apply_function("factorial")),
            ("π", lambda: self.append_number(str(math.pi))),
            ("e", lambda: self.append_number(str(math.e))),
            ("°→rad", lambda: self.convert_angle()),
            ("±", lambda: self.toggle_sign()),
        ]
        
        for i, (text, cmd) in enumerate(other_buttons):
            btn = tk.Button(other_frame, text=text, font=("Arial", 9, "bold"),
                           bg=self.btn_color, fg=self.key_text_color,
                           command=cmd, cursor="hand2", width=8)
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
        
        for i in range(5):
            other_frame.grid_columnconfigure(i, weight=1)
    
    def create_button(self, parent, text, row, col, default_color):
        """Create individual button"""
        # Determine button properties
        if text == "C":
            bg_color = self.operation_color
            command = self.clear
        elif text == "DEL":
            bg_color = self.operation_color
            command = self.delete
        elif text == "=":
            bg_color = self.equals_color
            command = self.calculate
        elif text in ["+", "-", "*", "/", "(", ")"]:
            bg_color = self.operation_color
            command = lambda t=text: self.append_number(t)
        else:
            bg_color = default_color
            command = lambda t=text: self.append_number(t)
        
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 16, "bold"),
            bg=bg_color,
            fg=self.key_text_color,
            border=0,
            activebackground=self.btn_hover,
            activeforeground=self.key_text_color,
            command=command,
            cursor="hand2"
        )
        btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
    
    def create_graph_area(self, parent):
        """Create the graph display area with equation input"""
        graph_container = tk.Frame(parent, bg=self.bg_color)
        graph_container.pack(fill=tk.BOTH, expand=True)
        
        # Equation input section at the top
        eq_frame = tk.Frame(graph_container, bg=self.bg_color)
        eq_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Title
        title = tk.Label(eq_frame, text="Equation Plotter", font=("Arial", 12, "bold"),
                         bg=self.bg_color, fg=self.display_color)
        title.pack()
        
        # Input frame
        input_frame = tk.Frame(eq_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="y = ", font=("Arial", 10), 
                bg=self.bg_color, fg=self.display_color).pack(side=tk.LEFT, padx=5)
        
        self.equation_var = tk.StringVar(value="x**2")
        self.equation_entry = tk.Entry(input_frame, textvariable=self.equation_var, 
                                       font=("Arial", 10), width=20)
        self.equation_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        plot_btn = tk.Button(input_frame, text="Plot", font=("Arial", 10, "bold"),
                            bg=self.equals_color, fg=self.text_color, command=self.plot_equation,
                            cursor="hand2")
        plot_btn.pack(side=tk.LEFT, padx=5)
        
        # Range frame
        range_frame = tk.Frame(eq_frame, bg=self.bg_color)
        range_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(range_frame, text="X range:", font=("Arial", 9),
                bg=self.bg_color, fg=self.display_color).pack(side=tk.LEFT, padx=5)
        
        self.x_min_var = tk.StringVar(value="-10")
        self.x_max_var = tk.StringVar(value="10")
        
        tk.Entry(range_frame, textvariable=self.x_min_var, font=("Arial", 9), width=6).pack(side=tk.LEFT, padx=2)
        tk.Label(range_frame, text="to", font=("Arial", 9),
                bg=self.bg_color, fg=self.display_color).pack(side=tk.LEFT, padx=2)
        tk.Entry(range_frame, textvariable=self.x_max_var, font=("Arial", 9), width=6).pack(side=tk.LEFT, padx=2)
        
        # Graph title
        graph_title = tk.Label(graph_container, text="Graph", font=("Arial", 14, "bold"),
                              bg=self.bg_color, fg=self.display_color)
        graph_title.pack(pady=(10, 5))
        
        # Canvas for matplotlib
        self.graph_frame = tk.Frame(graph_container, bg=self.bg_color)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize with empty plot
        self.initialize_plot()
    
    def initialize_plot(self):
        """Initialize an empty plot"""
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        fig.patch.set_facecolor(self.bg_color)
        ax.set_facecolor(self.surface_color)
        ax.grid(True, color=self.grid_color, alpha=0.45)
        ax.text(0.5, 0.5, 'Enter an equation and click Plot', 
                ha='center', va='center', transform=ax.transAxes,
                color=self.display_color, fontsize=12)
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas = canvas
        self.fig = fig
    
    def plot_equation(self):
        """Plot the entered equation"""
        try:
            equation = self.equation_var.get()
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            
            # Validate equation
            if not equation:
                messagebox.showerror("Error", "Please enter an equation")
                return
            
            # Generate x values
            x = np.linspace(x_min, x_max, 1000)
            
            # Evaluate equation (allow common math functions)
            safe_dict = {
                'x': x,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'asin': np.arcsin,
                'acos': np.arccos,
                'atan': np.arctan,
                'sqrt': np.sqrt,
                'exp': np.exp,
                'log': np.log,
                'log10': np.log10,
                'abs': np.abs,
                'pi': np.pi,
                'e': np.e,
            }
            
            y = eval(equation, {"__builtins__": {}}, safe_dict)
            
            # Clear previous plot
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            ax.set_facecolor(self.surface_color)
            fig = self.fig
            fig.patch.set_facecolor(self.bg_color)
            
            # Plot
            ax.plot(x, y, color=self.text_color, linewidth=2, label=f'y = {equation}')
            ax.grid(True, color=self.grid_color, alpha=0.45)
            ax.set_xlabel('x', color=self.display_color)
            ax.set_ylabel('y', color=self.display_color)
            ax.tick_params(colors=self.display_color)
            ax.legend(loc='upper left', facecolor=self.surface_color, edgecolor=self.display_color, 
                     labelcolor=self.display_color)
            
            # Color the spine
            for spine in ax.spines.values():
                spine.set_color(self.display_color)
            
            self.canvas.draw()
            
        except ValueError as e:
            messagebox.showerror("Value Error", f"Invalid range values: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid equation: {e}")
    
    def apply_function(self, func_name):
        """Apply a scientific function to the current number"""
        try:
            if self.current_number == "":
                messagebox.showwarning("Warning", "Please enter a number first")
                return
            
            value = float(self.current_number)
            result = None
            
            if func_name == "sin":
                val = math.radians(value) if self.angle_mode == "deg" else value
                result = math.sin(val)
            elif func_name == "cos":
                val = math.radians(value) if self.angle_mode == "deg" else value
                result = math.cos(val)
            elif func_name == "tan":
                val = math.radians(value) if self.angle_mode == "deg" else value
                result = math.tan(val)
            elif func_name == "asin":
                result = math.degrees(math.asin(value)) if self.angle_mode == "deg" else math.asin(value)
            elif func_name == "acos":
                result = math.degrees(math.acos(value)) if self.angle_mode == "deg" else math.acos(value)
            elif func_name == "atan":
                result = math.degrees(math.atan(value)) if self.angle_mode == "deg" else math.atan(value)
            elif func_name == "sqrt":
                result = math.sqrt(value)
            elif func_name == "log10":
                result = math.log10(value)
            elif func_name == "log":
                result = math.log(value)
            elif func_name == "exp":
                result = math.exp(value)
            elif func_name == "factorial":
                result = math.factorial(int(value))
            elif func_name == "reciprocal":
                result = 1 / value
            
            if result is not None:
                self.current_number = str(result)
                self.should_reset_display = True
                self.last_was_calculation = True
                self.update_display()
        
        except Exception as e:
            messagebox.showerror("Error", f"Invalid operation: {e}")
    
    def convert_angle(self):
        """Convert between degrees and radians"""
        try:
            if self.current_number == "":
                messagebox.showwarning("Warning", "Please enter a number first")
                return
            
            value = float(self.current_number)
            if self.angle_mode == "deg":
                result = math.radians(value)
                self.angle_mode = "rad"
            else:
                result = math.degrees(value)
                self.angle_mode = "deg"
            
            self.current_number = str(result)
            self.should_reset_display = True
            self.last_was_calculation = True
            self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid operation: {e}")
    
    def toggle_sign(self):
        """Toggle the sign of the current number"""
        if self.current_number == "":
            return
        
        try:
            value = float(self.current_number)
            self.current_number = str(-value)
            self.update_display()
        except:
            pass
    
    def append_number(self, number):
        """Append number to display"""
        # If we just finished a calculation and user presses a number/operator
        if self.should_reset_display:
            # If it's an operator, keep the result and add the operator
            if number in ['+', '-', '*', '/']:
                self.should_reset_display = False
            else:
                # If it's a number, start fresh
                self.current_number = str(number)
                self.should_reset_display = False
                self.update_display()
                return
        
        self.current_number += str(number)
        self.last_was_calculation = False
        self.update_display()
    
    def calculate(self):
        """Perform calculation"""
        try:
            if self.current_number == "":
                return
            
            expression = self.current_number
            result = eval(expression)
            
            self.current_number = str(result)
            self.should_reset_display = True
            self.last_was_calculation = True
            self.update_display()
            
        except Exception as e:
            self.display_var.set("Error")
            self.current_number = ""
    
    def clear(self):
        """Clear all"""
        self.current_number = ""
        self.previous_number = ""
        self.operation = None
        self.should_reset_display = False
        self.last_was_calculation = False
        self.update_display()
    
    def delete(self):
        """Delete last digit"""
        if self.current_number:
            self.current_number = self.current_number[:-1]
            self.should_reset_display = False
            self.last_was_calculation = False
            self.update_display()
    
    def update_display(self):
        """Update display"""
        if self.current_number == "":
            self.display_var.set("0")
        else:
            self.display_var.set(self.current_number)


def main():
    """Main function to run the calculator"""
    root = tk.Tk()
    calculator = Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
