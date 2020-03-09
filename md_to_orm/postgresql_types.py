
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql
from geoalchemy2 import Geometry


class DatabaseTypes:
    types = {
        "bigint": sa.BIGINT,
        "int": sa.INTEGER,
        "integer": sa.INTEGER,
        "double precision": psql.DOUBLE_PRECISION,
        "varchar": sa.VARCHAR,
        "json": sa.JSON,
        "text": sa.TEXT,
        "geometry point": Geometry("POINT"),
        "timestamp": sa.TIMESTAMP,
        "interval": sa.Interval,
        "string": sa.String,
        "float": sa.FLOAT,
        "boolean": sa.Boolean,
        "date": sa.Date
    }

    def __getitem__(self, item):
        if item.split(" ")[-1] == "array":
            db_type = self.types[item[:-6]]
            return psql.ARRAY(db_type)
        else:
            return self.types[item]


TYPES = DatabaseTypes()