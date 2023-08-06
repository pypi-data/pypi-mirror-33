# coding: utf-8

from django.db.migrations.operations.models import Operation, cached_property


class PartitionOperation(Operation):
    option_name = "partition"

    def __init__(self, name, column, begin, interval):
        self.name = name
        self.column = column
        self.begin = begin
        self.interval = interval

    @cached_property
    def name_lower(self):
        return self.name.lower()

    def deconstruct(self):
        args = []
        kwargs = {
            'name': self.name,
            'column': self.column,
            'begin': self.begin,
            'interval': self.interval,
        }
        return (
            self.__class__.__name__,
            args,
            kwargs,
        )

    def state_forwards(self, app_label, state):
        model_state = state.models[app_label, self.name_lower]
        model_state.options[self.option_name] = (self.column, self.begin, self.interval)
        state.reload_model(app_label, self.name_lower)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        new_model = to_state.apps.get_model(app_label, self.name)
        if self.allow_migrate_model(schema_editor.connection.alias, new_model):
            old_model = from_state.apps.get_model(app_label, self.name)
            schema_editor.range_partitions(
                new_model,
                getattr(old_model._meta, self.option_name, (None, None, None)),
                getattr(new_model._meta, self.option_name, (None, None, None)),
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return self.database_forwards(app_label, schema_editor, from_state, to_state)

    def references_model(self, name, app_label=None):
        return name.lower() == self.name_lower

    def describe(self):
        return "Add/remove %s for %s (via column %s)" % (self.option_name, self.name, self.column)
