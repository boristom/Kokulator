"""
Kokulator - An Advanced Calculator with Graphing
A graphical calculator application with equation plotting built with Tkinter and Matplotlib
"""

import tkinter as tk
from tkinter import font, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import re


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Kokulator - Advanced Calculator")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Configure color scheme
        self.bg_color = "#2c3e50"
        self.btn_color = "#34495e"
        self.btn_hover = "#3d5a80"
        self.display_color = "#ecf0f1"
        self.operation_color = "#e74c3c"
        self.text_color = "#ff9800"
        
        self.root.configure(bg=self.bg_color)
        
        # Display variable
        self.display_var = tk.StringVar(value="0")
        self.current_number = ""
        self.previous_number = ""
        self.operation = None
        self.should_reset_display = False
        self.equation_history = []
        
        # Create main frame
        self.create_ui()
    
    def create_ui(self):
        """Create the main UI with calculator and graph sections"""
        # Main container with two sections
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Calculator
        left_frame = tk.Frame(main_container, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # Right side - Graph
        right_frame = tk.Frame(main_container, bg=self.bg_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create calculator in left frame
        self.create_calculator(left_frame)
        
        # Create graph area in right frame
        self.create_graph_area(right_frame)
    
    def create_calculator(self, parent):
        """Create the calculator interface"""
        calc_frame = tk.Frame(parent, bg=self.bg_color)
        calc_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(calc_frame, text="Calculator", font=("Arial", 14, "bold"), 
                         bg=self.bg_color, fg=self.display_color)
        title.pack(pady=(0, 10))
        
        # Display
        self.create_display(calc_frame)
        
        # Buttons
        self.create_buttons(calc_frame)
        
        # Equation input section
        self.create_equation_section(calc_frame)
    
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
        """Create the button grid"""
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
                self.create_button(button_frame, btn_text, row_idx, col_idx)
        
        # Configure grid weights
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)
    
    def create_button(self, parent, text, row, col):
        """Create individual button"""
        # Determine button properties
        if text == "C":
            bg_color = self.operation_color
            command = self.clear
        elif text == "DEL":
            bg_color = self.operation_color
            command = self.delete
        elif text == "=":
            bg_color = "#27ae60"
            command = self.calculate
        elif text in ["+", "-", "*", "/", "(", ")"]:
            bg_color = self.operation_color
            command = lambda t=text: self.append_number(t)
        else:
            bg_color = self.btn_color
            command = lambda t=text: self.append_number(t)
        
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 16, "bold"),
            bg=bg_color,
            fg=self.text_color,
            border=0,
            activebackground=self.btn_hover,
            activeforeground=self.text_color,
            command=command,
            cursor="hand2"
        )
        btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
    
    def create_equation_section(self, parent):
        """Create the equation input and plotting section"""
        eq_frame = tk.Frame(parent, bg=self.bg_color)
        eq_frame.pack(pady=10, padx=10, fill=tk.BOTH)
        
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
                            bg="#27ae60", fg=self.text_color, command=self.plot_equation,
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
    
    def create_graph_area(self, parent):
        """Create the graph display area"""
        # Title
        title = tk.Label(parent, text="Graph", font=("Arial", 14, "bold"),
                        bg=self.bg_color, fg=self.display_color)
        title.pack(pady=(0, 10))
        
        # Canvas for matplotlib
        self.graph_frame = tk.Frame(parent, bg=self.bg_color)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize with empty plot
        self.initialize_plot()
    
    def initialize_plot(self):
        """Initialize an empty plot"""
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        fig.patch.set_facecolor('#2c3e50')
        ax.set_facecolor('#34495e')
        ax.grid(True, color='#555', alpha=0.3)
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
            ax.set_facecolor('#34495e')
            fig = self.fig
            fig.patch.set_facecolor('#2c3e50')
            
            # Plot
            ax.plot(x, y, color=self.text_color, linewidth=2, label=f'y = {equation}')
            ax.grid(True, color='#555', alpha=0.3)
            ax.set_xlabel('x', color=self.display_color)
            ax.set_ylabel('y', color=self.display_color)
            ax.tick_params(colors=self.display_color)
            ax.legend(loc='upper left', facecolor='#34495e', edgecolor=self.display_color, 
                     labelcolor=self.display_color)
            
            # Color the spine
            for spine in ax.spines.values():
                spine.set_color(self.display_color)
            
            self.canvas.draw()
            
        except ValueError as e:
            messagebox.showerror("Value Error", f"Invalid range values: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid equation: {e}")
    
    def append_number(self, number):
        """Append number to display"""
        if self.should_reset_display:
            self.current_number = str(number)
            self.should_reset_display = False
        else:
            self.current_number += str(number)
        
        self.update_display()
    
    def set_operation(self, op):
        """Set the operation"""
        if self.current_number == "":
            return
        
        if self.previous_number != "":
            self.calculate()
        
        self.operation = op
        self.previous_number = self.current_number
        self.current_number = ""
        self.should_reset_display = True
    
    def calculate(self):
        """Perform calculation"""
        try:
            expression = self.current_number
            result = eval(expression)
            
            self.current_number = str(result)
            self.should_reset_display = True
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
        self.update_display()
    
    def delete(self):
        """Delete last digit"""
        if self.current_number:
            self.current_number = self.current_number[:-1]
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
