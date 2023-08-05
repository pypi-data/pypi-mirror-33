from typing import Set, List, Union

from .api_service import MigacoreApiService


PRINT_OFFSET = 10


class OrganizationTreeNode:
    ROOT_ID = '-'

    def __init__(self, employee: str=ROOT_ID) -> None:
        self.employee = employee
        self.subordinates: Set[OrganizationTreeNode] = set()
        self.supervisor: Union[OrganizationTreeNode, None] = None

    def print(self, spaces: int) -> None:

        if self.supervisor is not None:
            if spaces > 0:
                print('{}|--- {}'.format(''.join([' ' for _ in range(0, spaces)]), self.employee))
            else:
                print('|--- {}'.format(self.employee))
        for node in self.subordinates:
            node.print(spaces + PRINT_OFFSET)


class OrganizationTreeBuilder:
    def __init__(self, target_employees: Union[Set[str], List[str]]) -> None:

        # I used a list (ordered structure) instead of a set (unordered structure)
        # to be able to deterministically test the building of the tree
        self.target_employees: List[str] = target_employees if isinstance(target_employees, list) else list(target_employees)

        self.root_node = OrganizationTreeNode()

    def print(self):
        print('\n')
        self.root_node.print(-PRINT_OFFSET)
        print('\n')

    def reports_to(self, subordinate: str, supervisor: str) -> bool:
        if supervisor == OrganizationTreeNode.ROOT_ID:
            return True
        if subordinate == OrganizationTreeNode.ROOT_ID:
            return False

        return MigacoreApiService.reports_to(subordinate, supervisor)

    def build(self) -> None:
        for employee in self.target_employees:
            self.insert(OrganizationTreeNode(employee))

    @staticmethod
    def insert_bellow(new_node: OrganizationTreeNode, existing_node: OrganizationTreeNode) -> None:
        existing_node.subordinates.add(new_node)
        new_node.supervisor = existing_node

    @staticmethod
    def insert_above(new_node: OrganizationTreeNode, existing_node: OrganizationTreeNode) -> None:
        parent = existing_node.supervisor
        assert parent is not None
        parent.subordinates.discard(existing_node)
        parent.subordinates.add(new_node)

        new_node.supervisor = parent
        new_node.subordinates.add(existing_node)

        existing_node.supervisor = new_node

    def insert(self, new_node: OrganizationTreeNode) -> None:
        parent_node = self.root_node
        child_nodes: Set[OrganizationTreeNode] = set([])

        node_q: List[OrganizationTreeNode] = [parent_node]

        while node_q:
            current_node = node_q.pop()

            if self.reports_to(current_node.employee, new_node.employee):
                child_nodes.add(current_node)
                # here we don't clear

            if not child_nodes:
                # we still don't know if this node is a leaf or not

                if self.reports_to(new_node.employee, current_node.employee):
                    parent_node = current_node
                    if not current_node.subordinates:
                        node_q.clear()  # no need to search any further
                    else:
                        node_q += current_node.subordinates  # found candidate but the search must continue

        if child_nodes:
            for node in child_nodes:
                self.insert_above(new_node, node)
        else:
            self.insert_bellow(new_node, parent_node)
