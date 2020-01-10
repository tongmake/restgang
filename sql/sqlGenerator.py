# coding=utf-8
__author__ = 'menghui'
import string
import re
import shlex
import service.utils as utils


class SQLExpParseError(Exception):
    '''
    SQL分析器异常
    '''

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class SQLDirector:
    def __init__(self, builder):
        self._builder = builder

    def construct(self):
        self._builder.buildSQL()
        return self._builder.getSQL()


class SQLBuilder:
    def __init__(self): self._sql = ''

    def buildSQL(self): return self

    def getSQL(self): return self._sql


class Criteria(SQLBuilder):
    '''
    定义一个条件
    '''

    def __init__(self):
        self.andCriterias = []

    def addCriterias(self, field, operation, value):
        self.andCriterias.append(field + operation + value)
        return self

    def buildSQL(self):
        self._sql = "(" + " OR ".join(self.andCriterias) + ")"
        return self


class SelectPagerBuilder(SQLBuilder):
    '''
    分页SQL构造器
    '''

    def __init__(self, selectbuilder, pagesize, pageindex, limit, sql="", dbtype="oracle"):
        self.pagesize = pagesize
        self.pageindex = pageindex
        self.limit = limit
        self.selectbuilder = selectbuilder
        self._sql = sql
        self.dbtype = dbtype

    def getRowNum(self):
        return [(self.pageindex - 1) * self.pagesize, self.pageindex * self.pagesize]

    def buildSQL(self):
        if self._sql == "":
            self._sql = self.selectbuilder.buildSQL().getSQL()
        if self.pagesize < 0 or self.limit < 0 or self.pageindex < 0:
            return self
        if self.pagesize == 0:
            if self.limit == 0:
                return self
            else:
                if self.dbtype=="oracle":
                    self._sql = "SELECT * FROM (" + self._sql + ") WHERE ROWNUM <=" + '%d' % self.limit
                if self.dbtype=="mssql":
                    self._sql = "SELECT TOP "+ ('%d' % self.limit)+" * FROM (" + self._sql + ") t"
        else:
            r = self.getRowNum()
            if self.dbtype=="oracle":
                self._sql = "SELECT * FROM (SELECT A.*,ROWNUM RN FROM (" + self._sql + ") A WHERE ROWNUM<" + '%d' % (
                    r[1]) + ") WHERE RN>=" + '%d' % (r[0])
            if self.dbtype=="mssql":
                self._sql ="select * from (select row_number()over(order by _tempCol) _RN,* from (select top "+('%d' % r[1])\
                           +" _tempCol=1,* from (select * from jeda_menu) _T_) _TT_) _TTT_ where _RN>"+('%d' % r[0])
        return self


class InnerSelectBuilder(SQLBuilder):
    def __init__(self, selectbuilder, innersql):
        self.innersql = innersql
        self.selectbuilder = selectbuilder

    def buildSQL(self):
        self._sql = self.selectbuilder.buildSQL().getSQL()
        i = self.innersql.find("from")
        if i == -1:
            return self
        fs = self.innersql[:i].split(',')  # 字段列表
        ts = self.innersql[i + 4:]
        i = ts.find("on")
        if i == -1:
            return self
        innertablename = ts[:i - 1]  # 内链接表名
        innerwhere = ts[i:]
        fs = ",".join(map(lambda x: innertablename + "." + x, fs))  # 字段列表，字符串格式
        self._sql = "SELECT src.*," + fs + " from (" + self._sql + ") src inner join " + innertablename + " " + innerwhere
        return self


class SelectBuilder(SQLBuilder):
    def __init__(self):
        self._orderby = []
        self._fields = []
        self._criteria = []
        self._where = None
        self._innerjoin = []

    def table(self, table):
        self._table = table
        return self

    def buildSQL(self):
        if len(self._fields) != 0:
            columns_str = ",".join(map(lambda x: "%s" % (x), self._fields))
        else:
            columns_str = "*"
        self._sql = "SELECT " + columns_str + " FROM " + self._table
        if len(self._criteria):
            where_str = " AND ".join(map(lambda x: x.buildSQL().getSQL(), self._criteria))
            self._sql += " WHERE " + where_str
        elif self._where is not None:
            self._sql += " WHERE " + self._where
        if len(self._orderby):
            order_str = " ".join(self._orderby)
            self._sql += " ORDER BY " + order_str
        return self

    def addWhere(self, where):
        self._where = where

    def andCriteria(self):
        cri = Criteria()
        self._criteria.append(cri)
        return cri

    def column(self, columnName):
        self._fields.append(columnName)
        return self

    def innerjoin(self, innerstr):
        self._innerjoin.append(innerstr)
        return self

    def orderby(self, order):
        self._orderby.append(order)
        return self


_EXPKEYWORD = [">", "<", "==", "!=", ">=", "<="]
_SUBKEYWORD = [">", "<", "=", "!"]


def dualexp(exp, param):
    '''
    不能包含括号，可以包含and or
    不区分数据类型
    @param exp:
    @param param:
    @return:
    '''
    # 拆分
    # 符号左侧为冒号站位的变量名，右侧为参数值，字符串以单引号修饰
    try:
        lex = shlex.shlex(exp)
        lex.wordchars += ":"
        lex.whitespace_split = False
        lex.quotes = "'"
        ts = list(lex)
    except Exception:
        raise SQLExpParseError(u"test表达式语法错误,使用:站位，使用单引号表示字符串")
    # print(ts)
    # 合并== ！= <= >=符号，合并后放在tss中
    tss = []
    index = 0
    while index < len(ts):
        if ts[index] in _SUBKEYWORD:
            if index + 1 == len(ts):
                tss.append(ts[index])
                tss.append("")
            else:
                if ts[index + 1] in _SUBKEYWORD:
                    tss.append(ts[index] + ts[index + 1])
                    index += 2
                else:
                    tss.append(ts[index])
                    index += 1
        else:
            tss.append(ts[index])
            index += 1
    # print(tss)
    # 计算表达式，不计算and和or语法
    result = None
    index = 0
    ts = []
    while index < len(tss):
        if tss[index][0] == ":":  # 变量名
            if not (tss[index][1:] in param):
                # raise SQLExpParseError(u"表达式中的参数没有包含在参数列表中")
                result = None
            else:
                result = param[tss[index][1:]]
            index += 1
        elif tss[index].upper() == "AND":
            ts.append("AND")
            index += 1
        elif tss[index].upper() == "OR":
            ts.append("OR")
            index += 1
        elif tss[index] in _EXPKEYWORD:
            oper = tss[index]
            index += 1
            if index == len(tss):  # 取右值越界，返回False
                raise SQLExpParseError(u"表达式错误，取右值时字符串越界")
            right = tss[index]
            if right[0] == "\'" and right[-1] == "\'":
                # 字符串
                right = right.strip("\"'")  # 取右值
            else:
                if utils.isnumeric(right):
                    right = utils.convertToNumber(right)
                elif right.upper() == "NULL" or right.upper() == "NONE":
                    right = None
                else:
                    raise SQLExpParseError(u"字符串必须添加引号")
            try:
                if oper == "==":  # 等于判断
                    result = (result == right)
                    ts.append(result)
                    index += 1
                elif oper == "!=":  # 等于判断
                    result = (result != right)
                    ts.append(result)
                    index += 1
                elif oper == ">":  # 等于判断
                    result = (result > right)
                    ts.append(result)
                    index += 1
                elif oper == "<":  # 等于判断
                    result = (result < right)
                    ts.append(result)
                    index += 1
                elif oper == "<=":  # 等于判断
                    result = (result <= right)
                    ts.append(result)
                    index += 1
                elif oper == ">=":  # 等于判断
                    result = (result >= right)
                    ts.append(result)
                    index += 1
            except Exception:
                return False
        else:
            return False
    # 计算and和or语法
    result = False
    index = 0
    while index < len(ts):
        item = ts[index]
        if item == "AND":
            if index + 1 == len(ts):
                return False
            result = result and ts[index + 1]
            index += 2

        elif item == "OR":
            if index + 1 == len(ts):
                return False
            result = result or ts[index + 1]
            index += 2
        else:
            result = item
            index += 1
    # print(ts)
    return result


def parseTrim(sql, param):
    '''
    处理trim标签
    @param sql:
    @param param:
    @return:
    '''
    result = []
    gp = re.search('<trim\s*([a-zA-Z]+\s*=\s*"([^"]*)"\s*)*>', sql)
    if gp is None:
        return sql
    tagstr = gp.group(0)  # 匹配的标记

    tagstart = gp.span()[0]  # 标记起始位置
    tagend = sql.find("</trim>", tagstart)  # 标记结束位置
    if tagend == -1:  # 没有找到结束标记，不处理直接返回
        raise SQLExpParseError(u"没有找到对应的</trim>标签")
    result.append(sql[:tagstart])
    attrs = dict(re.findall('([a-zA-Z]+)\s*=\s*"([^"]*)"', tagstr))  # 查找所有属性
    prefixOverrides = None
    if ("prefixOverrides" in attrs):
        prefixOverrides = attrs["prefixOverrides"].split("|")

    innerXML = sql[tagstart + len(tagstr):tagend]

    # print(innerXML)
    r = parseTest(innerXML, param, 0, prefixOverrides)
    if r[0] == True:
        if "prefix" in attrs:
            if result[-1].strip(" ")[-1 * len(attrs["prefix"])] != attrs["prefix"]:
                result.append(attrs["prefix"])
    result.append(r[1])
    result.append(sql[tagend + 7:])

    return parseTrim(" ".join(result), param)  # 递归处理下一个


def parseTest(sql, param, index, prefixOverrides):
    '''
    处理test标签
    @param sql:
    @param param:
    @param index:
    @param prefixOverrides:
    @return:
    '''
    result = []
    succeedTest = False
    tagstart = 0
    tagstr = ""
    gp = re.search('<if\s*([a-zA-Z]+\s*=\s*"([^"]*)"\s*)*>', sql)
    if gp is None:
        return [False, sql]

    tagstr = gp.group(0)  # 匹配的标记
    tagstart = gp.span()[0]  # 标记起始位置
    tagend = sql.find("</if>", tagstart)  # 标记结束位置
    if tagend == -1:  # 没有找到结束标记，不处理直接返回
        raise SQLExpParseError(u"没有找到对应的</if>标签")
    result.append(sql[:tagstart])
    attrs = dict(re.findall('([a-zA-Z]+)\s*=\s*"([^"]*)"', tagstr))  # 查找所有属性

    if (attrs["test"] is None) or (dualexp(attrs["test"], param) == True):
        succeedTest = True
        tmps = sql[tagstart + len(tagstr):tagend]
        if prefixOverrides is None:
            result.append(tmps)
        else:
            if index == 0 and not (prefixOverrides is None):
                for fix in prefixOverrides:
                    if tmps[:len(fix)] == fix:
                        result.append(" ")
                        result.append(tmps[len(fix):])
            else:
                result.append(tmps)
        index = index + 1
    result.append(sql[tagend + 5:])
    r = parseTest(" ".join(result), param, index, prefixOverrides)  # 递归处理下一个
    r[0] = r[0] or succeedTest  # 更新succeedTest，在该trim块中当有test条件成立时返回true
    return r


def findparam(sql):
    '''
    返回全部的参数
    @param sql:
    @return:
    '''
    gp = re.findall(':([a-zA-Z_][a-zA-Z0-9_]*)', sql)
    return gp


def findplaceholder(sql):
    '''
    返回SQL中的站位符
    @param sql:
    @return:
    '''
    gp = re.findall('\$([a-zA-Z_][a-zA-Z0-9_]*)', sql)
    return gp


if __name__ == "__main__":
    # param = {
    #     "name": "menghui2",
    #     "age": 11,
    #     "sex": "male"
    # }
    #
    # sql = parseTrim(
    #         '''select b.stcd,b.stnm,a.tm,a.z,a.q from stu.st_river_r a inner join stu.st_stbprp_b b on a.stcd=b.stcd
    #             <trim prefix="where" prefixOverrides="and |or ">
    #             <if test=":name!='menghui'">and a.tm>to_date(:tm,'YYYY-MM-DD')</if>
    #
    #             </trim>'''
    #         , param)
    param = {"rvnm": 'a', 'stcd': '123123'}
    sql = parseTrim(
        "SELECT *   FROM ST_STBPRP_B B <trim prefix=\"where\" prefixOverrides=\"and |or \"><if test=\":rvnm!=NULL\"> and rvNm like :rvnm</if></trim>",
        param)

    print(sql)
    # r = dualexp(":name ==\"menghui\"", {
    #     "name": "menghui",
    #     "age": 10,
    #     "sex": "male"
    # })
    # print(r)
