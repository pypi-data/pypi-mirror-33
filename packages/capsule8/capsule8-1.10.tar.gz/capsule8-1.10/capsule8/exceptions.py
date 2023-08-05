class SensorConnectionError(Exception):
    """
    Exception to handle when grpc cannot connect to the sensor socket.
    """
    pass


class InvalidSubscriptionError(Exception):
    """
    Exception to handle when a subscription is malformed
    """
    pass
