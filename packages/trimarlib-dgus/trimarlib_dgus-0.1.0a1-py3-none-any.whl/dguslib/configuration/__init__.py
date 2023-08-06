from . import configs
from . import descriptors

__all__ = ['make_configuration', 'configs', 'descriptors', 'PageConfiguration']


class PageConfiguration(object):
    __slots__ = 'page_idx', 'variables'

    def __init__(self, page_idx=0):
        self.page_idx = page_idx
        self.variables = []

    def __bytes__(self):
        bb = bytearray()
        for var in self.variables:
            bb.extend(bytes(var))
        if len(bb) < 2048:
            bb.extend(bytes(2048 - len(bb)))
        return bb

    def __iadd__(self, other):
        if not issubclass(type(other), configs.VariableConfiguration):
            raise TypeError('other is not a subclass of VariableConfiguration')
        self.variables.append(other)
        return self


def make_configuration(configuration_data, file_path=None):
    """Generates variable configuration binary data and returns it as a bytes object.

    Parameters
    ----------
    configuration_data : PageConfiguration object or a list of such objects
    file_path : path to the file where the binary data is to be written
    """
    page_config_list = []
    if type(configuration_data) is list:
        if len(configuration_data) == 0:
            return
        # sort provided list by page index
        configuration_data.sort(key=lambda x: x.page_idx)
        # check for duplicate entries
        page_idx_list = []
        for configuration in configuration_data:
            if configuration.page_idx in page_idx_list:
                raise RuntimeError('duplicate configurations for page {}'.format(configuration.page_idx))
            page_idx_list.append(configuration.page_idx)
        # no duplicate entries found
        del page_idx_list

        # fill page configuration list with consistent, sequential configurations
        for configuration in configuration_data:
            try:
                for i in range(page_config_list[-1].page_idx + 1, configuration.page_idx):
                    page_config_list.append(PageConfiguration(i))
            except IndexError:
                for i in range(configuration.page_idx):
                    page_config_list.append(PageConfiguration(i))
            page_config_list.append(configuration)

    elif type(configuration_data) is PageConfiguration:
        # single page configuration, fill preceding pages with empty configuration
        for i in range(configuration_data.page_idx):
            page_config_list.append(PageConfiguration(i))
        page_config_list.append(configuration_data)

    else:
        raise TypeError('configuration data')

    # page configuration list prepared
    if file_path is not None:
        fd = open(file_path, 'wb')
    else:
        fd = None
    bb = bytearray()
    for config in page_config_list:
        b = bytes(config)
        bb.extend(b)
        if fd is not None:
            fd.write(b)
    if fd is not None:
        fd.close()
    return bb
