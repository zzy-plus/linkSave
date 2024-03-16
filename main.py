import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import subprocess
from service import *
import requests
import sys

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
    extract_path = getUserDoc() + r'\Euro Truck Simulator 2\profiles'  # 存档路径
    local_file = extract_path + '\\' + filename  # 文件保存路径

    # 下载并解压
    ftpDownload(ftp_host, ftp_user, ftp_passwd, remote_file, local_file)
    local_file = unzip(local_file, extract_path)
    writeData(local_file)

    messagebox.showinfo('提示', '下载成功')


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
            if line.startswith(' truck_placement'):
                lines[index] = ' ' + dic[value]['truck']
            if line.startswith(' trailer_placement'):
                lines[index] = ' ' + dic[value]['trailer']
                break
            index += 1
    with open(game_sii_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        print('结束...')
    messagebox.showinfo('提示', '成功')


if __name__ == '__main__':

    ret = getRemote()
    datas = ret['points']
    saveName = ret['saveName']
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
        window.title('XM接档器')
        window.geometry('500x355')
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
        window.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        # menu.add_cascade(label='设置', menu=file)
        # file.add_command(label='添加欧卡路径', command=menu_addPath)

        # 大标题
        tk.Label(window, text="XM散人物流运输", font=('黑体', 22)).place(x=250, y=40, anchor='center')

        # 框架
        frame = tk.Frame(window, width=460, height=200)
        frame.place(x=250, y=200, anchor='n')

        # 按钮
        btn1 = tk.Button(frame, text='一键安装活动存档', font=('宋体', 12), width=18, height=2, command=installSaves)
        btn1.place(x=40, y=50)
        btn2 = tk.Button(frame, text='一键卸载活动存档', font=('宋体', 12), width=18, height=2, command=uninstallSaves)
        btn2.place(x=40, y=100)

        tk.Label(frame, text='选择传送位置:', font=('宋体', 12)).place(x=235, y=50)
        combox1 = ttk.Combobox(frame, state='readonly', width= 28)
        combox1.config(values=values)
        combox1.place(x=235, y=80)
        tk.Button(frame, text='传送', font=('宋体', 12), width=22, height=1,
                  command=lambda: onSave(combox1.get(), dic, saveName)).place(x=235, y=115)

        # tk.Label(frame,text="XM散人物流运输车队接待群:187174917", font=('黑体', 12)).place(x=230, y=170, anchor='center')

        window.mainloop()
    except Exception as e:
        print(e)
