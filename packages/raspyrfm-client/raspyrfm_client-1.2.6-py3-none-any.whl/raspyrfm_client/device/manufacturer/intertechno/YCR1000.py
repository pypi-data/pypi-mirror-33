from raspyrfm_client.device.manufacturer.intertechno.CMR1000 import CMR1000


class YCR1000(CMR1000):
    def __init__(self):
        from raspyrfm_client.device.manufacturer import manufacturer_constants
        super(CMR1000, self).__init__(manufacturer_constants.INTERTECHNO, manufacturer_constants.YCR_1000)
