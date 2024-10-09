import os
from lxml import etree
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xmltodict
import json


GUIWINDOW = True

INPUT_FILEPATH = r'./data/CtApMySwc.arxml'
OUTPUT_JSONPATH = r'./output/output.json'

def display_json(data, parent='', tree=None):
    """递归地将 JSON 数据插入到 Treeview 中"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                item_id = tree.insert(parent, 'end', text=key, values=('',), open=False)
                display_json(value, parent=item_id, tree=tree)
            else:
                # 拆分成两个单元格
                tree.insert(parent, 'end', text=key, values=(str(value),), open=False)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            item_id = tree.insert(parent, 'end', text=f'[{index}]', values=('',), open=False)
            display_json(item, parent=item_id, tree=tree)
    else:
        tree.insert(parent, 'end', text='', values=(str(data),), open=False)


def test():
    
    if GUIWINDOW:
        inputFilePath = filedialog.askopenfilename(
            title="选择一个文件",
            filetypes=[("ARXML文件", "*.arxml")],
            )
    else:
        inputFilePath = INPUT_FILEPATH

    # 读取 ARXML 文件并转换为字典
    with open(inputFilePath) as file:
        arxml_dict = xmltodict.parse(file.read())

    # 将字典转换为 JSON
    json_data = json.dumps(arxml_dict, indent=4)

    # 将 JSON 数据保存到文件
    with open(OUTPUT_JSONPATH, 'w') as json_file:
        json_file.write(json_data)
    
    json_data = arxml_dict
    # 创建主窗口
    root = tk.Tk()
    root.title("ARXML 数据展示")
    root.geometry("1600x400")

    # 创建 Treeview
    tree = ttk.Treeview(root, columns=('Value',), show='tree')
    tree.heading('#0', text='Key')
    tree.heading('Value', text='Value')
    tree.column('Value', width=400)  # 设置第二列的宽度

    # 允许用户调整列宽
    tree.column('#0', width=200, stretch=False)
    tree.pack(expand=True, fill='both')

    # 添加滚动条
    scrollbar = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscroll=scrollbar.set)

    # 插入 JSON 数据
    display_json(json_data, tree=tree)

    # 默认展开第一层，折叠其他层级
    for item in tree.get_children():
        tree.item(item, open=True)  # 展开第一层
        for child in tree.get_children(item):
            tree.item(child, open=False)  # 默认折叠子节点

    # 运行主循环
    root.mainloop()





