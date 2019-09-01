import argparse
from sys import stdout, stdin




# 微信公众号：Python高效编程
class Machine:
    def __init__(self, code):
        self.code = code
        self.stack = list()
        self.addr = 0


    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    @property
    def top(self):
        return self.stack[-1]


    def dispatch(self, opcode):
        dispatch_map = {
        "%":        self.mod,
        "*":        self.mul,
        "+":        self.plus,
        "-":        self.minus,
        "/":        self.div,
        "==":       self.eq,
        "cast_int": self.cast_int,
        "cast_str": self.cast_str,
        "drop":     self.drop,
        "dup":      self.dup,
        "exit":     self.exit,
        "if":       self.if_stmt,
        "jmp":      self.jmp,
        "over":     self.over,
        "print":    self.print,
        "println":  self.println,
        "read":     self.read,
        "stack":    self.dump_stack,
        "swap":     self.swap,
        }
        if opcode in dispatch_map:
            dispatch_map[opcode]()
        elif isinstance(opcode, int):
            self.push(opcode)
        elif isinstance(opcode, str)\
                and opcode[0] == opcode[-1] == '"':
            self.push(opcode[1:-1])




    def run(self):
        while self.addr < len(self.code):
            opcode = self.code[self.addr]
            self.addr += 1
            self.dispatch(opcode)


    def mod(self):
        v2 = self.pop()
        v1 = self.pop()
        self.push(v1 % v2)

    def mul(self):
        v2 = self.pop()
        v1 = self.pop()
        self.push(v1 * v2)

    def plus(self):
        v2 = self.pop()
        v1 = self.pop()
        self.push(v1 + v2)

    def minus(self):
        v2 = self.pop()
        v1 = self.pop()
        self.push(v1 - v2)

    def div(self):
        v2 = self.pop()
        v1 = self.pop()
        self.push(v1 - v2)

    def eq(self):
        v2 = self.pop()
        v1 = self.pop()
        self.push(v1 == v2)

    def cast_int(self):
        v = self.pop()
        self.push(int(v))

    def cast_str(self):
        v = self.pop()
        self.push(str(v))

    def drop(self):
        self.pop()

    def dup(self):
        v = self.pop()
        self.push(v)
        self.push(v)

    def exit(self):
        exit(0)

    def if_stmt(self):
        false_clause = self.pop()
        true_clause = self.pop()
        cond = self.pop()
        if cond:
            self.push(true_clause)
        else:
            self.push(false_clause)

    def over(self):
        v2 = self.pop()
        v1 = self.pop()
        self.push(v1)
        self.push(v2)
        self.push(v1)


    def print(self):
        v = self.pop()
        stdout.write(f"{v}")

    def println(self):
        v = self.pop()
        stdout.write(f"{v}\n")

    def read(self):
        text = input()
        self.push(text)

    def dump_stack(self):
        for v in reversed(self.stack):
            stdout.write(f"{v}\n")

    def swap(self):
        v2 = self.pop()
        v1 = self.pop()
        self.push(v2)
        self.push(v1)

    def jmp(self):
        addr = self.pop()
        if 0 <= addr < len(self.code):
            self.addr = addr
        else:
            raise RuntimeError("addr must be integer")




def constants_fold(code):
    for idx, (a, b, op) in enumerate(zip(code, code[1:], code[2:])):
        if isinstance(a, int) and isinstance(b, int)\
            and op in {"+", "-", "*", "/"}:
            m = Machine([a, b, op])
            m.run()
            code[idx:idx+3] = [m.top]
            stdout.write(f"常量折叠:{a} {b} {op} = {m.top}\n")
    return code



def welcome():
    stdout.write("Welcome to vm 0.1\nauthor: Python高效编程\n\n")

def read(prompt):
    stdout.write(prompt)
    stdout.flush()
    return stdin.readline()

def parse_word(word):
    try:
        return int(word)
    except ValueError:
        try:
            return float(word)
        except ValueError:
            return word

def tokenize(text):
    for word in text.split():
        yield parse_word(word)


def repl(prompt="VM>> "):
    welcome()
    while True:
        try:
            text = read(prompt)
            code = list(tokenize(text))
            code = constants_fold(code)
            Machine(code).run()
        except (RuntimeError, IndexError):
            stdout.write("1表达式不合法\n")
        except KeyboardInterrupt:
            stdout.write("请使用exit退出程序\n")


def test():
    print("测试 1\n")
    Machine([521, 1314,"+", 6, "*","println"]).run()
    print("*"*30)
    print("测试 2\n")
    # 无限循环
    Machine([
        '"请输入一个数: "', "print", "read", "cast_int",
        '"数值 "', "print", "dup", "print", '" 是"', "print",
        2, "%", 0, "==", '"偶数。"', '"奇数。"', "if", "println",
        0, "jmp"
    ]).run()
    print("*"*30)

def parse_args():
    parser = argparse.ArgumentParser(
            usage="test or repl",
            description="启动测试或者交互式界面")
    parser.add_argument("-t", "--test", action="store_false",default=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    if args.test:
        repl()
    else:
        test()

