
from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt
from mycms.views import  (
                       CMSContentsAPIView,
                       CMSEntriesAPIView,
                       CMSMarkUpsAPIView,
                       CMSTemplatesAPIView,
                       CMSPageView,
                       CMSPathsAPIView,
                       CMSEntriesROAPIView,
                       LoremIpsumAPIView,
                       AssetsUploaderView,
                       CMSPageTypesAPIView,
                       CMSFileUpload,

                       )

from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views as authtoken_views

from mycms.views import TemplateSampleLoader
from rest_framework import routers

from mycms import api

from mycms.views import CMSFormatterContent
urlpatterns = [

    url(r'^search/', include('haystack.urls')),
    
    
    #url(r'^cmsupload$',  csrf_exempt(CMSFileUpload.as_view()), name="cmsfileupload"),
    #url(r'^(?P<path>[-/\.a-z\d_]*)/assets_manager/$', csrf_exempt(CMSFileUpload.as_view()), name="assets_manager_get"),

    #url(r'^api/v1/cmsentriesro', CMSEntriesROAPIView.as_view(), name="cmsentriesro_apiview"),
    #url(r'^api/v1/docs/', include_docs_urls(title='YACMS API Documentation')),

    ##Read Write API Views
    #url(r'^api/v1/cmspagetypes', CMSPageTypesAPIView.as_view(), name="cmspagetypes_apiview"),
    
    #url(r'^api/v1/cmscontents/(?P<resource_id>[\d]+)/$', CMSContentsAPIView.as_view(), name="cmscontents_apiview"),
    #url(r'^api/v1/cmscontents', CMSContentsAPIView.as_view(), name="cmscontents_apiview"),
    
    #url(r'^api/v1/cmsentries/(?P<resource_id>[\d]+)/$', CMSEntriesAPIView.as_view(), name="cmsentries_apiview_detail"),
    #url(r'^api/v1/cmsentries', CMSEntriesAPIView.as_view(), name="cmsentries_apiview"),
    
    #url(r'^api/v1/cmsmarkups', CMSMarkUpsAPIView.as_view(), name="cmscmsmarkups_apiview"),
    #url(r'^api/v1/cmstemplates', CMSTemplatesAPIView.as_view(), name="cmstemplates_apiview"),
   
    #url(r'^api/v1/cmspaths', CMSPathsAPIView.as_view(), name="cmspaths_apiview"),
    #url(r'^api/v1/cmspaths/(?P<resource_id>[\d]+)?/?$', CMSPathsAPIView.as_view(), name="cmspaths_apiview_detail"),

    #url(r'^api/v1/loremipsum', LoremIpsumAPIView.as_view(), name="loremipsum"),

    ##CMS API Custom Views
    #url(r'^api/v1/cmsentries/(?P<id>[\d]*)/', 
        #CMSEntriesAPIView.as_view(), 
        #name="cmsentries_apiview"),
    
    #url(r'^api/v1/cmsentries/(?P<slug>[-/\.a-z\d_]*)/', 
        #CMSEntriesAPIView.as_view(), 
        #name="cmsentries_apiview"),

    ##Assets Manager Views
    #url(r'^(?P<path>[-/\.a-z\d_]*)/assets_manager/(?P<filename>[-/\.a-z\d_]*)$', 
        #AssetsUploaderView.as_view(), 
        #name="assets_manager_post"),
    
    #url(r'^(?P<path>[-/\.a-z\d_]*)/assets_manager/$', 
        #AssetsUploaderView.as_view(), 
        #name="assets_manager_get"),
        
    url(r'^(?P<path>[-/\.a-z\d_]*)/assets_manager/$', csrf_exempt(AssetsUploaderView.as_view()), name="assets_manager_get"),
    url(r'^(?P<path>[-/\.a-z\d_]*)/assets_manager/(?P<filename>[-/\.a-z\d_A-Z]*)$', csrf_exempt(AssetsUploaderView.as_view()), name="assets_manager_get"),
    url(r'^templates/(?P<template>[-._\w\W\d]*.html)$', TemplateSampleLoader.as_view()),
    url(r'^templates/?$', TemplateSampleLoader.as_view()),    
    
   


    #url(r'api/v2/utils/cmsformatter/(?P<content_id>[\d]*)/$', api.CMSFormatterContent.as_view()),
    ##CMS View - Returns website pages
    url(r'^(?P<path>[-/\.a-z\d_]*)/$', CMSPageView.as_view(), name="cms_page"),
    url(r'^$', CMSPageView.as_view(), name="cms_page"),
    
    
    #url(r'^fileupload$', 'mycms.views.fileupload', name="fileupload"),


    #url(r'^(?P<path>[-/\.a-z\d_]*)/fileUploader/$', 'mycms.views.fileupload', name="page"),
    #url(r'^(?P<path>[-/\.a-z\d_]*)/$', 'mycms.views.page', name="page"),
    #url(r'^(?P<path>[-/\.a-z\d_]*)$', 'mycms.views.page', name="page"),

]


schema_view = get_schema_view(title="MyCMS API")

cms_root = [url(r'^$', CMSPageView.as_view(), name="cms_page"),
            url(r'^api/v2/docs/', include_docs_urls(title='MyCMS API')),
             url('^api/v2/schemas/', schema_view),
            url(r'api/v2/cmsauthtoken', api.CMSAuthToken.as_view({'post': 'retrieve'}), name='cmsauthtoken')
        ]


router = routers.DefaultRouter()
#router.register(r'zones/(?P<zone_name>[-/\.a-z\d_]*)/records', RecordsViewSet, base_name='Records')
router.register(r'api/v2/cmscontents', api.CMSContentsViewSet, base_name='cmscontents')
router.register(r'api/v2/cmsentries', api.CMSEntriesViewSet, base_name='cmsentries')
router.register(r'api/v2/cmspaths', api.CMSPathsViewSet, base_name='cmspaths')
router.register(r'api/v2/cmspages', api.CMSPagesViewSet, base_name='cmspages')
#router.register(r'api/v2/cmsauthtoken', api.CMSAuthToken, base_name='cmsauthtoken')
#router.register(r'api/v2/utils/cmsformatter/(?P<content_id>[\d]*)/$', CMSFormatterContent, base_name='cmsformatter')

urlpatterns =  cms_root + router.urls + urlpatterns 

#for i in urlpatterns:
#    print(i)