from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class FTPTransferMethod(str, Enum):
    SEND = 'send'
    RECEIVE = 'receive'


class FTPTask(BaseModel):
    id: Optional[int] = None
    local_dir: str = ''
    ftp_host: str = ''
    ftp_port: int = Field(default=21, ge=1, le=65535)
    ftp_dir: str = ''
    ftp_login: str = ''
    ftp_password: str = Field(default='', repr=False)
    transfer_method: FTPTransferMethod = FTPTransferMethod.SEND
    signal_file_path: str = ''
    signal_text: str = ''
    is_enabled: bool = True

    model_config = {
        'frozen': False,
        'extra': 'forbid',
        'str_strip_whitespace': True,
    }
