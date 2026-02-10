import argparse
import logging
import socket
import ssl
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


class HtmlOnlyHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        request_path = urlparse(self.path).path
        if request_path.endswith("/"):
            request_path = f"{request_path}index.html"

        if not request_path.lower().endswith((".html", ".htm")):
            self.send_error(404, "Only .html files are served here")
            return

        self.path = request_path
        super().do_GET()

    def do_HEAD(self) -> None:
        request_path = urlparse(self.path).path
        if request_path.endswith("/"):
            request_path = f"{request_path}index.html"

        if not request_path.lower().endswith((".html", ".htm")):
            self.send_error(404, "Only .html files are served here")
            return

        self.path = request_path
        super().do_HEAD()


def build_arg_parser(project_root: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="HTTPS server for test/web HTML files.",
    )
    parser.add_argument(
        "--host",
        default="::",
        help="Listen host (default: ::)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Listen port (default: 8080)",
    )
    parser.add_argument(
        "--web-root",
        default=str(project_root / "test" / "web"),
        help="HTML root directory (default: test/web)",
    )
    parser.add_argument(
        "--cert",
        default=str(project_root / "cert" / "wthomec4.dns.army.cer"),
        help="TLS certificate path (default: cert/wthomec4.dns.army.cer)",
    )
    parser.add_argument(
        "--key",
        default=str(project_root / "cert" / "wthomec4.dns.army.key"),
        help="TLS private key path (default: cert/wthomec4.dns.army.key)",
    )
    return parser


class IPv6ThreadingHTTPServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6


def run_server(host: str, port: int, web_root: Path, cert_path: Path, key_path: Path) -> None:
    if not web_root.exists():
        raise FileNotFoundError(f"web root not found: {web_root}")
    if not cert_path.exists():
        raise FileNotFoundError(f"certificate not found: {cert_path}")
    if not key_path.exists():
        raise FileNotFoundError(f"key not found: {key_path}")

    handler = partial(HtmlOnlyHandler, directory=str(web_root))
    if ":" in host:
        httpd = IPv6ThreadingHTTPServer((host, port, 0, 0), handler)
    else:
        httpd = ThreadingHTTPServer((host, port), handler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    logging.info("Serving HTTPS on https://%s:%s (root: %s)", host, port, web_root)
    httpd.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="%(name)s: %(message)s")

    root = Path(__file__).resolve().parents[1]
    args = build_arg_parser(root).parse_args()

    run_server(
        host=args.host,
        port=args.port,
        web_root=Path(args.web_root),
        cert_path=Path(args.cert),
        key_path=Path(args.key),
    )
