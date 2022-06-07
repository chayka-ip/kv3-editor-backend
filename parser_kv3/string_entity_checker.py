
class StringEntityChecker:
    """
        Entity is some data limited with special sequences.
        Sequences can be different or same.
    """

    def __init__(self, line: str, open_seq: str, close_seq: str):
        self.line = line
        self.open_seq = open_seq
        self.close_seq = close_seq
        self.similar_seq = open_seq == close_seq

    @property
    def has_sequences(self):
        return self.has_open_seq or self.has_close_seq

    @property
    def no_sequences(self):
        return not self.has_sequences

    """whether valid entity is present in the line"""

    @property
    def has_valid_entity(self):
        return self.has_open_seq and self.has_close_seq

    """whether the line is valid entity itself"""

    @property
    def is_valid_entity(self):
        start = self.line.startswith(self.open_seq)
        end = self.line.endswith(self.close_seq)
        has_valid_entity = self.has_valid_entity
        return start and end and has_valid_entity

        # if nested type like object or array is checked - add new prop which allowes multiple occurencies,
        # but count shoul be proper

    @property
    def has_invalid_entity(self):
        return {True, False} in {self.has_open_seq, self.has_close_seq}

    @property
    def has_open_seq(self):
        return self.open_seq in self.line

    @property
    def has_close_seq(self):
        if not self.similar_seq:
            return self.close_seq in self.line
        return self.line.count(self.open_seq) == 2
