# coding: utf-8

from django.db.migrations.autodetector import MigrationAutodetector

from operation import PartitionOperation


def generate_altered_db_table_new(self):
    self.generate_altered_db_table_orig()
    self.generate_altered_partition()


def generate_altered_partition(self):
    option_name = PartitionOperation.option_name
    for app_label, model_name in sorted(self.kept_model_keys):
        old_model_name = self.renamed_models.get((app_label, model_name), model_name)
        old_model_state = self.from_state.models[app_label, old_model_name]
        new_model_state = self.to_state.models[app_label, model_name]

        old_value = old_model_state.options.get(option_name) or (None, None, None)
        new_value = new_model_state.options.get(option_name) or (None, None, None)

        if old_value != new_value:
            self.add_operation(app_label, PartitionOperation(model_name, *new_value))


def patch_autodetector():
    MigrationAutodetector.generate_altered_partition = generate_altered_partition
    MigrationAutodetector._detect_changes_orig = MigrationAutodetector._detect_changes
    MigrationAutodetector.generate_altered_db_table_orig = MigrationAutodetector.generate_altered_db_table
    MigrationAutodetector.generate_altered_db_table = generate_altered_db_table_new