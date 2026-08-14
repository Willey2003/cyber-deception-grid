import asyncio
import logging
import socket
import uuid
from datetime import datetime
from typing import Optional
import paramiko
from paramiko import ServerInterface, AUTH_SUCCESSFUL, AUTH_FAILED, OPEN_SUCCEEDED

from ...core import AttackerSession, DeceptionGridOrchestrator

logger = logging.getLogger(__name__)

class SSHHoneypotServer(ServerInterface):
    def __init__(self, orchestrator: DeceptionGridOrchestrator, client_ip: str):
        self.orchestrator = orchestrator
        self.client_ip = client_ip
        self.session_id = str(uuid.uuid4())[:8]
        self.session = AttackerSession(self.session_id, client_ip, "ssh")
        self.session.start_time = datetime.utcnow()
        self.authenticated = False
        self.command_count = 0
        
    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        self.session.add_command(f"login attempt: {username}:{password}")
        logger.info(f"SSH login attempt from {self.client_ip}: {username}:{password}")
        self.authenticated = True
        return AUTH_SUCCESSFUL

    def check_auth_publickey(self, username: str, key) -> int:
        return AUTH_FAILED

    def get_allowed_auths(self, username: str) -> str:
        return 'password'

class SSHHoneypot:
    def __init__(self, orchestrator: DeceptionGridOrchestrator, host: str = "0.0.0.0", port: int = 2222):
        self.orchestrator = orchestrator
        self.host = host
        self.port = port
        self.server_key = paramiko.RSAKey.generate(2048)
        self.running = False
        
    async def start(self):
        self.running = True
        logger.info(f"Starting SSH honeypot on {self.host}:{self.port}")
        
        server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        
        async with server:
            await server.serve_forever()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client_ip = writer.get_extra_info('peername')[0]
        logger.info(f"New SSH connection from {client_ip}")
        
        transport = paramiko.Transport(writer.transport)
        transport.add_server_key(self.server_key)
        
        server = SSHHoneypotServer(self.orchestrator, client_ip)
        transport.start_server(server=server)
        
        chan = transport.accept(20)
        if chan is None:
            return
            
        chan.settimeout(60)
        
        try:
            while self.running:
                data = await asyncio.get_event_loop().run_in_executor(None, chan.recv, 1024)
                if not data:
                    break
                    
                command = data.decode('utf-8', errors='ignore').strip()
                if command:
                    server.session.add_command(command)
                    server.command_count += 1
                    response = self._generate_fake_response(command)
                    chan.send(response.encode())
                    
        except Exception as e:
            logger.error(f"SSH session error: {e}")
        finally:
            server.session.end_time = datetime.utcnow()
            server.session.calculate_threat_score()
            self.orchestrator.register_service(f"session_{server.session_id}", server.session)
            chan.close()
            transport.close()

    def _generate_fake_response(self, command: str) -> str:
        command_lower = command.lower()
        
        if command_lower.startswith('ls'):
            return "bin  dev  etc  home  lib  opt  root  sbin  tmp  usr  var\n"
        elif command_lower.startswith('pwd'):
            return "/home/user\n"
        elif command_lower.startswith('whoami'):
            return "user\n"
        elif command_lower.startswith('id'):
            return "uid=1000(user) gid=1000(user) groups=1000(user)\n"
        elif command_lower.startswith('uname'):
            return "Linux ubuntu 5.15.0-91-generic #101-Ubuntu SMP x86_64 x86_64 x86_64 GNU/Linux\n"
        elif command_lower.startswith('cat /etc/passwd'):
            return "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\n"
        elif command_lower.startswith('ps'):
            return "  PID TTY          TIME CMD\n    1 ?        00:00:01 systemd\n  123 ?        00:00:00 sshd\n  456 ?        00:00:00 bash\n"
        elif command_lower.startswith('netstat'):
            return "Active Internet connections (servers and established)\nProto Recv-Q Send-Q Local Address           Foreign Address         State\n"
        elif command_lower == 'exit' or command_lower == 'logout':
            return "Connection to host closed.\n"
        else:
            return f"bash: {command}: command not found\n"

    def stop(self):
        self.running = False
        logger.info("SSH honeypot stopped")