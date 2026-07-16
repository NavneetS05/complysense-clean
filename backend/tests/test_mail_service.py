import unittest

from app.services.mail_service import MailService


class MailServiceTests(unittest.TestCase):
    def test_build_message_contains_template_content(self) -> None:
        message = MailService._build_message(
            to_email="user@example.com",
            subject="ComplySense — Welcome",
            template_key="welcome",
            context={
                "full_name": "Ada Lovelace",
                "login_url": "https://app.example.com/login",
                "temporary_password": "SetupTemp123!",
            },
        )

        rendered = message.as_string()
        self.assertIn("ComplySense", rendered)
        self.assertIn("Ada Lovelace", rendered)
        self.assertIn("SetupTemp123!", rendered)
        self.assertIn("https://app.example.com/login", rendered)


if __name__ == "__main__":
    unittest.main()
