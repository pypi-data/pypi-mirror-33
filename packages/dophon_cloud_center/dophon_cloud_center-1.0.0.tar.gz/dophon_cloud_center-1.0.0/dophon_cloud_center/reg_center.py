from flask import Flask, render_template,redirect, request, jsonify, abort
from dophon_cloud_center import kits
import threading
import urllib3
from flask_bootstrap import Bootstrap


req_pool=urllib3.PoolManager()

'''
注册中心
默认端口为8361
'''

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# h5添加bootstrap样式
Bootstrap(app)

reg_info = {}

heart_cell = None

'''
访问注册中心首页
'''
@app.route('/',methods=['get','post'])
def hello_world():
    return redirect('/center',)


@app.route('/center', methods=['get', 'post'])
def center():
    m = request.method
    if m == 'GET':
        return render_template('center.html',reg_info=reg_info)
    if m == 'POST':
        return jsonify(reg_info)
    return abort(400)

@app.route('/request/<service_name>/<instance_id>')
def request_instance(service_name,instance_id):
    if service_name in reg_info.keys():
        s_instances=reg_info[service_name]
        for instance in s_instances:
            if instance_id == instance['id']:
                res=req_pool.request('POST','http://'+str(instance['host']+':'+instance['port']+'/heart'))
                if 200 == res.status:
                    return jsonify(instance)
                else:
                    return abort(404)
    else:
        return abort(404)

'''
暴露注册服务接口
'''
@app.route('/reg/service/<name>', methods=['get'])
def reg_service(name):
    global reg_info
    reg_info_cache=reg_info
    # 处理多实例服务注册
    if name.upper() in reg_info:
        cache=reg_info_cache[name.upper()]
    else:
        cache=[]
    h = request.headers
    # 组装服务细胞信息
    if 'prefer_ip' in h:
        ip=h['prefer_ip']
    else:
        ip=str(h['Host']).split(':')[0]
    if 'u_heart_interface' in h:
        heart=h['u_heart_interface']
        s_c=kits.service_cell(ip,h['service_port'],heart)
    else:
        s_c=kits.service_cell(ip,h['service_port'])
    for item in cache:
        if item==s_c:
            return jsonify(reg_info)
    cache.append(s_c.__dict__())
    reg_info_cache[name.upper()] = cache
    heart_cell.update_reg(reg_info_cache)
    reg_info=reg_info_cache
    return jsonify(reg_info_cache)

@app.route('/health',methods=['GET'])
def health():
    '''
    检查注册中心健康状态
    :return:
    '''
    return jsonify({})

'''
注册实例列表更新接口
'''
@app.route('/reg/update')
def get_reg_info():
    return jsonify(reg_info)

def run(properties={}):
    # 初始化心跳模块
    global heart_cell
    heart_cell=kits.get_heart()
    global __prop
    __prop=properties
    if 'heart_check' in properties.keys() and properties['heart_check']:
        threading.Thread(target=heart_cell.start_heart).start()
    app.run(host='0.0.0.0',port=properties['port'] if 'port' in properties.keys() else 8361)


run({'heart_check':True})

