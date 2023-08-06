
from validators.fasta_validator import Fasta
from validators.fastq_validator import Fastq


def available_formats():
    """Returns a list of all supported file-types"""
    return ["fasta-dna", "fasta-aa", "fastq"]


def get_format_from_ending(file_ending):
    """Returns the corresponding format-name to the given file-ending and an empty string if the ending is unknown."""
    if file_ending == "fasta":
        return "fasta-dna"
    if file_ending == "fastq":
        return "fastq"

    # in case of an unknown ending return empty string.
    return ""


def get_validator(name):
    """Returns the corresponding validator to the given format-name"""
    if name == "fasta-dna":
        return Fasta("DNA")
    if name == "fasta-aa":
        return Fasta("AA")
    if name == "fastq":
        return Fastq()

    raise Exception("FormatFactory.get_format() - Error: Unknown Format identifier.")


def get_uncertain_endings():
    """returns a list of all file endings that don't fully define their format.
        For formats that for example can contain different kinds of data
        like .fasta with genetic and aminoacid sequences.
    """
    return ["fasta"]
