from typing import Dict, Any, List, Optional, Union

from blurr.core.errors import BaseSchemaError, InvalidTypeError, TypeLoaderError, SpecNotFoundError
from blurr.core.errors import SchemaErrorCollection
from blurr.core.loader import TypeLoader
from blurr.core.type import Type
from blurr.core.validator import ATTRIBUTE_TYPE, ATTRIBUTE_NAME, validate_required_attributes


class SchemaLoader:
    """
    Provides functionality to operate on the schema using fully qualified names.
    """
    ITEM_SEPARATOR = '.'

    def __init__(self):
        self._spec_cache: Dict[str, Any] = {}
        self._schema_cache: Dict[str, 'BaseSchema'] = {}
        self._error_cache: SchemaErrorCollection = SchemaErrorCollection()
        self._store_cache: Dict[str, 'Store'] = {}

    def add_schema_spec(self, spec: Dict[str, Any],
                        fully_qualified_parent_name: str = None) -> Optional[str]:
        """
        Add a schema dictionary to the schema loader. The given schema is stored
        against fully_qualified_parent_name + ITEM_SEPARATOR('.') + schema.name.
        :param spec: Schema specification.
        :param fully_qualified_parent_name: Full qualified name of the parent.
        If None is passed then the schema is stored against the schema name.
        :return: The fully qualified name against which the spec is stored.
        None is returned if the given spec is not a dictionary or the spec does not
        contain a 'name' key.
        """
        if not isinstance(spec, dict) or ATTRIBUTE_NAME not in spec:
            return None

        name = spec[ATTRIBUTE_NAME]
        fully_qualified_name = name if fully_qualified_parent_name is None else self.get_fully_qualified_name(
            fully_qualified_parent_name, name)

        # Ensure that basic validation for each spec part is done before it is added to spec cache
        if isinstance(spec, dict):
            self._error_cache.add(
                validate_required_attributes(fully_qualified_name, spec, ATTRIBUTE_NAME,
                                             ATTRIBUTE_TYPE))
            if ATTRIBUTE_TYPE in spec and not Type.contains(spec[ATTRIBUTE_TYPE]):
                self._error_cache.add(
                    InvalidTypeError(fully_qualified_name, spec, ATTRIBUTE_TYPE,
                                     InvalidTypeError.Reason.TYPE_NOT_DEFINED))

        self._spec_cache[fully_qualified_name] = spec
        for key, val in spec.items():
            if isinstance(val, list):
                for item in val:
                    self.add_schema_spec(item, fully_qualified_name)
            self.add_schema_spec(val, fully_qualified_name)

        return spec[ATTRIBUTE_NAME]

    def add_errors(self, *errors: Union[BaseSchemaError, SchemaErrorCollection]) -> None:
        """ Adds errors to the error store for the schema """
        for error in errors:
            self._error_cache.add(error)

    def get_errors(self, fully_qualified_name: str = None,
                   include_nested: bool = True) -> List[BaseSchemaError]:
        if not fully_qualified_name:
            return self._error_cache.errors

        return self._error_cache[fully_qualified_name] + ([
            error for error in self._error_cache.errors
            if error.fully_qualified_name.startswith(fully_qualified_name + self.ITEM_SEPARATOR)
        ] if include_nested else [])

    def raise_errors(self) -> None:
        """ Raises errors that have been collected in the error cache """
        self._error_cache.raise_errors()

    # Using forward reference to avoid cyclic dependency.
    def get_schema_object(self, fully_qualified_name: str) -> 'BaseSchema':
        """
        Used to generate a schema object from the given fully_qualified_name.
        :param fully_qualified_name: The fully qualified name of the object needed.
        :return: An initialized schema object
        """

        if fully_qualified_name not in self._schema_cache:
            spec = self.get_schema_spec(fully_qualified_name)

            if spec:
                try:
                    self._schema_cache[fully_qualified_name] = TypeLoader.load_schema(
                        spec.get(ATTRIBUTE_TYPE, None))(fully_qualified_name, self)
                except TypeLoaderError as err:
                    self.add_errors(
                        InvalidTypeError(fully_qualified_name, spec, ATTRIBUTE_TYPE,
                                         InvalidTypeError.Reason.TYPE_NOT_LOADED,
                                         err.type_class_name))

        return self._schema_cache.get(fully_qualified_name, None)

    def get_store(self, fully_qualified_name: str) -> Optional['Store']:
        """
        Used to generate a store object from the given fully_qualified_name.
        :param fully_qualified_name: The fully qualified name of the store object needed.
        :return: An initialized store object
        """

        if fully_qualified_name not in self._store_cache:
            schema = self.get_schema_object(fully_qualified_name)
            if not schema:
                return None

            if Type.is_store_type(schema.type):
                self._store_cache[fully_qualified_name] = TypeLoader.load_item(schema.type)(schema)
            else:
                self.add_errors(
                    InvalidTypeError(fully_qualified_name, {}, ATTRIBUTE_TYPE,
                                     InvalidTypeError.Reason.INCORRECT_BASE, schema.type,
                                     InvalidTypeError.BaseTypes.STORE))

        return self._store_cache.get(fully_qualified_name, None)

    def get_all_stores(self) -> List['Store']:
        """
        Returns a list of stores that have been instantiated.
        """
        return list(self._store_cache.values())

    def get_nested_schema_object(self, fully_qualified_parent_name: str,
                                 nested_item_name: str) -> Optional['BaseSchema']:
        """
        Used to generate a schema object from the given fully_qualified_parent_name
        and the nested_item_name.
        :param fully_qualified_parent_name: The fully qualified name of the parent.
        :param nested_item_name: The nested item name.
        :return: An initialized schema object of the nested item.
        """
        return self.get_schema_object(
            self.get_fully_qualified_name(fully_qualified_parent_name, nested_item_name))

    @staticmethod
    def get_fully_qualified_name(fully_qualified_parent_name: str, nested_item_name: str) -> str:
        """
        Returns the fully qualified name by combining the fully_qualified_parent_name
        and nested_item_name.
        :param fully_qualified_parent_name: The fully qualified name of the parent.
        :param nested_item_name: The nested item name.
        :return: The fully qualified name of the nested item.
        """
        return fully_qualified_parent_name + SchemaLoader.ITEM_SEPARATOR + nested_item_name

    def get_schema_spec(self, fully_qualified_name: str) -> Dict[str, Any]:
        """
        Used to retrieve the specifications of the schema from the given
        fully_qualified_name of schema.
        :param fully_qualified_name: The fully qualified name of the schema needed.
        :return: Schema dictionary.
        """

        if fully_qualified_name not in self._spec_cache:
            self.add_errors(SpecNotFoundError(fully_qualified_name, {}))

        return self._spec_cache.get(fully_qualified_name, None)

    def has_schema_spec(self, fully_qualified_name: str) -> bool:
        """
        Checks if a schema spec exists in the schema loader
        :param fully_qualified_name: The fully qualified name of the schema needed.
        :return: True if spec definition exists, False otherwise.
        """

        return fully_qualified_name in self._spec_cache

    def get_schema_specs_of_type(self, *schema_types: Type) -> Dict[str, Dict[str, Any]]:
        """
        Returns a list of fully qualified names and schema dictionary tuples for
        the schema types provided.
        :param schema_types: Schema types.
        :return: List of fully qualified names and schema dictionary tuples.
        """

        return {
            fq_name: schema
            for fq_name, schema in self._spec_cache.items()
            if Type.is_type_in(schema.get(ATTRIBUTE_TYPE, ''), list(schema_types))
        }

    @staticmethod
    def get_transformer_name(fully_qualified_name: str) -> str:
        """
        Returns the BTS transformer name based on the given fully_qualified_name
        of one of the nested child items.
        :param fully_qualified_name: Fully qualified name of the nested child item.
        :return: BTS transformer name.
        """
        return fully_qualified_name.split(SchemaLoader.ITEM_SEPARATOR, 1)[0]
