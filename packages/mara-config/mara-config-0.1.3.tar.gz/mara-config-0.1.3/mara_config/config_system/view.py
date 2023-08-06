"""Mara config views"""

import html
import logging

import flask
from mara_page import acl
from mara_page import navigation, response, _, bootstrap

from mara_config.config_system.config_display import get_config_for_display

log = logging.getLogger(__name__)

mara_config = flask.Blueprint('mara_config', __name__, url_prefix='/config_system', static_folder='static')

acl_resource = acl.AclResource('Configuration')


@mara_config.route('/')
@acl.require_permission(acl_resource)
def configuration_page():
    config = get_config_for_display()
    current_user_has_permission = acl.current_user_has_permission(acl_resource)

    return response.Response(
        html=[(bootstrap.card(id=module_name,
            header_left=html.escape(module_name),
            body=[_.p[_.em[html.escape(str(module_content.doc))]],
                  bootstrap.table(
                      [],
                      [_.tr[
                           _.td[_.tt[html.escape(config_name).replace('_', '_<wbr/>')],
                                [_.br, ' ⟵ ', _.tt[html.escape(config_function.func_desc)
                                    .replace('.', '<wbr/>.').replace('_', '_<wbr/>')]]
                                if config_function.set_func else ''],
                           _.td[_.em[html.escape(config_function.doc)]],
                           _.td[
                               _.pre[html.escape(str(config_function))]
                               if current_user_has_permission
                               else acl.inline_permission_denied_message()
                           ]] for config_name, config_function in module_content.items()])
                  ]) if module_content.config_functions else '')
              for module_name, module_content in config.items()],
        title='Mara Configuration')



def navigation_entry():
    return navigation.NavigationEntry('Configuration (via config system)',
                                      uri_fn=lambda: flask.url_for('mara_config.configuration_page'),
                                      icon='cogs', rank=100)
