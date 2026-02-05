__menu = {
    'uri': __package__,
    'name': 'RSS2',
    'list': [
        {'uri': 'search', 'name': '검색'},
        {'uri': 'group', 'name': '그룹'},
        {'uri': 'scheduler', 'name': '스케줄러'},
        {'uri': 'site', 'name': '지원 사이트'},
        {'uri': 'setting', 'name': '설정'},
        {'uri': 'log', 'name': '로그'},
    ]
}

setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': False,
    'home_module': None,
    'menu': __menu,
    'setting_menu': None,
    'default_route': 'normal',
}

from plugin import *  # FlaskFarm 공용 (PluginModuleBase, render_template, jsonify, request 등)
import logging

package_name = __package__

# 구버전 rss2에서 사용하던 plugin_info를 호환 차원에서 유지
plugin_info = {
    'version' : '0.1.0.0',
    'name' : u'RSS',
    'category_name' : 'torrent',
    'icon' : '',
    'developer' : 'soju6jan',
    'description' : u'토렌트 크롤링. 크롤링한 데이터, Bot으로 수신한 데이터 검색',
    'home' : 'https://github.com/soju6jan/rss2',
    'more' : '',
}

P = create_plugin_instance(setting)

# 로거: 신형 FlaskFarm에서는 framework.logger가 없을 수 있어 P.logger 우선 사용
logger = getattr(P, 'logger', logging.getLogger(__package__))

from .mod_main import ModuleSetting, ModuleSite, ModuleScheduler, ModuleGroup, ModuleSearch
P.set_module_list([ModuleSearch, ModuleGroup, ModuleScheduler, ModuleSite, ModuleSetting])