class Resolver:
    def __init__(self, config_content, data):
        pass

    def provides(self, package_name):
        return False

    def get_resolver_name(self):
        return ""

    def resolve_to_installer(self, package_name):
        return None

    @classmethod
    def get_check_line(cls):
        return ""

    def update_resolver(self):
        pass
