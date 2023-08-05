# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from django.db.models import Q
from .models import Course, Section, CourseSectionMid, Video, UserImage, UserCourse, UserAssignment, \
    UserAssignmentImage, SectionVideo, Preference, SectionAttach, UserSectionNote
from django.forms.models import inlineformset_factory


# ===== course contract======
class CourseForm(forms.ModelForm):
    status = forms.ChoiceField(choices=((0, '显示'), (1, '不显示')), label='显示状态')

    class Meta:
        model = Course
        fields = ['name', "subtitle", "level", "status", "image"]


# ===== section contract======
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name', "info", 'video_length_req',
                  'has_imagework', 'image_count_req','auto_pass']

class SectionAttachForm(forms.ModelForm):
    class Meta:
        model = SectionAttach
        fields = ['file']

section_attach_form = inlineformset_factory(Section, SectionAttach, form=SectionAttachForm, extra=1)


# 用户笔记
class UserSectionNoteForm(forms.ModelForm):
    class Meta:
        model = UserSectionNote
        fields = ['note', 'is_open']


class CourseSectionForm(forms.ModelForm):
    class Meta:
        model = CourseSectionMid
        fields = ['section', 'order_by']

    def __init__(self, course=None, *args, **kwargs):
        super(CourseSectionForm, self).__init__(*args, **kwargs)
        if course:
            self.fields['section'].queryset = Section.objects.filter(~Q(coursesectionmid__course=course))


class CourseSectionOrderForm(forms.ModelForm):
    class Meta:
        model = CourseSectionMid
        fields = ['order_by']



class CourseSectionMinForm(forms.ModelForm):
    class Meta:
        model = CourseSectionMid
        fields = ['section', 'order_by', 'mins']


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'info']


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserImage
        fields = ['image']

class UserCourseForm(forms.ModelForm):
    class Meta:
        model = UserCourse
        fields = ('course',)

    def __init__(self, user, *args, **kwargs):
        super(UserCourseForm, self).__init__(*args, **kwargs)

        self.fields['course'].queryset = Course.objects.exclude(usercourse__user=user)


class UserAssignmentForm(forms.ModelForm):
    class Meta:
        model = UserAssignment
        fields = ['content', ]


class UserAssignmentImageForm(forms.ModelForm):
    class Meta:
        model = UserAssignmentImage
        fields = ['image', ]


class SectionVideoForm(forms.ModelForm):
    class Meta:
        model = SectionVideo
        fields = ['video', ]

    def __init__(self, section=None, *args, **kwargs):
        super(SectionVideoForm, self).__init__(*args, **kwargs)

        if section:
            self.fields['video'].queryset = Video.objects.exclude(sectionvideo__section=section)


class PreferenceForm(forms.ModelForm):
    how_to_pass = forms.ChoiceField(choices=((0,'自动'), (1,'手动')), label='课程通过方式')

    class Meta:
        model = Preference
        fields = ['how_to_pass',]