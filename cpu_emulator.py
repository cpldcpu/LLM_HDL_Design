# Python CPU emulator for VerySimple16bit_Oct2023 instruction set architecture

import sys

# Define CPU class
class CPU:
    def __init__(self):
        self.registers = [0] * 16
        self.memory = [0] * 65536
        self.pc = 0
        self.carry_flag = 0

    def load_program(self, filename):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                self.memory[i] = int(line.strip(), 2)

    def execute_instruction(self, instruction):
        opcode = instruction >> 12
        operand = instruction & 0xfff

        if opcode == 0:
            self.registers[0] = self.memory[operand]
        elif opcode == 1:
            self.memory[operand] = self.registers[0]
        elif opcode == 2:
            if self.carry_flag == 0:
                self.pc = operand
        elif opcode == 3:
            if self.carry_flag == 1:
                self.pc = operand
        elif opcode == 4:
            self.registers[0] += self.memory[operand]
            if self.registers[0] > 0xffff:
                self.registers[0] &= 0xffff
                self.carry_flag = 1
            else:
                self.carry_flag = 0
        elif opcode == 5:
            self.registers[0] -= self.memory[operand]
            if self.registers[0] < 0:
                self.registers[0] &= 0xffff
                self.carry_flag = 1
            else:
                self.carry_flag = 0
        elif opcode == 6:
            self.registers[0] &= self.memory[operand]
        elif opcode == 7:
            self.registers[0] ^= self.memory[operand]

    def run(self, cycles=20):
        for i in range(cycles):
            instruction = self.memory[self.pc]
            self.execute_instruction(instruction)
            print(f"Cycle {i+1}: PC={self.pc}, Reg={self.registers}, Carry={self.carry_flag}, Instruction={instruction:04x}")
            self.pc += 1

# Main program
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python cpu_emulator.py <filename>")
        sys.exit(1)

    cpu = CPU()
    cpu.load_program(sys.argv[1])
    cpu.run()