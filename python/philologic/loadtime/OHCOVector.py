#!/usr/bin/env python3


import sys
from json import dumps

### CompoundStack is the class to use for all parsers.


class ParallelRecord(object):
    """ParallelRecord tracks objects that are parallel to a primary record stack.  Used by CompoundStack."""

    def __init__(self, type, name, id):
        self.type = type
        self.name = name
        self.id = id
        self.attrib = {}

    def __str__(self):
        print_id = [self.id[0], 0, 0, 0, 0, 0, 0, 0, self.id[1]]
        return "%s\t%s\t%s\t%s" % (self.type, self.name, " ".join(str(i) for i in print_id), dumps(self.attrib))

    def __getitem__(self, n):
        return self.attrib[n]

    def __setitem__(self, n, val):
        self.attrib[n] = val

    def get(self, key, default):
        if key in self.attrib:
            return self.attrib[key]
        else:
            return default

    def getid(self):
        return [self.id[0], 0, 0, 0, 0, 0, 0, 0, self.id[1]]


class CompoundRecord(object):
    """CompoundRecord is the base Record type for the CompoundStack."""

    def __init__(self, type, name, id):
        self.type = type
        self.name = name
        self.id = id  # Maybe page hack goes in here?  yeah, I think so.
        self.attrib = {}

    def __str__(self):
        print_id = self.id
        try:
            parent_index = self.id.index(0) - 1
        except ValueError:
            parent_index = len(self.id) - 1
        parent_id = [x if i < parent_index else 0 for i, x in enumerate(self.id)]
        print_id.append(self.attrib.get("start_byte", 0))
        print_id.append(self.attrib.get("page", 0))
        self.attrib["parent"] = " ".join(str(x) for x in parent_id)
        clean_attrib = {}
        for k, v in list(self.attrib.items()):
            if isinstance(v, str):
                clean_attrib[k] = " ".join(v.split())
            else:
                clean_attrib[k] = v
        return "%s\t%s\t%s\t%s" % (self.type, self.name, " ".join(str(i) for i in print_id), dumps(clean_attrib))

    def __getitem__(self, n):
        return self.attrib[n]

    def __setitem__(self, n, val):
        self.attrib[n] = val

    def __contains__(self, n):
        if n in self.attrib:
            return True
        else:
            return False

    def get(self, key, default):
        if key in self.attrib:
            return self.attrib[key]
        else:
            return default

    def getid(self):
        return self.id + [self.attrib.get("start_byte", 0)] + [self.attrib.get("page", 0)]


class CompoundStack:
    """CompoundStack is the class instantiated by a parser. It itself creates a NewStack,
    but also tracks parallel objects. The API is quite minimal. You can push and pull objects by type.
    CompoundStack doesn't actually do deep object arithmetic or recursion--it handles parallel objects manually,
    and passes other calls on to the NewStack."""

    def __init__(
        self,
        types,
        page,
        docid=0,
        out=None,
        ref="",
        line="",
        graphic="",
        punctuation="punct",
        factory=CompoundRecord,
        p_factory=ParallelRecord,
    ):
        self.stack = NewStack(types[:], out, factory)
        self.out = out
        self.v_max = self.stack.v_max
        self.stack.v[0] = docid
        self.p_type = page
        self.current_p = None
        self.ref = ref
        self.current_ref = None
        self.line = line
        self.current_line = None
        self.graphic = graphic
        self.current_graphic = None
        self.punctuation = punctuation
        self.current_punctuation = None
        self.punctuation_count = 0
        self.p = 0
        self.r = 0
        self.l = 0
        self.g = 0
        self.p_factory = p_factory

    def __getitem__(self, n):
        if n == self.p_type:
            return self.current_p
        elif n == self.ref:
            return self.current_ref
        elif n == self.line:
            return self.current_line
        elif n == self.graphic:
            return self.current_graphic
        else:
            return self.stack[n]

    def __contains__(self, n):
        if n == self.p_type:
            if self.current_p:
                return True
            else:
                return False
        elif n == self.ref:
            if self.current_ref:
                return True
            else:
                return False
        elif n == self.line:
            if self.current_line:
                return True
            else:
                return False
        elif n == self.graphic:
            if self.current_graphic:
                return True
            else:
                return False
        else:
            if n in self.stack:
                return True
            else:
                return False

    def push(self, type, name, byte):
        if type == self.p_type:
            self.pull(type, byte)
            self.p += 1
            self.current_p = self.p_factory(type, name, [self.stack.v[0], self.p])
            self.current_p.attrib["start_byte"] = byte
            return self.current_p
        elif type == self.ref:
            self.r += 1
            self.current_ref = self.p_factory(type, name, [self.stack.v[0], self.r])
            self.current_ref.attrib["start_byte"] = byte
            return self.current_ref
        elif type == self.line:
            self.l += 1
            self.current_line = self.p_factory(type, name, [self.stack.v[0], self.l])
            self.current_line.attrib["start_byte"] = byte
            return self.current_line
        elif type == self.graphic:
            self.g += 1
            self.current_graphic = self.p_factory(type, name, [self.stack.v[0], self.g])
            self.current_graphic.attrib["start_byte"] = byte
            return self.current_graphic
        elif type == self.punctuation:
            self.punctuation_count += 1
            try:
                current_sent_id = self.stack["sent"].id[:6]
            except IndexError:
                try:
                    current_sent_id = self.stack["para"].id[:5] + [1]
                except IndexError:
                    try:
                        current_sent_id = self.stack["div3"].id[:4] + [1, 1]
                    except IndexError:
                        try:
                            current_sent_id = self.stack["div2"].id[:3] + [1, 1, 1]
                        except IndexError:
                            try:
                                current_sent_id = self.stack["div1"].id[:2] + [1, 1, 1, 1]
                            except IndexError:
                                current_sent_id = self.stack["doc"].id[:1] + [1, 1, 1, 1, 1]
            self.current_punctuation = Record("punct", name, current_sent_id + [0, 0, self.punctuation_count])
            self.current_punctuation.attrib["start_byte"] = byte
        else:
            self.stack.push(type, name, byte)
            if self.current_p:
                self.stack[type]["page"] = self.current_p.id[1]

    def pull(self, text_obj_type, byte):
        if text_obj_type == self.p_type:
            if self.current_p:
                self.current_p.attrib["end_byte"] = byte
                print(self.current_p, file=self.out)
                self.current_p = None
        elif text_obj_type == self.ref:
            if self.current_ref:
                self.current_ref.attrib["end_byte"] = byte
                print(self.current_ref, file=self.out)
        elif text_obj_type == self.line:
            if self.current_line:
                self.current_line.attrib["end_byte"] = byte
                print(self.current_line, file=self.out)
        elif text_obj_type == self.graphic:
            if self.current_graphic:
                self.current_graphic.attrib["end_byte"] = byte
                print(self.current_graphic, file=self.out)
        elif text_obj_type == self.punctuation:
            self.current_punctuation.attrib["end_byte"] = byte
            print(self.current_punctuation, file=self.out)
        else:
            return self.stack.pull(text_obj_type, byte)


class NewStack:
    """ NewStack is where the low-level object arithmetic and instantiation happens.  Pretty wonky,
    so there's inline documentation where needed"""

    def __init__(self, types, out=None, factory=None):
        self.v = []
        self.v_max = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.types = types
        self.v_types = {}
        self.current_objects = []
        self.out = out or sys.stdout
        self.factory = factory or Record

        for type in self.types:
            self.v.append(0)
            self.v_max.append(0)
            if type[-1].isdigit():
                v_type = type[:-1]
                if v_type not in self.v_types:
                    self.v_types[v_type] = [type]
                else:
                    self.v_types[v_type].append(type)

    def __getitem__(self, n):
        i = self.index(n)
        if i < len(self):
            return self.current_objects[i]
        else:
            raise IndexError

    def __len__(self):
        return len(self.current_objects)

    def __contains__(self, n):
        i = self.index(n)
        if len(self) > i:
            return True
        else:
            return False

    def index(self, type):
        if type in self.types:
            return self.types.index(type)
        elif type in self.v_types:
            possible_types = self.v_types[type][:]
            possible_types.reverse()
            for t in possible_types:
                i = self.types.index(t)
                if t in self and self[t].name != "__philo_virtual":
                    break
            return i
        raise IndexError

    def push(self, type, name, byte):
        # create any necessary virtual ancestors
        #        print [x.name for x in self.current_objects]

        i = self.index(type)
        if type in self.types:
            while len(self) < i:
                self.push(self.types[len(self)], "__philo_virtual", byte)
            # if we're currently in a node, we have to pull it first. and [implicitly] all its children
            if type in self:
                self.pull(type, byte)
            # now we can create a new node.  increment field here ONLY TO MARK INITIALIZATION
            if self.v[i] == 0:
                self.v[i] = 1
            r = self.factory(type, name, self.v[:])
            r.attrib["start_byte"] = byte
            self.current_objects.append(r)
        elif type in self.v_types:
            #           print "trying to push %s out of %s" % (type, self.v_types[type])
            possible_types = self.v_types[type][:]
            for t in possible_types:
                if t in self and self[t].name == "__philo_virtual":
                    #                    print "found at %s" % t
                    break
                if t not in self:
                    break
            self.push(t, name, byte)

    def pull(self, type, byte):
        # have to pull all descendants. recursively? no, too much overhead.  reverse order, real types.
        i = self.index(type)
        if type in self.types:
            if type in self:
                descendants = self.types[i + 1 :]
                descendants.reverse()
                for d in descendants:
                    self.pull(d, byte)
                # print
                self.current_objects[i].attrib["end_byte"] = byte
                print(self.current_objects[i], file=self.out)
                self.v_max = [max(new, prev) for new, prev in zip(self.v_max, self.current_objects[i].getid())]
                # we know all descendants have already been pulled.  so only have to reset the next one. and increment.
                self.v[i] += 1
                if (i + 1) < len(self.v):  # check to see we're not in a leaf node
                    self.v[i + 1] = 0  # then set child to 0
                self.current_objects.pop()
        # if virtual type, have to identify a non-virtual node.
        elif type in self.v_types:
            possible_types = self.v_types[type][:]
            possible_types.reverse()
            for t in possible_types:
                if t in self and self[t].name != "__philo_virtual":
                    break
            self.pull(t, byte)


class Record(object):
    # A baseline implementation of a PhiloLogic Record class.
    # Not usually used in parsers, but convenient and frequently used in loadFilters.
    def __init__(self, type, name, id):
        self.type = type
        self.name = name
        self.id = id  # Maybe page hack goes in here?  yeah, I think so.
        self.attrib = {}

    def __str__(self):
        clean_attrib = {}
        for k, v in list(self.attrib.items()):
            if isinstance(v, str):
                clean_attrib[k] = " ".join(v.split())
            else:
                clean_attrib[k] = v

        # Using json.dumps to write dict as it is much faster to read from a json string
        return "%s\t%s\t%s\t%s" % (self.type, self.name, " ".join(str(i) for i in self.id), dumps(clean_attrib))

    def __repr__(self):
        return "Record('%s','%s',%s)" % (self.type, self.name, self.id)


if __name__ == "__main__":
    print("testing OHCOVector.CompoundStack")
    my_types = ["doc", "div1", "div2", "div3", "para", "sent", "word"]
    stack = CompoundStack(my_types, "page")
    stack.push("doc", "<doc>", 0)
    stack.push("div1", "<div1>", 0)
    stack.push("word", "a", 0)
    stack.push("word", "b", 1)
    stack.push("word", "c", 2)
    stack.push("div2", "<div2>", 3)
    stack.push("word", "d", 3)
    stack.push("page", "pg1", 4)
    stack.push("word", "e", 4)
    stack.pull("div1", 4)
    stack.push("word", "f", 5)
    stack.push("div1", "<div1>", 6)
    stack.push("div3", "<div3>", 6)
    stack.push("word", "g", 6)
    stack.pull("doc", 7)
    stack.push("page", "lastpg", 7)