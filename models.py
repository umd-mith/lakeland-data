"""

Omeka database schema created with peewee's pwiz utilty:

    python3 -m pwiz -e mysql -u root omekadblakeland -P

"""

from peewee import *
from peewee import SelectQuery


from os import environ

db_name = environ.get('DB_NAME')
db_user = environ.get('DB_USER')
db_password = environ.get('DB_PASSWORD')
database = MySQLDatabase(db_name, password=db_password, user=db_user)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Collection(BaseModel):
    added = DateTimeField()
    collectors = TextField()
    description = TextField()
    featured = IntegerField(index=True)
    modified = DateTimeField()
    name = CharField()
    owner = IntegerField(db_column='owner_id', index=True)
    public = IntegerField(index=True)

    class Meta:
        db_table = 'omeka_collections'

class Tag(BaseModel):
    name = CharField(null=True, unique=True)

    class Meta:
        db_table = 'omeka_tags'

class Tagging(BaseModel):
    entity = IntegerField(db_column='entity_id')
    relation = IntegerField(db_column='relation_id')
    tag = ForeignKeyField(Tag)
    time = DateTimeField()
    type = CharField()

    class Meta:
        db_table = 'omeka_taggings'
        indexes = (
            (('relation', 'tag', 'entity', 'type'), True),
        )

class ItemType(BaseModel):
    description = TextField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'omeka_item_types'

class ItemTypesElement(BaseModel):
    element = IntegerField(db_column='element_id', index=True)
    item_type = IntegerField(db_column='item_type_id', index=True)
    order = IntegerField(null=True)

    class Meta:
        db_table = 'omeka_item_types_elements'
        indexes = (
            (('item_type', 'element'), True),
        )

class Item(BaseModel):
    added = DateTimeField()
    collection = ForeignKeyField(Collection, null=True, related_name='items')
    featured = IntegerField(index=True)
    item_type = ForeignKeyField(ItemType, null=True, related_name='items')
    modified = DateTimeField()
    public = IntegerField(index=True)

    # also: files, locations, notes

    @property
    def tags(self):
        q = (Tag
             .select(Tag.name)
             .join(Tagging, on=(Tagging.tag_id == Tag.id))
             .join(Item, on=(Tagging.relation == Item.id))
             .where(Item.id == self.id, Tagging.type == 'Item'))
        for tag in q:
            yield tag.name

    @property
    def elements(self):
        m = {}
        for et in ElementTexts.select().where(ElementTexts.record == self.id):
            name = et.element.name
            value = et.text or et.html
            if name not in m:
                m[name] = []
            m[name].append(value)
        return m

    class Meta:
        db_table = 'omeka_items'

class ItemsSectionPage(BaseModel):
    caption = TextField(null=True)
    item = IntegerField(db_column='item_id', null=True)
    order = IntegerField()
    page = IntegerField(db_column='page_id')
    text = TextField(null=True)

    class Meta:
        db_table = 'omeka_items_section_pages'


class ContributionContributedItem(BaseModel):
    contributor = IntegerField(db_column='contributor_id')
    item = IntegerField(db_column='item_id', unique=True)
    public = IntegerField()

    class Meta:
        db_table = 'omeka_contribution_contributed_items'

class ContributionContributorField(BaseModel):
    order = IntegerField(index=True)
    prompt = CharField()
    type = CharField()

    class Meta:
        db_table = 'omeka_contribution_contributor_fields'

class ContributionContributorValue(BaseModel):
    contributor = IntegerField(db_column='contributor_id')
    field = IntegerField(db_column='field_id')
    value = TextField()

    class Meta:
        db_table = 'omeka_contribution_contributor_values'
        indexes = (
            (('contributor', 'field'), True),
        )

class ContributionContributor(BaseModel):
    email = CharField()
    ip_address = CharField()
    name = CharField()

    class Meta:
        db_table = 'omeka_contribution_contributors'

class ContributionTypeElement(BaseModel):
    element = IntegerField(db_column='element_id')
    order = IntegerField(index=True)
    prompt = CharField()
    type = IntegerField(db_column='type_id')

    class Meta:
        db_table = 'omeka_contribution_type_elements'
        indexes = (
            (('type', 'element'), True),
        )

class ContributionType(BaseModel):
    display_name = CharField()
    file_permissions = CharField()
    item_type = IntegerField(db_column='item_type_id', unique=True)

    class Meta:
        db_table = 'omeka_contribution_types'

class Contributor(BaseModel):
    birth_year = UnknownField(null=True)  # year
    entity = BigIntegerField(db_column='entity_id')
    gender = TextField(null=True)
    id = BigIntegerField(primary_key=True)
    ip_address = TextField()
    occupation = TextField(null=True)
    race = TextField(null=True)
    zipcode = TextField(null=True)

    class Meta:
        db_table = 'omeka_contributors'

class CsvImportImportedItem(BaseModel):
    import_ = IntegerField(db_column='import_id', index=True)
    item = IntegerField(db_column='item_id')

    class Meta:
        db_table = 'omeka_csv_import_imported_items'

class CsvImportImport(BaseModel):
    added = DateTimeField()
    collection = IntegerField(db_column='collection_id')
    csv_file_name = TextField()
    error_details = TextField(null=True)
    is_featured = IntegerField(null=True)
    is_public = IntegerField(null=True)
    item_count = IntegerField()
    item_type = IntegerField(db_column='item_type_id')
    serialized_column_maps = TextField()
    status = CharField(null=True)
    stop_import_if_file_download_error = IntegerField(null=True)

    class Meta:
        db_table = 'omeka_csv_import_imports'

class DataType(BaseModel):
    description = TextField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'omeka_data_types'

class Element(BaseModel):
    data_type = IntegerField(db_column='data_type_id', index=True)
    description = TextField(null=True)
    element_set = IntegerField(db_column='element_set_id', index=True)
    name = CharField()
    order = IntegerField(null=True)
    record_type = IntegerField(db_column='record_type_id', index=True)

    class Meta:
        db_table = 'omeka_elements'
        indexes = (
            (('element_set', 'name'), True),
            (('element_set', 'order'), True),
        )

class ElementSet(BaseModel):
    description = TextField(null=True)
    name = CharField(unique=True)
    record_type = IntegerField(db_column='record_type_id', index=True)

    class Meta:
        db_table = 'omeka_element_sets'

class ElementTexts(BaseModel):
    element = ForeignKeyField(Element)
    html = IntegerField()
    record = IntegerField(db_column='record_id', index=True)
    record_type = IntegerField(db_column='record_type_id', index=True)
    text = TextField(index=True)

    class Meta:
        db_table = 'omeka_element_texts'

class Entity(BaseModel):
    email = TextField(null=True)
    first_name = TextField(null=True)
    institution = TextField(null=True)
    last_name = TextField(null=True)
    middle_name = TextField(null=True)

    class Meta:
        db_table = 'omeka_entities'

class EntitiesRelations(BaseModel):
    entity = IntegerField(db_column='entity_id', null=True)
    relation = IntegerField(db_column='relation_id', index=True, null=True)
    relationship = IntegerField(db_column='relationship_id', index=True, null=True)
    time = DateTimeField(null=True)
    type = CharField(index=True)

    class Meta:
        db_table = 'omeka_entities_relations'

class EntityRelationship(BaseModel):
    description = TextField(null=True)
    name = TextField(null=True)

    class Meta:
        db_table = 'omeka_entity_relationships'

class Exhibit(BaseModel):
    credits = TextField(null=True)
    description = TextField(null=True)
    featured = IntegerField(null=True)
    public = IntegerField(index=True, null=True)
    slug = CharField(null=True, unique=True)
    theme = CharField(null=True)
    theme_options = TextField(null=True)
    title = CharField(null=True)

    class Meta:
        db_table = 'omeka_exhibits'

class File(BaseModel):
    added = DateTimeField()
    archive_filename = TextField()
    authentication = CharField(null=True)
    has_derivative_image = IntegerField()
    item = ForeignKeyField(Item, related_name='files')
    mime_browser = CharField(null=True)
    mime_os = CharField(null=True)
    modified = DateTimeField()
    original_filename = TextField()
    size = IntegerField()
    type_os = CharField(null=True)

    class Meta:
        db_table = 'omeka_files'


class Location(BaseModel):
    address = TextField()
    id = BigIntegerField(primary_key=True)
    item = ForeignKeyField(Item, related_name='locations')
    latitude = FloatField()
    longitude = FloatField()
    map_type = CharField()
    zoom_level = IntegerField()

    class Meta:
        db_table = 'omeka_locations'

class MimeElementSetLookup(BaseModel):
    element_set = IntegerField(db_column='element_set_id')
    mime = CharField(unique=True)

    class Meta:
        db_table = 'omeka_mime_element_set_lookup'

class Note(BaseModel):
    date_modified = DateTimeField()
    id = BigIntegerField(primary_key=True)
    item = ForeignKeyField(Item, related_name='notes')
    note = TextField()
    user = BigIntegerField(db_column='user_id')

    class Meta:
        db_table = 'omeka_notes'

class Option(BaseModel):
    name = CharField(unique=True)
    value = TextField(null=True)

    class Meta:
        db_table = 'omeka_options'

class Plugin(BaseModel):
    active = IntegerField(index=True)
    name = CharField(unique=True)
    version = TextField()

    class Meta:
        db_table = 'omeka_plugins'

class Poster(BaseModel):
    date_created = DateTimeField()
    date_modified = DateTimeField()
    description = TextField(null=True)
    id = BigIntegerField(primary_key=True)
    title = CharField()
    user = BigIntegerField(db_column='user_id')

    class Meta:
        db_table = 'omeka_posters'

class PostersItem(BaseModel):
    annotation = TextField(null=True)
    id = BigIntegerField(primary_key=True)
    item = BigIntegerField(db_column='item_id')
    ordernum = IntegerField()
    poster = BigIntegerField(db_column='poster_id')

    class Meta:
        db_table = 'omeka_posters_items'

class Processe(BaseModel):
    args = TextField()
    class_ = CharField(db_column='class')
    pid = IntegerField(index=True, null=True)
    started = DateTimeField(index=True)
    status = CharField()
    stopped = DateTimeField(index=True)
    user = IntegerField(db_column='user_id', index=True)

    class Meta:
        db_table = 'omeka_processes'

class RecordType(BaseModel):
    description = TextField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'omeka_record_types'

class SchemaMigration(BaseModel):
    version = CharField(unique=True)

    class Meta:
        db_table = 'omeka_schema_migrations'
        primary_key = False

class SectionPage(BaseModel):
    layout = CharField(null=True)
    order = IntegerField()
    section = IntegerField(db_column='section_id')
    slug = CharField()
    title = CharField()

    class Meta:
        db_table = 'omeka_section_pages'

class Section(BaseModel):
    description = TextField(null=True)
    exhibit = IntegerField(db_column='exhibit_id')
    order = IntegerField()
    slug = CharField(index=True)
    title = CharField(null=True)

    class Meta:
        db_table = 'omeka_sections'

class SimplePagesPage(BaseModel):
    add_to_public_nav = IntegerField(index=True)
    created_by_user = IntegerField(db_column='created_by_user_id', index=True)
    inserted = DateTimeField(index=True)
    is_published = IntegerField(index=True)
    modified_by_user = IntegerField(db_column='modified_by_user_id', index=True)
    order = IntegerField(index=True)
    parent = IntegerField(db_column='parent_id', index=True)
    slug = TextField()
    template = TextField()
    text = TextField(null=True)
    title = TextField()
    updated = DateTimeField(index=True)

    class Meta:
        db_table = 'omeka_simple_pages_pages'

class User(BaseModel):
    active = IntegerField(index=True)
    entity = IntegerField(db_column='entity_id', index=True)
    password = CharField()
    role = CharField()
    salt = CharField(null=True)
    username = CharField(unique=True)

    class Meta:
        db_table = 'omeka_users'

class UsersActivation(BaseModel):
    added = DateTimeField(null=True)
    url = CharField(null=True)
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'omeka_users_activations'

