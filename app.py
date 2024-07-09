from viktor import ViktorController, Color
from viktor.parametrization import ViktorParametrization, NumberField, SetParamsButton
from viktor.views import DataView, DataResult, DataGroup, DataItem, GeometryResult, GeometryView
from viktor.result import SetParamsResult
from viktor.geometry import Group, Line, Material, RectangularExtrusion, Point
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
from viktor.views import ImageView, ImageResult
import math

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

    @ImageView("Visualisierung", duration_guess=1)
    def create_result(self, params, **kwargs):
        # Get x (Abstand in der Länge) and y (Abstand in der Höhe) from params
        x = params.x
        y = params.y

        # Get angle (Steigung in Grad) and slope (Steigung in Prozent) from params
        angle = params.angle
        slope = params.slope

        # Calculate coordinates for the line
        if x != 0 and y != 0:
            # Both x and y are provided
            end_point = [x, y]
        elif x != 0 and angle != 0:
            # x and angle are provided
            end_point = [x, x * np.tan(np.radians(angle))]
        elif x != 0 and slope != 0:
            # x and slope are provided
            end_point = [x, x * slope / 100]
        elif y != 0 and angle != 0:
            # y and angle are provided
            end_point = [y / np.tan(np.radians(angle)), y]
        elif y != 0 and slope != 0:
            # y and slope are provided
            end_point = [y / (slope / 100), y]
        else:
            raise ValueError("Ungültige Kombination von Inputs")

        # Initialize figure
        fig = plt.figure()

        # Plot the line
        plt.plot([0, end_point[0]], [0, end_point[1]], marker='o')

        # Set equal aspect ratio to make steps equal
        plt.gca().set_aspect('equal', adjustable='box')

        # Remove step labels from axes
        plt.xticks([])
        plt.yticks([])

        # Add labels and title with formatted strings
        plt.xlabel(f'Abstand horizontal: {end_point[0]}')
        plt.ylabel(f'Abstand vertikal: {end_point[1]}')
        plt.title('Visualisierung')

        # Save figure as SVG
        svg_data = StringIO()
        fig.savefig(svg_data, format='svg')
        plt.close()

        # Return the SVG data as ImageResult
        return ImageResult(svg_data)