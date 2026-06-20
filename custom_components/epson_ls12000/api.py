"""Async Epson ESC/VP21 clients."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    AUTH_USERNAME,
    CONNECTION_TCP,
    CONNECTION_WEB_API,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

ESCVPNET_HANDSHAKE = b"ESC/VP.net\x10\x03\x00\x00\x00\x00"


class EpsonConnectionError(Exception):
    """Raised when the Epson projector cannot be reached."""


class EpsonProtocolError(Exception):
    """Raised when the Epson projector returns an invalid response."""


@dataclass
class DigestChallenge:
    """Parsed HTTP digest challenge."""

    realm: str
    nonce: str
    qop: str | None = None
    opaque: str | None = None


class EpsonWebClient:
    """Client for Epson projector Web API ESC/VP21 endpoint."""

    def __init__(
        self,
        hass,
        host: str,
        port: int,
        use_ssl: bool = False,
        verify_ssl: bool = True,
        password: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.hass = hass
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        self.password = password or None
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._state: dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._session = async_get_clientsession(hass, verify_ssl=verify_ssl)

    @property
    def state(self) -> dict[str, str]:
        """Return the last known command state."""
        return dict(self._state)

    @property
    def base_url(self) -> str:
        """Return projector base URL."""
        scheme = "https" if self.use_ssl else "http"
        return f"{scheme}://{self.host}:{self.port}"

    async def test_connection(self) -> str | None:
        """Probe the projector power state."""
        return await self.query("PWR")

    async def query_many(self, commands: list[str]) -> dict[str, str]:
        """Query several ESC/VP21 commands."""
        for command in commands:
            try:
                await self.query(command)
            except EpsonProtocolError as exc:
                _LOGGER.debug("Epson query unsupported for %s: %s", command, exc)
        return self.state

    async def query(self, command: str) -> str | None:
        """Query an ESC/VP21 command without the trailing question mark."""
        command = command.rstrip("?")
        response = await self.send_escvp21(f"{command}?")
        if response is None:
            return None
        value = self._extract_value(command, response)
        if value is not None:
            self._state[command] = value
        return value

    async def set_command(self, command: str, value: str | int) -> bool:
        """Set an ESC/VP21 command to a value."""
        await self.send_escvp21(f"{command} {value}")
        self._state[command] = str(value)
        return True

    async def send_raw(self, command: str) -> str | None:
        """Send a raw ESC/VP21 command."""
        return await self.send_escvp21(command.strip())

    async def send_escvp21(self, command: str) -> str | None:
        """Execute a command through Epson Projector Control Web API."""
        if not command:
            raise EpsonProtocolError("Empty command")

        encoded = quote(command.replace(" ", "+"), safe="+?")
        url = f"{self.base_url}/api/v01/control/escvp21?cmd={encoded}"
        async with self._lock:
            try:
                response = await self._request_with_optional_digest("GET", url)
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                raise EpsonConnectionError(str(exc)) from exc

        text = (await response.text()).strip()
        _LOGGER.debug("Epson ESC/VP21 %s -> %s", command, text)
        if response.status >= 400:
            raise EpsonConnectionError(f"HTTP {response.status}: {text}")
        if text.upper().startswith("ERR"):
            raise EpsonProtocolError(text)
        return text or None

    async def _request_with_optional_digest(
        self, method: str, url: str, **kwargs: Any
    ) -> aiohttp.ClientResponse:
        response = await self._session.request(
            method,
            url,
            timeout=self.timeout,
            **kwargs,
        )
        if response.status != 401 or not self.password:
            return response

        challenge = _parse_digest_challenge(response.headers.get("WWW-Authenticate", ""))
        response.release()
        if challenge is None:
            return response

        headers = dict(kwargs.pop("headers", {}))
        headers["Authorization"] = _build_digest_header(
            method=method,
            uri=url.split(self.base_url, 1)[1],
            username=AUTH_USERNAME,
            password=self.password,
            challenge=challenge,
        )
        return await self._session.request(
            method,
            url,
            timeout=self.timeout,
            headers=headers,
            **kwargs,
        )

    @staticmethod
    def _extract_value(command: str, response: str) -> str | None:
        prefix = f"{command}="
        for line in response.replace("\r", "\n").split("\n"):
            line = line.strip().strip(":")
            if line.startswith(prefix):
                return line.split("=", 1)[1].strip()
        if "=" in response:
            name, value = response.split("=", 1)
            if name.strip() == command:
                return value.strip().strip(":")
        return None


class EpsonTcpClient:
    """Client for direct ESC/VP21 over TCP."""

    def __init__(
        self,
        host: str,
        port: int,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._state: dict[str, str] = {}
        self._lock = asyncio.Lock()

    @property
    def state(self) -> dict[str, str]:
        """Return the last known command state."""
        return dict(self._state)

    async def test_connection(self) -> str | None:
        """Probe the projector power state."""
        return await self.query("PWR")

    async def query_many(self, commands: list[str]) -> dict[str, str]:
        """Query several ESC/VP21 commands."""
        for command in commands:
            try:
                await self.query(command)
            except EpsonProtocolError as exc:
                _LOGGER.debug("Epson TCP query unsupported for %s: %s", command, exc)
        return self.state

    async def query(self, command: str) -> str | None:
        """Query an ESC/VP21 command without the trailing question mark."""
        command = command.rstrip("?")
        response = await self.send_escvp21(f"{command}?")
        value = EpsonWebClient._extract_value(command, response or "")
        if value is not None:
            self._state[command] = value
        return value

    async def set_command(self, command: str, value: str | int) -> bool:
        """Set an ESC/VP21 command to a value."""
        await self.send_escvp21(f"{command} {value}")
        self._state[command] = str(value)
        return True

    async def send_raw(self, command: str) -> str | None:
        """Send a raw ESC/VP21 command."""
        return await self.send_escvp21(command.strip())

    async def send_escvp21(self, command: str) -> str | None:
        """Send one command over TCP and read until the ESC/VP21 prompt."""
        if not command:
            raise EpsonProtocolError("Empty command")

        async with self._lock:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=self.timeout,
                )
                try:
                    writer.write(ESCVPNET_HANDSHAKE)
                    await writer.drain()
                    await self._read_handshake_response(reader)
                    writer.write(f"{command}\r".encode("ascii", errors="ignore"))
                    await writer.drain()
                    response = await self._read_until_prompt(reader)
                finally:
                    writer.close()
                    try:
                        await writer.wait_closed()
                    except (OSError, RuntimeError):
                        pass
            except (asyncio.TimeoutError, OSError) as exc:
                raise EpsonConnectionError(str(exc)) from exc

        text = response.strip().strip(":").strip()
        _LOGGER.debug("Epson TCP ESC/VP21 %s -> %s", command, text)
        if text.upper().startswith("ERR"):
            raise EpsonProtocolError(text)
        return text or None

    async def _read_handshake_response(self, reader: asyncio.StreamReader) -> None:
        """Read the ESC/VP.net handshake response when the projector sends one."""
        try:
            await asyncio.wait_for(reader.read(len(ESCVPNET_HANDSHAKE)), timeout=1.0)
        except asyncio.TimeoutError:
            return

    async def _read_until_prompt(
        self,
        reader: asyncio.StreamReader,
        allow_timeout: bool = False,
    ) -> str:
        buffer = bytearray()
        while True:
            try:
                raw = await asyncio.wait_for(reader.read(1), timeout=self.timeout)
            except asyncio.TimeoutError:
                if allow_timeout:
                    return ""
                raise
            if not raw:
                if buffer:
                    return buffer.decode("ascii", errors="ignore")
                raise EpsonConnectionError("Connection closed")
            if raw == b":":
                return buffer.decode("ascii", errors="ignore")
            buffer.extend(raw)


EpsonClient = EpsonWebClient | EpsonTcpClient


def create_client(
    hass,
    connection_type: str,
    host: str,
    port: int,
    use_ssl: bool = False,
    verify_ssl: bool = True,
    password: str | None = None,
) -> EpsonClient:
    """Create the configured Epson client."""
    if connection_type == CONNECTION_WEB_API:
        return EpsonWebClient(
            hass=hass,
            host=host,
            port=port,
            use_ssl=use_ssl,
            verify_ssl=verify_ssl,
            password=password,
        )
    if connection_type == CONNECTION_TCP:
        return EpsonTcpClient(host=host, port=port)
    raise EpsonProtocolError(f"Unsupported connection type: {connection_type}")


def _parse_digest_challenge(header: str) -> DigestChallenge | None:
    if not header.lower().startswith("digest "):
        return None
    values: dict[str, str] = {}
    for part in header[7:].split(","):
        if "=" not in part:
            continue
        key, value = part.strip().split("=", 1)
        values[key] = value.strip().strip('"')
    if "realm" not in values or "nonce" not in values:
        return None
    return DigestChallenge(
        realm=values["realm"],
        nonce=values["nonce"],
        qop=values.get("qop", "").split(",")[0] or None,
        opaque=values.get("opaque"),
    )


def _build_digest_header(
    method: str,
    uri: str,
    username: str,
    password: str,
    challenge: DigestChallenge,
) -> str:
    nc = "00000001"
    cnonce = secrets.token_hex(8)
    ha1 = hashlib.md5(
        f"{username}:{challenge.realm}:{password}".encode(), usedforsecurity=False
    ).hexdigest()
    ha2 = hashlib.md5(f"{method}:{uri}".encode(), usedforsecurity=False).hexdigest()
    if challenge.qop:
        response = hashlib.md5(
            f"{ha1}:{challenge.nonce}:{nc}:{cnonce}:{challenge.qop}:{ha2}".encode(),
            usedforsecurity=False,
        ).hexdigest()
    else:
        response = hashlib.md5(
            f"{ha1}:{challenge.nonce}:{ha2}".encode(),
            usedforsecurity=False,
        ).hexdigest()

    parts = [
        f'username="{username}"',
        f'realm="{challenge.realm}"',
        f'nonce="{challenge.nonce}"',
        f'uri="{uri}"',
        f'response="{response}"',
        "algorithm=MD5",
    ]
    if challenge.opaque:
        parts.append(f'opaque="{challenge.opaque}"')
    if challenge.qop:
        parts.extend([f"qop={challenge.qop}", f"nc={nc}", f'cnonce="{cnonce}"'])
    return "Digest " + ", ".join(parts)
