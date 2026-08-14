import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent.parent / "configs"

def load_config(config_name: str) -> Dict[str, Any]:
    config_path = CONFIG_DIR / config_name
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

class DeceptionGridOrchestrator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.services = {}
        self.running = False
        
    def register_service(self, name: str, service: Any):
        self.services[name] = service
        logger.info(f"Registered service: {name}")
        
    def start(self):
        self.running = True
        logger.info("Deception Grid started")
        for name, service in self.services.items():
            if hasattr(service, 'start'):
                service.start()
                
    def stop(self):
        self.running = False
        logger.info("Deception Grid stopped")
        for name, service in self.services.items():
            if hasattr(service, 'stop'):
                service.stop()

    def get_service(self, name: str) -> Optional[Any]:
        return self.services.get(name)

class AttackerSession:
    def __init__(self, session_id: str, ip: str, service: str):
        self.session_id = session_id
        self.ip = ip
        self.service = service
        self.commands = []
        self.files_accessed = []
        self.techniques = []
        self.start_time = None
        self.end_time = None
        self.threat_score = 0.0
        
    def add_command(self, command: str):
        self.commands.append(command)
        
    def add_technique(self, technique_id: str):
        if technique_id not in self.techniques:
            self.techniques.append(technique_id)
            
    def calculate_threat_score(self) -> float:
        score = len(self.commands) * 0.1
        score += len(self.techniques) * 5.0
        score += len(self.files_accessed) * 0.5
        self.threat_score = min(score, 100.0)
        return self.threat_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "ip": self.ip,
            "service": self.service,
            "commands": self.commands,
            "files_accessed": self.files_accessed,
            "techniques": self.techniques,
            "threat_score": self.threat_score,
            "start_time": self.start_time,
            "end_time": self.end_time
        }