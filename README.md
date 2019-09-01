### 超级简单的虚拟机（Python 实现）

我们这次实现的简单虚拟机，和计算机的 cpu 有点类似。无非就是取指令，执行指令之类的操作。

常见的虚拟机通常分为两类，一种是栈式虚拟机，另一种是寄存器虚拟机。比如说 CPython, Jvm 就是基于栈的虚拟机，而 lua 则是基于寄存器的虚拟机。

我们这次实现的“玩具”虚拟机，就是一种基于栈的虚拟机。

虚拟机有三个重要属性，code 代表要执行的指令列表，stack 用于保存临时变量，而 addr 代表当前指令的地址。

```python
# Python高效编程
class Machine:
    def __init__(self, code):
        self.code = code
        self.stack = list()
        self.addr = 0
```

原理其实很简单，我们通过不断获取当前指令地址，从指令列表中获取指令和数据，如果是数字或者字符串，就压入栈中；如果是指令，就执行相应函数。

为了少些几个字符，我们向 Machine 类中添加几个方法：

```python
def push(self, value):
    self.stack.append(value)

def pop(self):
    return self.stack.pop()

@property
def top(self):
    return self.stack[-1]
```

我们通过 dispatch 方法，来判断当前从指令列表中取得的片段是指令还是数据：

```python
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
```

dispatch_map 就对应我们在 Machine 类中实现的方法。

比如说 plus 方法和 jmp 方法：

```python
def plus(self):
    v2 = self.pop()
    v1 = self.pop()
    self.push(v1 + v2)
    
    
def jmp(self):
    addr = self.pop()
    if 0 <= addr < len(self.code):
        self.addr = addr
    else:
        raise RuntimeError("addr must be integer")
```

其余方法也很简单，大家可以直接查看源代码。

好了，在加入一个 run 函数，我们就可以解释代码了。只要当前地址小于指令长度，就不断取指令，执行指令。

```python
def run(self):
    while self.addr < len(self.code):
        opcode = self.code[self.addr]
        self.addr += 1
        self.dispatch(opcode)
```

我们创建 Machine 类，并执行 run 函数：

```python
>>> from vm import Machine
>>> Machine([521, 1314,"+", 6, "*","println"]).run()
11010
```

我们还可以给虚拟机加一个交互式界面：

```python
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
```

在读取用户输入字符串之后，对字符串处理：

```python
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
```

