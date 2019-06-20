# new source file, defs of tag class, etc.
# =========================


# ------------------ 根据输入的字符串列表创建<table>中的一行
def strlist2tr(strlist : list) -> str:
    """
    convert a list of strings to a line (<tr>/) in <table> tag;
    returns an HTML string;
    """
    if not all([ isinstance(x,str) for x in strlist ]):
        raise AssertionError("requires a list of strings")
    ret = [ '<td>' + x + '</td>\n' for x in strlist ]
    return '<tr>\n' + ''.join(ret) + '</tr>\n'









