from collections import OrderedDict
class WhitespaceInt(int):
    """Helper class to manage integers in Whitespace."""
    def __new__(cls, num):
        return super().__new__(cls, num)

    def __str__(self):
        return super().__str__()

    @classmethod
    def from_whitespace(cls, code):
        """Converts the Whitespace representation of a number to an integer."""
        if len(code) == 1:
            num = 0
            return cls(num)
        keys = [' ', '\t']
        sign = 2 * (1 - keys.index(code[0])) - 1
        binary = ''.join([str(keys.index(x)) for x in code[1:]])
        num = int(binary, 2) * sign
        return cls(num)


class Interpreter:
    """The main interpreter for the program handles our state and responds to input."""

    """Instruction Modification Parameters (IMPs)
    [space]: Stack Manipulation
    [tab][space]: Arithmetic
    [tab][tab]: Heap Access
    [tab][line-feed]: Input/Output
    [line-feed]: Flow Control
    """
    IMP = OrderedDict({
    ' ': 'Stack',
    '\t ': 'Arithmetic',
    '\t\t': 'Heap',
    '\t\n': 'IO',
    '\n': 'FlowControl'
    })

    def __init__(self, code, inp=''):
        self.stack = []
        self.heap = {}
        self.pos = 0
        self.code = code
        self.code_length = len(code)
        self.inp = inp
        self.input = list(inp)
        self.output = ''
        self.loading = True

        self.instruction = ''
        self.command = ''
        self.labels = {}
        self.return_positions = []

    @property
    def stack_size(self):
        """Alias for the size of the stack."""
        return len(self.stack)

    def clean(self, s):
        """Returns a readable string representation of whitespace."""
        return s.replace(' ', 's').replace('\t', 't').replace('\n', 'n')

    def num_parameter(self):
        """Retrieves the next number in the sequence.
        Format of a number:
        sign - binary - terminator
        sign: [space] + / [tab] -
        binary: [space] 0 / [tab] 1
        terminator: \n
        """
        code = self.code
        index = code.find('\n', self.pos)
        # Only including a terminal causes an error
        if index == self.pos:
            raise SyntaxError('Number must include more than just the terminal.')
        item = WhitespaceInt.from_whitespace(code[self.pos:index])
        return index, item

    def label_parameter(self):
        """Sets a label in the sequence if possible.
        Format of a label:
        name - terminator
        *name: any number of [space] and [tab]
        terminator: \n
        *Must be unique.
        """
        code = self.code
        index = code.find('\n', self.pos) + 1
        # Empty string is a valid label
        name = code[self.pos:index]
        return index, name

    def get_command(self, imp):
        """Gets the token for an IMP category."""
        pos = self.pos
        code = self.code
        token = code[pos:pos + 1]
        if token not in imp:
            token = code[pos:pos + 2]
        # Check if our token is a valid IMP
        for key, value in imp.items():
            if key == token:
                self.command = value
                self.pos += len(key)
                break
        else:
            raise KeyError(f'No IMP found for token: {token}')

    def run(self):
        """Main loop of the program goes through each instruction."""
        if self.code_length == 0:
            raise SyntaxError('Unclean termination of program')
        if self.loading:
            print(f'Code: {self.clean(self.code)}')
            print(f'Input: {self.input}')
        while self.pos < self.code_length:
            pos = self.pos
            code = self.code
            token = code[pos:pos + 1]
            if token not in self.IMP:
                token = code[pos:pos + 2]
            # Check if our token is a valid IMP
            for key, value in self.IMP.items():
                if key == token:
                    self.instruction = value
                    break
            else:
                print(self.clean(code))
                raise SyntaxError(f'Unknown instruction ' + self.instruction)

            if not self.loading:
                print(f'({self.pos}) Instruction: {self.instruction} - Stack: {self.stack} - Heap: {self.heap}')
            self.pos += len(key)
            getattr(self, self.instruction).parse(self)
        if self.loading:
            print(f'Finished marking labels. Starting program sequence...')
            self.pos = 0
            self.loading = False
            self.run()
        elif self.return_positions and self.pos != float('inf'):
            raise SyntaxError('Subroutine does not properly exit or return')
        elif self.pos == self.code_length:
            raise RuntimeError('Unclean termination')
            #raise Exception('Unclean termination')

    class Stack:
        """Handles stack manipulation instructions."""

        """Instructions
        [space] (number): Push n onto the stack.
        [tab][space] (number): Duplicate the nth value from the top of the stack.
        [tab][line-feed] (number): Discard the top n values below the top of the stack from the stack.
            (For n<0 or n>=stack.length, remove everything but the top value.)
        [line-feed][space]: Duplicate the top value on the stack.
        [line-feed][tab]: Swap the top two value on the stack.
        [line-feed][line-feed]: Discard the top value on the stack.
        """
        STACK_IMP = OrderedDict({
        ' ': 'push_num',
        '\t ': 'duplicate_nth',
        '\t\n': 'discard_n',
        '\n ': 'duplicate_top',
        '\n\t': 'swap',
        '\n\n': 'discard_top'
        })

        def parse(self):
            """Parses the next stack IMP."""
            Stack = self.Stack
            self.get_command(Stack.STACK_IMP)
            if self.command == 'push_num':
                index, item = self.num_parameter()
                if not self.loading:
                    print(f'\tCommand: {self.command}({item})')
                    Stack.push_num(self, item)
                self.pos = index + 1
            elif self.command == 'duplicate_nth':
                index, item = self.num_parameter()
                if not self.loading:
                    print(f'\tCommand: {self.command}({item})')
                    Stack.duplicate_nth(self, item)
                self.pos = index + 1
            elif self.command == 'discard_n':
                index, item = self.num_parameter()
                if not self.loading:
                    print(f'\tCommand: {self.command}({item})')
                    Stack.discard_n(self, item)
                self.pos = index + 1
            elif self.command == 'duplicate_top':
                if not self.loading:
                    print(f'\tCommand: {self.command}')
                    Stack.duplicate_nth(self, 0)
            elif self.command == 'swap':
                if not self.loading:
                    print(f'\tCommand: {self.command}')
                    Stack.swap(self)
            elif self.command == 'discard_top':
                if not self.loading:
                    print(f'\tCommand: {self.command}')
                    Stack.discard_top(self)

        def push_num(self, item):
            self.stack.append(item)

        def duplicate_nth(self, n):
            if n > self.stack_size - 1:
                raise ValueError('Cannot duplicate - Value exceeds stack size limit')
            elif n < 0:
                raise IndexError('Cannot duplicate negative stack index')
            item = self.stack[-n - 1]
            self.stack.append(item)

        def discard_n(self, n):
            if n >= self.stack_size or n < 0:
                n = self.stack_size - 1
            top = self.stack.pop()
            for _ in range(n):
                self.stack.pop()
            self.stack.append(top)

        def discard_top(self):
            self.stack.pop()

        def swap(self):
            a, b = self.stack.pop(), self.stack.pop()
            self.stack.append(a)
            self.stack.append(b)

    class IO:
        """Handles input/output operations."""

        """Instructions
        [space][space]: Pop a value off the stack and output it as a character.
        [space][tab]: Pop a value off the stack and output it as a number.
        [tab][space]: Read a character from input, a, Pop a value off the stack, b, then store the ASCII value of a at heap address b.
        [tab][tab]: Read a number from input, a, Pop a value off the stack, b, then store a at heap address b.
        """
        IO_IMP = {
        '  ': 'output_char',
        ' \t': 'output_num',
        '\t ': 'input_char',
        '\t\t': 'input_num'
        }

        def parse(self):
            """Parses the next I/O IMP."""
            IO = self.IO
            self.get_command(IO.IO_IMP)
            if self.loading:
                return
            print(f'\tCommand: {self.command}')
            if self.command == 'output_char':
                IO.output_char(self)
            elif self.command == 'output_num':
                IO.output_num(self)
            elif self.command == 'input_char':
                IO.input_char(self)
            elif self.command == 'input_num':
                IO.input_num(self)

        def output_char(self):
            char = chr(self.stack.pop())
            self.output += char
            print(f'>>> {char}')

        def output_num(self):
            num = int(self.stack.pop())
            self.output += str(num)
            print(f'>>> {num}')

        def input_char(self):
            a = self.input.pop(0)
            b = self.stack.pop()
            self.heap[b] = ord(a)

        def input_num(self):
            b = self.stack.pop()
            index = self.input.index('\n')
            num = ''.join(self.input[:index])
            self.input = self.input[index + 1:]
            self.heap[b] = int(num)

    class FlowControl:
        """Handles flow control operations."""

        """Instructions
        [space][space] (label): Mark a location in the program with label n.
        [space][tab] (label): Call a subroutine with the location specified by label n.
        [space][line-feed] (label): Jump unconditionally to the position specified by label n.
        [tab][space] (label): Pop a value off the stack and jump to the label specified by n if the value is zero.
        [tab][tab] (label): Pop a value off the stack and jump to the label specified by n if the value is less than zero.
        [tab][line-feed]: Exit a subroutine and return control to the location from which the subroutine was called.
        [line-feed][line-feed]: Exit the program.
        """
        FLOW_IMP = {
        '  ': 'mark_label',
        ' \t': 'call_subroutine',
        ' \n': 'jump',
        '\t ': 'jump_zero',
        '\t\t': 'jump_lt_zero',
        '\t\n': 'exit_subroutine',
        '\n\n': 'exit'
        }

        def parse(self):
            """Parses the next flow control IMP."""
            Flow = self.FlowControl
            self.get_command(Flow.FLOW_IMP)
            if self.command == 'exit':
                if not self.loading:
                    print(f'\tCommand: {self.command}')
                    Flow.exit(self)
            elif self.command == 'mark_label':
                index, label = self.label_parameter()
                if self.loading:
                    print(f'\tCommand: {self.command}({self.clean(label)})')
                    Flow.mark_label(self, label)
                else:
                    print(f'\tIgnoring label marker')
                self.pos = index
            elif self.command == 'jump':
                index, label = self.label_parameter()
                if not self.loading:
                    print(f'\tCommand: {self.command}({self.clean(label)})')
                    Flow.jump(self, label)
                else:
                    self.pos = index
            elif self.command == 'jump_zero':
                index, label = self.label_parameter()
                if not self.loading:
                    print(f'\tCommand: {self.command}({self.clean(label)})')
                    num = self.stack.pop()
                    if num == 0:
                        Flow.jump(self, label)
                    else:
                        self.pos = index
                else:
                    self.pos = index
            elif self.command == 'jump_lt_zero':
                index, label = self.label_parameter()
                if not self.loading:
                    print(f'\tCommand: {self.command}({self.clean(label)})')
                    num = self.stack.pop()
                    if num < 0:
                        Flow.jump(self, label)
                    else:
                        self.pos = index
                else:
                    self.pos = index
            elif self.command == 'exit_subroutine':
                if not self.loading:
                    print(f'\tCommand: {self.command}')
                    Flow.exit_subroutine(self)
            elif self.command == 'call_subroutine':
                index, label = self.label_parameter()
                self.pos = index
                if not self.loading:
                    print(f'\tCommand: {self.command}({self.clean(label)})')
                    Flow.call_subroutine(self, label)

        def exit(self):
            print('Program terminated.')
            self.pos = float('inf')

        def mark_label(self, label):
            if label in self.labels:
                raise ValueError('Label already exists')
            self.labels[label] = self.pos + len(label)
            print(f'\t{self.labels}')

        def jump(self, label):
            self.pos = self.labels[label]

        def exit_subroutine(self):
            if self.return_positions:
                self.pos = self.return_positions.pop()
            else:
                raise SyntaxError('Return outside of subroutine')

        def call_subroutine(self, label):
            self.return_positions.append(self.pos)
            self.pos = self.labels[label]

    class Arithmetic:
        """Handles arithmetic operations on the stack."""

        """Instructions
        [space][space]: Pop a and b, then push b+a.
        [space][tab]: Pop a and b, then push b-a.
        [space][line-feed]: Pop a and b, then push b*a.
        [tab][space]: Pop a and b, then push b/a*. If a is zero, throw an error.
        *Note that the result is defined as the floor of the quotient.
        [tab][tab]: Pop a and b, then push b%a*. If a is zero, throw an error.
        *Note that the result is defined as the remainder after division and sign (+/-) of the divisor (a).
        """
        ARITHMETIC_IMP = {
        '  ': 'add',
        ' \t': 'sub',
        ' \n': 'mul',
        '\t ': 'floordiv',
        '\t\t': 'mod'
        }

        def parse(self):
            """Parses the next arithmetic IMP."""
            Arithmetic = self.Arithmetic
            self.get_command(Arithmetic.ARITHMETIC_IMP)
            if self.loading:
                return
            if self.command == 'add':
                print(f'\tCommand: {self.command}')
                Arithmetic.add(self)
            elif self.command == 'sub':
                print(f'\tCommand: {self.command}')
                Arithmetic.sub(self)
            elif self.command == 'mul':
                print(f'\tCommand: {self.command}')
                Arithmetic.mul(self)
            elif self.command == 'floordiv':
                print(f'\tCommand: {self.command}')
                Arithmetic.floordiv(self)
            elif self.command == 'mod':
                print(f'\tCommand: {self.command}')
                Arithmetic.mod(self)

        def add(self):
            a, b = self.stack.pop(), self.stack.pop()
            c = b + a
            self.stack.append(c)

        def sub(self):
            a, b = self.stack.pop(), self.stack.pop()
            c = b - a
            self.stack.append(c)

        def mul(self):
            a, b = self.stack.pop(), self.stack.pop()
            c = b * a
            self.stack.append(c)

        def floordiv(self):
            a, b = self.stack.pop(), self.stack.pop()
            if a == 0:
                raise ZeroDivisionError('Cannot divide by zero')
            c = b // a
            self.stack.append(c)

        def mod(self):
            a, b = self.stack.pop(), self.stack.pop()
            if a == 0:
                raise ZeroDivisionError('Cannot divide by zero')
            c = b % a
            self.stack.append(c)

    class Heap:
        """Handles operations on the heap."""

        """Instructions
        [space]: Pop a and b, then store a at heap address b.
        [tab]: Pop a and then push the value at heap address a onto the stack.
        """
        HEAP_IMP = {
        ' ': 'store',
        '\t': 'push'
        }

        def parse(self):
            """Parses the next heap IMP."""
            Heap = self.Heap
            self.get_command(Heap.HEAP_IMP)
            if self.loading:
                return
            if self.command == 'store':
                print(f'\tCommand: {self.command}')
                Heap.store(self)
            elif self.command == 'push':
                print(f'\tCommand: {self.command}')
                Heap.push(self)

        def store(self):
            a, b = self.stack.pop(), self.stack.pop()
            self.heap[b] = a

        def push(self):
            a = self.stack.pop()
            self.stack.append(self.heap[a])

def uncomment(s):
    """Removes extranneous characters from the code input."""
    return ''.join(char for char in s if char in ' \t\n')

def whitespace(code, inp = ''):
    code = uncomment(code)
    interpreter = Interpreter(code, inp)
    interpreter.run()
    print(f'Output: {interpreter.output}')
    return interpreter.output

def to_whitespace(s):
    s = ''.join([char.lower() for char in s if char in 'STNstn'])
    return s.replace('s',' ').replace('t','\t').replace('n','\n')

# Sample Code - Fibonacci Sequence
fibonacci_whitespace = """Ask the user how	many  	   
fibonacci	numbers
they want from the sequence 		 				
and	print
that many one number per line.			 			
	
     	     
	
     		 		 	
	
     		    	
	
     		 			 
	
     				  	
	
     						
	
     	     
	
     	 
	
		    
   	
 
 	
 	   	 	 
	
  
  	
 
    	
 
			 	      	
			 
	 
 	
 	   	 	 
	
     	 
			   	
	  	 
    	 
 
			 
			 

 
	

  	 


"""
whitespace(fibonacci_whitespace)