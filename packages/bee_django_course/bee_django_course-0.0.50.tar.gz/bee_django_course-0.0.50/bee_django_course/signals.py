# -*- coding:utf-8 -*-
from django.dispatch import Signal

# 作业被评分前发出的信号
assignment_will_be_scored = Signal(providing_args=["user_course_section", "request"])

# 作业评分后发出的信号
assignment_was_scored = Signal(providing_args=["user_course_section", "request"])

# 直播回调后发出的信号
live_callback_finished = Signal(providing_args=["user_live", "coin_multiple"])

# 笔记创建的信号
section_note_created = Signal(providing_args=["user_section_note_id"])
