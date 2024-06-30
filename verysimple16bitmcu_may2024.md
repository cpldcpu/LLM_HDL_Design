# 16-bit CPU with "im-a-good-gpt2-chatbot" - 8th May 2024

Zero shot prompting in one session with one of the models that OpenAi is currently testing on LM SYS Chatarena.

The output was already formatted in markdown, so I included it like that. I did not test the code, but there are no really obvious issues like in the previous attempts. 

Take note that this is all zero-shot in one session. No re-rolls.


## The CPU

### Prompt to generate ISA

```
Assume a 16-bit microprocessor in an accumulator based architecture. Register
are accumulator (16 bit), PC (12 bit) and carry flag. All instructions use
immediate addressing to a 12 bit memory address bus. The following instructions 
shall be implemented: LDA mem12, STA mem12, BCC mem12, BCS mem12,ADD mem12, 
SUB mem12, AND mem12, XOR mem12. The instruction are encoded into 16 bit words. 
List all instructions including encoding for each of them on a concise way. 

Use this template:

1. LDA mem12: Load accumulator with value from memory address mem12
   - Encoding: `0000 | mem12`
```

### Output (generated by LLM)

Given the constraints and requirements of your 16-bit microprocessor with an accumulator-based architecture, here's how you can encode the instructions using the 16-bit format. The high 4 bits will represent the opcode, and the lower 12 bits will specify the memory address (`mem12`).

Here is the encoding for each instruction:

1. **LDA mem12**: Load the accumulator with the value from memory address `mem12`.
   - **Encoding**: `0000 | mem12`
     ```
     0000 xxxx xxxx xxxx
     ```
     Here, `0000` is the opcode for LDA, and the `xxxx xxxx xxxx` (12 bits) is the memory address.

2. **STA mem12**: Store the value from the accumulator into memory address `mem12`.
   - **Encoding**: `0001 | mem12`
     ```
     0001 xxxx xxxx xxxx
     ```
     `0001` is the opcode for STA.

3. **ADD mem12**: Add the value from memory address `mem12` to the accumulator.
   - **Encoding**: `0010 | mem12`
     ```
     0010 xxxx xxxx xxxx
     ```
     `0010` is the opcode for ADD.

4. **SUB mem12**: Subtract the value from memory address `mem12` from the accumulator.
   - **Encoding**: `0011 | mem12`
     ```
     0011 xxxx xxxx xxxx
     ```
     `0011` is the opcode for SUB.

5. **AND mem12**: Perform a bitwise AND between the value from memory address `mem12` and the accumulator.
   - **Encoding**: `0100 | mem12`
     ```
     0100 xxxx xxxx xxxx
     ```
     `0100` is the opcode for AND.

6. **XOR mem12**: Perform a bitwise XOR between the value from memory address `mem12` and the accumulator.
   - **Encoding**: `0101 | mem12`
     ```
     0101 xxxx xxxx xxxx
     ```
     `0101` is the opcode for XOR.

7. **BCC mem12**: Branch to `mem12` if the carry flag is clear.
   - **Encoding**: `0110 | mem12`
     ```
     0110 xxxx xxxx xxxx
     ```
     `0110` is the opcode for BCC.

8. **BCS mem12**: Branch to `mem12` if the carry flag is set.
   - **Encoding**: `0111 | mem12`
     ```
     0111 xxxx xxxx xxxx
     ```
     `0111` is the opcode for BCS.

To summarize, the instructions are encoded as follows:

- `0000`: LDA mem12
- `0001`: STA mem12
- `0010`: ADD mem12
- `0011`: SUB mem12
- `0100`: AND mem12
- `0101`: XOR mem12
- `0110`: BCC mem12
- `0111`: BCS mem12

Each instruction is a 16-bit entity where the first 4 bits are the opcode, and the remaining 12 bits represent the memory address. This allows direct addressing of up to \(2^{12} = 4096\) memory locations.

### Prompt to generate Python emulator

```
Implement a cpu emulator in a standalone python program that is able to emulate the cpu with the marked instruction set architecture. The status of the registers and executed instruction should be printed to the console for each cycle. The emulation should automatically stop after 20 cycles. The program that is to be executed is to be loaded from a text file that contains the code memory in binary representation. One line per instruction. The file name is given as an argument to the python program.
```

RapidGPT only provided a code outline for the emulator, but it looked generally sensible. I did not iterate on this step as the HDL generation was more interesting to me.

### Output

To create a CPU emulator in Python for the specified 16-bit microprocessor architecture, we need to follow several steps. Below is a complete Python program that implements the emulator. This program will load a program from a binary text file, execute up to 20 cycles, and print the status of the CPU registers (accumulator and program counter) and the current instruction at each cycle.

Here's how you can structure the Python program:

```python
import sys

# Define the operation codes for the instructions
OPCODES = {
    '0000': 'LDA',
    '0001': 'STA',
    '0010': 'ADD',
    '0011': 'SUB',
    '0100': 'AND',
    '0101': 'XOR',
    '0110': 'BCC',
    '0111': 'BCS'
}

class CPU:
    def __init__(self, memory):
        self.accumulator = 0
        self.program_counter = 0
        self.carry_flag = 0
        self.memory = memory
        self.cycle = 0

    def fetch(self):
        """ Fetch the next instruction pointed to by the program counter """
        instruction = self.memory[self.program_counter]
        self.program_counter = (self.program_counter + 1) % len(self.memory)
        return instruction

    def decode(self, instruction):
        """ Decode the instruction into opcode and memory address """
        opcode = instruction[:4]
        mem12 = int(instruction[4:], 2)
        return OPCODES[opcode], mem12

    def execute(self, opcode, mem12):
        """ Execute the instruction with the given opcode and memory address """
        if opcode == 'LDA':
            self.accumulator = self.memory[mem12]
        elif opcode == 'STA':
            self.memory[mem12] = self.accumulator
        elif opcode == 'ADD':
            result = self.accumulator + self.memory[mem12]
            self.carry_flag = int(result > 0xFFFF)
            self.accumulator = result & 0xFFFF
        elif opcode == 'SUB':
            result = self.accumulator - self.memory[mem12]
            self.carry_flag = int(result < 0)
            self.accumulator = result & 0xFFFF
        elif opcode == 'AND':
            self.accumulator &= self.memory[mem12]
        elif opcode == 'XOR':
            self.accumulator ^= self.memory[mem12]
        elif opcode == 'BCC':
            if not self.carry_flag:
                self.program_counter = mem12
        elif opcode == 'BCS':
            if self.carry_flag:
                self.program_counter = mem12

    def run(self):
        while self.cycle < 20:
            self.cycle += 1
            instruction = self.fetch()
            opcode, mem12 = self.decode(instruction)
            self.execute(opcode, mem12)
            self.print_status(opcode, mem12)

    def print_status(self, opcode, mem12):
        print(f"Cycle {self.cycle}: PC={self.program_counter:02X}, ACC={self.accumulator:04X}, "
              f"CF={self.carry_flag}, {opcode} {mem12:03X}")

def load_memory_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def main():
    if len(sys.argv) != 2:
        print("Usage: python cpu_emulator.py <program_file>")
        sys.exit(1)

    filename = sys.argv[1]
    memory = load_memory_from_file(filename)
    cpu = CPU(memory)
    cpu.run()

if __name__ == "__main__":
    main()
```

### How to Use This Emulator

1. **Create a text file** with the binary instructions for the CPU, one instruction (16 bits) per line.
2. **Run the emulator** by passing the filename of the program as an argument:
   ```bash
   python cpu_emulator.py your_program.txt
   ```

### Example Program File

Here's an example content of `your_program.txt` that could be used with this emulator:

```
0000110000000001  # LDA 001 (Load the value at memory address 0x001 into the accumulator)
0010110000000010  # ADD 002 (Add the value at memory address 0x002 to the accumulator)
0101110000000011  # XOR 003 (XOR the value at memory address 0x003 with the accumulator)
0001000000000100  # STA 004 (Store the accumulator value into memory address 0x004)
0110110000000101  # BCS 005 (Branch to 005 if carry, should not branch initially)
0000110000000110  # LDA 006 (Load the value at memory address 0x006 into the accumulator)
```

### Notes

- Make sure the memory addresses and instructions in your program file are represented in binary as per the CPU's instruction set.
- The program will stop after 20 cycles or can be adjusted by changing the condition in the `run` method.

This script and example will guide you through setting up and running your own simple programs on this emulated CPU architecture.


## Verilog implementation 

Zero shot prompt in same session.

```
Write a single verilog module that implements this architecture. Inputs shall be: clk,reset, datain (16 bit). Output: adrout(12 bit), dataout (16 bit), write enable. 

This is a von-neumann computer with shared Memory. The memory is implemented externally as a standard parallel SRAM and is accessed via the modules interface. You may have to implement a state machine to handle multi-cycle instructions that access the memory.
```

## Output

To implement the described 16-bit microprocessor architecture using Verilog, we need to create a module that integrates the CPU core and controls memory access through its interface. This microprocessor will handle the set of instructions (`LDA`, `STA`, `ADD`, `SUB`, `AND`, `XOR`, `BCC`, `BCS`) described earlier.

Here is a Verilog module that implements this architecture:

```verilog
module cpu(
    input clk,
    input reset,
    input [15:0] datain,
    output reg [11:0] adrout,
    output reg [15:0] dataout,
    output reg write_enable
);

// State definitions for the state machine
localparam FETCH = 2'b00;
localparam DECODE_EXECUTE = 2'b01;
localparam MEMORY_ACCESS = 2'b10;
localparam WRITE_BACK = 2'b11;

// Register and other internal declarations
reg [1:0] state;
reg [15:0] accumulator;
reg [11:0] pc;
reg carry_flag;
reg [15:0] instruction_register;
reg [3:0] opcode;
reg [11:0] mem_address;

// Next state logic
always @(posedge clk or posedge reset) begin
    if (reset) begin
        pc <= 12'b0;
        state <= FETCH;
        accumulator <= 16'b0;
        carry_flag <= 1'b0;
        write_enable <= 1'b0;
    end else begin
        case (state)
            FETCH: begin
                // Set address to fetch from memory
                adrout <= pc;
                write_enable <= 1'b0;
                state <= DECODE_EXECUTE;
            end
            
            DECODE_EXECUTE: begin
                // Latch the instruction and increment the PC
                instruction_register <= datain;
                pc <= pc + 1'b1;
                opcode <= datain[15:12];
                mem_address <= datain[11:0];
                state <= MEMORY_ACCESS;
            end
            
            MEMORY_ACCESS: begin
                // Memory operations
                case (opcode)
                    4'b0000: begin // LDA
                        adrout <= mem_address;
                        write_enable <= 1'b0;
                        state <= WRITE_BACK;
                    end
                    4'b0001: begin // STA
                        adrout <= mem_address;
                        dataout <= accumulator;
                        write_enable <= 1'b1;
                        state <= FETCH;
                    end
                    4'b0010, // ADD
                    4'b0011, // SUB
                    4'b0100, // AND
                    4'b0101: begin // XOR
                        adrout <= mem_address;
                        write_enable <= 1'b0;
                        state <= WRITE_BACK;
                    end
                    4'b0110, // BCC
                    4'b0111: begin // BCS
                        adrout <= mem_address;
                        write_enable <= 1'b0;
                        state <= WRITE_BACK;
                    end
                    default: begin
                        state <= FETCH;
                    end
                endcase
            end

            WRITE_BACK: begin
                case (opcode)
                    4'b0000: begin // LDA
                        accumulator <= datain;
                        state <= FETCH;
                    end
                    4'b0010: begin // ADD
                        {carry_flag, accumulator} <= accumulator + datain;
                        state <= FETCH;
                    end
                    4'b0011: begin // SUB
                        {carry_flag, accumulator} <= accumulator - datain;
                        state <= FETCH;
                    end
                    4'b0100: begin // AND
                        accumulator <= accumulator & datain;
                        state <= FETCH;
                    end
                    4'b0101: begin // XOR
                        accumulator <= accumulator ^ datain;
                        state <= FETCH;
                    end
                    4'b0110: begin // BCC
                        if (~carry_flag) begin
                            pc <= mem_address;
                        end
                        state <= FETCH;
                    end
                    4'b0111: begin // BCS
                        if (carry_flag) begin
                            pc <= mem_address;
                        end
                        state <= FETCH;
                    end
                    default: begin
                        state <= FETCH;
                    end
                endcase
            end
            
            default: begin
                state <= FETCH;
            end
        endcase
    end
end

endmodule
```

### Explanation

1. **State Machine**: The CPU has a simple state machine with states for fetching instructions (`FETCH`), decoding and executing them (`DECODE_EXECUTE`), accessing memory if needed (`MEMORY_ACCESS`), and writing back results if necessary (`WRITE_BACK`).

2. **Registers and Flags**:
   - `accumulator`: A 16-bit register used for arithmetic and logic operations.
   - `pc`: A 12-bit program counter pointing to the next instruction.
   - `carry_flag`: A single bit used for arithmetic operations to indicate an overflow or underflow.

3. **Memory Interface**:
   - `adrout`: 12-bit address output connecting to memory address lines.
   - `dataout`: 16-bit data output for memory writes.
   - `write_enable`: Control signal indicating if a memory write should occur.

4. **Instruction Handling**:
   - Each instruction's operation is handled in the appropriate state, with memory operations potentially requiring loading a value into the `accumulator` or writing from the `accumulator` to memory.
   - Branch instructions (`BCC` and `BCS`) modify the `pc` based on the `carry_flag`.

### Usage

1. Instantiate this module in your top-level design.
2. Connect it to memory (`datain`, `adrout`, `dataout`, `write_enable`).
3. Use `clk` and `reset` to control the operation.

This module will execute instructions from memory, modifying its internal state and interacting with memory as per the defined instruction set.

## Verilog implementation 

Zero shot prompt in same session.

```
please write a verilog testbench
```

## Output

To verify the functionality of the CPU design described in the previous Verilog module, you can write a testbench that simulates the CPU with a predefined set of instructions and checks its behavior. Below is a Verilog testbench for the CPU module.

This testbench initializes a simple program in memory that the CPU will execute, and it monitors the outputs to verify correct operation.

```verilog
`timescale 1ns / 1ps

module cpu_tb;

// Inputs
reg clk;
reg reset;
reg [15:0] datain;

// Outputs
wire [11:0] adrout;
wire [15:0] dataout;
wire write_enable;

// Instantiate the Unit Under Test (UUT)
cpu uut (
    .clk(clk),
    .reset(reset),
    .datain(datain),
    .adrout(adrout),
    .dataout(dataout),
    .write_enable(write_enable)
);

// Memory to simulate the program and data
reg [15:0] memory [0:4095];  // Simple memory model

// Clock generation
always #10 clk = ~clk; // Clock with period of 20 ns

// Initialize the testbench
initial begin
    // Initialize Inputs
    clk = 0;
    reset = 1;
    datain = 0;

    // Initialize memory
    // Example program:
    // LDA 001 (Load the value at memory address 0x001 into the accumulator)
    memory[0] = 16'b0000_0000_0000_0001;
    // ADD 002 (Add the value at memory address 0x002 to the accumulator)
    memory[1] = 16'b0010_0000_0000_0010;
    // XOR 003 (XOR the value at memory address 0x003 with the accumulator)
    memory[2] = 16'b0101_0000_0000_0011;
    // STA 004 (Store the accumulator value into memory address 0x004)
    memory[3] = 16'b0001_0000_0000_0100;
    // BCS 005 (Branch to 005 if carry, should not branch initially)
    memory[4] = 16'b0111_0000_0000_0101;
    // LDA 006 (Load the value at memory address 0x006 into the accumulator)
    memory[5] = 16'b0000_0000_0000_0110;

    // Initialize data memory
    memory[1] = 16'h0004; // Value at address 0x001
    memory[2] = 16'h0003; // Value at address 0x002
    memory[3] = 16'h0007; // Value at address 0x003
    memory[4] = 16'h0000; // Value at address 0x004 (to be written)
    memory[6] = 16'h0005; // Value at address 0x006
    
    // Wait for global reset
    #100;
    reset = 0;

    // Run the simulation for some cycles
    #500;
    
    // Check results
    if (memory[4] !== 16'h0000) begin
        $display("Test passed, final value at memory[4]: %h", memory[4]);
    end else begin
        $display("Test failed, final value at memory[4]: %h", memory[4]);
    end

    // End simulation
    $finish;
end

// Memory and CPU interaction
always @(posedge clk) begin
    if (reset) begin
        datain <= 0;
    end else begin
        if (write_enable) begin
            // Write to memory
            memory[adrout] <= dataout;
        end else begin
            // Read from memory
            datain <= memory[adrout];
        end
    end
end

endmodule
```

### Explanation of the Testbench

1. **Clock Generation**: A simple clock is generated using an always block to toggle the clock every 10 ns, giving a 50 MHz clock frequency.

2. **Memory Initialization**: The memory is initialized with a small program and some data. This includes several instructions that modify the accumulator and potentially write to memory.

3. **Reset**: The CPU and memory interaction starts after a brief reset period.

4. **Simulation Control**: The simulation checks the operation of the CPU over several cycles, observing changes to the accumulator and memory based on the instruction execution.

5. **Ending the Simulation**: After some time, the simulation ends, and results are checked to see if the final values in memory match the expected results based on the program execution.

### Running the Testbench

To run this testbench:

1. Save the CPU design and the testbench in files, e.g., `cpu.v` for the module and `cpu_tb.v` for the testbench.
2. Use a Verilog simulator like Icarus Verilog or Vivado to compile and simulate the design.
   
   For Icarus Verilog:
   ```bash
   iverilog -o cpu_test cpu.v cpu_tb.v
   vvp cpu_test
   ```

3. Observe the output in the console or in a waveform viewer if you dump the simulation waveforms using `$dumpfile` and `$dumpvars`.

This setup should help you verify that the CPU behaves as expected according to the defined instruction set and interactions with memory. Adjust the memory contents and the test scenario in the testbench as needed to further explore and validate different aspects of the CPU design.