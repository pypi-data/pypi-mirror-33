import claripy

class StringTableSpec(object):
    @staticmethod
    def string_to_ast(string):
            return claripy.Concat(*(claripy.BVV(ord(c), 8) for c in string))

    def __init__(self, byte_width=8):
        self._contents = []
        self._str_len = 0
        self._byte_width = byte_width

    def append_args(self, args, add_null=True):
        for arg in args:
            self.add_string(arg)
        if add_null:
            self.add_null()

    def append_env(self, env, add_null=True):
        for k, v in env.iteritems():
            if type(k) is str:  # pylint: disable=unidiomatic-typecheck
                k = claripy.BVV(k)
            elif type(k) is unicode:  # pylint: disable=unidiomatic-typecheck
                k = claripy.BVV(k.encode('utf-8'))
            elif isinstance(k, claripy.ast.Bits):
                pass
            else:
                raise TypeError("Key in env must be either string or bitvector")

            if type(v) is str:  # pylint: disable=unidiomatic-typecheck
                v = claripy.BVV(v)
            elif type(v) is unicode:  # pylint: disable=unidiomatic-typecheck
                v = claripy.BVV(v.encode('utf-8'))
            elif isinstance(v, claripy.ast.Bits):
                pass
            else:
                raise TypeError("Value in env must be either string or bitvector")

            self.add_string(k.concat(claripy.BVV('='), v))
        if add_null:
            self.add_null()

    def add_string(self, string):
        if isinstance(string, str):
            self._contents.append(('string', self.string_to_ast(string+'\0')))
            self._str_len += len(string) + 1
        elif isinstance(string, claripy.ast.Bits):
            self._contents.append(('string', string.concat(claripy.BVV(0, self._byte_width))))
            self._str_len += len(string) // self._byte_width + 1
        else:
            raise ValueError('String must be either string literal or claripy AST')

    def add_pointer(self, pointer):
        self._contents.append(('pointer', pointer))

    def add_null(self):
        self.add_pointer(0)

    def dump(self, state, end_addr, align=0x10):
        if isinstance(end_addr, (int, long)):
            end_addr = state.se.BVV(end_addr, state.arch.bits)
        ptr_size = len(self._contents) * state.arch.bytes
        size = self._str_len + ptr_size
        start_addr = end_addr - size
        zero_fill = state.se.eval(start_addr % align)
        start_addr -= zero_fill
        start_str = start_addr + ptr_size

        ptr_i = start_addr
        str_i = start_str
        for itemtype, item in self._contents:
            if itemtype == 'string':
                state.memory.store(ptr_i, str_i, endness=state.arch.memory_endness)
                state.memory.store(str_i, item)
                ptr_i += state.arch.bytes
                str_i += len(item)//self._byte_width
            else:
                if isinstance(item, (int, long)):
                    item = state.se.BVV(item, state.arch.bits)
                state.memory.store(ptr_i, item, endness=state.arch.memory_endness)
                ptr_i += state.arch.bytes

        if zero_fill != 0:
            state.memory.store(end_addr - zero_fill, state.se.BVV(0, self._byte_width*zero_fill))

        return start_addr
