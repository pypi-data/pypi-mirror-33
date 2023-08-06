from restclients_core.util.decorators import use_mock
from uw_mailman.dao import Mailman_DAO


fdao_mailman_override = use_mock(Mailman_DAO())
