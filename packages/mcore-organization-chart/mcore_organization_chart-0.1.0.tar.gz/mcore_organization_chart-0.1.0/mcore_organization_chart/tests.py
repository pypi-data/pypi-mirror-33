from unittest import TestCase
from unittest.mock import patch
from typing import Set
from itertools import permutations

from mcore_organization_chart import OrganizationTreeBuilder, OrganizationTreeNode


class EmployeeLevel:
    C_LEVEL = 'C'
    VP_LEVEL = 'VP'
    ENG_LEVEL = 'E'

    LEVEL_HIERARCHY = {
        C_LEVEL: 3,
        VP_LEVEL: 2,
        ENG_LEVEL: 1
    }

    def __init__(self, level: str, branch_ids: Set[int]) -> None:
        self.level = level
        self.branch_ids = branch_ids

    @property
    def value(self) -> int:
        return self.LEVEL_HIERARCHY.get(self.level, 0)


class OrganizationChartTest(TestCase):
    CEO_1_2_3 = 'Sarah Watson'
    VP_1 = 'Ellie Ross'
    VP_2_3 = 'Owen Taylor'
    VP_4 = 'John Misty'
    ENG_2 = 'Isaiah Martin'
    ENG_3 = 'Joao Valverde'

    def mocked_reports_to(self, subordinate_id: str, supervisor_id: str) -> bool:
        # deal with root node
        if supervisor_id == '-':
            return True
        if subordinate_id == '-':
            return False

        # deal with regular nodes
        supervisor = self.organization[supervisor_id]
        subordinate = self.organization[subordinate_id]

        higher_hierarchy = supervisor.value > subordinate.value
        common_branch_ids = bool(supervisor.branch_ids & subordinate.branch_ids)

        return higher_hierarchy and common_branch_ids

    def setUp(self):
        self.organization = {
            self.CEO_1_2_3: EmployeeLevel(EmployeeLevel.C_LEVEL, {1, 2, 3}),
            self.VP_1: EmployeeLevel(EmployeeLevel.VP_LEVEL, {1}),
            self.VP_2_3: EmployeeLevel(EmployeeLevel.VP_LEVEL, {2, 3}),
            self.VP_4: EmployeeLevel(EmployeeLevel.VP_LEVEL, {4}),
            self.ENG_2: EmployeeLevel(EmployeeLevel.ENG_LEVEL, {2}),
            self.ENG_3: EmployeeLevel(EmployeeLevel.ENG_LEVEL, {3}),
        }

        # mock api call for testing purposes
        self.patcher = patch('mcore_organization_chart.tests.OrganizationTreeBuilder.reports_to')
        self.mock = self.patcher.start()
        self.mock.side_effect = self.mocked_reports_to

    def tearDown(self):
        self.patcher.stop()

    def test_root(self) -> None:
        tree_builder = OrganizationTreeBuilder(set())
        self.assertEqual(tree_builder.root_node.employee, '-')
        self.assertFalse(tree_builder.root_node.subordinates)
        self.assertIsNone(tree_builder.root_node.supervisor)

    def test_first_node(self) -> None:
        tree_builder = OrganizationTreeBuilder({self.ENG_3})
        tree_builder.build()

        self.assertEqual(len(tree_builder.root_node.subordinates), 1)
        self.assertEqual(list(tree_builder.root_node.subordinates)[0].employee, self.ENG_3)

    def assertions_two_peer_nodes(self, tree_builder: OrganizationTreeBuilder) -> None:
        self.assertEqual(len(tree_builder.root_node.subordinates), 2)

        for node in tree_builder.root_node.subordinates:
            self.assertFalse(node.subordinates)
            self.assertEqual(node.supervisor, tree_builder.root_node)

    def test_two_peer_nodes(self) -> None:
        for employees in permutations([self.ENG_3, self.ENG_2]):
            tree_builder = OrganizationTreeBuilder(list(employees))
            tree_builder.build()
            self.assertions_two_peer_nodes(tree_builder)

    def assert_two_dependent_nodes(self, tree_builder: OrganizationTreeBuilder) -> None:
        self.assertEqual(len(tree_builder.root_node.subordinates), 1)

        vp_2_3_node = list(tree_builder.root_node.subordinates)[0]
        self.assertEqual(vp_2_3_node.employee, self.VP_2_3)

        self.assertEqual(len(vp_2_3_node.subordinates), 1)
        self.assertEqual(list(vp_2_3_node.subordinates)[0].employee, self.ENG_2)

    def test_two_dependent_nodes(self) -> None:
        for employees in permutations([self.VP_2_3, self.ENG_2]):
            tree_builder = OrganizationTreeBuilder(list(employees))
            tree_builder.build()
            self.assert_two_dependent_nodes(tree_builder)

    def assert_all_ENG(self, node: OrganizationTreeNode) -> None:
        self.assertEqual(len(node.subordinates), 0)

    def assert_all_VP_2_3(self, node: OrganizationTreeNode) -> None:
        for _node in node.subordinates:
            if _node.employee == self.ENG_2:
                self.assert_all_ENG(_node)
            elif _node.employee == self.ENG_3:
                self.assert_all_ENG(_node)
            else:
                self.assertTrue(False)

    def assert_all_VP_1(self, node: OrganizationTreeNode) -> None:
        self.assertEqual(len(node.subordinates), 0)

    def assert_all_VP_4(self, node: OrganizationTreeNode) -> None:
        self.assertEqual(len(node.subordinates), 0)

    def assert_all_CEO_1_2_3(self, node: OrganizationTreeNode) -> None:
        for _node in node.subordinates:
            if _node.employee == self.VP_1:
                self.assert_all_VP_1(_node)
            elif _node.employee == self.VP_2_3:
                self.assert_all_VP_2_3(_node)
            else:
                self.assertTrue(False)

    def assert_all_nodes(self, tree_builder: OrganizationTreeBuilder) -> None:
        for _node in tree_builder.root_node.subordinates:
            if _node.employee == self.CEO_1_2_3:
                self.assert_all_CEO_1_2_3(_node)
            elif _node.employee == self.VP_4:
                self.assert_all_VP_4(_node)
            else:
                self.assertTrue(False)

    def test_all_nodes(self):
        for employees in permutations([key for key, _ in self.organization.items()]):
            tree_builder = OrganizationTreeBuilder(list(employees))
            tree_builder.build()
            self.assert_all_nodes(tree_builder)

    def test_print(self):
        tree_builder = OrganizationTreeBuilder([key for key, _ in self.organization.items()])
        tree_builder.build()
        tree_builder.print()
