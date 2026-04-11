from typing import List, Any, Dict, Optional

class CommandSpecsArgsException(Exception):
    pass


class CommandSpecsHandler:
    
    @staticmethod
    def _parse_kv_tokens(tokens: List[str]) -> Dict[str, Any]:
        """Parse key=value tokens into payload"""
        payload: Dict[str, Any] = {}
        for token in tokens:
            if "=" not in tokens:
                raise CommandSpecsArgsException(f"Expected key=value token, got '{token}'")
            key, value = token.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key or value == "":
                raise CommandSpecsArgsException(f"Invalid key=value token '{token}'")
            payload[key] = value
        return payload

    @staticmethod
    def cmd_cm(tokens: List[str], **args):
        ...

    @staticmethod
    def cmd_rm(tokens: List[str], **args):
        ...

    @staticmethod
    def cmd_um(tokens: List[str], **args):
        ...

    @staticmethod
    def cmd_dm(tokens: List[str], **args):
        ...
    
    @staticmethod
    def cmd_newdb(tokens: List[str], **args):
        ...

    @staticmethod
    def cmd_listdb(tokens: List[str], **args):
        ...

    @staticmethod
    def cmd_savedb(tokens: List[str], **args):
        ...

    @staticmethod
    def cmd_loaddb(tokens: List[str], **args):
        ...

    @staticmethod
    def cmd_deldb(tokens: List[str], **args):
        ...

    @staticmethod
    def cmd_debug(tokens: List[str], **args):
        ...