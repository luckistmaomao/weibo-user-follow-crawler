#encoding=utf8
'''
Created on 2014��4��21��

@author: cc
'''

import traceback

try:
    from advance_weibo_frame import URLWrapper
except ImportError as err:
    
    s = traceback.format_exc()
    
    print s
####################################URLWrapper Related#########################################
class AdvKeywordRealWeiboURLWrapper(URLWrapper):
    
    def __init__(self, keyword, page_num):
        '''
        Notice that page_num's type is string
        '''
        URLWrapper.__init__(self, URLWrapper.ADV_KEYWORD_REAL_WEIBO)
        self.keyword = keyword
        
        self.page_num = page_num
        self.is_first_parse = True
        
    def tostring(self):
        
        return 'url_type:' + self.url_type + 'keyword:' + self.keyword + 'page number' + self.page_num
    
    def to_url(self):
    
        url = 'http://weibo.com/' + self._get_uid(self.keyword) + '/info'
        
        return url
    
    def _get_uid(self, username):
        
        pass
###############################################################################################

####################################URLParser Related##########################################
###############################################################################################
####################################WeiboCrawler Related#######################################

###############################################################################################
####################################DataStorer Related#########################################
###############################################################################################