from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Self, Union, Any
import pathlib
import os
import yaml

if __name__ == "__main__":
    from .docks_clan_cb import docks_clan_cb
    from .mgmt_abc import ICallbackMapper

yaml_cb_fns_mapper: Dict[str, ICallbackMapper] = {
    "docks_clan_commands": docks_clan_cb
}

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
    def parse_yaml(cls, data) -> bool:
        pass

    @abstractmethod
    def process(self, cmd_lst:List[str]) -> bool:
        pass


class YamlLeafNode(Node):
    def __init__(self, name, def_type, desc, fn_cb, mandatory):
        super().__init__(name, def_type, desc, fn_cb, mandatory)
    
    @classmethod
    def parse_yaml(cls, data: dict, typedefs: YamlTypeDefs) -> Self:
        """Parse a leaf node including types: empty, string, uint, date, bool, and custom types from type defs"""
        if data:
            if len(data) > 1:
                raise TypeError(f"Data received more than one value: {data}")
            
            for leaf_name, leaf_values in data.items():
                leaf_type = leaf_values.get("_type_", None)
                desc_type = leaf_values.get("_desc_", "")
                fn_cb = leaf_values.get("_callback_", None)
                mandatory = leaf_values.get("_mandatory_", False)

                if leaf_type is None:
                    raise TypeError(f"Leaf value does not exist for {leaf_name}")
                
                match leaf_name:
                    case ("empty" | "string" | "uint" | "date" | "bool") :
                        break
                    case _ if typedefs.contains(leaf_name):
                        break
                    case _:
                        raise TypeError(f"Type {leaf_type} is not found or supported")

                return cls(leaf_name, leaf_type, desc_type, fn_cb, mandatory)

class YamlEnumNode(Node):
    
    def __init__(self, name, values, desc):
        self._values: dict = values
        super().__init__(name, "enum", desc)
    
    def contains_member(self, member):
        return member in self._values.keys()
    
    def get_value(self, member):
        return self._values.get(member, None)

class YamlTypeDefs:

    def __init__(self, type_defs, enums):
        self._type_defs: Dict[str, str] = type_defs 
        self._enums: Dict[str, YamlEnumNode] = enums

    @classmethod
    def parse_yaml(cls, data: dict) -> Self:
        """Parse _macros_ from the yaml including types: enum"""
        if data:
            enums = dict()
            type_defs = dict()
            for name, values in data:
                values_type = values.pop("_type_", None)
                values_desc = values.pop("_desc_", "")
                if values_type is None:
                    raise TypeError(f"_type_ is missing under {name}")
                
                if name in type_defs:
                    raise TypeError(f"Duplicate name in type defs: {name}")

                type_defs[name] = values_type
                match values_type:
                    case "enum":
                        enums[name] = YamlEnumNode(name, values, values_desc)
                    case _:
                        raise TypeError(f"Invalid type in macros: {values_type}")
                
            return cls(type_defs, enums)
        
    def contains(self, member: str) -> bool:
        return member in self._type_defs
    
    def get(self, member: str, value: str) -> Union[str]:
        if member not in self._type_defs:
            return None
        
        match self._type_defs[member]:
            case "enum":
                return self._enums[member].get_value(value)
            case _:
                raise TypeError(f"Should not reach here, something's wrong: {self._type_defs[member]}")
    

class YamlGroupings:

    def __init__(self, groupings, typedefs):
        self._groupings : dict = groupings
        self._typedefs: YamlTypeDefs = typedefs

    @classmethod
    def parse_yaml(cls, data, typedefs: YamlTypeDefs) -> Self:
        """Parse _groupings_ from yaml"""
        if data:
            groupings = dict()
            for grouping_name, values in data:
                if grouping_name in groupings:
                    raise TypeError(f"Duplicate name in groupings: {grouping_name}")
                leaf_nodes = dict()
                for leaf_name in values:
                    if leaf_name in leaf_nodes:
                        raise TypeError(f"Duplicate name in grouping {grouping_name}: {leaf_name}")
                    leaf_nodes[leaf_name] = YamlLeafNode.parse_yaml(values, typedefs)
                groupings[grouping_name] = leaf_nodes
            return cls(groupings, typedefs)

class YamlBlock:

    def __init__(self, name, desc, validate_fn, cb):
        self._desc: str = desc
        self._cb: Optional[Callable] = cb
        self._validate_fn: Optional[Callable] = validate_fn

    @classmethod
    def parse_yaml(cls, data: dict, type_defs: YamlTypeDefs, groupings: YamlGroupings, mapper_cb: Any) -> Self:
        pass

    def process(self, cmd_lst: List[str]) -> bool:
        ...


class YamlConfigs:

    def __init__(self, blocks):
        self._blocks: Dict[str, YamlBlock] = blocks

    @classmethod
    def parse_yaml(cls, data: dict, type_defs: YamlTypeDefs, groupings: YamlGroupings, mapper_cb: Any) -> Self:
        """Parse Configs commands to Blocks"""
        blocks = dict()
        for name, values in data.items():
            if name in blocks:
                raise TypeError(f"Duplicate config command found: {name}")
            blocks[name] = YamlBlock.parse_yaml(values, type_defs, groupings, mapper_cb)
        return cls(blocks)

    def process(self, cmd_list: List[str]) -> bool:
        if (not cmd_list) or (block := self._blocks.get(cmd_list[0], None)) is None:
            return False
        return block.process(cmd_list[0])


class YamlOpers:
    
    def __init__(self, blocks):
        self._blocks : Dict[str, YamlBlock] = blocks

    @classmethod
    def parse_yaml(cls, data: dict, type_defs: YamlTypeDefs, groupings: YamlGroupings, mapper_cb: Any) -> Self:
        """Parse Opers commands to Opers Blocks"""       
        blocks = dict()
        for name, values in data.items():
            if name in blocks:
                raise TypeError(f"Duplicate oper command found: {name}")
            blocks[name] = YamlBlock.parse_yaml(values, type_defs, groupings, mapper_cb)
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

        match cmd_list[0]:
            case "show":
                return self._opers.process(cmd_list[1:])
            case _:
                return self._configs.process(cmd_list[1:])

class YamlCommandParser:

    def __init__(self):
        self._yaml_dir: str = os.path.join(str(pathlib.Path(__file__).parent.absolute()),"yaml")
        self._yaml_tree : YamlRootNode = None

    def init_yaml_commands(self, root_name: str) -> Self:
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
        """Parse root sections - _macros_, _groupings_, _configs_, _opers_"""
        tag = yaml_data.keys()[0]      
        if (mapper_cb := yaml_cb_fns_mapper.get(tag, None)) is None:
            return False
        
        type_defs = YamlTypeDefs.parse_yaml(yaml_data[tag].get("_typedefs_", {}))
        groupings = YamlGroupings.parse_yaml(yaml_data[tag].get("_groupings_", {}),
                                             type_defs)
        configs = YamlConfigs.parse_yaml(yaml_data[tag].get("_configs_", {}),
                                         type_defs,
                                         groupings,
                                         mapper_cb)
        opers = YamlOpers.parse_yaml(yaml_data[tag].get("_opers_", {}),
                                     type_defs,
                                     groupings,
                                     mapper_cb)
            
        self._yaml_tree = YamlRootNode(tag, configs, opers)
