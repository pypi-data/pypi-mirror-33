#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_course'

urlpatterns = [
    url(r'^$', views.CourseRedirectView.as_view(), name='index'),
    # 偏好设置
    url(r'^preference$', views.set_preference, name='preference'),

    # =======课程========
    url(r'^courseList$', views.CourseList.as_view(), name='course_list'),
    url(r'^course/detail/(?P<pk>[0-9]+)$', views.CourseDetail.as_view(), name='course_detail'),
    url(r'^course/add/$', views.CourseCreate.as_view(), name='course_add'),
    url(r'^course/update/(?P<pk>[0-9]+)/$', views.CourseUpdate.as_view(), name='course_update'),
    url(r'^course/delete/(?P<pk>[0-9]+)/$', views.CourseDelete.as_view(), name='course_delete'),

    # =======课件========
    url(r'^sectionList$', views.SectionList.as_view(), name='section_list'),
    url(r'^section/detail/(?P<pk>[0-9]+)$', views.SectionDetail.as_view(), name='section_detail'),
    url(r'^section/add/$', views.SectionCreate.as_view(), name='section_add'),
    url(r'^section/update/(?P<pk>[0-9]+)/$', views.SectionUpdate.as_view(), name='section_update'),
    url(r'^section/delete/(?P<pk>[0-9]+)/$', views.SectionDelete.as_view(), name='section_delete'),

    # ===== 课程课件======
    url(r'^course/section/add/(?P<course_id>[0-9]+)/$', views.CourseSectionMidCreate.as_view(),
        name='course_section_mid_add'),
    # 修改课程课件的排序
    url(r'^course/section/update/(?P<csm_id>\d+)$', views.update_coursesectionmid, name='update_coursesectionmid'),
    # 图片上传
    url(r'^upload_image$', views.upload_image, name='upload_image'),
    # 给课件添加视频
    url(r'^create_section_video/(?P<section_id>\d+)$', views.create_section_video, name='create_section_video'),

    # ===== 视频 ======
    url(r'^video/list/$', views.VideoList.as_view(), name='video_list'),
    url(r'^video/detail/(?P<pk>[0-9]+)/$', views.VideoDetail.as_view(), name='video_detail'),
    url(r'^video/update/(?P<pk>[0-9]+)/$', views.VideoUpdate.as_view(), name='video_update'),
    url(r'^video/upload/$', views.VideoUpload.as_view(), name='video_upload'),
    # 1.选取文件后,获取video信息
    url(r'^cc/video/info/add/$', views.CCVideoInfoCreate.as_view(), name='cc_video_info_add'),
    # 2.上传完成后，记录video信息到数据库
    url(r'^cc/video/upload/done/$', views.cc_video_upload_done, name='cc_video_upload_done'),
    # 3.转码完成后cc的回调
    url(r'^cc/video/callback/', views.cc_video_callback, name='cc_video_callback'),
    # url(r'^vodio/play/$', views.play_video, name='play_video'),

    # ===== 录播 ======
    url(r'^live/list/$', views.LiveList.as_view(), name='live_list'),
    url(r'^live/list/(?P<user_id>[0-9]+)/$', views.manage_user_live_list, name='user_live_list'),
    # 查看录播视频页
    url(r'^live/video/(?P<live_video_id>(.)+)/$', views.live_video_detail, name='live_video_detail'),
    # 直播/录播 回调
    url(r'^live_callback$', views.cc_live_callback, name='user_live_callback'),

    # 用户课程
    url(r'^user_course/(?P<user_id>\d+)$', views.user_course, name='user_course'),
    # 用户学习的某一课程详情
    url(r'^user_course_section_list/(?P<user_course_id>\d+)$', views.user_course_section_list,
        name='user_course_section_list'),
    # 管理用户某一课程的列表
    url(r'^manage_user_course_section_list/(?P<user_course_id>\d+)$', views.manage_user_course_section_list,
        name='manage_user_course_section_list'),
    # 用户查看课程
    url(r'^view_courses$', views.view_courses, name='view_courses'),
    # 用户查看课程章节
    url(r'^user_course_section_detail/(?P<ucs_id>\d+)$', views.user_course_section_detail,
        name='user_course_section_detail'),

    # 查看用户列表
    url(r'^users$', views.user_list, name='users'),
    # 管理查看用户课程
    url(r'^manage_user_course/(?P<user_id>\d+)$', views.manage_user_course, name='manage_user_course'),
    # 给用户分配课程
    url(r'^choose_user_course/(?P<user_id>\d+)$', views.choose_user_course, name='choose_user_course'),
    # 删除用户课程
    url(r'^delete_user_course/(?P<user_course_id>\d+)$', views.delete_user_course, name='delete_user_course'),
    # 查看用户待评分作业列表
    url(r'^manage_assignments$', views.manage_user_assignments, name='manage_user_assignments'),

    # 查看指定用户所有作业
    url(r'^manage/user/(?P<user_id>\d+)/assignments$', views.manage_user_assignment_list,
        name='manage_user_assignment_list'),

    # 用户写作业的页面
    url(r'^user_assignment/(?P<ucs_id>\d+)$', views.user_assignment, name='user_assignment'),

    # 助教查看用户作业
    url(r'^manage_user_assignment/(?P<ucs_id>\d+)$', views.manage_user_assignment, name='manage_user_assignment'),

    # 用户提交作业图片
    url(r'^user_assignment_image_upload/(?P<ucs_id>\d+)$', views.user_assignment_image_upload,
        name='user_assignment_image_upload'),
    # 用户保存作业
    url(r'^save_user_assignment/(?P<ucs_id>\d+)$', views.save_user_assignment, name='save_user_assignment'),
    # 用户提交作业
    url(r'^submit_user_assignment/(?P<ucs_id>\d+)$', views.submit_user_assignment, name='submit_user_assignment'),

    # 给作业评分
    url(r'^review_user_assignment/(?P<ucs_id>\d+)/(?P<level>\d+)$', views.review_user_assignment,
        name='review_user_assignment'),

    # 手动开启课件
    url(r'^manage_open_user_course_section/(?P<ucs_id>\d+)$', views.open_user_course_section, name='open_user_course_section'),
]
