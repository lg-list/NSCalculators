import unittest
import build


class ConversionDashboardRouting(unittest.TestCase):
    def test_specialized_engines_keep_their_dashboards(self):
        calc = {'slug': 'centimeters-to-inches-calculator', 'engine': 'linear_convert', 'cat': 'Conversion'}
        for engine in ('length_convert', 'feet_meters', 'liters_cubic_inches_advanced',
                       'seconds_hours_advanced', 'square_feet_acres_advanced',
                       'stones_pounds_advanced', 'weeks_months_advanced'):
            self.assertNotIn('linear-conversion-dashboard', build.analysis_extra_html(calc, engine))
        self.assertIn('linear-conversion-dashboard', build.analysis_extra_html(calc, 'linear_convert'))
