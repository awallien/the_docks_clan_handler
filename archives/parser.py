from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Self, Set, Type, Union, Any
import pathlib
import os
import re
import shlex
import yaml
from datetime import datetime

from .docks_clan_cb import docks_clan_cb
from .mgmt_abc import ICallbackMapper, INodeType, INode

def TAB(n): return "  "*n

yaml_cb_fns_mapper: Dict[str, ICallbackMapper] = {
    "docks_clan_commands": docks_clan_cb
}

base_types: Set[str] = {
    "string", "date", "uint",
    "enum", "bool", "empty"
}

class GetCommands:
    def __init__(self, commands):
        self._commands = commands

    def get_cmds(self):
        max_len = max((len(name) for name in self._commands), default=0)
        return "\n".join(
            f"{TAB(1)}{name.ljust(max_len)} - {block._desc}" for name, block in self._commands.items()
        )


class EmptyType(INodeType):
    def __init__(self, op, value):
        super().__init__(op, value, "empty")

    @classmethod
    def parse(cls, op: str, value: str, **kwargs) -> Union[Self, None]:
        if op or value:
            raise ValueError(f"EmptyNode({op}, {value}) should not have any operation or value")
        return cls('', True)


class BoolType(INodeType):
    def __init__(self, op, value):
        super().__init__(op, value, "bool")

    @classmethod
    def parse(cls, op: str, value: str, **kwargs) -> Union[Self, None]:
        if (
            cls._raise_unsupported_ops(op, ["="])
            and (val := value.lower()) in ["true", "false"]
        ):
            return cls(op, True if val == "true" else False)
        raise ValueError(f"BoolNode({op}, {value}) should only have '=' operation with 'true' or 'false' value")


class StringType(INodeType):
    def __init__(self, op, value):
        super().__init__(op, value, "string")

    @classmethod
    def parse(cls, op: str, value: str, **kwargs) -> Union[Self, None]:
        if cls._raise_unsupported_ops(op, ["="]) and isinstance(value, str):
            return cls(op, str(value))
        raise ValueError(f"StringNode({op}, {value}) only supports '=' operation with a non-empty string value")


class UIntType(INodeType):
    def __init__(self, op, value):
        super().__init__(op, value, "uint")

    @classmethod
    def parse(cls, op: str, value: str, **kwargs) -> Union[Self, None]:
        if not value.isdigit() and int(value) < 0:
            raise ValueError(f"UIntNode({op}, {value}) should only have a non-negative integer value")
        cls._raise_unsupported_ops(op, ["=", "<", ">"])
        return cls(op, int(value))


class DateType(INodeType):
    def __init__(self, op, value):
        super().__init__(op, value, "date")
    
    @classmethod
    def parse(cls, op: str, value: str, **kwargs) -> Union[Self, None]:
        try:
            if value == 'now':
                dt = datetime(*(datetime.now().timetuple()[:3]))
            else:
                dt = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"DateNode({op}, {value}) '{value}' is not a valid datetime string")

        cls._raise_unsupported_ops(op, ["=", "<", ">"])
        return cls(op, dt)


class EnumType(INodeType):
    def __init__(self, op, value):
        super().__init__(op, value, "enum")
        
    @classmethod
    def parse(cls, op: str, value: str, **kwargs) -> Union[Self, None]:
        cls._raise_unsupported_ops(op, ["=", "<", ">"])
        alias: YamlEnumNode = kwargs.get("alias", None)
        if alias is None:
            raise ValueError(f"EnumNode({op}, {value}) requires 'alias' in kwargs for evaluation")
        if not alias.contains_value(value):
            raise ValueError(f"EnumNode({op}, {value}) '{value}' is not a valid enum value in {alias.name}")
        return cls(op, value)


class YamlLeafNode(INode):
    def __init__(self, name, def_type, desc, fn_cb, node_type, alias):
        self._node_type: INodeType = node_type
        self._alias: INode = alias
        super().__init__(name, def_type, desc, fn_cb)
    
    @classmethod
    def parse_yaml(cls, data: dict, typedefs: YamlTypeDefs, mapper_cb: ICallbackMapper) -> Self:
        """Parse a leaf node including types: empty, string, uint, date, bool, and custom types from type defs"""
        if data:
            if len(data) > 1:
                raise TypeError(f"Data received more than one leaf value: {data}")
            for leaf_name, leaf_values in data.items():
                leaf_type = leaf_values.get("_type_", None)
                desc_type = leaf_values.get("_desc_", "N/A")
                fn_cb = leaf_values.get("_callback_", None)

                if leaf_type is None:
                    raise TypeError(f"Leaf value does not exist for {leaf_name}")
                
                if fn_cb:
                    if fn_cb not in mapper_cb:
                        raise ValueError(f"Leaf {leaf_name} fn cb {fn_cb} not found in mapper")
                    fn_cb = mapper_cb[fn_cb]

                leaf_type, alias = typedefs.get_type(leaf_type) or (leaf_type, dict())
                match leaf_type:
                    case "empty":
                        node_type = EmptyType
                    case "string":
                        node_type = StringType
                    case "uint":
                        node_type = UIntType
                    case "date":
                        node_type = DateType
                    case "bool":
                        node_type = BoolType
                    case "enum":
                        node_type = EnumType
                        alias["alias"] = typedefs.get_typedef(alias["alias"])      
                    case _:
                        raise TypeError(f"Type {leaf_type} is not found or supported")

            return cls(leaf_name, leaf_type, desc_type, fn_cb, node_type, alias)

    def process(self, op, value) -> INodeType:
        node = self._node_type.parse(op, value, **self._alias)
        if self.fn_cb and not self.fn_cb(**{self.name: node}):
            raise ValueError(f"Callback failed in {self._fn_cb.__name__}")
        return node

class YamlEnumNode(INode):
    
    def __init__(self, name, values, desc):
        self._values: dict = values
        super().__init__(name, "enum", desc)
    
    def contains_member(self, member):
        return member in self._values.keys()
    
    def contains_value(self, val):
        return val in self._values.values()
    
    @classmethod
    def parse_yaml(cls, data: dict) -> Self:
        """Parse enum node including types: enum"""
        if data:
            name = next(iter(data))
            values = data[name]
            desc = values.get("_desc_", "")
            enum_type = values.get("_type_", None)

            if not enum_type == "enum":
                raise TypeError(f"Enum type is missing or invalid for {name}")

            # Remove "_desc_" and "_type_" keys from values without modifying values itself
            enum_values = {k: v for k, v in values.items() if k not in ("_desc_", "_type_")}
            return cls(name, enum_values, desc)
        
    def process(self, cmd_lst: List[str]) -> bool:
        pass
            

class YamlTypeDefs:

    def __init__(self, type_defs, aliases):
        self._type_defs: Dict[str, str] = type_defs 
        self._aliases: Dict[str, INode] = aliases

    @classmethod
    def parse_yaml(cls, data: dict) -> Self:
        """Parse _typedefs_ from the yaml including types: enum"""
        if data:
            aliases = dict()
            type_defs = dict()
            for name, values in data.items():
                values_type = values.get("_type_", None)

                if values_type is None:
                    raise TypeError(f"_type_ is missing under {name}")
                
                if name in type_defs:
                    raise TypeError(f"Duplicate name in type defs: {name}")

                if values_type == "enum":
                    aliases[name] = YamlEnumNode.parse_yaml({name: values})
                elif not(values_type in base_types or values_type in type_defs):
                    raise TypeError(f"Invalid type in typedefs: {values_type}")

                type_defs[name] = values_type

            return cls(type_defs, aliases)
        
    def contains(self, member: str) -> bool:
        return member in self._type_defs
    
    def get_typedef(self, member: str) -> Optional[INode]:
        return self._aliases.get(member, None)
    
    def get_type(self, member: str) -> Union[str]:
        if member not in self._type_defs:
            return None
        
        def_type = self._type_defs.get(member, None)
        sub_type = dict()
        seen = set()
        while def_type and def_type not in base_types and def_type not in seen:
            seen.add(def_type)
            sub_type["alias"] = def_type
            def_type = self._type_defs.get(def_type, None)
        
        if not def_type:
            raise ValueError(f"Type definition for {member} is not found or invalid")
        
        return def_type, sub_type

class YamlBlock(GetCommands):

    def __init__(
        self,
        name,
        desc,
        sub_blocks,
        cb_fn=None,
    ):
        self._name: str = name
        self._desc: str = desc
        self._sub_blocks: Dict[str, Union[YamlBlock, YamlLeafNode]] = sub_blocks
        self._cb_fn: Optional[Callable] = cb_fn
        super().__init__(self._sub_blocks)

    @classmethod
    def parse_yaml(
        cls,
        data: dict,
        typedefs: YamlTypeDefs,
        mapper_cb: ICallbackMapper
    ) -> Self:
        """Parse Configs commands to Blocks - Blocks can contain sub blocks or leaf/grouping nodes"""
        if data:
            blocks = dict()
            desc = ""
            cb_fn = None
            block_name = list(data.keys())[0]
            block_values = data[block_name]
            for values_name, values_value in block_values.items():
                match values_name:
                    case "_desc_":
                        desc = values_value
                    case "_callback_":
                        assert values_value in mapper_cb, f"Cannot find callback {values_value} in mapper"
                        cb_fn = mapper_cb[values_value]
                    case _ if "_type_" in values_value:
                        blocks[values_name] = YamlLeafNode.parse_yaml({values_name:values_value}, typedefs, mapper_cb)
                    case _:
                        blocks[values_name] = YamlBlock.parse_yaml({values_name:values_value}, typedefs, mapper_cb)
            return cls(block_name, desc, blocks, cb_fn)
    
    def process(self, cmd_lst: List[str]) -> bool:
        """
        1. Find the sub block by name
        2. Process that block - if command is empty but block is incomplete, return
        3. Call validation function if provided
        4. Call callback function if provided
        """
        result = True
        leafs = dict()

        while cmd_lst:
            cmd = cmd_lst.pop(0)
            if cmd == "?":
                return self.get_cmds()
            
            args = re.split(r'(=|<|>)', cmd, maxsplit=1)

            block_name, op, value = '', '', ''
            if len(args) == 1:
                block_name = args[0].strip()
            elif len(args) == 3:
                block_name, op, value = map(str.strip, args)
            else:
                raise ValueError(f"Invalid command syntax: {cmd}")
            
            if (block := self._sub_blocks.get(block_name, None)) is None:
                raise ValueError(f"{block_name} is not defined in block {self._name}")
            
            if isinstance(block, YamlLeafNode):
                leafs[block_name] = block.process(op, value)
            elif isinstance(block, YamlBlock):
                result = block.process(cmd_lst)
            else:
                raise NotImplementedError(f"Block type {type(block)} is not supported in block {self._name}")

        if not result:
            raise ValueError(f"{self._name} returns None/False")

        if self._cb_fn and not self._cb_fn(**leafs):
            raise SystemError(f"Callback function failed in block {block_name}")

        return result

class YamlConfigs(GetCommands):

    def __init__(self, blocks):
        self._blocks: Dict[str, YamlBlock] = blocks
        super().__init__(self._blocks)

    @classmethod
    def parse_yaml(
        cls,
        data: dict,
        type_defs: YamlTypeDefs,
        mapper_cb: Any
    ) -> Self:
        """Parse Configs commands to Blocks"""
        blocks = dict()
        for name, values in data.items():
            if name in blocks:
                raise TypeError(f"Duplicate config command found: {name}")
            blocks[name] = YamlBlock.parse_yaml({name: values}, type_defs, mapper_cb)
        return cls(blocks)

    def process(self, cmd_list: List[str]) -> bool:
        if not cmd_list:
            return False
        
        match cmd_list[0]:
            case "?":
                return self.get_cmds()
            case _ if (block := self._blocks.get(cmd_list[0], None)):
                return block.process(cmd_list[1:])
            case _:
                raise ValueError(f"Invalid command, {cmd_list[0]} does not exist.")


class YamlOpers(GetCommands):
    
    def __init__(self, blocks):
        self._blocks : Dict[str, YamlBlock] = blocks
        super().__init__(self._blocks)

    @classmethod
    def parse_yaml(
        cls,
        data: dict,
        type_defs: YamlTypeDefs,
        mapper_cb: Any
    ) -> Self:
        """Parse Opers commands to Opers Blocks"""       
        blocks = dict()
        for name, values in data.items():
            if name in blocks:
                raise TypeError(f"Duplicate oper command found: {name}")
            blocks[name] = YamlBlock.parse_yaml({name: values}, type_defs, mapper_cb)
        return cls(blocks)
            
    def process(self, cmd_list: List[str]) -> bool:
        if not cmd_list:
            return False
        
        match cmd_list[0]:
            case "?":
                return self.get_cmds()
            case _ if (block := self._blocks.get(cmd_list[0], None)):
                return block.process(cmd_list[1:])
            case _:
                raise ValueError(f"Invalid command, {cmd_list[0]} does not exist.")


class YamlRootNode:
    
    def __init__(self, name, cb_fns, configs, opers):
        self._name = name
        self._cb_fns: dict = cb_fns
        self._configs: YamlConfigs = configs
        self._opers: YamlOpers = opers

    @property
    def name(self) -> str:
        return self._name
    
    def get_cmds(self):
        return (
            f"{TAB(1)}config         - Execute config commands\n"
            f"{TAB(1)}show           - Execute oper commands\n"
        )
    
    def process(self, cmd_list: List[str]) -> bool:
        """
        Process command list at root, 
        if starts with "show":oper, "no":negate config, else config
        Empty command list means newline in command
        """
        if not cmd_list:
            return True
        try:
            match cmd_list[0].lower():
                case "show":
                    return self._opers.process(cmd_list[1:])
                case "config":
                    #TODO: parse "no" and pass into configs
                    return self._configs.process(cmd_list[1:])
                case _:
                    return ""
        except Exception as e:
            print(f"Error: {e}")

class YamlCommandParser:
    _yaml_dir: str = os.path.join(str(pathlib.Path(__file__).parent.absolute()),"yaml")

    def __init__(self):
        self._yaml_tree : YamlRootNode = None

    def parse(self, root_name: str) -> Self:
        yaml_file = f"{root_name}.yaml"
        with open(os.path.join(self._yaml_dir, yaml_file)) as fp:
            yaml_data = yaml.safe_load(fp.read())
            assert yaml_data is not None, f"{root_name} yaml file is invalid"
            self._parse_tag_section(yaml_data)
            return self

    def process(self, cmd: str) -> bool:
        cmd_list = shlex.split(cmd)
        if self._yaml_tree is None:
            return False
        return self._yaml_tree.process(cmd_list)
    
    @classmethod
    def yaml_file_exists(cls, cmd_file):
        return os.path.exists(os.path.join(cls._yaml_dir, cmd_file + ".yaml"))
    
    @classmethod
    def get_yaml_files(cls):
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(cls._yaml_dir)
            if os.path.isfile(os.path.join(cls._yaml_dir, f)) and f not in ('.', '..')
        ]
    
    def get_cmds(self):
        if self._yaml_tree is None:
            return ""
        return f"[{self._yaml_tree.name}]\n" + self._yaml_tree.get_cmds()
        
    def _parse_tag_section(self, yaml_data: dict):
        """Parse root sections - _typedefs_, _groupings_, _configs_, _opers_"""
        tag = list(yaml_data.keys())[0]    
        if (mapper_cb := yaml_cb_fns_mapper.get(tag, None)) is None:
            raise ValueError(f"Unable to find callback functions for {tag}")

        type_defs = YamlTypeDefs.parse_yaml(yaml_data[tag].get("_typedefs_", {}))

        configs = YamlConfigs.parse_yaml(yaml_data[tag].get("_configs_", {}),
                                         type_defs,
                                         mapper_cb)

        opers = YamlOpers.parse_yaml(yaml_data[tag].get("_opers_", {}),
                                     type_defs,
                                     mapper_cb)
            
        self._yaml_tree = YamlRootNode(tag, mapper_cb, configs, opers)
