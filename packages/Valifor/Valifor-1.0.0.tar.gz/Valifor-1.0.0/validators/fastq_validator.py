
from validators.abstract_validator import AbsValidator


class Fastq(AbsValidator):
    """The class to validate the Fastq format."""

    def validate_file(self, file_path):
        """Validates whether the file at the given path is of the fastq format or not.
            (also see AbsValidator.)

            :returns boolean whether the format is valid
                string message why it is not valid or an empty string.
        """

        with open(file_path, "r") as file:

            count = 0
            len_of_sequence = -1

            for line in file:
                line = line.strip()

                if line == "":
                    return False, "Empty line at line: " + str(count+1)

                line_kind = count % 4
                valid_line, msg = self.test_line(line, line_kind)

                if not valid_line:
                    return False, msg + " Line: " + str(count+1)

                if line_kind == 1:
                    len_of_sequence = len(line)
                elif line_kind == 3:
                    if len(line) != len_of_sequence:
                        return False, "The quality sequence is not the same length as the DNA sequence. Line:" + str(count+1)

                count += 1

            if count % 4 != 0:
                return False, "Last entry is missing information. Line:" + str(count+1)

        return True, ""

    def test_line(self, line, kind):
        """calls the corresponding test depending on the given kind.

            kind:
            0 - header
            1 - DNA sequence
            2 - Plus-line between sequence and quality
            3 - Quality sequence

        """
        if kind == 0:
            return line.startswith("@"), "Expected header line does not start with '@'."
        elif kind == 1:
            return self.test_sequence(line), "Expected DNA sequence contains banned characters."
        elif kind == 2:
            return line.startswith('+'), "Expected Plus-line does not start with a '+'."
        elif kind == 3:
            return self.test_quality(line), "Expected quality sequence contains banned characters."

    @staticmethod
    def test_sequence(line):
        """tests the given line to only contain characters in the set [A, C, T, G]"""
        for c in line:
            if c not in ['A', 'C', 'T', 'G']:
                return False
        return True

    def test_quality(self, line):
        """tests the given line's characters to be in the set of allowed symbols defined in get_quality_symbols()."""
        symbols = self.get_quality_symbols()
        for c in line:
            if c not in symbols:
                return False
        return True

    @staticmethod
    def get_quality_symbols():
        """returns a list of all allowed quality symbols in asc order:
            lowest--->highest
            !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~]
        """

        all_string = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~]"
        return list(all_string)
