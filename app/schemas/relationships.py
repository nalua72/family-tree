from enum import Enum
from pydantic import BaseModel, ConfigDict


class RelationshipType(str, Enum):
    SELF = "SELF"
    PARENT = "PARENT"
    GRANDPARENT = "GRANDPARENT"
    CHILD = "CHILD"
    GRANDCHILD = "GRANDCHILD"
    SIBLING = "SIBLING"
    UNCLE = "UNCLE"
    NEPHEW = "NEPHEW"
    COUSIN = "COUSIN"
    DISTANT_RELATIVE = "DISTANT_RELATIVE"


class RelationshipResponse(BaseModel):
    relationship: RelationshipType  # e.g. COUSIN, PARENT, SIBLING
    distance: int   # number of steps between persons

    model_config = ConfigDict(use_enum_values=True)
