from qip.pipeline import run_graph, get_deps
from qip.pipeline import GraphAccumulator

from qip.qip import *
from qip.operators import *


class SvgFeeder(GraphAccumulator):
    BLACKLIST = ["SplitQubit", "Q"]

    def __init__(self, n, linespacing=20, opheight=10, opbuffer=10, linewidth=2, opoutlinewidth=1):
        self.svg_acc = ''
        self.n = n
        self.linespacing = linespacing
        self.opheight = opheight
        self.opbuffer = opbuffer
        self.linewidth = linewidth
        self.opoutlinewidth = opoutlinewidth
        self.font_size = 5

        self.last_x_center = 0
        self.last_x_max = 0

        # Ops to draw once lines have been drawn.
        self.ops_to_draw = []

    def feed(self, qbitindex, node):
        print(node)
        # Get new node position
        nodestr = repr(node)
        paren_pos = nodestr.find('(')
        if paren_pos > 0:
            nodestr = nodestr[:paren_pos]
        if nodestr in SvgFeeder.BLACKLIST:
            return

        stringn = len(nodestr)

        total_op_size = 10
        new_x_center = self.last_x_max + self.opbuffer + int(total_op_size/2.0)
        new_x_max = new_x_center + total_op_size - int(total_op_size/2.0)

        # Start by extending lines to new position.
        for i in range(self.n):
            line_y = i*self.linespacing + self.opheight
            line_str = '<line x1="{}" x2="{}" y1="{}" y2="{}" style="stroke:black;stroke-width:{}"></line>\n'.format(
                self.last_x_center, new_x_center,
                line_y, line_y,
                self.linewidth
            )
            self.svg_acc += line_str

        # Add ops to list with relevant positions.
        for input_node in node.inputs:
            node_indices = qbitindex[input_node]
            for node_index in node_indices:
                op_info = (nodestr, new_x_center, node_index*self.linespacing + self.opheight)
                self.ops_to_draw.append(op_info)

        # Get ready for next node.
        self.last_x_center = new_x_center
        self.last_x_max = new_x_max

    def get_op_str(self):
        acc_str = ''
        for op_name, op_x, op_y in self.ops_to_draw:
            half_x_width = self.font_size * len(op_name)/2
            half_y_width = self.opheight/2

            poly_str = '<rect x="{}" y="{}" width="{}" height="{}" style="fill:white;stroke:black;stroke-width:{}"></rect>'.format(
                op_x - half_x_width,
                op_y - half_y_width,
                2*half_x_width,
                2*half_y_width,
                self.opoutlinewidth
            )

            text_str = '<text x="{}" y="{}" font-size="{}" alignment-baseline="middle" text-anchor="middle">{}</text>\n'.format(
                op_x, op_y, self.font_size, op_name
            )

            acc_str += poly_str + text_str

        return acc_str

    def get_svg_text(self):
        op_str = self.get_op_str()
        tmp = '<svg viewBox="0 0 {} {}" xmlns="http://www.w3.org/2000/svg">\n{}\n{}\n</svg>'.format(
            self.last_x_max, self.linespacing*self.n + 2*self.opheight,
            self.svg_acc, op_str
        )
        return tmp

def make_svg(*args):
    frontier, graphnodes = get_deps(*args)
    print(frontier)
    frontier = list(sorted(frontier, key=lambda q: q.qid))
    n = sum(f.n for f in frontier)
    graphacc = SvgFeeder(n)
    run_graph(frontier, graphnodes, graphacc)

    return graphacc.get_svg_text()

if __name__ == "__main__":
    x = Qubit(n=1)
    y = Qubit(n=1)
    z1 = Not(x)
    z = Not(x,y)

    print(make_svg(z))