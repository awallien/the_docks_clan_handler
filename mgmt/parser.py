from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Self, Set, Union, Any
import pathlib
import os
import yaml
from datetime import datetime

from .docks_clan_cb import docks_clan_cb
from .mgmt_abc import ICallbackMapper

yaml_cb_fns_mapper: Dict[str, ICallbackMapper] = {
    "docks_clan_commands": docks_clan_cb
}

base_types: Set[str] = {
    "string", "date", "uint",
    "enum", "bool", "empty"
}

class Op():
    def __init__(self, op: str, value: str):
        self.op: str = op
        self.value: str = value

    @classmethod
    def parse(cls, op: str, value: str) -> Union[Self, None]:
        if op not in ["=", "<", ">", ''] or not value:
            return None
        return cls(op, value)
        
    def expr_str(self, other: str) -> str:
        if not self.op or not other:
            return None
        return f"{other} {self.op} {self.value}"


class NodeType(ABC):
    def __init__(self):
        pass

    def raise_unsupported_ops(self, op: str, ops: List[str]) -> False:
        if op not in ops:
            raise ValueError(f"Operation '{op}' is not supported. Supported operations are: {', '.join(ops)}")
        return False

    @abstractmethod   
    def eval(self, op: str, value: str, **kwargs) -> Union[Op, None]:
        pass


class EmptyType(NodeType):
    def __init__(self):
        super().__init__()

    def eval(self, op: str, value: str, **kwargs) -> Union[Op, None]:
        if op or value:
            raise ValueError(f"EmptyNode({op}, {value}) should not have any operation or value")
        return Op.parse('', '')


class BoolType(NodeType):
    def __init__(self):
        super().__init__()

    def eval(self, op: str, value: str, **kwargs) -> Union[Op, None]:
        if (
            self.raise_unsupported_ops(op, ["="])
            and isinstance(value, str)
            and (val := value.lower()) in ["true", "false"]
        ):
            return Op.parse(op, val)
        raise ValueError(f"BoolNode({op}, {value}) should only have '=' operation with 'true' or 'false' value")


class StringType(NodeType):
    def __init__(self):
        super().__init__()

    def eval(self, op: str, value: str, **kwargs) -> Union[Op, None]:
        if self.raise_unsupported_ops(op, ["="]) and isinstance(value, str):
            return Op.parse(op, value)
        raise NotImplementedError(f"StringNode({op}, {value}) only supports '=' operation with a non-empty string value")


class UIntType(NodeType):
    def __init__(self):
        super().__init__()

    def eval(self, op: str, value: str, **kwargs) -> Union[Op, None]:
        if not value.isdigit() and int(value) < 0:
            raise ValueError(f"UIntNode({op}, {value}) should only have a non-negative integer value")
        self.raise_unsupported_ops(op, ["=", "<", ">"])
        return Op.parse(op, value)


class DateType(NodeType):
    def __init__(self):
        super().__init__()
    
    def eval(self, op: str, value: str, **kwargs) -> Union[Op, None]:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"DateNode({op}, {value}) '{value}' is not a valid datetime string")

        self.raise_unsupported_ops(op, ["=", "<", ">"])
        return Op.parse(op, dt.strftime("%Y-%m-%d"))


class EnumType(NodeType):
    def __init__(self):
        super().__init__()
        
    def eval(self, op: str, value: str, **kwargs) -> Union[Op, None]:
        self.raise_unsupported_ops(op, ["=", "<", ">"])
        rank_def: YamlEnumNode = kwargs.get("rank_def", None)
        if rank_def is None:
            raise ValueError(f"EnumNode({op}, {value}) requires 'rank_def' in kwargs for evaluation")
        if not rank_def.contains_value(value):
            raise ValueError(f"EnumNode({op}, {value}) '{value}' is not a valid enum value in {rank_def.name}")
        return Op.parse(op, value)


class Node(ABC):
    def __init__(self, name, def_type, desc, fn_cb=None, mandatory=False):
        self._name : str = name
        self._def_type : str = def_type
        self._desc : str = desc
        self._fn_cb : Callable = fn_cb
        self._mandatory = mandatory

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def def_type(self) -> str:
        return self._def_type

    @property
    def desc(self) -> str:
        return self._desc
    
    @property
    def fn_cb(self) -> Callable:
        return self.fn_cb
    
    @property
    def mandatory(self) -> bool:
        return self._mandatory
    
    @classmethod
    @abstractmethod
    def parse_yaml(cls, data) -> Any:
        pass

    @abstractmethod
    def process(self, cmd_lst:List[str]) -> Any:
        pass

    def _validate_process_syntax(self, cmd, cmd_len=None) -> bool:
        def raise_msg(msg):
            return f"Invalid syntax: {msg}"

        if cmd_len and not cmd_len == len(cmd):
            raise SyntaxError(raise_msg(f"Length of command does not match length {cmd_len}"))
        if "=" not in cmd:
            raise SyntaxError(raise_msg(f"{cmd} does not contain '='"))


class YamlLeafNode(Node):
    def __init__(self, name, def_type, desc, fn_cb, mandatory, node_type):
        self.node_type: NodeType = node_type
        super().__init__(name, def_type, desc, fn_cb, mandatory)
    
    @classmethod
    def parse_yaml(cls, data: dict, typedefs: YamlTypeDefs) -> Self:
        """Parse a leaf node including types: empty, string, uint, date, bool, and custom types from type defs"""
        if data:
            if len(data) > 1:
                raise TypeError(f"Data received more than one leaf value: {data}")
            for leaf_name, leaf_values in data.items():
                leaf_type = leaf_values.get("_type_", None)
                desc_type = leaf_values.get("_desc_", "")
                fn_cb = leaf_values.get("_callback_", None)
                mandatory = leaf_values.get("_mandatory_", False)

                if leaf_type is None:
                    raise TypeError(f"Leaf value does not exist for {leaf_name}")
                
                match leaf_type:
                    case "empty":
                        node_type = EmptyType()
                    case "string":
                        node_type = StringType()
                    case "uint":
                        node_type = UIntType()
                    case "date":
                        node_type = DateType()
                    case "bool":
                        node_type = BoolType()
                    case _ if typedefs.contains(leaf_type):
                        match typedefs.get(leaf_type).def_type:
                            case "enum":
                                node_type = EnumType()
                            case _:
                                raise TypeError(f"Type {leaf_type} is not found. Should not reach here.")
                    case _:
                        raise TypeError(f"Type {leaf_type} is not found or supported")

            return cls(leaf_name, leaf_type, desc_type, fn_cb, mandatory, node_type)

    def process(self, cmd_lst: List[str]) -> Any:
        pass

class YamlEnumNode(Node):
    
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
            

class OneOfNode(Node):
    def __init__(self, values, mandatory):
        self._leafs: Dict[str, YamlLeafNode] = values
        super().__init__(None, None, None, None, mandatory) 

    @classmethod
    def parse_yaml(cls, data: dict, typedefs: YamlTypeDefs) -> Self:
        if data:
            mandatory = False
            leafs = dict()
            for name, value in data.items():
                match name:
                    case "_mandatory_": 
                        mandatory = True
                    case _ if name in leafs:
                        raise ValueError(f"Duplicate leaf name found in _oneof_: {name}")
                    case _:
                        leafs[name] = YamlLeafNode.parse_yaml({name:value}, typedefs)
            
            return cls(leafs, mandatory)
    
    def process(self, cmd_lst:List[str]) -> Any:
        self._validate_process_syntax(cmd_lst, 1)
        name,value = cmd_lst[0].split("=")
        if name not in self._leafs:
            raise ValueError(f"{name} not found")
        return self._leafs[name].process([value])
    
    def __contains__(self, item: str) -> bool:
        return item in self._leafs

class YamlTypeDefs:

    def __init__(self, type_defs, enums):
        self._type_defs: Dict[str, str] = type_defs 
        self._enums: Dict[str, YamlEnumNode] = enums

    @classmethod
    def parse_yaml(cls, data: dict) -> Self:
        """Parse _typedefs_ from the yaml including types: enum"""
        if data:
            enums = dict()
            type_defs = dict()
            for name, values in data.items():
                values_type = values.get("_type_", None)

                if values_type is None:
                    raise TypeError(f"_type_ is missing under {name}")
                
                if name in type_defs:
                    raise TypeError(f"Duplicate name in type defs: {name}")

                if values_type == "enum":
                    enums[name] = YamlEnumNode.parse_yaml({name: values})
                elif not(values_type in base_types or values_type in type_defs):
                    raise TypeError(f"Invalid type in typedefs: {values_type}")

                type_defs[name] = values_type

            return cls(type_defs, enums)
        
    def contains(self, member: str) -> bool:
        return member in self._type_defs
    
    def get(self, member: str) -> Union[Node]:
        if member not in self._type_defs:
            raise ValueError(f"Member {member} not found in type definitions")
        
        match self._type_defs[member]:
            case "enum":
                return self._enums[member]
            case _:
                raise TypeError(f"Should not reach here, something's wrong: {self._type_defs[member]}")
    
class YamlBlock:

    def __init__(
        self,
        name,
        desc,
        sub_blocks,
        validate_fn=None,
        cb_fn=None,
        incomplete=False,
    ):
        self._name: str = name
        self._desc: str = desc
        self._sub_blocks: Dict[str, Union[YamlBlock, YamlLeafNode]] = sub_blocks
        self._incomplete: bool = incomplete
        self._cb_fn: Optional[Callable] = cb_fn
        self._validate_fn: Optional[Callable] = validate_fn

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
            incomplete = False
            desc = ""
            validate = None
            cb_fn = None
            block_name = list(data.keys())[0]
            block_values = data[block_name]
            for values_name, values_value in block_values.items():
                match values_name:
                    case "_incomplete_":
                        incomplete = values_value
                    case "_desc_":
                        desc = values_value
                    case "_validate_":
                        assert values_value in mapper_cb
                        validate = values_value
                    case "_callback_":
                        assert values_value in mapper_cb
                        cb_fn = values_value
                    case _ if "_type_" in values_value:
                        blocks[values_name] = YamlLeafNode.parse_yaml({values_name:values_value}, typedefs)
                    case "_oneof_":
                        blocks[f"{values_name}_{hash(str(values_value))}"] = OneOfNode.parse_yaml(values_value, typedefs)
                    case _:
                        blocks[values_name] = YamlBlock.parse_yaml({values_name:values_value}, typedefs, mapper_cb)
            return cls(block_name, desc, blocks, validate, cb_fn, incomplete)
            
    def process(self, cmd_lst: List[str]) -> bool:
        pass


class YamlConfigs:

    def __init__(self, blocks):
        self._blocks: Dict[str, YamlBlock] = blocks

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
        if (not cmd_list) or (block := self._blocks.get(cmd_list[0], None)) is None:
            return False
        return block.process(cmd_list[1:])


class YamlOpers:
    
    def __init__(self, blocks):
        self._blocks : Dict[str, YamlBlock] = blocks

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
        if (not cmd_list) or (block := self._blocks.get(cmd_list[0], None)) is None:
            return False
        return block.process(cmd_list[1:])


class YamlRootNode:
    
    def __init__(self, name, cb_fns, configs, opers):
        self._name = name
        self._cb_fns: dict = cb_fns
        self._configs: YamlConfigs = configs
        self._opers: YamlOpers = opers
    
    def process(self, cmd_list: List[str]) -> bool:
        """
        Process command list at root, 
        if starts with "show":oper, "no":negate config, else config
        Empty command list means newline in command
        """
        if not cmd_list:
            return True

        match cmd_list[0].lower():
            case "show":
                return self._opers.process(cmd_list[1:])
            case _:
                #TODO: parse "no" and pass into configs
                return self._configs.process(cmd_list[1:])

class YamlCommandParser:

    def __init__(self):
        self._yaml_dir: str = os.path.join(str(pathlib.Path(__file__).parent.absolute()),"yaml")
        self._yaml_tree : YamlRootNode = None

    def parse(self, root_name: str) -> Self:
        with open(os.path.join(self._yaml_dir, f"{root_name}.yaml")) as fp:
            yaml_data = yaml.safe_load(fp.read())
            assert yaml_data is not None, f"{root_name} yaml file is invalid"
            self._parse_tag_section(yaml_data)
            return self

    def process(self, cmd_list: List[str]) -> bool:
        if self._yaml_tree is None:
            return False
        return self._yaml_tree.process(cmd_list)
        
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
