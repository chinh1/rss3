from .setup import *

# rss2 구버전 코드의 'ajax/<sub>' 분기 로직을 그대로 옮긴 공용 디스패처
def dispatch_ajax(sub, req):
    try:
        # 원본과 동일하게 request.form / request.args 사용
        from framework import scheduler, app, db
        from system.model import ModelSetting as SystemModelSetting
        from .logic import Logic
        from .model import ModelSetting, ModelSite2
        from .logic_self import LogicSelf
        from .logic_search_self import LogicSearchSelf

        ret = {}

        # setting
        if sub == 'setting_save':
            ret = ModelSetting.setting_save(req)
            return jsonify(ret)

        elif sub == 'scheduler':
            go = req.form['scheduler']
            logger.debug('scheduler :%s', go)
            if go == 'true':
                Logic.scheduler_start()
            else:
                Logic.scheduler_stop()
            return jsonify(go)

        elif sub == 'one_execute':
            ret = Logic.one_execute()
            return jsonify(ret)

        elif sub == 'reset_db':
            ret = Logic.reset_db()
            return jsonify(ret)

        # site
        elif sub == 'load_site':
            ret['site'] = ModelSite2.get_list(by_dict=True)
            return jsonify(ret)

        elif sub == 'test':
            ret = LogicSelf.action_test(req)
            return jsonify(ret)

        elif sub == 'site_delete':
            ret['ret'] = ModelSite2.delete(req.form['site_id'])
            ret['site'] = ModelSite2.get_list(by_dict=True)
            return jsonify(ret)

        elif sub == 'site_edit':
            ret['ret'] = LogicSelf.site_edit(req)
            ret['site'] = ModelSite2.get_list(by_dict=True)
            return jsonify(ret)

        # scheduler
        elif sub == 'load_scheduler':
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['scheduler'] = LogicSelf.get_scheduler_list()
            return jsonify(ret)

        elif sub == 'add_scheduler':
            ret['ret'] = LogicSelf.add_scheduler(req)
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['scheduler'] = LogicSelf.get_scheduler_list()
            return jsonify(ret)

        elif sub == 'remove_scheduler_db':
            ret['ret'] = LogicSelf.remove_scheduler_db_from_id(req.form['db_id'])
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['scheduler'] = LogicSelf.get_scheduler_list()
            return jsonify(ret)

        elif sub == 'remove_scheduler':
            ret['ret'] = LogicSelf.remove_scheduler(req)
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['scheduler'] = LogicSelf.get_scheduler_list()
            return jsonify(ret)

        # group
        elif sub == 'load_group':
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['group'] = LogicSelf.get_group_list()
            ret['info'] = LogicSelf.get_search_form_info()
            return jsonify(ret)

        elif sub == 'add_group':
            ret['ret'] = LogicSelf.add_group(req)
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['group'] = LogicSelf.get_group_list()
            ret['info'] = LogicSelf.get_search_form_info()
            return jsonify(ret)

        elif sub == 'remove_group':
            ret['ret'] = LogicSelf.remove_group(req)
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['group'] = LogicSelf.get_group_list()
            ret['info'] = LogicSelf.get_search_form_info()
            return jsonify(ret)

        elif sub == 'add_group_child':
            ret['ret'] = LogicSelf.add_group_child(req)
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['group'] = LogicSelf.get_group_list()
            ret['info'] = LogicSelf.get_search_form_info()
            return jsonify(ret)

        elif sub == 'remove_group_child':
            ret['ret'] = LogicSelf.remove_group_child(req)
            ret['site'] = ModelSite2.get_list(by_dict=True)
            ret['group'] = LogicSelf.get_group_list()
            ret['info'] = LogicSelf.get_search_form_info()
            return jsonify(ret)

        # search
        elif sub == 'list':
            ret = LogicSearchSelf.get_list_by_web(req)
            return jsonify(ret)

        elif sub == 'torrent_info':
            try:
                from torrent_info import Logic as TorrentInfoLogic
                data = req.form['hash']
                logger.debug(data)
                if data.startswith('magnet'):
                    ret = TorrentInfoLogic.parse_magnet_uri(data)
                else:
                    ret = TorrentInfoLogic.parse_torrent_url(data)
                return jsonify(ret)
            except Exception as e:
                logger.error('Exception:%s', e)
                import traceback
                logger.error(traceback.format_exc())
                return jsonify({'ret':'fail', 'msg':str(e)})

        elif sub == 'server_test':
            logger.debug('server_test')
            # 원본에선 서버에서만 테스트 실행. 여기서는 noop로 유지.
            return jsonify({'ret':'success', 'msg':'server_test endpoint is disabled in FF port'})

        return jsonify({'ret':'fail', 'msg':f'Unknown command: {sub}'})
    except Exception as e:
        import traceback
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())
        return jsonify({'ret':'fail', 'msg':str(e)})


class _BaseModule(PluginModuleBase):
    template_name = None

    def __init__(self, P, name):
        super(_BaseModule, self).__init__(P, name=name)

    def process_menu(self, page, req):
        return render_template(self.template_name, arg=self.get_arg(req))

    def process_command(self, command, arg1, arg2, arg3, req):
        # command에 ajax sub 이름을 그대로 사용
        return dispatch_ajax(command, req)

    def get_arg(self, req):
        # 페이지 렌더링에 필요한 arg를 원본 first_menu 로직에서 그대로 가져옴
        from framework import scheduler, app

        # 구버전(SJVA/구 FlaskFarm)에서는 system.model.ModelSetting 을 사용했지만
        # 신형 FlaskFarm에서는 모듈 경로가 달라져 ImportError가 발생할 수 있습니다.
        # rss3 포팅본은 가능한 한 "동작"을 우선하도록, 설정 모델이 없으면 기본값으로 처리합니다.
        SystemModelSetting = None
        try:
            from system.model import ModelSetting as SystemModelSetting  # type: ignore
        except Exception:
            try:
                from flaskfarm.lib.system.model import ModelSetting as SystemModelSetting  # type: ignore
            except Exception:
                try:
                    from flaskfarm.lib.system import ModelSetting as SystemModelSetting  # type: ignore
                except Exception:
                    SystemModelSetting = None

        class _DummySystemSetting:
            @staticmethod
            def get(key, default=None):
                return default

            @staticmethod
            def get_bool(key, default=False):
                return default

        if SystemModelSetting is None:
            SystemModelSetting = _DummySystemSetting
        from .model import ModelSetting, ModelSite2
        arg = {'package_name': package_name}

        if self.name == 'setting':
            arg.update(ModelSetting.to_dict())
            arg['scheduler'] = str(scheduler.is_include(package_name))
            arg['is_running'] = str(scheduler.is_running(package_name))
            arg['is_test_server'] = (app.config['config']['is_server'] or app.config['config']['is_debug'])

        elif self.name in ['site', 'scheduler', 'group']:
            pass

        elif self.name == 'search':
            arg['ddns'] = SystemModelSetting.get('ddns', '')
            try:
                import downloader
                arg['is_available_normal_download'] = downloader.Logic.is_available_normal_download()
            except Exception:
                arg['is_available_normal_download'] = False

            arg['search_word'] = req.args.get('search_word')
            arg['is_torrent_info_installed'] = False
            try:
                import torrent_info
                arg['is_torrent_info_installed'] = True
            except Exception:
                pass

            arg['apikey'] = ''
            if SystemModelSetting.get_bool('auth_use_apikey', False):
                arg['apikey'] = SystemModelSetting.get('auth_apikey', '')

        return arg


class ModuleSetting(_BaseModule):
    def __init__(self, P):
        super(ModuleSetting, self).__init__(P, name='setting')
        self.template_name = 'setting.html'


class ModuleSite(_BaseModule):
    def __init__(self, P):
        super(ModuleSite, self).__init__(P, name='site')
        self.template_name = 'site.html'


class ModuleScheduler(_BaseModule):
    def __init__(self, P):
        super(ModuleScheduler, self).__init__(P, name='scheduler')
        self.template_name = 'scheduler.html'


class ModuleGroup(_BaseModule):
    def __init__(self, P):
        super(ModuleGroup, self).__init__(P, name='group')
        self.template_name = 'group.html'


class ModuleSearch(_BaseModule):
    def __init__(self, P):
        super(ModuleSearch, self).__init__(P, name='search')
        self.template_name = 'search.html'
