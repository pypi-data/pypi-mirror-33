import re
import os
import win32com.client
from idea_wrapper.table_def import TableDef
from datetime import date, time


class RecordSet:
    def _generate_regex(self):
        string_regex = r"\"(.*)\""
        date_regex = r"(?:\")?(\d\d\d\d\d\d\d\d)(?:\")?"
        time_regex = r"(?:\")?(\d\d\:\d\d\:\d\d)(?:\")?"
        num_regex = r"(?:\")?((?:(?:\+)?(?:-)?)\d*((?:\.|,)\d*)?)(?:\")?"

        regex = "^"
        for field in self.table_def:
            type = field.type
            if type == 3:
                regex += string_regex
            elif type == 4:
                regex += num_regex
            elif type == 5:
                regex += date_regex
            elif type == 11:
                regex += time_regex
            else:
                regex += r"(?:\")?(.*)(?:\")?"
            regex += ";"
        return regex[:len(regex) - 1] + "$"

    @staticmethod
    def _convert(string, type, include_empty_fields):
        try:
            if type == 4:
                if "." in string or "," in string:
                    return float(string.replace(",", "."))
                else:
                    return int(string)
            elif type == 5:
                return date(int(string[:4]), int(string[4:6]), int(string[6:]))
            elif type == 11:
                return time(int(string[:2]), int(string[3:5]), int(string[6:]))
            else:
                return string
        except ValueError as e:
            if include_empty_fields:
                return None
            else:
                raise e
        except TypeError:
            return None

    group_amount = {  # how many groups does a field type represent (in regex)?
        3: 1,
        4: 2,
        5: 1,
        11: 1
    }

    def _read(self, text, include_empty_fields):
        self._content = []
        matches = []
        for line in text.split("\n"):
            if not line:
                print("Encountered empty line!")
                continue

            match = re.match(self._regex, line)
            if match:
                matches.append(match)
            else:
                print("Did not match!")
                print(line)
                exit(1)
        for match in matches:
            try:
                i = 1
                line = []
                for field in self.table_def:
                    type = field.type
                    length = self.group_amount[type]
                    line.append(RecordSet._convert(match.group(i), type, include_empty_fields))
                    i += length
                self._content.append(Record(line))
            except ValueError:
                pass

    def _export(self, utf8):
        task = self._db.exportDatabase()
        task.includeAllFields()
        eqn = ""
        db_name = self._client.uniqueFileName("export.DEL")
        db_name = db_name[:len(db_name)-4]
        task.performTask(db_name, "Database", "DEL UTF-8" if utf8 else "DEL", 1, self._db.count, eqn)

        content = ""
        with open(db_name, "r") as f:
            line = f.readline()
            while line:
                line = f.readline()
                if line:
                    content += line
        os.remove(db_name)

        return content

    def __init__(self, db, utf8=False, include_empty_fields=True):
        self._client = win32com.client.Dispatch(dispatch="Idea.IdeaClient")
        self._db = db

        content = self._export(utf8)
        self.table_def = TableDef(db.tableDef())

        self._regex = self._generate_regex()
        self._read(content, include_empty_fields)
        self.count = len(self._content)

    def __len__(self):
        return len(self._content)

    def __getitem__(self, item):
        return self.get_at(item)

    def __str__(self):
        return str(self._content)

    def __iter__(self):
        return iter(self._content)

    def get_at(self, index):
        return self._content[index]


class Record:
    def __init__(self, data):
        self._data = data
        self.number_of_fields = len(data)

    def __getitem__(self, item):
        return self.value_at(item)

    def __len__(self):
        self.number_of_fields = len(self._data)
        return self.number_of_fields

    def __iter__(self):
        return iter(self._data)

    def __str__(self):
        return str(self._data)

    def value_at(self, index):
        return self._data[index]
