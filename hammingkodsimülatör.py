import tkinter as tk
from tkinter import messagebox

# Hamming code functions
def calculate_parity_bits(data_bits):
    n = len(data_bits)
    r = 0
    while (2**r) < (n + r + 1):
        r += 1
    return r

def generate_hamming_code(data_bits):
    n = len(data_bits)
    r = calculate_parity_bits(data_bits)
    hamming_code = [0] * (n + r)
    
    j = 0
    k = 1
    for i in range(1, n + r + 1):
        if i == 2**j:
            j += 1
        else:
            hamming_code[i - 1] = data_bits[k - 1]
            k += 1

    for i in range(r):
        parity_pos = 2**i
        parity = 0
        for j in range(1, n + r + 1):
            if j & parity_pos and j != parity_pos:
                parity ^= hamming_code[j - 1]
        hamming_code[parity_pos - 1] = parity

    return hamming_code

def detect_and_correct_error(hamming_code):
    n = len(hamming_code)
    r = calculate_parity_bits([0] * (n - len(bin(n)[2:]) + 1))
    
    error_pos = 0
    for i in range(r):
        parity_pos = 2**i
        parity = 0
        for j in range(1, n + 1):
            if j & parity_pos:
                parity ^= hamming_code[j - 1]
        if parity != 0:
            error_pos += parity_pos
    
    if error_pos != 0:
        hamming_code[error_pos - 1] ^= 1
        return error_pos, hamming_code
    return None, hamming_code

def extract_data_bits(hamming_code):
    n = len(hamming_code)
    r = calculate_parity_bits([0] * (n - len(bin(n)[2:]) + 1))
    data_bits = []

    j = 0
    for i in range(1, n + 1):
        if i != 2**j:
            data_bits.append(hamming_code[i - 1])
        else:
            j += 1

    return data_bits

# Memory class
class Memory:
    def __init__(self):
        self.memory = {}

    def write(self, address, data):
        self.memory[address] = data

    def read(self, address):
        return self.memory.get(address, None)

    def inject_error(self, address, bit_position):
        if address in self.memory:
            data = self.memory[address]
            data[bit_position] ^= 1
            self.memory[address] = data
        else:
            print("Address not found!")

memory = Memory()

# Tkinter UI class
class HammingSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hamming Code Simulator")
        self.geometry("600x500")

        self.data_label = tk.Label(self, text="Data (4, 8, 16 bits):")
        self.data_label.pack()
        self.data_entry = tk.Entry(self)
        self.data_entry.pack()

        self.generate_button = tk.Button(self, text="Generate Hamming Code", command=self.generate_hamming_code)
        self.generate_button.pack()

        self.hamming_code_label = tk.Label(self, text="Hamming Code will be shown here.")
        self.hamming_code_label.pack()

        self.write_button = tk.Button(self, text="Write to Memory", command=self.write_to_memory)
        self.write_button.pack()

        self.read_button = tk.Button(self, text="Read from Memory", command=self.read_from_memory)
        self.read_button.pack()

        self.inject_error_label = tk.Label(self, text="Inject Error Bit Position (0-based):")
        self.inject_error_label.pack()
        self.inject_error_entry = tk.Entry(self)
        self.inject_error_entry.pack()
        self.inject_error_button = tk.Button(self, text="Inject Error", command=self.inject_error)
        self.inject_error_button.pack()

        self.output_label = tk.Label(self, text="")
        self.output_label.pack()

    def generate_hamming_code(self):
        data = list(map(int, self.data_entry.get().split()))
        hamming_code = generate_hamming_code(data)
        self.hamming_code_label.config(text=f"Generated Hamming Code: {hamming_code}")

    def write_to_memory(self):
        data = list(map(int, self.data_entry.get().split()))
        address = "0x01"
        hamming_code = generate_hamming_code(data)
        memory.write(address, hamming_code)
        self.output_label.config(text=f"Data written to address {address}: {hamming_code}")

    def read_from_memory(self):
        address = "0x01"
        hamming_code = memory.read(address)
        if hamming_code:
            error_pos, corrected_code = detect_and_correct_error(hamming_code)
            if error_pos is not None:
                self.output_label.config(text=f"Data read from address {address} with error at position {error_pos}. Corrected data: {corrected_code}")
            else:
                self.output_label.config(text=f"Data read from address {address} without errors: {hamming_code}")
        else:
            messagebox.showwarning("Warning", "Data not found!")

    def inject_error(self):
        address = "0x01"
        try:
            bit_position = int(self.inject_error_entry.get())
            memory.inject_error(address, bit_position)
            self.output_label.config(text=f"Error injected at position {bit_position}")
            hamming_code = memory.read(address)
            if hamming_code:
                error_pos, _ = detect_and_correct_error(hamming_code)
                if error_pos == bit_position + 1:
                    self.output_label.config(text=f"Error injected at position {bit_position}. Error correctly detected at position {error_pos - 1}.")
                else:
                    self.output_label.config(text=f"Error injected at position {bit_position}. Error detected at a different position {error_pos - 1}.")
        except ValueError:
            messagebox.showerror("Error", "Invalid bit position")

if __name__ == "__main__":
    app = HammingSimulator()
    app.mainloop()
