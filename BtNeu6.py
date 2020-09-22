"""
六维空间 部分API接口
@LMR 20200922
"""
import requests
from bs4 import BeautifulSoup

class BtNeu6(object):
    def __init__(self,username,password):
        """username六维空间用户名，password密码"""
        self.host='http://bt.neu6.edu.cn/'
        self.session=requests.Session()
        self.username=username
        self.password=password
        self.state=False

        
    def login(self):
        """登录六维空间，返回tuple[0]表示登录是否成功，tuple[1]表示错误原因"""
        #获取登录所需formhash和referer参数值（直接存在于登录界面的html文件里）
        soup=BeautifulSoup(self.session.get(self.host).text, 'lxml')
        formhash=soup.find('input',attrs={'name':'formhash'})['value']
        referer=soup.find('input',attrs={'name':'referer'})['value']
        #post数据
        postdata={
            'formhash': formhash,
            'referer':referer,
            'username':self.username.encode("gbk"),#注意post的编码操作方法
            'password':self.password,
            'questionid': '0',
            'answer': ''
            }
        try:
            #登录接口
            response=self.session.post(self.host+'member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LNSDs&inajax=1',
                     data=postdata).text
            if(response.find('succeedmessage')!=-1):
                self.state=True
                return (True,'成功')
            else:
                return (False,response)
        except Exception as e:
            return (False,e)


    def getinf(self):
        """获取基本信息，包括浮云和积分，返回tuple[0]表示获取是否成功，tuple[1]表示信息json或错误原因"""
        if(self.state==True):
            try:
                soup=BeautifulSoup(self.session.get(self.host+'home.php?mod=spacecp&ac=credit&showcredit=1').text, 'lxml')
                li=soup.find('ul',class_="creditl mtm bbda cl")
                fi=li.find_all('li')
                
                inf={
                    '浮云':fi[0].text[fi[0].text.find(':')+2:fi[0].text.find(' ',fi[0].text.find(':')+2)],
                    '积分':fi[-1].text[fi[-1].text.find(':')+2:fi[-1].text.find(' ',fi[-1].text.find(':')+2)]
                    }
                return (True,inf)
            except Exception as e:
                return (False,e)
        else:
            return (False,'未登录')

            
    def getlist(self,to):
        """获取模块页面内的种子信息，to表示页面标签（如free表示免费区），
            返回tuple[0]表示获取是否成功，tuple[1]表示列表json或错误原因"""
        if(self.state==True):
            try:
                if(to=='free'):
                    url=self.host+'forum-401-1.html'
                else:
                    return (False,'暂不支持')
                #解析列表
                soup=BeautifulSoup(self.session.get(url).text, 'lxml')
                listdata=[]
                for i in soup.find_all('tr'):
                    try:
                        Type='NA'
                        for j in i.find('th').find_all('img'):
                            if(j['src'].find('free')!=-1):
                                Type='free'
                        listdata.append({
                            'title':i.find('a',class_='s xst').text,
                            'href':self.host+i.find('a',class_='s xst')['href'],
                            'class':i.find('th').em.a.text,
                            'type':Type,
                            'size':i.find_all('td')[2].text,
                            'date':i.find('td',class_="by").em.span.text
                            })
                    except:
                        pass
                return (True,listdata)
            except Exception as e:
                return (False,e)
        else:
            return (False,'未登录')

                
    def gettorrent(self,href,path):
        path="up_torrents"
        """下载种子文件，href链接地址（通过getlist获取），path保存位置（输入''不下载只显示种子信息），
            返回tuple[0]表示获取是否成功，tuple[1]表示保存位置或错误原因"""
        if(self.state==True):
            try:
                soup=BeautifulSoup(self.session.get(href).text, 'lxml')
                torrent={
                    'filename':soup.find('p',class_='attnm').a.text,
                    'href':self.host+soup.find('p',class_='attnm').a['href']
                    }
                if(path==''):
                    return (True,torrent)
                else:
                    filename='%s/%s'%(path,torrent['filename'])
                    with open(filename,'wb') as f:
                        f.write(self.session.get(torrent['href']).content)
                    return (True,filename)
            except Exception as e:
                    return (False,e)
        else:
            return (False,'未登录')
        
if __name__=="__main__":
    demo=BtNeu6(input("用户名"),input("密码"))
    if(demo.login()[0]==True):
        inf=demo.getinf()
        if(inf[0]==True):
            print(inf[1])
        if(input("是否开始批量下载免费区种子？Y/N").lower()=='y'):
            ilist=demo.getlist('free')
            if(ilist[0]==True):
                path=input("输入路径")
                for i in ilist[1]:
                    if(i['type']=='free'):
                        print(i['title'],i['type'])
                        print(demo.gettorrent(i['href'],path))
