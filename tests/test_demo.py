import unittest
from backend.demo_rag import demo_topic
from backend.chatbot import Chatbot,Session

class FakeDemo:
    def retrieve(self,question,k=2):
        return [{'id':'intro-rag','titulo':'Recuperación aumentada','texto':'RAG recupera textos.'}]

class DemoTest(unittest.TestCase):
    def test_topic(self):
        self.assertEqual(demo_topic('¿Qué es RAG?'),'rag')
        self.assertEqual(demo_topic('¿Para qué sirve ChromaDB?'),'chroma')
        self.assertIsNone(demo_topic('¿Dónde queda la luna?'))
    def test_extractives(self):
        r=Chatbot(None,FakeDemo()).reply('¿Qué es RAG?',Session())
        self.assertEqual(r['route'],'RAG_DEMO_EXTRACTIVO')
        self.assertIn('intro-rag',r['sources'])
        self.assertFalse(r['qwen_executed'])
    def test_no_case_leakage(self):
        r=Chatbot(None,FakeDemo()).reply('¿Dónde puedo recibir orientación psicosocial y jurídica en Casa Matria de Cali?',Session())
        self.assertEqual(r['route'],'DOCUMENTACION_PENDIENTE')
    def test_emergency_over_demo(self):
        r=Chatbot(None,FakeDemo()).reply('Mi hermana está siendo golpeada y necesita ayuda urgente',Session())
        self.assertEqual(r['route'],'SEGURIDAD_INMEDIATA_189')
if __name__=='__main__':unittest.main()
