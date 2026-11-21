"""Power-source enum words agree on sensor tiles and in the top bar without changing HA states."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'screen_manager/app'))
import ha_catalogue  # noqa: E402
import header_bar  # noqa: E402
import i18n  # noqa: E402


class InputSourceWords(unittest.TestCase):
    def setUp(self):
        self.screen_token = i18n.SCREEN.set({'language': 'uk', 'legacy': False})

    def tearDown(self):
        i18n.SCREEN.reset(self.screen_token)

    def test_ukrainian_source_words_on_sensor_tiles_and_top_bars(self):
        expected = {'grid': 'Мережа', 'generator': 'Генератор',
                    'shore_power': 'Берегова мережа', 'not_connected': 'Не підключено'}
        for raw, label in expected.items():
            with self.subTest(state=raw):
                attrs = {'device_class': 'enum'}
                words = {f'component.sensor.entity_component._.state.{raw}': raw.replace('_', ' ').capitalize()}
                state = {'state': raw, 'attributes': attrs}
                self.assertEqual(header_bar.value('sensor.input_source', state, words=words), (label, None))
                self.assertEqual(ha_catalogue.screen_word('sensor.input_source', raw, attrs, {}, words), label)

    def test_english_screen_keeps_english_source_words(self):
        i18n.SCREEN.set({'language': 'en', 'legacy': False})
        self.assertEqual(header_bar.value('sensor.input_source', {'state': 'grid', 'attributes': {}}), ('Grid', None))
        self.assertEqual(ha_catalogue.screen_word('sensor.input_source', 'grid', {}, {}, {}), 'Grid')

    def test_other_enum_values_keep_home_assistants_translation(self):
        words = {'component.sensor.entity_component._.state.custom_mode': 'Власний режим'}
        state = {'state': 'custom_mode', 'attributes': {'device_class': 'enum'}}
        self.assertEqual(header_bar.value('sensor.mode', state, words=words), ('Власний режим', None))
        self.assertEqual(ha_catalogue.screen_word('sensor.mode', 'custom_mode', state['attributes'], {}, words),
                         'Власний режим')

    def test_select_options_keep_the_integrations_own_words(self):
        words = {'component.select.entity_component._.state.grid': 'Ввід з мережі'}
        state = {'state': 'grid', 'attributes': {}}
        self.assertEqual(header_bar.value('select.input_source', state, words=words), ('Ввід з мережі', None))
        self.assertEqual(ha_catalogue.screen_word('select.input_source', 'grid', {}, {}, words), 'Ввід з мережі')


if __name__ == '__main__':
    unittest.main()
