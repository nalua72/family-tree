import uuid
from sqlalchemy.orm import Session
from collections import deque

from app.services.person_service import (get_person_by_id_service)
from app.services.tree_utils import (
    build_edge, get_neighbors, map_person_to_node)
from app.schemas.tree import (PersonEdge, PersonNode, PersonTreeResponse)
from app.types.tree_types import (EdgeDict, NodeDict)


def get_person_tree_service(session: Session, person_uuid: uuid.UUID, depth: int) -> PersonTreeResponse:

    root_person = get_person_by_id_service(session, person_uuid)

    queue: list[tuple(uuid.UUID, int)] = deque([(person_uuid, 0)])
    visited: set[uuid.UUID] = {person_uuid}
    nodes_id: set[str] = {str(person_uuid)}
    edges_set: set[tuple[str, str]] = set()

    nodes: list[NodeDict] = [map_person_to_node(root_person)]
    edges: list[EdgeDict] = []

    while queue:

        current_uuid, level = queue.popleft()

        current_id = str(current_uuid)

        if level >= depth:
            continue

        next_level = level + 1

        for direction, neighbors in get_neighbors(session, current_uuid):
            for neighbor in neighbors:

                neighbor_id = str(neighbor.uuid)

                # ---- nodes ----
                if neighbor_id not in nodes_id:
                    nodes_id.add(neighbor_id)
                    nodes.append(map_person_to_node(neighbor))

                # ---- edges ----
                source, target, relationship = build_edge(
                    direction, current_id, neighbor_id
                )

                edge_key = (source, target)

                if edge_key not in edges_set:
                    edges_set.add(edge_key)
                    edges.append(
                        {
                            "source": source,
                            "target": target,
                            "type": relationship,
                        }
                    )

                # ---- queue ----
                if neighbor.uuid not in visited:
                    visited.add(neighbor.uuid)
                    queue.append((neighbor.uuid, next_level))

    return PersonTreeResponse(
        root=str(person_uuid),
        nodes=[PersonNode(**n) for n in nodes],
        edges=[PersonEdge(**e) for e in edges],
    )
