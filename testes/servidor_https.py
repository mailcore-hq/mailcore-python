"""Servidor HTTPS sintético, restrito ao loopback do container de testes."""

from __future__ import annotations

import atexit
import json
import socket
import ssl
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable


class _Servidor(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 64

    def handle_error(self, _pedido, _endereco) -> None:
        # Desconexões, cancelamentos e TLS recusado são cenários esperados.
        pass


class _Atendimento(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, _formato, *_argumentos) -> None:
        pass

    def tratar(self) -> None:
        tamanho = int(self.headers.get("Content-Length", "0"))
        corpo = self.rfile.read(tamanho) if tamanho else b""
        registro = {
            "metodo": self.command,
            "alvo": self.path,
            "cabecalhos": {nome.lower(): valor for nome, valor in self.headers.items()},
            "corpo": corpo,
            "conexao": self.client_address,
        }
        dono = self.server.dono
        with dono._mutex:
            dono._registros.append(registro)
        try:
            if dono._atender is None:
                self.enviar(corpo={"id": "email-sintetico", "estado": "aceita"})
            else:
                dono._atender(self)
        except (OSError, ssl.SSLError):
            self.close_connection = True

    do_GET = tratar
    do_POST = tratar
    do_PATCH = tratar
    do_PUT = tratar
    do_DELETE = tratar

    def cabecalhos(self, status: int = 200, **campos: str) -> None:
        self.send_response(status)
        for nome, valor in campos.items():
            self.send_header(nome, valor)
        self.end_headers()
        self.wfile.flush()

    def enviar(
        self, status: int = 200, corpo=None, cabecalhos: dict[str, str] | None = None
    ) -> None:
        campos = dict(cabecalhos or {})
        if corpo is None:
            dados = b""
        elif isinstance(corpo, bytes):
            dados = corpo
            campos.setdefault("Content-Type", "application/octet-stream")
        elif isinstance(corpo, str):
            dados = corpo.encode("utf-8")
            campos.setdefault("Content-Type", "text/plain; charset=utf-8")
        else:
            dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
            campos.setdefault("Content-Type", "application/json")
        campos.setdefault("Content-Length", str(len(dados)))
        self.cabecalhos(status, **campos)
        if dados:
            self.wfile.write(dados)
            self.wfile.flush()

    def iniciar_fluxo(self, **campos: str) -> None:
        campos.setdefault("Content-Type", "application/octet-stream")
        campos.setdefault("Transfer-Encoding", "chunked")
        self.cabecalhos(**campos)

    def parte(self, dados: bytes) -> None:
        self.wfile.write(f"{len(dados):x}\r\n".encode("ascii") + dados + b"\r\n")
        self.wfile.flush()

    def finalizar_fluxo(self) -> None:
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    def desconectar(self) -> None:
        self.close_connection = True
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.connection.close()


class ServidorHttpsSintetico:
    _diretorio = tempfile.TemporaryDirectory(prefix="mailcore-python-tls-")
    _identidade: tuple[Path, Path] | None = None
    _mutex_identidade = threading.Lock()

    @classmethod
    def identidade(cls, nome: str = "principal") -> tuple[Path, Path]:
        certificado = Path(cls._diretorio.name) / f"{nome}.pem"
        chave = Path(cls._diretorio.name) / f"{nome}.key"
        with cls._mutex_identidade:
            if not certificado.exists():
                subprocess.run(
                    [
                        "openssl",
                        "req",
                        "-x509",
                        "-newkey",
                        "rsa:2048",
                        "-nodes",
                        "-days",
                        "1",
                        "-subj",
                        "/CN=API sintetica Mailcore",
                        "-addext",
                        "subjectAltName=IP:127.0.0.1",
                        "-keyout",
                        str(chave),
                        "-out",
                        str(certificado),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                chave.chmod(0o600)
        return certificado, chave

    def __init__(self, atender: Callable | None = None) -> None:
        self._atender = atender
        self._registros: list[dict] = []
        self._mutex = threading.Lock()
        certificado, chave = self.identidade()
        self.certificado_ca = str(certificado)
        self._servidor = _Servidor(("127.0.0.1", 0), _Atendimento)
        self._servidor.dono = self
        contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        contexto.minimum_version = ssl.TLSVersion.TLSv1_2
        contexto.load_cert_chain(str(certificado), str(chave))
        self._servidor.socket = contexto.wrap_socket(self._servidor.socket, server_side=True)
        self.porta = self._servidor.server_address[1]
        self._thread = threading.Thread(
            target=self._servidor.serve_forever,
            kwargs={"poll_interval": 0.01},
            daemon=True,
        )
        self._thread.start()

    def url_base(self, host: str = "127.0.0.1") -> str:
        return f"https://{host}:{self.porta}/v1"

    @property
    def registros(self) -> list[dict]:
        with self._mutex:
            return list(self._registros)

    def __enter__(self):
        return self

    def __exit__(self, *_erro) -> None:
        self._servidor.shutdown()
        self._servidor.server_close()
        self._thread.join(timeout=3)
        if self._thread.is_alive():
            raise RuntimeError("O servidor HTTPS sintético não encerrou.")


atexit.register(ServidorHttpsSintetico._diretorio.cleanup)
