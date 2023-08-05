import configparser


class ConfigurationError(Exception):
    pass


class Config(dict):
    """A basic Configuration type

    This configuration class can use subscriptable syntax `['item']` or dotted syntaxt `config.item`
    """

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setattr__(self, item, value):
        return self.__setitem__(item, value)

    def __delattr__(self, item):
        return self.__delitem__(item)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError as e:
            raise ConfigurationError(f'Unable to find configuration value for key {item}')

    @classmethod
    def _parsed_to_dict(cls, config):
        return cls([
            (s, cls(config.items(s)))
            for s in config.sections()
        ])

    @classmethod
    def from_inis(cls, *fpaths):
        """Read the configuration for ini files

        *fpaths is passed straight to `ConfigParser.read` so it can be multiple configuration files
        and it will read them in order.
        """
        config = configparser.ConfigParser()
        config.read(fpaths)

        return cls._parsed_to_dict(config)

