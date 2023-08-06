class DataWrongShapeError(ValueError):
    pass


class DataTypeNotSupportedError(TypeError):
    pass


class CouldNotAcquireFileLockError(OSError):
    pass
