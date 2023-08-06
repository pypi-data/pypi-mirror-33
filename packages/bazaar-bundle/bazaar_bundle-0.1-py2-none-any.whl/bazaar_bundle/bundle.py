from applauncher.kernel import ConfigurationReadyEvent, KernelShutdownEvent
from bazaar import FileSystem


class BazaarBundle(object):
    def __init__(self):

        self.config_mapping = {
            "bazaar": {
                "storage_uri": None,
                "db_uri": None,
                "default_namespace": ""
            }
        }

        self.fs = None

        self.event_listeners = [
            (ConfigurationReadyEvent, self.configuration_ready),
            (KernelShutdownEvent, self.kernel_shutdown),
        ]

        self.injection_bindings = {}

    def configuration_ready(self, event):
        config = event.configuration.bazaar
        self.fs = FileSystem(storage_uri=config.storage_uri, db_uri=config.db_uri, namespace=config.default_namespace)
        self.injection_bindings[FileSystem] = self.fs

    def kernel_shutdown(self, event):
        self.fs.close()
