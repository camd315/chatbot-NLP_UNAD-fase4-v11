import unittest
from backend.chatbot import Chatbot,Session
from backend.validated import exact_route

class ControlTests(unittest.TestCase):
    def test_emergency_clears_memory(self):
        s=Session();s.history.append({'topic':'prior'})
        r=Chatbot().reply('Auxilio, me están golpeando',s)
        self.assertEqual(r['route'],'SEGURIDAD_INMEDIATA_189')
        self.assertEqual(len(s.history),0)
    def test_unvalidated_abstains(self):
        s=Session();r=Chatbot().reply('¿Qué es la violencia psicológica?',s)
        self.assertEqual(r['route'],'DOCUMENTACION_PENDIENTE')
        self.assertFalse(r['qwen_executed'])
    def test_exact_queries(self):
        self.assertEqual(exact_route('¿Qué derechos reconoce la Ley 1257 de 2008?'),'ley')
        self.assertEqual(exact_route('¿Dónde puedo recibir orientación psicosocial y jurídica en Casa Matria de Cali?'),'casa')
    def test_no_documentary_without_corpus(self):
        s=Session();r=Chatbot().reply('¿Qué derechos reconoce la Ley 1257 de 2008?',s)
        self.assertEqual(r['route'],'DOCUMENTACION_PENDIENTE')

if __name__=='__main__':unittest.main()
