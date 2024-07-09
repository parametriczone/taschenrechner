from viktor import ViktorController, Color
from viktor.parametrization import ViktorParametrization, NumberField, SetParamsButton
from viktor.views import DataView, DataResult, DataGroup, DataItem, GeometryResult, GeometryView
from viktor.result import SetParamsResult
import math
from viktor.geometry import Group, LinearPattern, SquareBeam, Material


class Parametrization(ViktorParametrization):
    x = NumberField('Abstand in der Länge', suffix='m', default=0, step=0.01)
    y = NumberField('Abstand in der Höhe', suffix='m', default=0, step=0.01)
    angle = NumberField('Steigung in Grad', suffix='°', default=0, step=0.01)
    slope = NumberField('Steigung in Prozent', suffix='%', default=0, step=0.01)
    reset_button = SetParamsButton('Zurücksetzen', method='reset_params')

class RechnerController(ViktorController):
    label = 'Gefällerechner'
    parametrization = Parametrization

    def reset_params(self, params, **kwargs):
        return SetParamsResult({
            'x': 0,
            'y': 0,
            'angle': 0,
            'slope': 0,
        })

    @DataView('Ergebnis', duration_guess=1)
    def get_data_view(self, params, **kwargs):
        x = params.x
        y = params.y
        angle = params.angle
        slope = params.slope

        # Check how many values are provided
        provided_values = [x, y, angle, slope].count(0)
        if provided_values > 2:
            result = "Bitte geben Sie mindestens zwei Werte ein."
            main_data_group = DataGroup(
                DataItem('Fehler', result),
            )
            return DataResult(main_data_group)

        try:
            if x != 0 and y != 0:
                # Calculate angle and slope
                slope = (y / x) * 100
                angle = math.atan(y / x) * (180 / math.pi)
            elif x != 0 and angle != 0:
                # Calculate y and slope
                y = x * math.tan(angle * math.pi / 180)
                slope = (y / x) * 100
            elif x != 0 and slope != 0:
                # Calculate y and angle
                y = (slope / 100) * x
                angle = math.atan(y / x) * (180 / math.pi)
            elif y != 0 and angle != 0:
                # Calculate x and slope
                x = y / math.tan(angle * math.pi / 180)
                slope = (y / x) * 100
            elif y != 0 and slope != 0:
                # Calculate x and angle
                x = y / (slope / 100)
                angle = math.atan(y / x) * (180 / math.pi)
            elif angle != 0 and slope != 0:
                # Calculate x and y
                x = slope / (100 * math.tan(angle * math.pi / 180))
                y = (slope / 100) * x
            else:
                raise ValueError("Ungültige Kombination von Inputs")

            main_data_group = DataGroup(
                DataItem('Abstand in der Länge (x)', x),
                DataItem('Abstand in der Höhe (y)', y),
                DataItem('Steigung in Grad (angle)', angle),
                DataItem('Steigung in Prozent (slope)', slope),
            )
        except Exception as e:
            main_data_group = DataGroup(
                DataItem('Fehler', str(e)),
            )

        return DataResult(main_data_group)

    @GeometryView("Geometry", duration_guess=1, x_axis_to_right=True)
    def geometry_view(self, params, **kwargs):

        # Define Materials
        glass = Material("Glass", color=Color(150, 150, 255))
        facade = Material("Facade", color=Color.white())

        # Create one floor
        width = 30
        length = 30
        number_of_floors = 20
        floor_glass = SquareBeam(width, length, 2, material=glass)
        floor_facade = SquareBeam(width + 1, length + 1, 1, material=facade)
        floor_facade.translate([0, 0, 1.5])
    
        # Pattern (duplicate) the floor to create a building
        floor = Group([floor_glass, floor_facade])
        building = LinearPattern(floor, direction=[0, 0, 1], number_of_elements=number_of_floors, spacing=3)
    
        return GeometryResult(building)    
