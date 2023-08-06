class TableDef:
    def __init__(self, table_def):
        self._fields = []
        self._field_dict = {}
        for i in range(table_def.count):
            f = Field(table_def.getFieldAt(i + 1))
            self._fields.append(f)
            self._field_dict[f.name] = f

        self.record_length = table_def.recordLength

    def get_field(self, name):
        return self._field_dict[name]

    def get_field_at(self, index):
        return self._fields[index]

    def __getitem__(self, item):
        if isinstance(item, type("")):
            return self.get_field(item)
        else:
            return self.get_field_at(item)

    def __iter__(self):
        return iter(self._fields)


class Field:
    def __init__(self, field):
        self.decimals = field.decimals
        self.description = field.description
        self.equation = field.equation
        self.has_action_field = field.hasActionField
        self.is_character = field.isCharacter
        self.is_date = field.isDate
        self.is_implied_decimal = field.isImpliedDecimal
        self.is_numeric = field.isNumeric
        self.is_time = field.IsTime
        self.is_virtual = field.IsVirtual
        self.length = field.length
        self.name = field.name
        self.protected = field.protected
        self.type = field.type

    def __len__(self):
        return self.count

    def __str__(self):
        return self.name
