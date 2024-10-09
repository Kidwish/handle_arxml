import os
from lxml import etree
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
import xmltodict
import json


GUIWINDOW = True

INPUT_FILEPATH = r'./data/CtApMySwc.arxml'
OUTPUT_JSONPATH = r'./output/output.json'

def tk_display(data, parent='', tree=None):
    """递归地将数据插入到 Treeview 中"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                item_id = tree.insert(parent, 'end', text=key, values=('',), open=False)
                tk_display(value, parent=item_id, tree=tree)
            else:
                # 拆分成两个单元格
                tree.insert(parent, 'end', text=key, values=(str(value),), open=False)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            item_id = tree.insert(parent, 'end', text=f'[{index}]', values=('',), open=False)
            tk_display(item, parent=item_id, tree=tree)
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
    

    def tk_on_item_left_click(event):
        """根据内容自动调整 Key 列宽度"""
        newWidth = get_max_width_of_open_items()
        item_id = tree.selection()[0]
        current_item_width = get_tree_item_width(item_id)
        newWidth = max(current_item_width, newWidth)
        tree.column('#0', width=newWidth, stretch=False)  

    def tk_on_item_right_click(event):
        # 获取当前选中的项
        selected_item = tree.selection()
        if selected_item:
            item_id = selected_item[0]
            item_text = tree.item(item_id, 'text')  # 获取项的文本
            item_value = tree.item(item_id, 'values')  # 获取项的值

            # 组合文本
            text_to_copy = f"{item_text}: {item_value[0] if item_value else ''}"
            
            # 复制到剪贴板
            root.clipboard_clear()  # 清空剪贴板
            root.clipboard_append(text_to_copy)  # 添加文本到剪贴板
            print(f"已复制: {text_to_copy}")


    def get_max_width_of_open_items():
        max_width = 200
        def check_width(item_id):
            nonlocal max_width
            if tree.item(item_id, 'open'):
                # 获取当前项的宽度
                current_width = get_tree_item_width(item_id)
                max_width = max(max_width, current_width)

                # 递归检查子项
                for child in tree.get_children(item_id):
                    check_width(child)

        # 遍历所有根节点
        for item in tree.get_children():
            check_width(item)

        return max_width

    def get_tree_item_width(item_id):
        indent = 20
        item_text = tree.item(item_id, 'text')  # 获取文本
            
        level = 0
        while item_id:
            item_id = tree.parent(item_id)  # 获取父节点 ID
            level += 1  # 每向上移动一层，层级加 1
        
        return level * indent + len(item_text) * 10


    def expand_all(tree):
        """展开所有节点"""
        for item in tree.get_children():
            tree.item(item, open=True)  # 展开当前节点
            expand_all_children(tree, item)  # 递归展开子节点

    def expand_all_children(tree, parent):
        """递归展开所有子节点"""
        for child in tree.get_children(parent):
            tree.item(child, open=True)  # 展开子节点
            expand_all_children(tree, child)  # 递归展开其子节点

    def collapse_all(tree):
        """折叠所有节点"""
        for item in tree.get_children():
            tree.item(item, open=False)  # 折叠当前节点
            collapse_all_children(tree, item)  # 递归折叠子节点

    def collapse_all_children(tree, parent):
        """递归折叠所有子节点"""
        for child in tree.get_children(parent):
            tree.item(child, open=False)  # 折叠子节点
            collapse_all_children(tree, child)  # 递归折叠其子节点

    # 创建主窗口
    root = tk.Tk()
    root.title("ARXML 数据展示")
    root.geometry("800x400")

    # 创建 Treeview
    tree = ttk.Treeview(root, columns=('Value',), show='tree')
    tree.heading('#0', text='Key')  # 主树形结构列
    tree.heading('Value', text='Value')

    # 设置列宽
    tree.column('#0', width=200, stretch=False)  # 固定 Key 列宽
    tree.column('Value', width=400, stretch=True)  # 允许用户调整 Value 列宽

    tree.pack(expand=True, fill='both')

    # 插入数据
    tk_display(arxml_dict, tree=tree)


    # 默认展开第一层，折叠其他层级
    for item in tree.get_children():
        tree.item(item, open=True)  # 展开第一层
        for child in tree.get_children(item):
            tree.item(child, open=False)  # 默认折叠子节点
            
    # 添加按钮
    button_frame = tk.Frame(root)
    button_frame.pack(side='bottom', fill='x')

    expand_button = tk.Button(button_frame, text="全部展开", command=lambda: expand_all(tree))
    expand_button.pack(side='left', padx=10, pady=10)

    collapse_button = tk.Button(button_frame, text="全部折叠", command=lambda: collapse_all(tree))
    collapse_button.pack(side='right', padx=10, pady=10)

    # 绑定事件
    tree.bind('<ButtonRelease-1>', tk_on_item_left_click)  # 左键事件
    tree.bind('<ButtonRelease-3>', tk_on_item_right_click)  # 右键事件


    # 运行主循环
    root.mainloop()



