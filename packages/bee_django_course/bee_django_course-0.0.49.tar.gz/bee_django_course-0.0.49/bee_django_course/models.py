#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import os

# Create your models here.



# 课程
class Course(models.Model):
    name = models.CharField(max_length=180, verbose_name='课程名字')  # 名字
    subtitle = models.CharField(max_length=180, null=True, verbose_name='课程副标题', blank=True)  # 副标题
    level = models.IntegerField(default=0, verbose_name='课程的level', blank=True)  # 课程的level
    is_del = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, verbose_name='授课老师')
    image = models.ImageField(null=True, blank=True, verbose_name='配图', upload_to='course/face')
    status = models.IntegerField(verbose_name='状态', default=0) # 0 不显示，1 显示在列表

    class Meta:
        db_table = 'bee_django_course_course'
        app_label = 'bee_django_course'
        ordering = ["-id"]
        verbose_name = 'course课程'
        permissions = (
            ('can_manage_course', '可以进入课程管理页'),
            ('view_all_courses', '可以查看所有课程'),
            ('can_choose_course', 'can choose course'),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bee_django_course:course_detail', kwargs={'pk': self.pk})

    def is_my_course(self, user):
        user_course = UserCourse.objects.filter(user=user, course=self)
        if user_course.exists():
            return user_course.first()
        else:
            return None


class Section(models.Model):
    name = models.CharField(max_length=180, verbose_name='课件名字')  # 名字
    info = models.TextField(null=True, blank=True, verbose_name='正文')
    videos = models.ManyToManyField("bee_django_course.Video")
    has_textwork = models.BooleanField(verbose_name='是否需要文字作业', default=False)
    textwork_info = models.TextField(verbose_name='作业说明', null=True, blank=True)
    has_videowork = models.BooleanField(verbose_name='是否需要视频录制', default=True)
    has_imagework = models.BooleanField(verbose_name='是否需要上传图片', default=False)

    video_length_req = models.IntegerField(verbose_name='要求录制时长(分钟)', default=0)
    image_count_req = models.IntegerField(verbose_name='要求提交图片数量', default=0)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'bee_django_course_section'
        app_label = 'bee_django_course'
        ordering = ["-id"]
        verbose_name = 'course课件'
        permissions = (
            ('view_all_sections', '可以查看所有课件'),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bee_django_course:section_detail', kwargs={'pk': self.pk})


# 课件的用户笔记
class UserSectionNote(models.Model):
    section = models.ForeignKey(Section)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    note = models.TextField(verbose_name='学习笔记')
    is_open = models.BooleanField(default=True, verbose_name='公开笔记')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


# 课件的附件
class SectionAttach(models.Model):
    section = models.ForeignKey(Section)
    file = models.FileField(verbose_name='附件', upload_to='sections/%Y/%m/%d/')
    upload_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bee_django_course_section_attach'

    def file_name(self):
        return os.path.basename(self.file.name)


# 课程课件中间件
class CourseSectionMid(models.Model):
    course = models.ForeignKey("bee_django_course.Course", verbose_name='课程')  # 课程
    section = models.ForeignKey("bee_django_course.Section", verbose_name="课件")  # 课程包
    order_by = models.IntegerField(default=0, verbose_name="顺序")  # 顺序
    mins = models.IntegerField(null=True, blank=True, verbose_name='达标分钟数')  # 达标分钟数

    class Meta:
        db_table = 'bee_django_course_section_mid'
        app_label = 'bee_django_course'
        ordering = ['order_by']

    def __unicode__(self):
        return ("CourseSectionMid->course:" + self.course.name)


class Video(models.Model):
    video_id = models.CharField(max_length=180, null=True)  # 视频 id，16位 hex 字符串
    status = models.CharField(max_length=180, null=True)  # 视频状态。”OK”表示视频处理成功，”FAIL”表示视频处理失败。
    duration = models.CharField(max_length=180, null=True)  # 片长（单位:秒）
    image = models.CharField(max_length=180, null=True)  # 视频截图地址
    # ===========
    title = models.CharField(max_length=180, null=True, verbose_name='标题')  # 视频标题
    info = models.TextField(verbose_name='说明', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey("users.User", related_name='cc_video_user', null=True)  # 由谁上传
    # video_status = models.IntegerField(default=1, null=True)  # 状态 1-正常，2-正常（删除视频）

    class Meta:
        db_table = 'bee_django_course_video'
        app_label = 'bee_django_course'
        ordering = ['-created_at']
        verbose_name='course视频'
        permissions = (
            ('view_all_videos', '可以查看所有视频'),
        )

    def __unicode__(self):
        return ("视频:" + self.title)

    def get_absolute_url(self):
        # return reverse('bee_django_course:video_detail', kwargs={'pk': self.pk})
        return reverse('bee_django_course:video_list')


class SectionVideo(models.Model):
    section = models.ForeignKey(Section, verbose_name='关联的课件')
    video = models.ForeignKey(Video, verbose_name='关联的视频')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bee_django_course_section_video'


class UserLive(models.Model):
    provider_name = models.CharField(max_length=180)  # 平台商
    cc_user_id = models.CharField(max_length=180, null=True)  # CC账号
    room_id = models.CharField(max_length=180, null=True)  # 直播间ID
    live_id = models.CharField(max_length=180, null=True)  # 直播ID
    stop_status = models.CharField(max_length=180, null=True)  # 直播结束状态，10：正常结束，20：非正常结束
    record_status = models.CharField(max_length=180, null=True)  # 直播录制状态，10：录制成功，20：录制失败，30：直播过长
    record_video_id = models.CharField(max_length=180, null=True)  # 录制视频ID（如果录制成功，则返回该参数）
    replay_url = models.CharField(max_length=180, null=True)  # 直播回放地址（如果录制成功，则返回该参数）
    start_time = models.DateTimeField(null=True)  # 直播开始时间
    end_time = models.DateTimeField(null=True)  # 直播结束时间
    user = models.ForeignKey(settings.AUTH_USER_MODEL)  # 学生
    duration = models.IntegerField(null=True)  # 秒
    record_video_duration = models.IntegerField(null=True)  # 秒 返回的视频时间
    status = models.IntegerField(default=1, null=True)  # 状态 1-正常，2-正常（删除视频），-1：删除 -2 删除（删除视频）
    created_at = models.DateTimeField(auto_now_add=True)
    call_count = models.IntegerField(default=0)  # 回调了几次

    class Meta:
        db_table = 'bee_django_course_user_live'
        app_label = 'bee_django_course'
        ordering = ['-created_at']
        verbose_name='course学生录播'
        permissions = (
            ('view_all_userlives', '可以查看所有学生的录播'),
            ('view_teach_userlives', '可以查看所教的学生的录播'),
        )

    def __unicode__(self):
        return ("UserLive->room_id:" + self.room_id)


class UserImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    image = models.ImageField(verbose_name='图片', upload_to='course/%Y/%m/%d')
    upload_at = models.DateTimeField(verbose_name='上传时间', auto_now_add=True)

    class Meta:
        db_table = 'bee_django_course_user_image'


class UserCourse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    course = models.ForeignKey(Course, verbose_name='课程')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0, verbose_name='状态')  # 0 学习中，1 已完成
    passed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'bee_django_course_user_course'


class UserCourseSection(models.Model):
    user_course = models.ForeignKey(UserCourse)
    section = models.ForeignKey(Section)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(default=0)  # 0 未开始， 1 学习中，2 通过，3 退回重修, 4 提交
    score = models.IntegerField(blank=True, null=True, verbose_name='得分')
    work_time = models.IntegerField(verbose_name='总共练习时间', null=True, blank=True, default=0)  # 学生总共练习时间
    comment = models.TextField(null=True, blank=True, verbose_name='评语')

    class Meta:
        db_table = 'bee_django_course_user_course_section'
        ordering = ['-created_at']
        verbose_name='course学生课件'
        permissions=[
            ('view_all_usercoursesection', '查看所有学生课件'),
            ('view_teach_usercoursessection', '查看所教的学生课件'),
        ]

    def open_ucs(self):
        self.status = 1
        self.updated_at = timezone.now()
        self.save()

    def is_learning(self):
        return self.status == 1

    def is_passed(self):
        return self.status == 2

    def is_rejected(self):
        return self.status == 3

    def is_submit(self):
        return self.status == 4

    def be_submit(self):
        self.status = 4
        self.updated_at = timezone.now()
        self.save()

    @transaction.atomic
    def get_pass(self, score, comment=None):
        self.score = score
        self.comment = comment
        self.updated_at = timezone.now()
        self.status = 2
        self.save()

        # 自动开启下一课
        next_section = self.next_section()
        if next_section:
            next_section.open_ucs()

    @transaction.atomic
    def reject(self):
        self.score = None
        self.updated_at = timezone.now()
        self.comment = None
        self.status = 3
        self.save()

    def update_work_time(self, minutes):
        if not self.work_time:
            self.work_time = 0
        self.work_time += minutes
        self.save()

        # 如果此课件只有视频的练习，则练习时间达标后，自动通过
        if self.section.has_videowork and not self.section.has_imagework and not self.section.has_textwork:
            if self.work_time >= self.section.video_length_req:
                self.get_pass()

    def next_section(self):
        order_sets = self.section.coursesectionmid_set.filter(course=self.user_course.course,
                                                              section=self.section)
        if order_sets.exists():
            order = order_sets.first().order_by
            ucs = UserCourseSection.objects.filter(user_course=self.user_course, status=0,
                                                   section__coursesectionmid__order_by__gte=order) \
                .order_by('section__coursesectionmid__order_by')
            if ucs.exists():
                return ucs.first()
            else:
                return None
        else:
            return None


class UserAssignment(models.Model):
    user_course_section = models.ForeignKey(UserCourseSection)
    content = models.TextField(verbose_name='正文', null=True, blank=True)  # 文字作业
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(blank=True, null=True, verbose_name='得分')

    class Meta:
        permissions = (
            ('can_review', 'can review'),
        )
        db_table = 'bee_django_course_user_assignment'

    def submit(self):
        self.status = 1
        self.submit_at = timezone.now()
        self.save()

    def reject(self):
        self.status = 2
        self.rejected_at = timezone.now()
        self.save()


class UserAssignmentImage(models.Model):
    user_course_section = models.ForeignKey(UserCourseSection, null=True, blank=True)
    image = models.ImageField(verbose_name='图片作业', upload_to='assignments/%Y/%m/%d')
    upload_at = models.DateTimeField(verbose_name='上传时间', auto_now_add=True)

    class Meta:
        db_table = 'bee_django_course_user_assignment_image'


class Preference(models.Model):
    how_to_pass = models.IntegerField(verbose_name='课程通过模式', default=0)  # 0 自动， 1 手动
