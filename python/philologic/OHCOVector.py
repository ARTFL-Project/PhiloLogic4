#!/usr/bin/python
import re
import sys
from simplejson import dumps

### NOTE: Much of this code developed iteratively, and there are some older variants at the bottom; due for a cleanup.
### CompoundStack is the class to use for all parsers.


class ParallelRecord(object):
    """ParallelRecord tracks page objects that are parallel to a primary record stack.  Used by CompoundStack."""

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
        print_id.append(self.attrib.get("byte_start", 0))
        print_id.append(self.attrib.get("page", 0))
        self.attrib["parent"] = " ".join(str(x) for x in parent_id)
        clean_attrib = {}
        for k, v in self.attrib.items():
            if isinstance(v, basestring):
                clean_attrib[k] = " ".join(v.split())
            else:
                clean_attrib[k] = v
        return "%s\t%s\t%s\t%s" % (self.type, self.name, " ".join(str(i) for i in print_id), dumps(clean_attrib))

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
        return self.id + [self.attrib.get("byte_start", 0)] + [self.attrib.get("page", 0)]


class CompoundStack(object):
    """CompoundStack is the class instantiated by a parser.  It itself creates a NewStack, but also tracks parallel objects
    The API is quite minimal. You can push and pull objects by type.
    CompoundStack doesn't actually do deep object arithmetic or recursion--it handles parallel objects manually,
    and passes other calls on to the NewStack."""

    def __init__(self, types, parallel, docid=0, out=None, factory=CompoundRecord, p_factory=ParallelRecord):
        self.stack = NewStack(types[:], out, factory)
        self.out = out
        self.v_max = self.stack.v_max
        self.stack.v[0] = docid
        self.p_type = parallel
        self.current_p = None
        self.p = 0
        self.p_factory = p_factory

    def __getitem__(self, n):
        if n == self.p_type:
            return self.current_p
        else:
            return self.stack[n]

    def __contains__(self, n):
        if n == self.p_type:
            if self.current_p:
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
        else:
            self.stack.push(type, name, byte)
            if self.current_p:
                self.stack[type]["page"] = self.current_p.id[1]

    def pull(self, type, byte):
        if type == self.p_type:
            if self.current_p:
                self.current_p.attrib["end_byte"] = byte
                print >> self.out, self.current_p
                self.current_p = None
        else:
            return self.stack.pull(type, byte)


class NewStack(object):
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
        #      print "%s %d" % (type,i)
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
            r.attrib["byte_start"] = byte
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
                descendants = self.types[i + 1:]
                descendants.reverse()
                for d in descendants:
                    self.pull(d, byte)
                # print
                self.current_objects[i].attrib["byte_end"] = byte
                print >> self.out, self.current_objects[i]
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
        for k, v in self.attrib.items():
            if isinstance(v, basestring):
                clean_attrib[k] = " ".join(v.split())
            else:
                clean_attrib[k] = v

        # Using simplejson.dumps to write dict as it is much faster to read from a json string
        return "%s\t%s\t%s\t%s" % (self.type, self.name, " ".join(str(i) for i in self.id), dumps(clean_attrib))

    def __repr__(self):
        return "Record('%s','%s',%s)" % (self.type, self.name, self.id)


class ARTFLRecord(Record):
    # A record subclass with some hacks specific to the standard ARTFL index layout.
    # I believe this is replaced by CompoundRecord
    def __init__(self, type, name, id):
        self = Record.__init__(self, type, name, id)

    def __str__(self):
        # Page hack goes in here.
        return "%s\t%s\t%s\t%s" % (self.type, self.name, " ".join(str(i) for i in self.id), self.attrib)


class Stack(object):
    # Obsolete
    def __init__(self, types, parallel, out=None, meta_out=None, factory=None):
        self.v = []
        self.v_max = []
        self.types = types
        self.virtual_types = {}
        self.current_objects = []
        self.depends_on = {}
        self.out = out or sys.stdout
        self.meta_out = meta_out or open("/dev/null", "w")
        self.factory = factory or Record

        prior_type = None
        for type in self.types:
            self.depends_on[type] = []
            self.v.append(0)
            self.v_max.append(0)
            self.current_objects.append(None)
            if prior_type:
                self.depends_on[prior_type].append(type)
            if type[-1].isdigit():
                v_type = type[:-1]
                if v_type not in self.virtual_types:
                    self.virtual_types[v_type] = [type]
                else:
                    self.virtual_types[v_type].append(type)
            prior_type = type

        for p_type in parallel:
            self.v.append(0)
            self.v_max.append(0)
            self.types.append(p_type)
            self.current_objects.append(None)
            self.depends_on[p_type] = []
            root_type = self.types[0]
            self.depends_on[root_type].append(p_type)

    def _had_children(self, type):  #only legal on real types...just a helper function.
        has_children = False
        i = self.types.index(type)
        dep_types = self.depends_on[type]
        for d_type in dep_types:
            d_i = self.types.index(d_type)
            if self.v[d_i] > 0:
                has_children = True
            has_children = has_children or self._had_children(d_type)
        return has_children

    def get_current(self, type):  #get_item
        if type in self.virtual_types:
            prev = None
            real_types = self.virtual_types[type]
            for r_type in real_types:
                i = self.types.index(r_type)
                if self.current_objects[i]:
                    prev = i
                    continue
                else:
                    break
            if prev:
                return self.current_objects[prev]
            else:
                return None
        else:
            i = self.types.index(type)
            return self.current_objects[i]

    def get_parent(self, type):  # should move to Record class
        this_obj = self.get_current(type)
        parent = None
        for obj in self.current_objects:
            if obj == this_obj:
                break
            else:
                parent = obj
        return parent

    def push(self, type, name, value=None):
        r = []
        if type in self.virtual_types:
            real_types = self.virtual_types[type][:]
            for r_type in real_types:
                i = self.types.index(r_type)
                if self.current_objects[i]:
                    continue
                else:
                    break
            r.extend(self.push(r_type, name))

        elif type in self.types:
            i = self.types.index(type)  # should this include parallel objcts?  if so, add them to types.  probably.
            if self._had_children(type) or self.current_objects[i]:
                self.pull(type)

            if value is not None:
                self.v[i] = value
            elif self.v[i] == 0:
                self.v[i] = 1

            r.extend((Record(type, name, self.v[:]),))
            self.current_objects[i] = r[-1]
        return r

    def pull(self, type):
        r = []
        if type in self.virtual_types:
            real_types = self.virtual_types[type][:]
            real_types.reverse()
            for r_type in real_types:
                i = self.types.index(r_type)
                if self.current_objects[i]:
                    break
            r.extend(self.pull(r_type))

        elif type in self.types:
            i = self.types.index(type)
            dependents = self.depends_on[type][:]
            dependents.reverse()
            for dep_type in dependents:
                r.extend(self.pull(dep_type))
                j = self.types.index(dep_type)
                self.v[j] = 0
            if self.current_objects[i]:
                r.extend((self.current_objects[i],))
                print >> self.out, r[-1]
                new_id = r[-1].id
                for k, n in enumerate(new_id):
                    self.v_max[k] = max(self.v_max[k], n)
                self.current_objects[i] = None
                self.v[i] += 1
        return r


class OHCOVector:
    # Obsolete, here for reference.
    """OHCOVector manages all the index arithmetic necessary to construct a PhiloLogic index.

    OHCOVector is constructed with two arguments: a list of types,
    and a supplementary list of (parallel_type, dependes_on_type).
    A type list typically takes the form ('doc','div1','div2','div3','para','sent','word'),
    whereas a typical set of parallel types are ( ('byte','doc'),('page','doc'),('line','doc') ).
    The subsequence 'div1','div2','div3' indicates a nested type, which can be addressed simply as
    'div'; in addition, the 'div' type can handle overflow by tesselating deeper structures.
    This isn't ideal, and may cause you to lose metadata on trailing segments--if it happens to you,
    increase the depth of the type.
    """

    def __init__(self, inner_types, *depends):
        self.v = []
        self.inner_types = inner_types
        self.outer_types = []
        self.maxdepths = {}  #the width of each hier type.  anything beyond is nested. #OUTERMAXDEPTH
        self.currentdepths = {}  # for hier types--from 1 up to max #OUTERCURRENTDEPTH
        self.nesteddepths = {}  # for hier types--only greater than 0 when current==max OUTERNESTEDDEPTH
        self.types = {}  #maps literal levels onto hierarchical types. # TYPEMAP?
        self.depends = depends  # needs to map parallel fields onto inner types, not outer.
        self.parallel = []
        self.current_objects = []
        self.current_metadata = []

        for i, lev in enumerate(inner_types):
            self.v.append(0)
            m = re.match(r"(.+)(\d+)$", lev)
            if m:
                type = m.group(1)
                n = m.group(2)
                self.types[lev] = type
                if type not in self.outer_types:
                    self.outer_types.append(type)
                self.maxdepths[type] = int(n)
                self.currentdepths[type] = 1
                self.nesteddepths[type] = 0
            elif re.match(r"(.+)$", lev):
                type = lev
                self.types[lev] = type
                self.maxdepths[lev] = 1
                self.currentdepths[type] = 1
                self.nesteddepths[type] = 0
                self.outer_types.append(type)
            else:
                sys.stderr.write("bad vector definition\n")

    def push(self, otype):
        """handles the start of an object.  nested types are special."""
        depth = 0
        #if we have a verbatim type listed in self.inner_types,
        #we can calculate it's position directly.
        if otype in self.inner_types:
            depth = self.inner_types.index(otype)
            type = self.types[otype]
            order = self.outer_types.index(type)  # oo bad.
            current = depth + 1
            for htype in self.outer_types[:order]:
                for k in range(self.maxdepths[htype]):
                    current -= 1
            self.currentdepths[type] = current
            self.v[depth] += 1
            for j in range(depth + 1, len(self.inner_types)):
                self.v[j] = 0
            #should check if we need to reset a parallel type
            return 0
        #if we have a hierarchical type listed in self.hier,
        #we have to walk through the hierarchy, and check the stack,
        #to find the correct position
        elif otype in self.outer_types:
            d = self.outer_types.index(otype)
            for htype in self.outer_types[:d]:
                for i in range(self.maxdepths[htype]):
                    depth += 1
            for j in range(1, self.currentdepths[otype]):
                depth += 1
            if self.currentdepths[otype] < self.maxdepths[otype]:
                self.currentdepths[otype] += 1
            else:
                self.nesteddepths[otype] += 1
            self.v[depth] += 1
            for j in range(depth + 1, len(self.inner_types)):
                self.v[j] = 0
            #should check if we need to reset a parallel type
            return 0
        # should check for parallel type push here
        elif otype in [p[0] for p in self.parallel]:
            # need to figure out where in v the parallel object lives, then increment.
            pass

    def pull(self, otype):
        #can't push to parallel type.
        depth = 0
        if otype in self.inner_types:
            depth = self.inner_types.index(otype)
            r = [i if n <= depth else 0 for n, i in enumerate(self.v)]
        elif otype in self.outer_types:
            d = self.outer_types.index(otype)
            for htype in self.outer_types[:d]:
                for i in range(self.maxdepths[htype]):
                    depth += 1
            for j in range(self.currentdepths[otype]):
                depth += 1
            if self.nesteddepths[otype] > 0:
                self.nesteddepths[otype] -= 1
            else:
                self.currentdepths[otype] -= 1
            r = [i if n <= depth else 0 for n, i in enumerate(self.v)]
            self.v[depth] += 1
            self.v = [j if n <= depth else 0 for n, j in enumerate(self.v)]
        return r

    def currentdepth(self):
        d = len(self.v)
        while d >= 0:
            d -= 1
            if self.v[d] != 0:
                return d

    def typedepth(self, type):
        if type in self.inner_types:  #levels should become inner_types
            return self.inner_types.index(type)
        elif type in self.outer_types:  #hier should become outer_types
            d = 0
            for t in self.outer_types[:self.outer_types.index(type)]:
                d += self.maxdepths[t]
            d += self.currentdepths[type]
            return d

    def __str__(self):
        r = []
        for l, n in zip(self.inner_types, self.v):
            r.append("%s:%d" % (l, n))
        return "(%s)" % ", ".join(r)


if __name__ == "__main__":
    print "testing OHCOVector.CompoundStack"
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
