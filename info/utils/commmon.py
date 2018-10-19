"""自定义公共工具类"""


# 定义前端模板的过滤器,定以后要添加到当前过滤器集
def do_index_class(index):
    """定义过滤器"""
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    return ""
