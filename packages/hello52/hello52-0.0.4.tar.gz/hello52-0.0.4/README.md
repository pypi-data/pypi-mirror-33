### setuptools

打包
----

    # 创建egg包
    python setup.py bdist_egg
    
    # 创建tar.gz包
    python setup.py sdist --formats=gztar
    
安装应用
----
    # 安装应用
    python setup.py install
    
    # 开发方式安装 
    python setup.py develop

测试
----
    
    python setup.py test

上传包
----

1. 首先去 [pypi](https://pypi.org/),[test pypi](https://test.pypi.org/) 注册账号
2. 配置~/.pypirc如下：


    [distutils]
    index-servers =
        pypi
        pypitest
     
    [pypi]
    username:<username>
        password:<password>
     
    [pypitest]
    username:<username>
    password:<password>

3. 上传


    python setup.py register -r pypi
    python setup.py sdist upload -r pypi

    
更换源
----
    pip install requests -i https://pypi.douban.com/simple


安装包
----
    
    pip3 install hello52
