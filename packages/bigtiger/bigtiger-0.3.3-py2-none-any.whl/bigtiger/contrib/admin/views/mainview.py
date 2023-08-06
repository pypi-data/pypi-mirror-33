# -*- coding: utf-8 -*-

'''
Created on 2014-5-18
@author: linkeddt.com
'''

from __future__ import unicode_literals

import json

from django import forms
from django.conf import settings
from django.contrib import auth
from django.shortcuts import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.module_loading import import_string

from bigtiger.core.exceptions import AuthenticateError
from bigtiger.views.generic import TemplateResponseMixin, View, SysConfContextMixin, PermissionMixin
from bigtiger.utils.tree import tree_sorted


def load_backend(path):
    return import_string(path)()


class LoginView(SysConfContextMixin, TemplateResponseMixin, View):
    template_name = "admin/login.htm"

    def get(self, request, *args, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['form'] = LoginForm()
        context['errortip'] = None
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                return self.authenticate(cd['username'], cd['password'])
            except AuthenticateError as e:
                errortip = e.message
        else:
            errortip = u'用户名和密码不能为空，请输入。'

        context['form'] = LoginForm()
        context['errortip'] = errortip
        return self.render_to_response(context)

    def authenticate(self, username, password):
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise AuthenticateError(u'用户名或密码有误，请重新输入。')
        elif user.is_active == 0:
            raise AuthenticateError(u'用户名未激活，请联系管理员激活该用户。')
        else:
            auth.login(self.request, user)
            permissions = self.get_permissions(user)
            self.request.session[settings.PERMISSIONS_SESSION_KEY] = permissions
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    def get_permissions(self, user):
        backend_path = user.backend
        if backend_path in settings.AUTHENTICATION_BACKENDS:
            backend = load_backend(user.backend)
            permissions = backend.get_group_permissions(user)
            return permissions
        else:
            return None


def menu_order(menus):
    return sorted(menus, key=lambda e: e['order_number'], reverse=False)


def gen_menu_tree(parent_menu, menus):
    parent_menu_id = parent_menu['id']
    parent_menu_depth = (parent_menu['depth'] or 0) + 1

    chlid_menus = [item for item in menus if item['parent_id']
                   == parent_menu_id and item['depth'] == parent_menu_depth]
    chlid_menus = menu_order(chlid_menus)

    if chlid_menus:
        parent_menu['childs'] = chlid_menus
        for item in chlid_menus:
            gen_menu_tree(item, menus)


class MainView(SysConfContextMixin, PermissionMixin, TemplateResponseMixin, View):
    template_name = "admin/main.htm"

    def get(self, request, *args, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)

        ps = self.get_session_permissions()
        if ps is None:
            return HttpResponseRedirect('/')

        root_menu = [item for item in ps if item['parent_id'] is None].pop()
        gen_menu_tree(root_menu, ps)

        cols = self.gen_menu_cols(ps, 15)
        context['root_menu'] = root_menu
        context['menusJson'] = mark_safe(json.dumps(root_menu))
        context['cols'] = cols
        return self.render_to_response(context)

    def gen_menu_cols(self, ps, col_count=12):
        """ 构建菜单清单中的菜单数据，用于模板的显示
        """
        lst = tree_sorted(ps, key=lambda item: item['order_number'], join=lambda item,
                          parent_item: item['parent_id'] == parent_item['id'])
        lst = filter(lambda item: item['depth'] < 4, lst)

        cols, col, index, line, mainId = [], None, 0, None, None
        for item in lst:
            if index % col_count == 0:
                col = []
                cols.append(col)

            depth = item['depth']

            if depth == 1:
                mainId = item['id']

            if depth == 2:
                line = item
                line['children'] = []
                col.append(line)
            elif depth == 3:
                item['mainId'] = mainId
                line['children'].append(item)
            index = index + 1
        return cols


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(settings.LOGOUT_URL)


class LoginForm(forms.Form):
    username_error = {'required': '请输入用户名'}
    password_error = {'required': '请输入密码'}
    username = forms.CharField(label='用户名：', max_length=30,  widget=forms.TextInput(
        attrs={'class': 'form-control input-lg', 'placeholder': '请输入用户名'}), error_messages=username_error)
    password = forms.CharField(label='密码：',  max_length=30, widget=forms.PasswordInput(
        attrs={'class': 'form-control input-lg', 'placeholder': '请输入密码'}), error_messages=password_error)
