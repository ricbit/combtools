"""combtools: Extends itertools to provide more combinatorial constructs.

Author: Ricardo Bittencourt <ricbit@ricbit.com>

"""

import itertools
import unittest

def integer_compositions(n):
    """Compositions of an integer (as an ordered sum of positive integers).

    Returns an iterator over the compositions of the given integer n.
    Example: n=3 -> 3 = 2+1 = 1+2 = 1+1+1.
    Wiki: http://en.wikipedia.org/wiki/Composition_(combinatorics)
    OEIS: http://oeis.org/search?q=A000079
    Complexity: O(n)/element

    Args:
      n: positive integer to be represented as a composition.
    Returns:
      an iterator over the compositions of n. Each composition is a list
      of integers, whose sum is n.
    """
    if n == 0:
        yield []
    else:
        yield [n]
        for i in xrange(n - 1, 0, -1):
            for composition in integer_compositions(n - i):
                yield [i] + composition


def integer_partitions(n):
    """Partitions of an integer (as an unordered sum of positive integers).

    Returns an iterator over the compositions of the given integer n.
    Example: n=3 -> 3 = 2+1 = 1+1+1.
    Wiki: http://en.wikipedia.org/wiki/Partition_(number_theory)
    OEIS: http://oeis.org/search?q=A000041
    Complexity: O(n)/element

    Args:
      n: positive integer to be represented as a partition.
    Returns:
      an iterator over the partitions of n. Each partition is a list
      of integers, whose sum is n.
    """
    def _partitions(n, max_term):
        """Partitions of n where no term is greater than max_term."""
        if n == 0:
            yield []
        else:
            for i in xrange(max_term, 0, -1):
                for partition in _partitions(n - i, min(n - i, i)):
                    yield [i] + partition
    return _partitions(n, n)


def set_partitions(seq):
    """Partitions of a set.

    Returns an iterator over the set partitions of a sequence.
    Example: seq=1,2,3 -> 123, 1|2|3, 12|3, 13|2, 1|23
    Wiki: http://en.wikipedia.org/wiki/Partition_of_a_set
    OEIS: http://oeis.org/search?q=A000110
    Complexity: O(n)/element

    Args:
      seq: a sequence to be partitioned.
    Returns:
      an iterator over the set partitions of seq. Each partition is a list
      of elements of seq, whose union is seq.
    """
    def gen(pos, m, cur):
        if pos == n:
            yield cur
        else:
            for i in xrange(0, 1 + m):
                updated = cur + [i]
                for elem in gen(pos + 1, max(updated) + 1, updated):
                    yield elem
    def convert(partition):
        for encoded in partition:
            ans = [[] for i in xrange(n)]
            for i, j in enumerate(encoded):
                ans[j].append(seq[i])
            yield [x for x in ans if x]
    n = len(seq)
    return convert(gen(1, 1, [0]))


def bracketings(n):
    """Bracketings on n letters.

    Returns an iterator over all bracketings on n letters, represented
    as trees with n leaves and no unary branches.
    Example: n=3 -> ((ab)c) (a(bc)) (abc)
    Info: http://mathworld.wolfram.com/Bracketing.html
    OEIS: http://oeis.org/search?q=A000110
    Complexity: O(n)/element

    Args:
      n: positive integer with the size of the bracketings
    Returns:
      an iterator over all bracketings on n letters of seq. Each bracketing
      is represented as tree, where an internal node is a tuple of tuples,
      and an external node is the empty tuple.
    """
    if n == 1:
        yield ()
    for part in integer_compositions(n):
        if len(part) > 1:
            for brac in itertools.product(*(bracketings(i) for i in part)):
                yield brac


class _CombtoolsTest(unittest.TestCase):
    """Unit tests."""

    def _is_reverse_sorted(self, seq):
        for i in xrange(len(seq) - 1):
            if seq[i] < seq[i + 1]:
                return False
        return True

    def _immutable(self, seq):
        if isinstance(seq, list):
            return tuple(self._immutable(i) for i in seq)
        else:
            return seq

    def _unique_len(self, seq):
        return len(set(self._immutable(i) for i in seq))

    def _flatten_sort(self, seq):
        return list(sorted(itertools.chain(*seq)))

    def test_integer_compositions(self):
        # Sizes given by OEIS A000079.
        self.assertEqual(
            [1, 2, 4, 8, 16, 32, 64, 128],
            [self._unique_len(integer_compositions(i)) for i in xrange(1,9)])

        for n in xrange(1, 9):
            for composition in integer_compositions(n):
                # Terms must sum to n.
                self.assertEqual(n, sum(composition))
                # Terms must be less or equal to n.
                self.assertTrue(all(i <= n for i in composition))

        for n in xrange(1, 9):
            # Results must be in reverse lexicographical order.
            self.assertTrue(
                self._is_reverse_sorted(list(integer_compositions(n))))

    def test_integer_partitions(self):
        # Sizes given by OEIS A000041.
        self.assertEqual(
            [1, 2, 3, 5, 7, 11, 15, 22],
            [self._unique_len(integer_partitions(i)) for i in xrange(1,9)])

        for n in xrange(1, 9):
            for partition in integer_partitions(n):
                # Terms must sum to n.
                self.assertEqual(n, sum(partition))
                # Terms must be less or equal to n.
                self.assertTrue(all(i <= n for i in partition))
                # Terms must be sorted.
                self.assertTrue(self._is_reverse_sorted(partition))

        for n in xrange(1, 9):
            # Results must be in reverse lexicographical order.
            self.assertTrue(
                self._is_reverse_sorted(list(integer_partitions(n))))

    def test_set_partitions(self):
        # Sizes given by OEIS A000110.
        self.assertEqual(
            [1, 2, 5, 15, 52, 203, 877, 4140],
            [self._unique_len(set_partitions(range(i))) for i in xrange(1,9)])

        for n in xrange(1, 9):
            for partition in set_partitions(range(n)):
                # Terms must be lists of lists.
                self.assertTrue(all(isinstance(i, list) for i in partition))
                # After flattening and sorting, must be equal to range(n).
                self.assertEqual(range(n), self._flatten_sort(partition))

    def _is_bracketing(self, brac):
        if len(brac) == 1:
            return brac == ()
        else:
            return all(self._is_bracketing(b) for b in brac)

    def test_bracketings(self):
        # Sizes given by OEIS A001003.
        self.assertEqual(
            [1, 1, 3, 11, 45, 197, 903, 4279],
            [self._unique_len(bracketings(i)) for i in xrange(1,9)])

        for n in xrange(1, 9):
            for bracketing in bracketings(n):
                # Terms must be bracketings.
                self.assertTrue(self._is_bracketing(bracketing))
 
if __name__ == '__main__':
    unittest.main()
