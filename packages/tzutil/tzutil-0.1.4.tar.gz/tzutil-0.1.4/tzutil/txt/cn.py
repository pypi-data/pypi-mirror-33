

def has_chinese(s):
    for i in s:
        if i >= u'\u4e00' and i <= u'\u9fa5':
            return True
    return False


def 全角转半角(ustring):
    rstring = []
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
            uchar = 0
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248
            uchar = 0
        rstring.append(uchar or chr(inside_code))
    return "".join(rstring)
