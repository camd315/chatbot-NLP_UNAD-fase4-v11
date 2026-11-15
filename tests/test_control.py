
"""Pruebas de control, seguridad y memoria del chatbot V11."""

import unittest

from backend.chatbot import Chatbot, Session
from backend.security import evaluate
from backend.validated import exact_route


class ControlTests(unittest.TestCase):

    def setUp(self):
        self.bot = Chatbot()
        self.session = Session()

    def test_original_emergency_clears_memory(self):
        self.session.history.append({"topic": "prior"})

        response = self.bot.reply(
            "Auxilio, me están golpeando",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "SEGURIDAD_INMEDIATA_189",
        )
        self.assertEqual(len(self.session.history), 0)
        self.assertFalse(response["qwen_executed"])

    def test_reported_case_activates_prevention(self):
        question = (
            "Una mujer está viviendo una situación de violencia "
            "en Cali y necesita ayuda urgente. "
            "¿A dónde puede acudir?"
        )

        self.session.history.append({"topic": "prior"})
        response = self.bot.reply(question, self.session)

        self.assertEqual(
            response["route"],
            "SEGURIDAD_INMEDIATA_189",
        )
        self.assertIn("123", response["answer"])
        self.assertIn("155", response["answer"])
        self.assertEqual(len(self.session.history), 0)
        self.assertFalse(response["qwen_executed"])

    def test_third_party_immediate_danger(self):
        question = (
            "Mi amiga está en peligro y necesita ayuda ahora, "
            "¿a quién puede llamar?"
        )

        self.assertEqual(
            evaluate(question)["ruta"],
            "SEGURIDAD_INMEDIATA_189",
        )

    def test_third_party_violence(self):
        question = (
            "Mi hermana está siendo golpeada "
            "y necesita ayuda urgente"
        )

        self.assertEqual(
            evaluate(question)["ruta"],
            "SEGURIDAD_INMEDIATA_189",
        )

    def test_informational_question_is_not_urgent(self):
        self.assertNotEqual(
            evaluate("¿Qué es la violencia psicológica?")["ruta"],
            "SEGURIDAD_INMEDIATA_189",
        )

        self.assertNotEqual(
            evaluate("¿Qué hacer ante una emergencia?")["ruta"],
            "SEGURIDAD_INMEDIATA_189",
        )

    def test_conceptual_example_is_not_urgent(self):
        question = (
            "Explica un ejemplo de una mujer en situación "
            "de violencia que necesita ayuda urgente"
        )

        self.assertNotEqual(
            evaluate(question)["ruta"],
            "SEGURIDAD_INMEDIATA_189",
        )

    def test_negation_original_v11(self):
        self.assertNotEqual(
            evaluate("No estoy en peligro")["ruta"],
            "SEGURIDAD_INMEDIATA_189",
        )

    def test_unvalidated_abstains(self):
        response = self.bot.reply(
            "¿Qué es la violencia psicológica?",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "DOCUMENTACION_PENDIENTE",
        )
        self.assertFalse(response["qwen_executed"])

    def test_exact_queries(self):
        self.assertEqual(
            exact_route(
                "¿Qué derechos reconoce la Ley 1257 de 2008?"
            ),
            "ley",
        )

        self.assertEqual(
            exact_route(
                "¿Dónde puedo recibir orientación psicosocial "
                "y jurídica en Casa Matria de Cali?"
            ),
            "casa",
        )

    def test_no_documentary_without_corpus(self):
        response = self.bot.reply(
            "¿Qué derechos reconoce la Ley 1257 de 2008?",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "DOCUMENTACION_PENDIENTE",
        )

    def test_emergency_clears_previous_memory(self):
        self.session.history.append({
            "topic": "antecedente_academico"
        })

        self.assertEqual(len(self.session.history), 1)

        response = self.bot.reply(
            "Mi hermana está siendo golpeada "
            "y necesita ayuda urgente.",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "SEGURIDAD_INMEDIATA_189",
        )
        self.assertEqual(len(self.session.history), 0)
        self.assertEqual(response["memory"], 0)
        self.assertFalse(response["qwen_executed"])

    # =====================================================
    # NUEVAS PRUEBAS DE ORIENTACIÓN PREVENTIVA
    # =====================================================

    def test_first_person_physical_violence(self):
        response = self.bot.reply(
            "Estoy siendo golpeada",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "SEGURIDAD_INMEDIATA_189",
        )
        self.assertIn("123", response["answer"])
        self.assertEqual(len(self.session.history), 0)

    def test_third_person_brief_disclosure(self):
        response = self.bot.reply(
            "Mi hermana es golpeada",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "ORIENTACION_PREVENTIVA_V11",
        )
        self.assertIn("155", response["answer"])
        self.assertFalse(response["qwen_executed"])

    def test_typographical_variation(self):
        response = self.bot.reply(
            "Mi herma es golpeada",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "ORIENTACION_PREVENTIVA_V11",
        )
        self.assertEqual(len(self.session.history), 0)
        self.assertTrue(self.session.support_context)

    def test_followup_after_violence_disclosure(self):
        first = self.bot.reply(
            "Mi herma es golpeada",
            self.session,
        )

        self.assertEqual(
            first["route"],
            "ORIENTACION_PREVENTIVA_V11",
        )

        second = self.bot.reply(
            "Donde puedo llamar",
            self.session,
        )

        self.assertEqual(
            second["route"],
            "ORIENTACION_PREVENTIVA_V11",
        )
        self.assertIn("123", second["answer"])
        self.assertIn("155", second["answer"])
        self.assertEqual(len(self.session.history), 0)

    def test_followup_without_prior_context(self):
        response = self.bot.reply(
            "Donde puedo llamar",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "DOCUMENTACION_PENDIENTE",
        )

    def test_conceptual_physical_violence(self):
        response = self.bot.reply(
            "¿Qué es la violencia física?",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "DOCUMENTACION_PENDIENTE",
        )

    def test_negative_disclosure(self):
        response = self.bot.reply(
            "Mi hermana no es golpeada",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "DOCUMENTACION_PENDIENTE",
        )

    def test_sensitive_disclosure_clears_prior_history(self):
        self.session.history.append({
            "topic": "antecedente_academico"
        })

        response = self.bot.reply(
            "Mi hermana es golpeada",
            self.session,
        )

        self.assertEqual(
            response["route"],
            "ORIENTACION_PREVENTIVA_V11",
        )
        self.assertEqual(len(self.session.history), 0)
        self.assertEqual(response["memory"], 0)

    def test_unrelated_question_clears_support_context(self):
        self.bot.reply(
            "Mi herma es golpeada",
            self.session,
        )

        self.assertTrue(self.session.support_context)

        self.bot.reply(
            "¿Qué es un embedding?",
            self.session,
        )

        self.assertFalse(self.session.support_context)


if __name__ == "__main__":
    unittest.main()
