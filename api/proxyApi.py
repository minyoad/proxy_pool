# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :   WebApi
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/04: WebApi
                   2019/08/14: 集成Gunicorn启动方式
                   2020/06/23: 新增pop接口
                   2022/07/21: 更新count接口
-------------------------------------------------
"""
__author__ = 'JHao'

import platform
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

from util.six import iteritems
from helper.proxy import Proxy
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler

app = Flask(__name__)
conf = ConfigHandler()
proxy_handler = ProxyHandler()


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

# 支持的属性过滤参数
FILTER_KEYS = ("country", "province", "city", "isp")

_INDEX_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Proxy Pool</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:#f5f5f5;color:#333;font-size:14px}
.header{background:#2c3e50;color:#fff;padding:12px 24px;display:flex;align-items:center;justify-content:space-between}
.header h1{font-size:18px;font-weight:600}
.header .stats{font-size:13px;opacity:.85}
.toolbar{background:#fff;padding:12px 24px;border-bottom:1px solid #e0e0e0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.toolbar input,.toolbar select{padding:6px 10px;border:1px solid #ddd;border-radius:4px;font-size:13px}
.toolbar input{width:140px}
.toolbar select{width:110px;cursor:pointer}
.toolbar button{padding:6px 14px;border:none;border-radius:4px;background:#3498db;color:#fff;cursor:pointer;font-size:13px}
.toolbar button:hover{background:#2980b9}
.toolbar button.danger{background:#e74c3c}
.toolbar button.danger:hover{background:#c0392b}
.toolbar .spacer{flex:1}
.urlbar{background:#fff;padding:8px 24px;border-bottom:1px solid #e0e0e0;display:flex;gap:8px;align-items:center}
.urlbar input{border:1px solid #eee;border-radius:4px;padding:4px 8px;background:#fafafa}
table{width:100%;border-collapse:collapse;background:#fff}
th{background:#ecf0f1;padding:8px 10px;text-align:left;font-weight:600;font-size:12px;color:#666;border-bottom:2px solid #bdc3c7;position:sticky;top:0}
td{padding:6px 10px;border-bottom:1px solid #eee;font-size:13px;white-space:nowrap}
tr:hover{background:#f8f9fa}
.tag{display:inline-block;padding:2px 8px;border-radius:3px;font-size:11px}
.tag-http{background:#e8f5e9;color:#2e7d32}
.tag-https{background:#e3f2fd;color:#1565c0}
.fail{color:#e74c3c}
.empty{text-align:center;padding:40px;color:#999}
.pagination{padding:12px 24px;display:flex;justify-content:center;align-items:center;gap:8px}
.pagination button{padding:4px 12px;border:1px solid #ddd;border-radius:4px;background:#fff;cursor:pointer;font-size:13px}
.pagination button:hover:not(:disabled){background:#3498db;color:#fff;border-color:#3498db}
.pagination button:disabled{opacity:.4;cursor:not-allowed}
.pagination span{font-size:13px;color:#666}
.copy-btn{padding:2px 8px;border:1px solid #ddd;border-radius:3px;background:#fafafa;cursor:pointer;font-size:11px}
.copy-btn:hover{background:#3498db;color:#fff;border-color:#3498db}
th[onclick]{cursor:pointer;user-select:none}
th[onclick]:hover{color:#3498db}
.sort-arrow{color:#3498db;font-size:10px}
.loading{text-align:center;padding:30px;color:#999}
</style>
</head>
<body>
<div class="header">
  <h1>Proxy Pool</h1>
  <div style="display:flex;align-items:center;gap:16px">
    <div class="stats" id="stats">loading...</div>
    <a href="/api/" style="color:#3498db;text-decoration:none;font-size:13px" target="_blank">API</a>
  </div>
</div>
<div class="toolbar">
  <select id="f_type"><option value="">All Types</option><option value="http">HTTP</option><option value="https">HTTPS</option></select>
  <input id="f_country" placeholder="Country" />
  <input id="f_province" placeholder="Province" />
  <input id="f_city" placeholder="City" />
  <input id="f_isp" placeholder="ISP" />
  <input id="f_search" placeholder="Search ip:port..." style="width:200px" />
  <button onclick="loadData()">Search</button>
  <button onclick="clearFilters()" style="background:#95a5a6">Reset</button>
  <div class="spacer"></div>
  <button class="danger" onclick="deleteSelected()">Delete Selected</button>
</div>
<div class="urlbar">
  <span style="font-size:12px;color:#999">API:</span>
  <input id="apiUrl" readonly style="flex:1;font-family:monospace;font-size:12px;color:#555" />
  <button class="copy-btn" onclick="copyApiUrl(this)">Copy URL</button>
</div>
<table>
  <thead>
    <tr>
      <th><input type="checkbox" id="selectAll" onclick="toggleAll(this.checked)"></th>
      <th>#</th>
      <th onclick="sortBy('proxy')">Proxy <span id="s_proxy" class="sort-arrow"></span></th>
      <th onclick="sortBy('https')">Type <span id="s_https" class="sort-arrow"></span></th>
      <th onclick="sortBy('region')">Region <span id="s_region" class="sort-arrow"></span></th>
      <th onclick="sortBy('country')">Country <span id="s_country" class="sort-arrow"></span></th>
      <th onclick="sortBy('province')">Province <span id="s_province" class="sort-arrow"></span></th>
      <th onclick="sortBy('city')">City <span id="s_city" class="sort-arrow"></span></th>
      <th onclick="sortBy('isp')">ISP <span id="s_isp" class="sort-arrow"></span></th>
      <th onclick="sortBy('source')">Source <span id="s_source" class="sort-arrow"></span></th>
      <th onclick="sortBy('fail_count')">Fails <span id="s_fail_count" class="sort-arrow"></span></th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody id="tbody"><tr><td colspan="12" class="loading">Loading...</td></tr></tbody>
</table>
<div class="pagination">
  <button id="prevBtn" onclick="prevPage()" disabled>&laquo; Prev</button>
  <span id="pageInfo">0 / 0</span>
  <button id="nextBtn" onclick="nextPage()" disabled>Next &raquo;</button>
</div>
<script>
var allData=[], page=1, pageSize=50, sortKey='', sortAsc=true;
var SORT_KEYS=['proxy','https','region','country','province','city','isp','source','fail_count'];
function sortBy(key){if(sortKey===key){sortAsc=!sortAsc}else{sortKey=key;sortAsc=true}allData.sort(function(a,b){var x=a[key],y=b[key];if(key==='https'){x=x?1:0;y=y?1:0}else if(typeof x==='number'||typeof y==='number'){x=Number(x)||0;y=Number(y)||0}else{x=String(x==null?'':x).toLowerCase();y=String(y==null?'':y).toLowerCase()}return x<y?-1:x>y?1:0});if(!sortAsc)allData.reverse();for(var i=0;i<SORT_KEYS.length;i++){var el=document.getElementById('s_'+SORT_KEYS[i]);if(el)el.textContent=''}var cur=document.getElementById('s_'+key);if(cur)cur.textContent=sortAsc?'\u25B2':'\u25BC';page=1;render()}
function queryParams(){var p=[];var t=document.getElementById('f_type').value;if(t)p.push('type='+t);var c=document.getElementById('f_country').value.trim();if(c)p.push('country='+encodeURIComponent(c));var pr=document.getElementById('f_province').value.trim();if(pr)p.push('province='+encodeURIComponent(pr));var ci=document.getElementById('f_city').value.trim();if(ci)p.push('city='+encodeURIComponent(ci));var is=document.getElementById('f_isp').value.trim();if(is)p.push('isp='+encodeURIComponent(is));return p}
function loadData(){var tbody=document.getElementById('tbody');tbody.innerHTML='<tr><td colspan="12" class="loading">Loading...</td></tr>';var qs=queryParams();var url='/all/'+(qs.length?'?'+qs.join('&'):'');document.getElementById('apiUrl').value=location.origin+url;fetch(url).then(function(r){return r.json()}).then(function(d){allData=d.filter(function(p){var s=document.getElementById('f_search').value.trim().toLowerCase();return!s||p.proxy.toLowerCase().indexOf(s)>=0});page=1;render();loadCount()}).catch(function(e){tbody.innerHTML='<tr><td colspan="12" class="empty">Error: '+e.message+'</td></tr>'})}
function render(){var tbody=document.getElementById('tbody');if(!allData.length){tbody.innerHTML='<tr><td colspan="12" class="empty">No proxies found</td></tr>'}else{var start=(page-1)*pageSize,end=Math.min(start+pageSize,allData.length);var rows=[];for(var i=start;i<end;i++){var p=allData[i];rows.push('<tr>'+'<td><input type="checkbox" class="row-check" data-proxy="'+p.proxy+'"></td>'+'<td>'+(i+1)+'</td>'+'<td><b>'+p.proxy+'</b></td>'+'<td><span class="tag tag-'+(p.https?'https':'http')+'">'+(p.https?'HTTPS':'HTTP')+'</span></td>'+'<td>'+(p.region||'-')+'</td>'+'<td>'+(p.country||'-')+'</td>'+'<td>'+(p.province||'-')+'</td>'+'<td>'+(p.city||'-')+'</td>'+'<td>'+(p.isp||'-')+'</td>'+'<td>'+(p.source||'-')+'</td>'+'<td class="'+(p.fail_count>0?'fail':'')+'">'+p.fail_count+'</td>'+'<td><button class="copy-btn" onclick="copy(this,\''+p.proxy+'\')">Copy</button></td>'+'</tr>')}tbody.innerHTML=rows.join('')}var total=Math.ceil(allData.length/pageSize)||1;document.getElementById('pageInfo').textContent=page+' / '+total;document.getElementById('prevBtn').disabled=page<=1;document.getElementById('nextBtn').disabled=page>=total}
function prevPage(){if(page>1){page--;render()}}
function nextPage(){if(page<Math.ceil(allData.length/pageSize)){page++;render()}}
function toggleAll(checked){var c=document.querySelectorAll('.row-check');for(var i=0;i<c.length;i++){c[i].checked=checked}}
function clearFilters(){document.getElementById('f_type').value='';document.getElementById('f_country').value='';document.getElementById('f_province').value='';document.getElementById('f_city').value='';document.getElementById('f_isp').value='';document.getElementById('f_search').value='';loadData()}
function copy(btn,text){navigator.clipboard.writeText(text).then(function(){btn.textContent='OK';setTimeout(function(){btn.textContent='Copy'},1000)})}
function copyApiUrl(btn){var url=document.getElementById('apiUrl').value;navigator.clipboard.writeText(url).then(function(){btn.textContent='OK';setTimeout(function(){btn.textContent='Copy URL'},1000)})}
function deleteSelected(){var checked=document.querySelectorAll('.row-check:checked');if(!checked.length)return;if(!confirm('Delete '+checked.length+' proxy(es)?'))return;var done=0,total=checked.length;for(var i=0;i<checked.length;i++){(function(proxy){fetch('/delete/?proxy='+encodeURIComponent(proxy)).then(function(r){return r.json()}).then(function(){done++;if(done===total){loadData()}})})(checked[i].dataset.proxy)}}
function loadCount(){fetch('/count/').then(function(r){return r.json()}).then(function(d){var parts=[];for(var k in d.http_type){parts.push(k+': '+d.http_type[k])}parts.push('total: '+d.count);document.getElementById('stats').textContent=parts.join(' | ')})}
document.getElementById('f_search').addEventListener('input',function(){page=1;render()});
loadData();
</script>
</body>
</html>"""

api_list = [
    {"url": "/get", "params": "type: ''https'|''; country/province/city/isp: 按属性过滤", "desc": "get a proxy"},
    {"url": "/pop", "params": "type: ''https'|''; country/province/city/isp: 按属性过滤", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: ''https'|''; country/province/city/isp: 按属性过滤", "desc": "get all proxy from proxy pool"},
    {"url": "/list", "params": "type: ''https'|''; country/province/city/isp: 按属性过滤", "desc": "get all proxy as plain text (ip:port per line)"},
    {"url": "/count", "params": "", "desc": "return proxy count"}
    # 'refresh': 'refresh proxy pool',
]


def _get_filters():
    """从查询参数中提取属性过滤条件"""
    filters = {}
    for key in FILTER_KEYS:
        value = request.args.get(key, "").strip()
        if value:
            filters[key] = value
    return filters


@app.route('/')
def index():
    return Response(_INDEX_HTML, mimetype="text/html")


@app.route('/api/')
def api_index():
    return {'url': api_list}


@app.route('/get/')
def get():
    https = request.args.get("type", "").lower() == 'https'
    proxy = proxy_handler.get(https, filters=_get_filters())
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/pop/')
def pop():
    https = request.args.get("type", "").lower() == 'https'
    proxy = proxy_handler.pop(https, filters=_get_filters())
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    return 'success'


@app.route('/all/')
def getAll():
    https = request.args.get("type", "").lower() == 'https'
    proxies = proxy_handler.getAll(https, filters=_get_filters())
    return jsonify([_.to_dict for _ in proxies])


@app.route('/list/')
def getList():
    """纯文本输出 ip:port 列表, 每行一个"""
    https = request.args.get("type", "").lower() == 'https'
    proxies = proxy_handler.getAll(https, filters=_get_filters())
    return Response("\n".join(_.proxy for _ in proxies) + ("\n" if proxies else ""),
                    mimetype="text/plain")


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    status = proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}


@app.route('/count/')
def getCount():
    proxies = proxy_handler.getAll()
    http_type_dict = {}
    source_dict = {}
    for proxy in proxies:
        http_type = 'https' if proxy.https else 'http'
        http_type_dict[http_type] = http_type_dict.get(http_type, 0) + 1
        for source in proxy.source.split('/'):
            source_dict[source] = source_dict.get(source, 0) + 1
    return {"http_type": http_type_dict, "source": source_dict, "count": len(proxies)}


def runFlask():
    if platform.system() == "Windows":
        app.run(host=conf.serverHost, port=conf.serverPort)
    else:
        import gunicorn.app.base

        class StandaloneApplication(gunicorn.app.base.BaseApplication):

            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super(StandaloneApplication, self).__init__()

            def load_config(self):
                _config = dict([(key, value) for key, value in iteritems(self.options)
                                if key in self.cfg.settings and value is not None])
                for key, value in iteritems(_config):
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        _options = {
            'bind': '%s:%s' % (conf.serverHost, conf.serverPort),
            'workers': 4,
            'accesslog': '-',  # log to stdout
            'access_log_format': '%(h)s %(l)s %(t)s "%(r)s" %(s)s "%(a)s"'
        }
        StandaloneApplication(app, _options).run()


if __name__ == '__main__':
    runFlask()
