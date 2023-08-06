=================
TwT Auto Reporter
=================

使用 commit messages 自动编写和更新周报。

安装
====

0. `安装 Python <https://www.python.org/downloads/>`_
1. 通过 pip 安装此脚本::

    pip install auto-Reporter

2. 切换到你的项目目录::

    cd /path/to/my-awesome-project

3. （在项目根目录下）安装脚本，附上 at 系统用户名，密码，以及项目名称（可选）::

    install-auto-reporter -u caohao -p NotRealPassword -d "My Awesome Project"

4. 每次运行 (``git push``) 时，脚本就会在 push 到远程服务器前运行，将你本次要 push 的所有 commit 提交到周报。

选项
====

# (``-u``) 或 (``--username``)：at 系统用户名（一般为姓名全拼）
# (``-p``) 或 (``--password``)：at 系统密码（如忘记请自行找组长重置）
# (``-d``) 或 (``--display-name``)：项目名称。可选，若不指定，默认为项目目录名。
# (``-h``) 或 (``--helps``)：显示帮助
# (``--thanks``)：字面意思

注意事项
========
1. (``pip install``) 每台电脑只需执行一次。
2. (``install-auto-reporter``) 每个项目目录执行一次
3. (``install-auto-reporter``) 时忘记指定用户名和密码了，请重新安装。
4. 如何重新安装？删除 (``<PORJECT>/.git/hooks/pre-push``) 文件，然后执行 (``install-auto-reporter -u <username> -p <password> -d <project-name>``)
5. 如果由于各种原因（服务器爆炸等）没有提交周报，你仍然可以继续 push 修改到远程库，但本次 push 的所有 commits 不会再有机会提交到周报，请自行更新周报。

运行环境
========

Python 3.3+

LICENSE
=======

MIT