from collections import defaultdict
import bisect

class SortedArrayTracker:
    def __init__(self, max_errors=100):
        self.error_map = defaultdict(int)
        self.sorted_errors = []
        self.max_errors = max_errors

    def update_error(self, error_category, error_subcategory):
        error_key = f"{error_category}:{error_subcategory}"
        self.error_map[error_key] += 1
        count = self.error_map[error_key]

        index = self._binary_search(count, error_key)

        if index < len(self.sorted_errors) and self.sorted_errors[index][1] == error_key:
            self.sorted_errors[index] = (count, error_key)
        else:
            if len(self.sorted_errors) < self.max_errors:
                bisect.insort(self.sorted_errors, (count, error_key), key=lambda x: (-x[0], x[1]))
            elif count > self.sorted_errors[-1][0]:
                bisect.insort(self.sorted_errors, (count, error_key), key=lambda x: (-x[0], x[1]))
                self.sorted_errors.pop()

    def _binary_search(self, count, error_key):
        return bisect.bisect_left(self.sorted_errors, (-count, error_key), key=lambda x: (-x[0], x[1]))

    def get_top_n_errors(self, n):
        return [(count, key) for count, key in self.sorted_errors[:n]]