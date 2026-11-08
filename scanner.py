import argparse
import csv
import logging
import math
import socket

from datetime import datetime, timezone
from pathlib import Path


logger = logging.getLogger(__name__)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Mini TCP Port Scanner"
    )

    parser.add_argument(
        "host",
        help="Adres IPv4 lub nazwa hosta"
    )

    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Pierwszy port (domyślnie: %(default)s)"
    )

    parser.add_argument(
        "--end",
        type=int,
        default=1024,
        help="Ostatni port (domyślnie: %(default)s)"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Timeout TCP w sekundach (domyślnie: %(default)s)"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/results.csv"),
        help="Ścieżka raportu CSV"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Włącza diagnostykę DEBUG"
    )

    return parser.parse_args(argv)


def validate_args(args):
    if not (1 <= args.start <= 65535):
        raise ValueError(
            "Start port must be between 1 and 65535."
        )

    if not (1 <= args.end <= 65535):
        raise ValueError(
            "End port must be between 1 and 65535."
        )

    if args.start > args.end:
        raise ValueError(
            "Start port cannot be greater than end port."
        )

    if (
        not math.isfinite(args.timeout)
        or args.timeout <= 0
    ):
        raise ValueError(
            "Timeout must be finite and greater than zero."
        )

    host = args.host.strip()

    if not host:
        raise ValueError(
            "Host cannot be empty."
        )

    if any(ch.isspace() for ch in host):
        raise ValueError(
            "Host cannot contain whitespace."
        )

    if "://" in host:
        raise ValueError(
            "URL format is not supported."
        )

    if "/" in host:
        raise ValueError(
            "CIDR notation is not supported."
        )

    if ":" in host:
        raise ValueError(
            "IPv6 and host:port formats are not supported."
        )


def resolve_host(host):
    return socket.gethostbyname(host)


def check_port(target_ip, port, timeout):
    try:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        ) as sock:

            sock.settimeout(timeout)

            result = sock.connect_ex(
                (target_ip, port)
            )

            return result == 0

    except (
        socket.timeout,
        ConnectionRefusedError
    ):
        return False


def setup_logging(verbose=False):
    level = (
        logging.DEBUG
        if verbose
        else logging.INFO
    )

    logs_dir = Path("logs")
    logs_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    root_logger = logging.getLogger()

    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    root_logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        "logs/scanner.log",
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(
        console_handler
    )

    root_logger.addHandler(
        file_handler
    )


def write_csv_report(
    output_path,
    host,
    results
):
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open(
        mode="w",
        encoding="utf-8",
        newline=""
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "host",
                "port",
                "status",
                "timestamp"
            ]
        )

        writer.writeheader()

        open_results = sorted(
            (
                result
                for result in results
                if result["open"]
            ),
            key=lambda item: item["port"]
        )

        for result in open_results:
            writer.writerow(
                {
                    "host": host,
                    "port": result["port"],
                    "status": "open",
                    "timestamp": result[
                        "timestamp"
                    ].isoformat()
                }
            )


def main(argv=None):
    args = None

    try:
        args = parse_args(argv)

        setup_logging(
            getattr(
                args,
                "verbose",
                False
            )
        )

        validate_args(args)

        ip_address = resolve_host(
            args.host
        )

        logger.info(
            f"Starting scan "
            f"host={args.host} "
            f"ip={ip_address}"
        )

        logger.info(
            f"Range={args.start}-{args.end}, "
            f"timeout={args.timeout}"
        )

        results = []

        for port in range(
            args.start,
            args.end + 1
        ):
            is_open = check_port(
                ip_address,
                port,
                args.timeout
            )

            if args.verbose:
                logger.debug(
                    f"Port {port}: "
                    f"open={is_open}"
                )

            if is_open:
                logger.info(
                    f"Open port detected: "
                    f"{port}"
                )

            results.append(
                {
                    "port": port,
                    "open": is_open,
                    "timestamp": datetime.now(
                        timezone.utc
                    )
                }
            )

        open_ports = [
            result["port"]
            for result in results
            if result["open"]
        ]

        ports_checked = len(results)

        open_count = len(open_ports)

        write_csv_report(
            args.output,
            args.host,
            results
        )

        logger.info(
            f"CSV report saved: "
            f"{args.output}"
        )

        logger.info(
            f"Scan complete. "
            f"Checked={ports_checked}, "
            f"Open={open_count}"
        )

        print()
        print("Scan summary")
        print(f"Host: {args.host}")
        print(f"IPv4: {ip_address}")
        print(
            f"Range: "
            f"{args.start}-{args.end}"
        )
        print(
            f"Ports checked: "
            f"{ports_checked}"
        )
        print(
            f"Open ports: "
            f"{open_count}"
        )
        print(
            f"Detected: "
            f"{open_ports}"
        )
        print(
            f"CSV report: "
            f"{args.output}"
        )

        return 0

    except ValueError as exc:
        logger.error(str(exc))
        return 2

    except socket.gaierror:
        logger.error(
            "DNS resolution failed."
        )
        return 1

    except KeyboardInterrupt:
        logger.warning(
            "Scan interrupted by user."
        )
        return 130

    except OSError as exc:
        logger.error(
            f"File operation failed: "
            f"{exc}"
        )
        return 1

    except Exception as exc:
        logger.error(
            f"Unexpected error: "
            f"{exc}"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())