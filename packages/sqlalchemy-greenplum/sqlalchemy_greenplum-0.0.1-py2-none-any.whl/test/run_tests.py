
from sqlalchemy.dialects import registry

registry.register("greenplum", "sqlalchemy_greenplum.dialect", "GreenplumDialect")

from sqlalchemy.testing import runner

runner.mainx()
