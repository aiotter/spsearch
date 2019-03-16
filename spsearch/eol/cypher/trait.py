from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core import CypherExecutor


class BaseTerm:
    def __hash__(self):
        return hash(self.uri)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.name}">'


class TraitProxy(BaseTerm):
    # 軽量のTrait。最低限の情報を持つ
    def __init__(self, uri, name):
        self.uri = uri
        self.name = name


class Resource(BaseTerm):
    def __init__(self, data:dict):
        self._data = data
        self.resource_id = data.get('resource_id')


class Predicate(BaseTerm):
    def __init__(self, data: dict):
        self._data = data
        self.name = data.get('name')
        self.definition = data.get('definition')
        self.position = data.get('position')
        self.uri = data.get('uri')
        self.used_for = data.get('used_for')


class Object(BaseTerm):
    def __init__(self, data: dict):
        self._data = data
        self.attribution = data.get('attribution')
        self.definition = data.get('definition')
        self.name = data.get('name')
        self.uri = data.get('uri')
        self.position = data.get('position')
        self.type = data.get('type')
        self.used_for = data.get('used_for')


class Units(BaseTerm):
    def __init__(self, data: dict):
        self._data = data
        self.name = data.get('name')
        self.definition = data.get('definition')
        self.position = data.get('position')
        self.type = data.get('type')
        self.uri = data.get('uri')


class Literal(BaseTerm):
    def __init__(self, data: dict):
        self._data = data
        self.attribution = data.get('attribution')
        self.definition = data.get('definition')
        self.name = data.get('name')
        self.uri = data.get('uri')
        self.position = data.get('position')
        self.type = data.get('type')
        self.used_for = data.get('used_for')


class Trait:
    def __init__(self, executor: 'CypherExecutor', page, trait: dict, resource: dict, predicate: dict,
                 object: dict, units: dict, literal:dict):
        # Predicate は情報の種類を表す。
        # 情報がカテゴリデータであれば Trait.literal が情報の内容を示す。
        # 情報が数値データであれば、Trait.measurement がその大きさを、Trait.units が単位を示す。

        # Trait.type は measurement, association, None, '', metadata, value の6種。
        # measurement: 'extinction status', 'testis location', 'body temperature', 'locomotion', 'body mass',
        #              'habitat is', 'actual evapotranspiration rate in geographic range', 'age at eye opening',
        #              'diet breadth', 'dispersal age'
        # association: 'flowers visited by', 'has pathogen', 'kills', 'pathogen of', 'visits flowers of',
        #              'interacts with', 'eats', 'preys on', 'parasite of', 'pollinates'
        # metadata:    'scientific name', 'measurement remarks', 'locality', 'catalog number', 'individual count',
        #              'institution code', 'preparations', 'recorded by', 'type status', 'identified by'
        # value:       'protein composition of milk', 'body length', 'cytosol', 'larval mode of development',
        #              'nutrient composition of milk', 'semi-aquatic'
        # '':          'PlantHabit', 'Total length', 'Colonial', 'Body Temperature'

        self._data = trait
        self.executor = executor
        self.measurement = trait.get('normal_measurement') # normal_measurement は 83.59999999999999 を 83.6 に丸めたもの
        self.page = page
        self.eol_pk = trait.get('eol_pk')
        self.source = trait.get('source')
        self.type = trait.get('type')
        self.resource = Resource(resource)
        self.predicate = Predicate(predicate)
        self.object = Object(object) if object else None
        self.units = Units(units) if units else None
        self.literal = Literal(literal) if literal else None

    @property
    def key(self):
        # pk は primary key の略
        return self.eol_pk

    @property
    def id(self):
        return self.eol_pk

    @property
    def category(self):
        return self.predicate.name

    @property
    def category_definition(self):
        return self.predicate.definition

    @property
    def category_definition_uri(self):
        return self.predicate.uri

    @property
    def value(self):
        if self.measurement and self.units:
            return f"{self.measurement} {self.units.name}"
        elif self.object:
            return self.object.name
        else:
            return self.literal.name

    @property
    def value_definition(self):
        if self.measurement and self.units:
            return self.units.definition
        elif self.object:
            return self.object.definition
        else:
            return self.literal.definition

    @property
    def value_definition_uri(self):
        if self.measurement and self.units:
            return self.units.uri
        elif self.object:
            return self.object.uri
        else:
            return self.literal.uri

    def __str__(self):
        return f"{self.category}: {self.value}"

    def __repr__(self):
        return f"<Trait for {self.page.canonical}({self.page.page_id}): {self.category}: {self.value}>"

    def __hash__(self):
        return hash(self.eol_pk)
