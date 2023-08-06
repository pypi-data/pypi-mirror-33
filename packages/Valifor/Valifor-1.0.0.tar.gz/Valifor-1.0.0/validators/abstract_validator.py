
class AbsValidator:
    """The parent class for all validators.
        It defines the functions that all validator plugins have to implement and overwrite.
    """

    def validate_file(self, file_path):
        """ The function validate_file is the main workhorse and connection to the rest of the project.
            As its name indicates it is the function used to validate the files.

            It has two return values:
                the first is a boolean of whether the file is valid
                the second is a string. If the file is valid it should be empty
                                        If the file is corrupt it should be an explanation why(if possible)

         """
        valid = False
        return valid, "Error: Unimplemented validate_file function."
