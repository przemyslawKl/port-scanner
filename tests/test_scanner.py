import logging
import socket
import unittest

from unittest.mock import patch

import scanner
from io import StringIO
from unittest.mock import patch


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)


class TestDNSFailure(BaseTestCase):

    @patch(
        "scanner.resolve_host",
        side_effect=socket.gaierror
    )
    def test_dns_failure(
        self,
        mock_resolver
    ):
        result = scanner.main(
            [
                "localhost",
                "--start",
                "18080",
                "--end",
                "18080"
            ]
        )

        self.assertEqual(result, 1)


class TestKeyboardInterrupt(BaseTestCase):

    @patch(
        "scanner.check_port",
        side_effect=KeyboardInterrupt
    )
    def test_keyboard_interrupt(
        self,
        mock_check
    ):
        result = scanner.main(
            [
                "127.0.0.1",
                "--start",
                "18080",
                "--end",
                "18080"
            ]
        )

        self.assertEqual(result, 130)


class TestValidation(BaseTestCase):

    def test_invalid_port(self):
        result = scanner.main(
            [
                "127.0.0.1",
                "--start",
                "0"
            ]
        )

        self.assertEqual(result, 2)

    def test_invalid_range(self):
        result = scanner.main(
            [
                "127.0.0.1",
                "--start",
                "18082",
                "--end",
                "18080"
            ]
        )

        self.assertEqual(result, 2)

    def test_invalid_timeout(self):
        result = scanner.main(
            [
                "127.0.0.1",
                "--start",
                "18080",
                "--end",
                "18080",
                "--timeout",
                "0"
            ]
        )

        self.assertEqual(result, 2)


class TestResolver(BaseTestCase):

    def test_resolve_localhost(self):
        ip = scanner.resolve_host(
            "localhost"
        )

        self.assertIsInstance(ip, str)

        self.assertTrue(
            len(ip) > 0
        )


class TestCheckPort(BaseTestCase):

    @patch(
        "scanner.socket.socket"
    )
    def test_open_port(
        self,
        mock_socket
    ):
        instance = (
            mock_socket.return_value
            .__enter__
            .return_value
        )

        instance.connect_ex.return_value = 0

        result = scanner.check_port(
            "127.0.0.1",
            18080,
            1
        )

        self.assertTrue(result)

    @patch(
        "scanner.socket.socket"
    )
    def test_closed_port(
        self,
        mock_socket
    ):
        instance = (
            mock_socket.return_value
            .__enter__
            .return_value
        )

        instance.connect_ex.return_value = 111

        result = scanner.check_port(
            "127.0.0.1",
            18080,
            1
        )

        self.assertFalse(result)

    @patch(
        "scanner.socket.socket"
    )
    def test_socket_timeout(
        self,
        mock_socket
    ):
        instance = (
            mock_socket.return_value
            .__enter__
            .return_value
        )

        instance.connect_ex.side_effect = (
            socket.timeout
        )

        result = scanner.check_port(
            "127.0.0.1",
            18080,
            1
        )

        self.assertFalse(result)

    @patch(
        "scanner.socket.socket"
    )
    def test_connection_refused(
        self,
        mock_socket
    ):
        instance = (
            mock_socket.return_value
            .__enter__
            .return_value
        )

        instance.connect_ex.side_effect = (
            ConnectionRefusedError
        )

        result = scanner.check_port(
            "127.0.0.1",
            18080,
            1
        )

        self.assertFalse(result)


class TestSuccessFlow(BaseTestCase):

    @patch("scanner.write_csv_report")
    @patch("scanner.check_port")
    @patch("scanner.resolve_host")
    def test_successful_scan(
        self,
        mock_resolve,
        mock_check,
        mock_write
    ):
        mock_resolve.return_value = (
            "127.0.0.1"
        )

        mock_check.return_value = True

        fake_stdout = StringIO()

        with patch(
            "sys.stdout",
            new=fake_stdout
        ):
            result = scanner.main(
                [
                    "localhost",
                    "--start",
                    "18080",
                    "--end",
                    "18080"
                ]
            )

        output = fake_stdout.getvalue()

        self.assertEqual(result, 0)

        self.assertIn(
            "Scan summary",
            output
        )

        self.assertIn(
            "Host: localhost",
            output
        )

        self.assertIn(
            "IPv4: 127.0.0.1",
            output
        )

        self.assertIn(
            "Ports checked: 1",
            output
        )

        self.assertIn(
            "Open ports: 1",
            output
        )

        mock_resolve.assert_called_once()

        mock_write.assert_called_once()


if __name__ == "__main__":
    unittest.main()