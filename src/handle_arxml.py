# handle_arxml.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xmltodict
import json


GUIWINDOW   = True
INDENT      = 20
TEXTWIDTH   = 10

INPUT_FILEPATH  = r'./data/sample_input.arxml'
OUTPUT_JSONPATH = r'./output/sample_output.json'


def display_arxml_file():
    if GUIWINDOW:
        inputFilePath = filedialog.askopenfilename(
            title="选择一个文件",
            filetypes=[("ARXML文件", "*.arxml")],
            )
    else:
        inputFilePath = INPUT_FILEPATH
    
    inputFileName = inputFilePath.split("/")[-1]

    # 读取 ARXML 文件并转换为字典
    with open(inputFilePath) as file:
        arxml_dict = xmltodict.parse(file.read())


    # 递归地将数据插入到 Treeview 中
    def tk_display(data, parent=''):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    itemId = tree.insert(parent, 'end', text=key, values=('',), open=False)
                    tk_display(value, parent=itemId)
                else:
                    # 拆分成两个单元格
                    tree.insert(parent, 'end', text=key, values=(str(value),), open=False)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                itemId = tree.insert(parent, 'end', text=f'[{index}]', values=('',), open=False)
                tk_display(item, parent=itemId)
        else:
            tree.insert(parent, 'end', text='', values=(str(data),), open=False)

    def tk_on_item_left_click(event): # 自动调整列宽
        newWidth = get_max_width_of_open_items()
        itemId = tree.selection()[0]
        currentItemWidth = get_tree_item_width(itemId)
        newWidth = max(currentItemWidth, newWidth)
        tree.column('#0', width=newWidth, stretch=False)  

    def tk_on_item_right_click(event):
        selectedItem = tree.selection()
        if selectedItem:
            itemId = selectedItem[0]
            itemText = tree.item(itemId, 'text')  # 获取项的文本
            itemValue = tree.item(itemId, 'values')  # 获取项的值

            # 组合文本
            textToCopy = f"{itemText}: {itemValue[0] if itemValue else ''}"
            
            # 复制到剪贴板
            root.clipboard_clear()  # 清空剪贴板
            root.clipboard_append(textToCopy)  # 添加文本到剪贴板
            # print(f"已复制: {textToCopy}")

    def tk_on_button_press(event):
        nonlocal startX, startWidth
        region = tree.identify_region(event.x, event.y)
        if region == "tree":
            item = tree.identify_row(event.y)
            if item:
                startX = event.x
                startWidth = tree.column("#0")['width']

    def tk_on_mouse_drag(event):
        if startWidth > 0:
            newWidth = startWidth + (event.x - startX)
            tree.column("#0", width=newWidth)


    def get_max_width_of_open_items():
        maxWidth = 200
        def check_width(itemId):
            nonlocal maxWidth
            if tree.item(itemId, 'open'):
                # 获取当前项的宽度
                currentWidth = get_tree_item_width(itemId)
                maxWidth = max(maxWidth, currentWidth)

                # 递归检查子项
                for child in tree.get_children(itemId):
                    check_width(child)

        # 遍历所有根节点
        for item in tree.get_children():
            check_width(item)

        return maxWidth

    def get_tree_item_width(itemId):
        indent = INDENT
        itemText = tree.item(itemId, 'text')  # 获取文本

        level = 0
        while itemId:
            itemId = tree.parent(itemId)  # 获取父节点 ID
            level += 1  # 每向上移动一层，层级加 1
        
        return level * indent + len(itemText) * TEXTWIDTH


    def tk_bn_expand_all(tree):
        def expand_all_children(tree, parent):
            for child in tree.get_children(parent):
                tree.item(child, open=True)  # 展开子节点
                expand_all_children(tree, child)  # 递归展开其子节点
                
        for item in tree.get_children():
            tree.item(item, open=True)  # 展开当前节点
            expand_all_children(tree, item)  # 递归展开子节点
        
        infoLabel.config(text="按下左键并拖动以显示完整信息" )

    def tk_bn_collapse_all(tree):
        def collapse_all_children(tree, parent):
            for child in tree.get_children(parent):
                tree.item(child, open=False)  # 折叠子节点
                collapse_all_children(tree, child)  # 递归折叠其子节点

        for item in tree.get_children():
            tree.item(item, open=False)  # 折叠当前节点
            collapse_all_children(tree, item)  # 递归折叠子节点

    def tk_bn_save_json():
        if GUIWINDOW:
            outputFilePath = filedialog.asksaveasfilename(
                title="保存文件",
                defaultextension=".json",  # 默认扩展名
                filetypes=[("Json文件", "*.json")],  # 文件类型过滤
                initialfile=f"{inputFileName}.json"  # 默认文件名
                )
        else:
            outputFilePath = OUTPUT_JSONPATH

        # 将字典转换为 JSON
        json_data = json.dumps(arxml_dict, indent=4)

        # 将 JSON 数据保存到文件
        with open(outputFilePath, 'w') as json_file:
            json_file.write(json_data)


    # 创建主窗口
    root = tk.Tk()
    root.title("ARXML 数据展示")
    root.geometry("800x400")

    # 创建框架以容纳 Treeview 和滚动条
    mainFrame = tk.Frame(root)
    mainFrame.pack(expand=True, fill='both')

    # 创建 Treeview
    tree = ttk.Treeview(mainFrame, columns=('Value',), show='tree')
    tree.heading('#0', text='Key')  # 主树形结构列
    tree.heading('Value', text='Value')

    # 设置列宽
    tree.column('#0', width=200, stretch=False)  # 固定 Key 列宽
    tree.column('Value', width=400, stretch=True)  # 允许用户调整 Value 列宽

    # 创建纵向滚动条
    vScrollbar = ttk.Scrollbar(mainFrame, orient='vertical', command=tree.yview)
    vScrollbar.pack(side='right', fill='y')
    tree.configure(yscroll=vScrollbar.set)

    # 创建横向滚动条
    hScrollbar = ttk.Scrollbar(mainFrame, orient='horizontal', command=tree.xview)
    hScrollbar.pack(side='bottom', fill='x')
    tree.configure(xscroll=hScrollbar.set)

    tree.pack(expand=True, fill='both')

    # 插入数据
    tk_display(arxml_dict)


    # 默认展开第一层，折叠其他层级
    for item in tree.get_children():
        tree.item(item, open=True)  # 展开第一层
        for child in tree.get_children(item):
            tree.item(child, open=False)  # 默认折叠子节点

    startX = 0
    startWidth = 0

    bottomFrame = tk.Frame(root)
    bottomFrame.pack(side='bottom', fill='x')

    # 添加按钮
    saveJsonButtom = tk.Button(bottomFrame, text="保存为 JSON", command=lambda: tk_bn_save_json())
    saveJsonButtom.pack(side='right', padx=10, pady=10)
    collapseButton = tk.Button(bottomFrame, text="全部折叠", command=lambda: tk_bn_collapse_all(tree))
    collapseButton.pack(side='right', padx=10, pady=10)
    expandButton = tk.Button(bottomFrame, text="全部展开", command=lambda: tk_bn_expand_all(tree))
    expandButton.pack(side='right', padx=10, pady=10)

    # 添加提示标签
    infoLabel = tk.Label(bottomFrame, text="")
    infoLabel.pack(side='left', padx=10, pady=10)

    # 绑定事件
    # tree.bind('<ButtonRelease-1>', tk_on_item_left_click)  # 左键事件
    tree.bind('<ButtonRelease-3>', tk_on_item_right_click)  # 右键事件
    tree.bind('<Button-1>', tk_on_button_press)  # 鼠标左键按下事件
    tree.bind('<B1-Motion>', tk_on_mouse_drag)  # 鼠标左键拖动事件


    # 运行主循环
    root.mainloop()



