import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from service import *
import requests
import sys

_version = '0.2.2'

# pyinstaller -w -F main.py --add-data ".\\res\\*;.\\res\\" --icon=./res/favicon.ico
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def installSaves():
    ftp_host = '121.37.222.191'  # ftp服务器地址
    # ftp_host = 'errorserver.top'
    ftp_user = 'anonymous'  # 匿名登陆用户名用anonymous
    ftp_passwd = 'a@em.com'  # 密码随便

    filename = 'zip1.zip'
    remote_file = '/' + filename  # 远程文件路径
    profiles_path = getUserDoc() + r'\Euro Truck Simulator 2\profiles'  # 存档路径
    local_file = profiles_path + '\\' + filename  # 文件保存路径

    # 下载并解压
    ftpDownload(ftp_host, ftp_user, ftp_passwd, remote_file, local_file)
    local_file = unzip(local_file, profiles_path)
    writeData(local_file)

    # 拷贝配置文件
    copyList = copyConfigFiles(profiles_path + '\\' + saveName)

    message = f'下载成功！\n' +\
        f'成功将{"，".join(copyList)}，\n' +\
        f'{len(copyList)}个配置文件拷贝到新存档'
    messagebox.showinfo('提示', message)




def uninstallSaves():
    file_list = readData()
    removeFiles(file_list)
    messagebox.showinfo('提示', '删除成功')


def getRemote():
    resp = requests.get('http://121.37.222.191:8020/get')
    if resp.status_code != 200:
        return
    return resp.json()


def onSave(value, dic, saveName):
    # 默认只加载第一个存档
    game_sii_path = getUserDoc() + '\\Euro Truck Simulator 2\\profiles\\' + saveName + '\\save\\1\\game.sii'
    # 解密
    try:
        decryptPath = resource_path('.\\res\\SII_Decrypt')
        command = f'{decryptPath} \"{game_sii_path}\"'
        subprocess.run(command, shell=True, text=True)
        print(command)
    except Exception as e:
        print(e)
    # 修改
    with open(game_sii_path, 'r', encoding='utf-8') as f:
        contents = f.read()
        lines = contents.split('\n')
        index = 0
        for line in lines:
            if line.strip().startswith('truck_placement'):
                lines[index] = ' ' + dic[value]['truck'].strip()
            if line.strip().startswith('trailer_placement'):
                lines[index] = ' ' + dic[value]['trailer'].strip()
                break
            index += 1
    with open(game_sii_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        print('结束...')
    messagebox.showinfo('提示', '成功')


def updateDlg():
    updateInfo = getUpdateInfo()
    if updateInfo['version'] > _version:
        result = messagebox.askquestion("检测到可用的更新",f"V{_version} => V{updateInfo['version']}")
        if result == 'no':
            return
        url = 'http://121.37.222.191:8020/download'
        cmd = f"start {url}"
        try:
            subprocess.run(cmd, shell=True)
        except Exception as e:
            print(e)



if __name__ == '__main__':

    ret = getRemote()
    datas = ret['points']
    saveName = ret['saveName']
    linkGuideUrl = ret['linkGuideUrl']
    dic = {}
    values = []
    for item in datas:
        values.append(item['name'])
        dic[item['name']] = {
            'truck': item['truck'],
            'trailer': item['trailer']
        }

    try:

        window = tk.Tk()
        window.title('XM接档器' + 'V' + _version)
        screenWidth = window.winfo_screenwidth()  # 获取显示区域的宽度
        screenHeight = window.winfo_screenheight()  # 获取显示区域的高度
        width = 500  # 设定窗口宽度 500
        height = 320  # 设定窗口高度 320
        left = (screenWidth - width) // 2
        top = (screenHeight - height) // 2
        window.geometry(f'{width}x{height}+{left}+{top}')
        window.resizable(width=False, height=False)
        window.iconphoto(True, tk.PhotoImage(file=resource_path("res/icon1.png")))

        # 创建画布
        canvas = tk.Canvas(window, width=400, height=200)
        canvas.place(x=250, y=150, anchor='center')
        # 加载图片
        image = tk.PhotoImage(file=resource_path('res/logo.png'))
        # 渲染
        canvas.create_image(200, 80, anchor='center', image=image)

        # 菜单
        menu = tk.Menu(window)
        menu.add_command(label="设置配置文件路径", command=setConfigFilesPath)
        menu.add_command(label="关于", command=lambda: messagebox.showinfo('你好：', '憨批！'))
        window.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        # menu.add_cascade(label='设置', menu=file)
        # file.add_command(label='添加欧卡路径', command=menu_addPath)

        # 大标题
        tk.Label(window, text="XM散人物流运输", font=('黑体', 22)).place(x=250, y=40, anchor='center')

        # 框架
        frame = tk.Frame(window, width=460, height=110)
        frame.place(x=250, y=200, anchor='n')

        # 按钮
        btn1 = tk.Button(frame, text='一键安装活动存档', font=('宋体', 12), width=18, height=2, command=installSaves)
        btn1.place(x=40, y=10)
        btn2 = tk.Button(frame, text='一键卸载活动存档', font=('宋体', 12), width=18, height=2, command=uninstallSaves)
        btn2.place(x=40, y=60)

        tk.Label(frame, text='选择传送位置:', font=('宋体', 12)).place(x=220, y=10)
        combox1 = ttk.Combobox(frame, state='readonly', width=28)
        combox1.config(values=values)
        combox1.place(x=220, y=40)
        tk.Button(frame, text='传送', font=('宋体', 12), width=16, height=1,
                  command=lambda: onSave(combox1.get(), dic, saveName)).place(x=220, y=75)

        tk.Button(frame, text='打开教程', font=('宋体', 12), foreground='red',
                  command=lambda: openPage(linkGuideUrl)).place(x=362, y=75)

        updateDlg()

        window.mainloop()
    except Exception as e:
        print(e)
