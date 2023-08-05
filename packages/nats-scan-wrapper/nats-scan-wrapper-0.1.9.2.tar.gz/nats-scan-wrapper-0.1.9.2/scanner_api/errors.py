class ScanWrapperError(Exception):
    pass


class ModuleNameError(ScanWrapperError):
    def __str__(self):
        return "ScanWrapper: Not set module name in kwargs"


class WorkerError(ScanWrapperError):
    def __str__(self):
        return "ScanWrapper: Error in worker function"


class NotEnoughArgsError(ScanWrapperError):
    def __str__(self):
        return "ScanWrapper: Take me more arguments"


class BadPackageDataError(ScanWrapperError):
    def __str__(self):
        return "ScanWrapper: Data does not match the scanner"


class ExpiredTimeError(ScanWrapperError):
    def __str__(self):
        return "ScanWrapper: Max Task time is expired"

# class (ScanWrapperError):
#     def __str__(self):
#         return ""

# class (ScanWrapperError):
#     def __str__(self):
#         return ""
