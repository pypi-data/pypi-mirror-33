"""
https://en.wikipedia.org/wiki/Wavefront_.obj_file

test models can be found at:
  http://people.sc.fsu.edu/~jburkardt/data/obj/obj.html
"""
from __future__ import print_function
from codecs import open
from numpy import array, unique, hstack, zeros

def read_obj(obj_filename, log=None, debug=False):
    """loads a OBJ file"""
    model = OBJ(log=log, debug=debug)
    model.read_obj(obj_filename)
    return model

class OBJ(object):
    def __init__(self, log=None, debug=False):
        self.nodes = []
        self.lines = []
        self.tri_faces = []
        self.quad_faces = []

    @property
    def nnodes(self):
        return self.nodes.shape[0]
    @property
    def nelements(self):
        return self.tri_faces.shape[0] + self.quad_faces.shape[0]

    def read_obj(self, obj_filename):
        """
        v -0.0817245 0.000635 0.00421862
        v -0.0817245 0.000580371 0.00421862
        v -0.0817245 -0.000635 0.00421862
        l 1 2
        l 2 3
        """
        nodes = []
        lines = []
        tri_faces = []
        quad_faces = []
        with open(obj_filename, 'r') as obj_file:
            obj_lines = obj_file.readlines()

        for line in obj_lines:
            line = line.split('#')[0].strip()
            if not line:
                continue

            sline = line.split()
            #print(sline)
            entry_type = sline[0]
            if entry_type == 'v':  # vertex
                nodes.append(sline[1:])
            elif entry_type == 'l':  # line
                lines.append(sline[1:])
            elif entry_type == 'f':  # face
                assert '/' not in line, 'line=%s' % line
                if len(sline) == 5: # f + quad
                    quad_faces.append(sline[1:])
                elif len(sline) == 4: # f + tri
                    tri_faces.append(sline[1:])
                else:
                    raise NotImplementedError(sline)

            elif entry_type == 'mtllib': # material library path (str)
                continue
            elif entry_type == 'g': #  group_name (str)
                continue
            elif entry_type == 'usemtl': #  defines the material name (str)
                continue
            elif entry_type == 's': #  smooth shading (int? or string?)
                continue
            elif entry_type == 'vt':  # texture coordinate
                continue
            elif entry_type == 'vn':  # normal vector (not unit vector)
                continue
            elif entry_type == 'vp':  # parameter space vertex
                continue
            else:
                raise NotImplementedError('line = %r' % line)
        self.nodes = array(nodes, dtype='float64')

        # make it 0-based instead of 1 based
        if len(lines):
            self.lines = array(lines, dtype='int32') - 1
            #self.make_elements_from_lines()
        if len(tri_faces):
            self.tri_faces = array(tri_faces, dtype='int32') - 1
        if len(quad_faces):
            self.quad_faces = array(quad_faces, dtype='int32') - 1

    def make_elements_from_lines(self):
        #print(self.nodes.shape)
        unodes, indicies = unique_rows(self.nodes, return_inverse=True)

        #print(unodes)
        #print(list(indicies))
        #print(unodes.shape)
        #print(indicies.shape)

        n1 = self.lines[:, 0]
        n2 = self.lines[:, 1]
        i1 = indicies[n1]
        i2 = indicies[n2]
        nrows = len(i1)
        #self.lines = hstack([i1, i2], dtype='int32')
        self.lines = hstack([i1, i2])
        lines2 = zeros((nrows, 2), dtype='int32')
        lines2[:, 0] = i1
        lines2[:, 1] = i2
        self.lines = lines2
        #print(self.lines.shape)
        self.nodes = unodes

    def write_obj(self, obj_filename):
        float_fmt = '8.6f'
        int_fmt = 'i'
        node_fmt = 'v %%%s %%%s %%%s\n'  % (float_fmt, float_fmt, float_fmt)
        line_fmt = 'l %%%s %%%s\n'  % (int_fmt, int_fmt)
        tri_face_fmt = 'f %%%s %%%s %%%s\n'  % (int_fmt, int_fmt, int_fmt)
        quad_face_fmt = 'f %%%s %%%s %%%s %%%s\n'  % (int_fmt, int_fmt, int_fmt, int_fmt)
        #print(node_fmt)

        with open(obj_filename, 'w') as obj_file:
            for node in self.nodes:
                obj_file.write(node_fmt % tuple(node))
            if len(self.lines):
                for line in self.lines + 1:
                    obj_file.write(line_fmt % tuple(line))

            if len(self.tri_faces):
                for face in self.tri_faces + 1:
                    obj_file.write(tri_face_fmt % tuple(face))
            if len(self.quad_faces):
                for face in self.quad_faces + 1:
                    obj_file.write(quad_face_fmt % tuple(face))


def unique_rows(data, return_inverse=False):
    ncols = data.shape[1]
    dtype = data.dtype.descr * ncols
    struct = data.view(dtype)

    uniq, indicies = unique(struct, return_inverse=return_inverse)
    uniq = uniq.view(data.dtype).reshape(-1, ncols)
    return uniq, indicies

def main():  # pragma: no cover
    import sys
    obj_filename = '6.5e-06_edges.txt'
    obj_filename = sys.argv[1]
    obj = OBJ()
    obj.read_obj(obj_filename)
    obj.write_obj('b.txt')

if __name__ == '__main__':  # pragma: no cover
    main()
