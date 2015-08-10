class VirtualenvPathNotFound(EnvironmentError):
    pass


class VirtualenvCreationException(EnvironmentError):
    pass


class PackageInstallationException(EnvironmentError):
    pass


class PackageRemovalException(EnvironmentError):
    pass

class PackageWheelException(EnvironmentError):
    pass

class VirtualenvReadonlyException(Exception):
    message = 'The virtualenv was constructed readonly and cannot be modified'
