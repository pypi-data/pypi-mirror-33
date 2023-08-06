#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os


def set_token(token):
    dust_path = '~/.dust/Gitlab'

    if not os.path.exists(dust_path):
        os.makedirs(dust_path)

    f = open(dust_path + '/TOKEN', 'w')
    f.write(token)
    f.close()


def get_token():
    try:
        f = open('~/.dust/Gitlab/TOKEN', 'r')
        token = f.read()
        f.close()
        return token
    except expression as identifier:
        return ''
