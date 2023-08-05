from unittest import TestCase

import sorting

class TestAlgorithms(TestCase):
    unsorted_list = [54, 26, 93, 17, 77, 31, 44, 55, 20]
    sorted_list = [17, 20, 26, 31, 44, 54, 55, 77, 93]

    def test_bubble_sort(self):
        test_list = self.unsorted_list
        sorting.bubble_sort(test_list)
        self.assertListEqual(test_list, self.sorted_list)

    def test_selection_sort(self):
        test_list = self.unsorted_list
        sorting.bubble_sort(test_list)
        self.assertListEqual(test_list, self.sorted_list)

    def test_insertion_sort(self):
        test_list = self.unsorted_list
        sorting.bubble_sort(test_list)
        self.assertListEqual(test_list, self.sorted_list)

    def test_quick_sort(self):
        test_list = self.unsorted_list
        sorting.bubble_sort(test_list)
        self.assertListEqual(test_list, self.sorted_list)


# alist = [54, 26, 93, 17, 77, 31, 44, 55, 20]
# sorting.bubble_sort(alist)
# print(alist)

# alist=[54, 26, 93, 17, 77, 31, 44, 55, 20]
# sorting.selection_sort(alist)
# print(alist)

# alist=[54, 26, 93, 17, 77, 31, 44, 55, 20]
# sorting.insertion_sort(alist)
# print(alist)

# alist=[54, 26, 93, 17, 77, 31, 44, 55, 20]
# sorting.quick_sort(alist)
# print(alist)
