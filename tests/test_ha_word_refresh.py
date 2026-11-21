"""A Home Assistant translation refresh keeps drafts when HA returns English fallbacks."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch


@unittest.skipUnless(importlib.util.find_spec('aiohttp'), 'requires aiohttp')
class HaWordRefreshTests(unittest.TestCase):
    def test_english_fallback_preserves_draft_but_real_translation_replaces_it(self):
        path = Path(__file__).resolve().parents[1] / 'tools/i18n.py'
        spec = importlib.util.spec_from_file_location('ha_word_tool', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        languages = {
            'en': {'screen': {'ha': {'fan': {'low': 'Low'}, 'cover': {'closing': 'Closing', 'open': 'Open'},
                                   'unavailable': 'Unavailable'}}},
            'uk': {'screen': {'ha': {'fan': {'low': 'Низька'}, 'cover': {'closing': 'Старий переклад'},
                                   'unavailable': 'Недоступно'}}},
        }
        socket = AsyncMock()
        socket.receive_json.side_effect = [
            {}, {'type': 'auth_ok'},
            {'result': {'resources': {'fan.low': 'Low', 'cover.closing': 'Closing', 'cover.open': 'Open'}}},
            {'result': {'resources': {'fan.low': 'Low', 'cover.closing': 'Зачинення', 'cover.open': 'Open'}}},
        ]
        session = MagicMock()
        session.__aenter__.return_value = session
        session.ws_connect.return_value.__aenter__.return_value = socket
        with tempfile.TemporaryDirectory() as tmp, \
                patch.dict(os.environ, {'HA_URL': 'http://ha.test', 'HA_TOKEN': 'test-token'}), \
                patch('aiohttp.ClientSession', return_value=session), \
                patch.object(module, 'languages', return_value=languages), \
                patch.object(module, 'FOLDER', Path(tmp)), \
                patch.object(module, 'ha_sources', return_value={key: key for key in
                             ('fan.low', 'cover.closing', 'cover.open')}), \
                patch.object(module, 'frontend_words', return_value={
                    'en': {'unavailable': 'Unavailable'}, 'uk': {'unavailable': 'Unavailable'}}), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(module.ha_words(True), 0)
            saved = json.loads((Path(tmp) / 'uk.json').read_text())['screen']['ha']
        self.assertEqual(saved['fan']['low'], 'Низька')
        self.assertEqual(saved['unavailable'], 'Недоступно')
        self.assertEqual(saved['cover']['closing'], 'Зачинення')
        self.assertEqual(saved['cover']['open'], 'Open')


if __name__ == '__main__':
    unittest.main()
