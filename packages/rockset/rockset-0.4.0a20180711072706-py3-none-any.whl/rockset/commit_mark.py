"""Commit mark, indicating where a record landed in the log
"""

class CommitMark:
    def __init__(self, org_id, collection_name):
        self.org_id = org_id
        self.collection_name = collection_name
        self.positions = {}

    @staticmethod
    def deserialize(obj):
        mark = CommitMark(obj['org_id'], obj['collection_name'])
        for p in obj['positions']:
            mark.positions[p['microshard']] = p['position']
        return mark

    def merge_append(self, other):
        self._check(other)
        for ms, pos in other.positions.items():
            try:
                if pos <= self.positions[ms]:
                    raise ValueError(
                        'Out of order updates for microshard {}: {}, {}'.format(
                            ms, self.positions[ms], pos))
            except KeyError:
                pass
            self.positions[ms] = pos

    def merge_read_min(self, other):
        self._check(other)
        for ms, pos in other.positions.items():
            try:
                if pos >= self.positions[ms]:
                    continue
            except KeyError:
                pass
            self.positions[ms] = pos

    def merge_read_max(self, other):
        self._check(other)
        for ms, pos in other.positions.items():
            try:
                if pos <= self.positions[ms]:
                    continue
            except KeyError:
                pass
            self.positions[ms] = pos

    def is_included_in(self, other):
        self._check(other)
        for ms, pos in self.positions.items():
            try:
                if ms > other.positions[ms]:
                    return False
            except KeyError:
                return False
        return True

    def _check(self, other):
        if self.org_id != other.org_id:
            raise ValueError('Mismatched org ids')
        if self.collection_name != other.collection_name:
            raise ValueError('Mismatched collection names')

    def serialize(self):
        return {
            'org_id': self.org_id,
            'collection_name': self.collection_name,
            'positions': [{'microshard': ms, 'position': p}
                          for ms, p in self.positions.items()],
        }

    def __str__(self):
        return 'CommitMark' + str(self.serialize())
