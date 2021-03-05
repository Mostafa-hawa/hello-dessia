import volmdlr as vm
import volmdlr.primitives2d as p2d
import volmdlr.primitives3d as p3d
import plot_data.core as plot_data
import math

from dessia_common import DessiaObject
from typing import List


class Rivet(DessiaObject):
    _standalone_in_db = True

    def __init__(self, rivet_diameter: float, rivet_length: float,
                 head_diameter: float, head_length: float,
                 price_factor: float = 1, rho: float = 1, name: str = ''):
        self.rho = rho
        self.price_factor = price_factor
        self.head_diameter = head_diameter
        self.head_length = head_length
        self.rivet_diameter = rivet_diameter
        self.rivet_length = rivet_length

        DessiaObject.__init__(self, name=name)

        self.price = self._price()
        self.mass = self._mass()

    def volume(self):
        return (math.pi * self.head_diameter ** 2 / 4) * self.head_length + (
                math.pi * self.rivet_diameter ** 2 / 4) * self.rivet_length

    def _price(self):
        real_volume = self.volume()
        raw_volume = (math.pi * self.head_diameter ** 2 / 4) * (self.head_length + self.rivet_length)
        return self.price_factor * raw_volume / real_volume

    def _mass(self):
        return self.rho * self.volume()

    def contour(self, full_contour=False):

        p0 = vm.Point2D(0, 0)
        vectors = [vm.Vector2D(self.rivet_diameter / 2, 0),
                   vm.Vector2D(self.head_diameter / 2 - self.rivet_diameter / 2, 0),
                   vm.Vector2D(0, self.head_length),
                   vm.Vector2D(-self.head_diameter, 0),
                   vm.Vector2D(0, -self.head_length),
                   vm.Vector2D(self.head_diameter / 2 - self.rivet_diameter / 2, 0),
                   vm.Vector2D(0, -self.rivet_length),
                   vm.Vector2D(self.rivet_diameter, 0),
                   vm.Vector2D(0, self.rivet_length),
                   ]
        points = []
        p_init = p0
        for v in vectors:
            p1 = p_init.translation(v, copy=True)
            points.append(p1)
            p_init = p1

        c = p2d.ClosedRoundedLineSegments2D(points, {})
        if full_contour:
            return vm.wires.Contour2D(c.primitives)
        else:
            line = vm.edges.Line2D(p0, p0.translation(vm.Vector2D(0, -self.rivet_length), copy=True))
            contour = vm.wires.Contour2D(c.primitives)
            return contour.cut_by_line(line)[0]

    def volmdlr_primitives(self, center=vm.O3D, axis=vm.Z3D):
        contour = self.contour(full_contour=False)
        axis.normalize()
        y = axis.random_unit_normal_vector()
        z = axis.cross(y)
        irc = p3d.RevolvedProfile(center, z, axis, contour, center,
                                  axis, angle=2 * math.pi, name='rivet')
        return [irc]

    def plot_data(self, full_contour=True):
        hatching = plot_data.HatchingSet(0.1)
        edge_style = plot_data.EdgeStyle(line_width=1)
        surface_style = plot_data.SurfaceStyle(hatching=hatching)

        contour = self.contour(full_contour=full_contour)
        contour_data = contour.plot_data(edge_style=edge_style,
                                         surface_style=surface_style)
        return [plot_data.PrimitiveGroup(primitives=[contour_data])]


class Generator(DessiaObject):
    _standalone_in_db = True

    _dessia_methods = ['generate']

    def __init__(self, rivets_definition: List[List[float]], name: str = ''):
        self.rivets_definition = rivets_definition

        DessiaObject.__init__(self, name=name)

    def generate(self) -> List[Rivet]:
        solutions = []
        for i, rivet_definition in enumerate(self.rivets_definition):
            rivet_diameter, rivet_length, head_diameter, head_length = rivet_definition
            solutions.append(
                Rivet(rivet_diameter, rivet_length, head_diameter, head_length, name='rivet{}'.format(i + 1)))
        return solutions

#adding the example material#
rivets_definition1 = [[0.01, 0.05, 0.012, 0.005],
                     [0.012, 0.05, 0.013, 0.0055]]
generator1 = Generator(rivets_definition=rivets_definition1, name='first_generator')
print('generator1', generator1.generate()) #.generate() gives a list of two Rivet
for riv in generator1.generate():
    print(riv.name) #you see the name of each Rivet in the list 
