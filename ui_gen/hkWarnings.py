# create a custom warning called notImplementedWarning
class notImplementedWarning(Warning):
    def __init__(self, message: str = "This feature is not implemented yet"):
        """Custom warning for not implemented features

        Args:
            message (str, optional): error message with default message. 
        """
        self.message = message
        super().__init__(self.message)