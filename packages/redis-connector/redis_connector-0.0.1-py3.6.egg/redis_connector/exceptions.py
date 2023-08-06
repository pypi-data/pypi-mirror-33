class RedisConeectorException(Exception):
    """To be subclassed for any exception in the module."""
    pass


class RedisConnectorWrongConfiguration(RedisConeectorException):
    """To be raised when there is a configuration error when instancing the connector."""
    pass
