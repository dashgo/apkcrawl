# -*- encoding=utf-8
import datetime

apkcrawlitems = {
        0:{ 'site'         : 'apk.hiapk.com' , 
          'is_entry'     : True            , 
          'referer_url'  : 'http://apk.hiapk.com/'                                , 
          'entry_url'    : 'http://apk.hiapk.com/html/2013/01/1135399.html'       , 
          'download_url' : 'http://apk.hiapk.com/Download.aspx?aid=1135399&em=14' },
        1:{ 'site'         : 'apk.hiapk.com' , 
          'is_entry'     : True            , 
          'referer_url'  : 'http://apk.hiapk.com/'                           , 
          'entry_url'    : 'http://apk.hiapk.com/html/2013/01/1122483.html',
          'download_url' : 'http://apk.hiapk.com/Download.aspx?aid=1122483&em=14'},

        ## 3 相同站点相同地址(entry_url,download_url)，identifier不一样，apk文件MD5不同
        ### 安智网站 没有软件版本概念，地址只能下载最新版本，需要变更identifier以重新签入下载队列
        ### signin后更改identifier
        22:{
          'site'       : 'www.anzhi.com',
          'is_entry'   : True,
          'referer_url': 'http://www.anzhi.com/',
          'entry_url'  : 'http://www.anzhi.com/soft_620594.html',
          'download_url': 'http://www.anzhi.com/dl_app.php?s=620594',
        },
        2:{ "site": "android.myapp.com", 
            "is_entry": False, 
            "referer_url": "http://android.myapp.com/", 
            "download_url": "http://android.myapp.com/android/down.jsp?appid=656176&pkgid=802543", 
            "entry_url": "http://android.myapp.com/android/appdetail.jsp?appid=656176&pkgid=802543"},
        # 语音搜索 2.1.4 , 2.21MB

        3:{ "site": "android.myapp.com", 
            "is_entry": False, 
            "referer_url": "http://android.myapp.com/android/appdetail.jsp?appid=45592&pkgid=672257", 
            "download_url": "http://android.myapp.com/android/down.jsp?appid=45592&pkgid=668827", 
            "entry_url": "http://android.myapp.com/android/appdetail.jsp?appid=45592&pkgid=668827"},
        # 语音搜索 2.1.4 , 2.21MB
        4:{ 'site'         : 'apk.91.com' , 
          'is_entry'     : True            , 
          'referer_url'  : 'http://apk.91.com/'                           , 
          'entry_url'    : 'http://apk.91.com/Soft/Android/com.google.android.voicesearch-2.1.4.html',
          'download_url' : 'http://apk.91.com/soft/Controller.ashx?Action=Download&id=4104991'},
        # 一个 1.3 , 1.46MB
        5:{ 'site'         : 'apk.91.com' , 
          'is_entry'     : True            , 
          'referer_url'  : 'http://apk.91.com/'                           , 
          'entry_url'    : 'http://apk.91.com/Soft/Android/one.hh.oneclient-12.html',
          'download_url' : 'http://apk.91.com/soft/Controller.ashx?Action=Download&id=4717015'},
        # 网易公开课, 2.0.6, 3.76MB
        6:{ 'site'         : 'apk.hiapk.com' , 
          'is_entry'     : True            , 
          'referer_url'  : 'http://apk.hiapk.com/'                           , 
          'entry_url'    : 'http://apk.hiapk.com/html/2012/12/1075297.html',
          'download_url' : 'http://apk.hiapk.com/Download.aspx?aid=1075297&em=14'},
        # 搜狐新闻, 3.2.1, 2.73MB
        7:{ 'site'         : 'apk.hiapk.com' , 
          'is_entry'     : True            , 
          'referer_url'  : 'http://apk.hiapk.com/'                           , 
          'entry_url'    : 'http://apk.hiapk.com/html/2012/12/1070499.html',
          'download_url' : 'http://apk.hiapk.com/Download.aspx?aid=1070499&em=14'},
        # 时尚手电 4.9.4 , 1.28MB
        8:{ 'site'         : 'apk.hiapk.com' , 
          'is_entry'     : True            , 
          'referer_url'  : 'http://apk.hiapk.com/'                           , 
          'entry_url'    : 'http://apk.hiapk.com/html/2012/12/1030826.html',
          'download_url' : 'http://apk.hiapk.com/Download.aspx?aid=1030826&em=14'},
        # 前程无忧, 2.2.3, 2.82MB
        9:{ 'site'         : 'apk.hiapk.com' , 
          'is_entry'     : True            , 
          'referer_url'  : 'http://apk.hiapk.com/'                           , 
          'entry_url'    : 'http://apk.hiapk.com/html/2013/01/1111489.html',
          'download_url' : 'http://apk.hiapk.com/Download.aspx?aid=1111489&em=14'},

        # 安智网，做了ajax防盗链处理，暂时无法处理
        24:{ "site": "www.anzhi.com", 
             "is_entry": True, 
             "referer_url": "http://www.anzhi.com/search.php?search_key=%E6%89%8B%E6%9C%BAQQ2012&type=0", 
             "download_url": "http://www.anzhi.com/dl_app.php?s=274054",
             "entry_url": "http://www.anzhi.com/soft_274054.html", },
        25:{ "site": "apk.91.com", 
             "is_entry": True, 
             "referer_url": "http://apk.91.com/soft/Android/search/1_5_0_0_%E6%89%8B%E6%9C%BAQQ2012",
             "download_url": "http://apk.91.com/soft/Controller.ashx?Action=Download&id=4678215", 
             "entry_url": "http://apk.91.com/Soft/Android/com.book_gfdfd-2.html"},
        26:{
               'site'       : 'www.anzhi.com',
             "is_entry": True,
             "referer_url": "http://www.anzhi.com/search.php?search_key=%E6%8D%95%E9%B1%BC%E8%BE%BE%E4%BA%BA&type=0", 
             "download_url": "http://www.anzhi.com/dl_app.php?s=622459", 
             "entry_url": "http://www.anzhi.com/soft_622459.html"},
        27: { "site": "www.anzhi.com", 
              "is_entry": True, 
              "download_url": "http://www.anzhi.com/dl_app.php?s=398934",
              "entry_url": "http://www.anzhi.com/soft_398934.html", 
              "referer_url": "http://www.anzhi.com/search.php?search_key=%E6%8D%95%E9%B1%BC%E8%BE%BE%E4%BA%BA&type=0", },
         # 语音搜索 2.14 , 2.2M
        28: { "site": "www.anzhi.com", 
              "is_entry": True, 
              "download_url": "http://www.anzhi.com/dl_app.php?s=31143", 
              "entry_url": "http://www.anzhi.com/soft_31143.html", 
              "referer_url": "http://www.anzhi.com/", },
         # 中华万年历 4.1.0
        29: { "site": "www.anzhi.com", 
              "is_entry": True, 
              "download_url": "http://www.anzhi.com/dl_app.php?s=620663", 
              "entry_url": "http://www.anzhi.com/soft_620663.html", 
              "referer_url": "http://www.anzhi.com/", },
    

        ## 测试用例场景
        ## 1 同一站点，相同软件不同版本的处理, 
        ### 101,102,103
        ## 2 不同站点，相同软件相同版本，文件MD5都相同的（通过使用相同download_url）
        ### 100,101
        ## 2 相同站点，相同软件不同版本，文件MD5都相同的（通过使用相同download_url）
        ### 113,基于113伪造相同apk文件但
        100:{ 'site'       : 'apk.hiapk.com',
          'is_entry'   : True,
          'referer_url': 'http://apk.hiapk.com/',
          'entry_url'  : 'http://apk.hiapk.com/html/2012/12/1065190.html',
          'download_url': 'http://apk.hiapk.com/Download.aspx?aid=1065190&em=14', },
        # 虾米音乐 1.4.6
        101:{ 'site'       : 'apk.91.com',
          'is_entry'   : True,
          'referer_url': 'http://apk.91.com/',
          'entry_url'  : 'http://apk.91.com/Soft/Android/com.xiami-45.html',
          'download_url': 'http://apk.91.com/soft/Controller.ashx?Action=Download&id=4713534', },
        # 虾米音乐 1.4.4.2
        102:{ 'site'       : 'apk.91.com',
          'is_entry'   : False,
          'referer_url': 'http://apk.91.com/Soft/Android/com.xiami-45.html',
          'entry_url'  : 'http://apk.91.com/Soft/Android/com.xiami-39.html',
          'download_url': 'http://apk.91.com/soft/Controller.ashx?Action=Download&id=4660101', },
        # 虾米音乐 1.4.4.1
        103:{ 'site'       : 'apk.91.com',
          'is_entry'   : False,
          'referer_url': 'http://apk.91.com/Soft/Android/com.xiami-45.html',
          'entry_url'  : 'http://apk.91.com/Soft/Android/com.xiami-1.4.4.1.html',
          'download_url': 'http://apk.91.com/soft/Controller.ashx?Action=Download&id=4473456', },
        # 虾米音乐 1.4.4.1
        113:{ 'site'       : 'android.myapp.com',
          'is_entry'   : True,
          'referer_url': 'http://android.myapp.com/',
          'entry_url'  : 'http://android.myapp.com/android/appdetail.jsp?appid=15317&pkgid=654888',
          'download_url': 'http://android.myapp.com/android/down.jsp?appid=15317&pkgid=654888', },
    }
