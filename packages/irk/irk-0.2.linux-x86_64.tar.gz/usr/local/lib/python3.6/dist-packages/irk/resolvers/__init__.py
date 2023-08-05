from irk.resolvers.aptresolver import AptResolver
from irk.resolvers.customresolver import RegexResolver
from .pipresolver import PipResolver
import pkg_resources

ALL_RESOLVER_TYPES = [PipResolver, AptResolver, RegexResolver]
for ep in pkg_resources.iter_entry_points(group='irk.resolvers'):
    ALL_RESOLVER_TYPES.append(ep.load())
