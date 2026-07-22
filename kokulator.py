"""
Kokulator - A Simple Calculator with GUI
A graphical calculator application built with Tkinter
"""

import tkinter as tk
from tkinter import font


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Kokulator")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Configure color scheme
        self.bg_color = "#2c3e50"
        self.btn_color = "#34495e"
        self.btn_hover = "#3d5a80"
        self.display_color = "#ecf0f1"
        self.operation_color = "#e74c3c"
        self.text_color = "#ff9800"  # Orange text for better visibility
        
        self.root.configure(bg=self.bg_color)
        
        # Display variable
        self.display_var = tk.StringVar(value="0")
        self.current_number = ""
        self.previous_number = ""
        self.operation = None
        self.should_reset_display = False
        
        # Create UI
        self.create_display()
        self.create_buttons()
    
    def create_display(self):
        """Create the display area"""
        display_frame = tk.Frame(self.root, bg=self.bg_color)
        display_frame.pack(pady=20, padx=20, fill=tk.BOTH)
        
        # Display label
        display = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=("Arial", 36, "bold"),
            bg=self.display_color,
            fg=self.bg_color,
            anchor="e",
            padx=20,
            pady=20
        )
        display.pack(fill=tk.BOTH, expand=True)
    
    def create_buttons(self):
        """Create the button grid"""
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Button layout
        buttons = [
            ["C", "DEL", "/", "*"],
            ["7", "8", "9", "-"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "="],
            ["0", ".", "", ""]
        ]
        
        for row_idx, row in enumerate(buttons):
            for col_idx, btn_text in enumerate(row):
                if btn_text == "":
                    # Empty space
                    empty_label = tk.Label(button_frame, bg=self.bg_color)
                    empty_label.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")
                else:
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
        elif text in ["+", "-", "*", "/"]:
            bg_color = self.operation_color
            command = lambda: self.set_operation(text)
        else:
            bg_color = self.btn_color
            command = lambda: self.append_number(text)
        
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 18, "bold"),
            bg=bg_color,
            fg=self.text_color,
            border=0,
            activebackground=self.btn_hover,
            activeforeground=self.text_color,
            command=command,
            cursor="hand2"
        )
        btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    
    def append_number(self, number):
        """Append number to display"""
        if self.should_reset_display:
            self.current_number = number
            self.should_reset_display = False
        else:
            # Prevent multiple decimal points
            if number == "." and "." in self.current_number:
                return
            
            # Prevent leading zeros
            if self.current_number == "0" and number != ".":
                self.current_number = number
            else:
                self.current_number += number
        
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
        if self.operation is None or self.current_number == "":
            return
        
        try:
            prev = float(self.previous_number)
            current = float(self.current_number)
            
            if self.operation == "+":
                result = prev + current
            elif self.operation == "-":
                result = prev - current
            elif self.operation == "*":
                result = prev * current
            elif self.operation == "/":
                if current == 0:
                    self.display_var.set("Error: Division by zero")
                    self.current_number = ""
                    self.operation = None
                    self.previous_number = ""
                    return
                result = prev / current
            
            # Format result
            if result == int(result):
                self.current_number = str(int(result))
            else:
                self.current_number = str(round(result, 10))
            
            self.operation = None
            self.previous_number = ""
            self.should_reset_display = True
            self.update_display()
        
        except Exception as e:
            self.display_var.set("Error")
            self.current_number = ""
            self.operation = None
            self.previous_number = ""
    
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
