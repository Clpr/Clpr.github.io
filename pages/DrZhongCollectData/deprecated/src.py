# encoding: utf-8
# 定义一系列标准模板以快速修改form

import codecs
import json
from predefvars import * # 引入预定义的各个常量








# ---------------
def newSelect(ValList : list, id : str = 'id1', name : str = 'q1', flag_required : bool = False, placeholder :str = 'please select', style : str = '' ):
    """
    用于根据制定的选项列表ValList生成<select></select>多选下拉框。一个'please select'会作为第一个选项且默认选中。
    1. id : str, id value
    2. name : str, name address
    3. ValList : list, list of options (str)
    4. flag_required : bool = False, 是否是必做题，如果必做，那么'please select'就会加上disabled属性（不可选）
    5. placeholder : str, 可以选择替换掉默认的'please select'占位符
    6. style : str, CSS样式，默认留空
    """
    res = '<select id = "' + id + '" name="' + name + '"' +  ( ('style="' + style + '"' ) if style !='' else ' ' ) 
    if flag_required:
        res += 'required>'
    else:
        res += '>'
    # 至此完成<select>左标签，接下来构建选项（列表）
    tmpoptions = [ '<option value="' + x + '">' + x + '</option>' for x in ValList ]
    # 接下来插入占位符
    tmpplaceholder = ' selected disabled ' if flag_required else ' selected '
    tmpplaceholder = '<option value="' + placeholder + '"' + tmpplaceholder + '>' + placeholder + '</option>'
    tmpoptions.insert(0, tmpplaceholder ) 
    # 拼接，补全右标签</select>
    res += ''.join(tmpoptions) + '</select>'
    return res
# ---------------
def newYearType( since : int, until : int, id : str = 'idx1', name : str ='q1', flag_required : bool =False, style : str = ''):
    """
    根据输入的since和until生成一个number类型的<input>标签字符串，placeholder使用'since ~ until'。
    """
    res = '<input id="' + id + '" name="' + name + '" type="number" min=' + str(since) + ' max=' + str(until)
    res += ' style="' + style + '" placeholder="' + str(since) + ' ~ ' + str(until) + '"'
    res += ( ' required ' if flag_required else '' ) + '/>'
    return res 
# ---------------
def newMoreRecordRadio( count : int, name : str = "morerecords", flag_nochecked : bool = True ):
    """
    生成more than xx records? yes() no()这一问题，作为表格单独的一行，接受一个count，即提供槽位的最大个数（比如我们允许最大10条记录）
    返回一个<tr></tr>标签。flag_nochecked标记是否默认选中No，如果为False则默认选中Yes
    """
    res = ['<tr id="', 'q_'+name , '" >',
        '<td>More than ', str(count), ' records?</td>',
        '<td><label for="', name, '">',
        'Yes<input type="radio" name="', name, '" value="Yes" ', ( 'checked' if not flag_nochecked else ' ' ),'/></label>',
        'No<input type="radio" name="', name, '" value="No" ', ( 'checked' if flag_nochecked else ' ' ),'/></label>',
        '</td></tr>'
    ]
    return ''.join(res)
    



# -------------------------- small functions
def valid( x ):
    """
    doing validation, returning a striped string for any input vars (if applicable)
    """
    return ( x.strip() if isinstance(x, str) else str(x).strip() )


# -------------------------- 结构化标签类型
class HtmlTag:
    tagName : str  # e.g. font, select, a
    tagId : str  # the unique id of the tag
    content : str  # content, e.g. <a>content</a>
    attrSingle : list  # single attribute without a =, e.g. <input required>
    attrPair : dict  # attribute(s) and their values, e.g. { 'name' : 'sucker', 'style' : '"width:50%;"' }
    # ---------
    def maketag(self) -> str:
        """
        construct complete tag using attributes
        """
        res = '<' + self.tagName + ' id = "' + self.tagId + '" '
        res += ' '.join([ key + '=' + val for key,val in self.attrPair.items() ])
        res += ' ' + ' '.join(self.attrSingle)
        res += '>' + self.content + '</' + self.tagName + '>'
        return res
    # ---------
    def __init__(self, tagName : str, tagId : str, content : str, attrSingle : list, attrPair : dict ):
        """
        constructor
        """
        # init
        self.tagName = valid( tagName )
        self.tagId = valid( tagId )
        self.content = valid( content )
        self.attrSingle = [ valid(x) for x in attrSingle ]
        self.attrPair = attrPair
        # construct complete tag string
        return None


# -------------------- 从字符串列表生成table中某行的各列（<td></td>)
def makecols( x : list, add_tr : bool = True ) -> str :
    if isinstance(x, list):
        res = ''.join([ '<td>' + str(tmp_x) + '</td>' for tmp_x in x ])
    else:
        raise TypeError('needs a list')
    return ( '<tr>' + res + '</tr>') if add_tr else res





















# --------------- 形式父类，用于 mask 掉 constructor
class ExpRecord:
    """
    basic template class of experience records, e.g. working exp, serving exp
    """
    id : str = "name"  # unique id of the element
    style : str = ""  # style string
    def __init__(self,id = "1", style:str = "font-size:11pt;" ):
        self.id = id
        self.style = style






# --------------- 工作经历：教职
class WorkExp_teaching(ExpRecord):
    """
    工作经历模板类，默认应用class="auto_alluniv"属性。默认封装在一个table里，生成两行（一行标签，一行input）
    """
    # ----------------- 生成第一行标题行
    def get_1stRowLabel(self, x : dict, prefix : str = 'q_', flag_required : bool = False ) -> tuple :
        res = x.copy() # get a copy which will be returned
        for x in res.keys():
            # 使用给定的idx产生对当前记录特定的 names，如 'workexp1_title'
            res[x] = prefix + res[x]
        # 生成第1行标题行(str_required is a public variable defined in this module)
        tmp1stRow = []
        for x,y in res.items():
            tmpstr = '<td><label for="' + y + '">' + x + ( str_required if flag_required else '' ) + '</label></td>'
            tmp1stRow.append(tmpstr)
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # final return
        return (res,tmp1stRow)

    # ----------------- new
    def new(self, idx:str, flag_required : bool = False ):
        """
        生成一个给定序号 index 的 working experience 记录，其中 index 指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项
        """
        # 1. 首先构建第一行的标签们（显示名称 + name字段名）
        tmp_labels = {
            'Title' : 'title',
            'Institution' : 'univ',
            'Department' : 'department',
            'Since' : 'sinceyear',
            'Until' : 'untilyear',
            'Until Now?' : 'untilnow',
        }
        questionNames, tmp1stRow = self.get_1stRowLabel( 
            tmp_labels, 
            prefix = 'workexp_teach_' + str(idx) + '_',  # 用于标识 work experience 的前缀
            flag_required = flag_required
        )
        # ----------------------------------------
        # 然后生成第二行（先填充再用 makecols() 加入<td><tr>生成一行）
        tmp2ndRow = []
        # 2.0 title，使用公用字符串列表 li_worktitle_teach 和方法 newSelect()
        tmpstr = newSelect(
            li_worktitle_teach, 
            id = 'q_' + questionNames['Title'], # unique question id
            name = questionNames['Title'], 
            style='', 
            flag_required = flag_required, 
            placeholder='please select' 
        )
        tmp2ndRow.append(tmpstr)
        # 2.1 univ, 使用 CSS class auto_alluniv
        tmpstr = HtmlTag(
            'input',
            'q_' + questionNames['Institution'],
            ''
        )



        # tmp2ndRow.append( '<td>' + 
        #     newSelect(li_worktitle_teach, id = 'q_' + tmpnames[0], name=tmpnames[0], 
        #     style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        # )
        # 2.1 univ，使用CSS class auto_alluniv
        tmp2ndRow.append(
            '<td>' + '<input class="auto_alluniv" name ="' + tmpnames[1] + '" placeholder="type to search" style="width:80%;"' + 
            ( ' required ' if flag_required else '' ) + '/></td>'
        )
        # 3.2 department, 使用公用字符串列表li_departtype和方法newSelect
        tmp2ndRow.append( '<td>' + 
            newSelect(li_departtype, id = 'q_' + tmpnames[2], name=tmpnames[2], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 3.3 since year, 使用公用方法newYearInput(since,until)
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[3], name=tmpnames[3], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.4 until year, 同since year
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[4], name=tmpnames[4], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.5 until now?，现在还在干嘛，使用checkbox，如果当前记录required，则默认checked
        tmp2ndRow.append(
            '<td>' + '<input type="checkbox" id="q_workexp"' + idx + '_untilnow"' + ' name="' + tmpnames[5] + '" ' + 
            ( ' checked required ' if flag_required else ' ' ) + '/></td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow



# --------------- 工作经历：专职full-time non-teaching exp
class WorkExp_nonteach(ExpRecord):
    """
    全职研究工作经历模板类，默认封装在一个table里，生成两行（一行标签，一行input）
    """
    def new(self, idx:str, flag_required : bool = False ):
        """
        生成一个给定序号index的working experience记录，其中index指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项
        """
        # 首先构建第一行的标签们
        tmplabels = [ 'Title', 'Institution Type', 'Institution', 'Since', 'Until', 'Until Now?' ]
        # 以及对应的问题names（数据字段名，keys）
        tmpnames = [ 'title', 'institutiontype', 'institution', 'sinceyear', 'untilyear', 'untilnow' ]
        tmpnames = [ 'workexp_nonteach_' + idx + '_' + x for x in tmpnames ] # 使用给定的idx产生对当前记录特定的names，如'workexp1_title'
        # 接下来产生第一行（标签行），使用公用红色星号字符串（如果该记录为required）
        tmp1stRow = [ '<td><label for="' + nomen + '">' + lab + ( str_required if flag_required else '' ) + '</label></td>' for nomen,lab in zip(tmpnames,tmplabels) ]
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # 然后生成第二行
        tmp2ndRow = []
        # 2.0 title，使用公用字符串列表li_worktitle_research和方法newSelect
        tmp2ndRow.append( '<td>' + 
            newSelect(li_worktitle_nonteach, id = 'q_' + tmpnames[0], name=tmpnames[0], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 2.1 institution type，使用li_workinstituiontype_nonteach，下拉菜单
        tmp2ndRow.append( '<td>' + 
            newSelect(li_workinstituiontype_nonteach, id = 'q_' + tmpnames[1], name=tmpnames[1], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 2.2 institution, 使用li_workinstitution_nonteach，下拉菜单
        tmp2ndRow.append( '<td>' + 
            newSelect(li_workinstituion_nonteach, id = 'q_' + tmpnames[2], name=tmpnames[1], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 2.3 since year, 使用公用方法newYearInput(since,until)
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[3], name=tmpnames[3], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 2.4 until year, 同since year
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[4], name=tmpnames[4], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 2.5 until now?，现在还在干嘛，使用checkbox，如果当前记录required，则默认checked
        tmp2ndRow.append(
            '<td>' + '<input type="checkbox" id="q_workexp"' + idx + '_untilnow"' + ' name="' + tmpnames[5] + '" ' + 
            ( ' checked required ' if flag_required else ' ' ) + '/></td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow









# --------------- 教育经历
class EduExp(ExpRecord):
    """
    教育经历模板类，包含institution, degree/major, grad year等
    """
    def new(self, idx:str, flag_required : bool = False, degreetype : str = 'PhD' ):
        """
        生成一个给定序号index的education experience记录，其中index指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项

        """
        # 首先构建第一行的标签们
        tmplabels = [ degreetype + ' Institution', 'Major', 'Graduate Year' ]
        # 以及对应的问题names（数据字段名，keys）
        tmpnames = [ 'institution', 'major', 'gradyear' ]
        tmpnames = [ 'eduexp_' + degreetype + idx + '_' + x for x in tmpnames ] # 使用给定的idx产生对当前记录特定的names，如'workexp1_title'
        # 接下来产生第一行（标签行），使用公用红色星号字符串（如果该记录为required）
        tmp1stRow = [ '<td><label for="' + nomen + '">' + lab + ( str_required if flag_required else '' ) + '</label></td>' for nomen,lab in zip(tmpnames,tmplabels) ]
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # 然后生成第二行
        tmp2ndRow = []
        # 2.0 institution, 使用CSS class auto_alluniv
        tmp2ndRow.append(
            '<td>' + '<input class="auto_alluniv" name ="' + tmpnames[0] + '" placeholder="type to search" style="width:80%;"' + 
            ( ' required ' if flag_required else '' ) + '/></td>'
        )
        # 2.1 depart/major, 下拉框，使用公用列表li_degreemajor和公共方法newSelect()
        tmp2ndRow.append( '<td>' + 
            newSelect(li_degreemajor, id = 'q_' + tmpnames[1], name=tmpnames[1], 
            style='width:60%;', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 2.2 graduate year，数字，使用共用方法newYearInput()
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[2], name=tmpnames[2], style='width:60%;', flag_required=flag_required ) + '</td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow





# --------------- serving 经历：编辑
class ServeExp_editorial(ExpRecord):
    """
    editorial模板类，默认封装在一个table里，生成两行（一行标签，一行input）
    """
    def new(self, idx:str, flag_required : bool = False ):
        """
        生成一个给定序号index的 editorial experience 记录，其中index指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项

        """
        # 首先构建第一行的标签们
        tmplabels = [ 'Title', 'Journal', 'Since', 'Until', 'Until Now?' ]
        # 以及对应的问题names（数据字段名，keys）
        tmpnames = [ 'title', 'journal', 'sinceyear', 'untilyear', 'untilnow' ]
        tmpnames = [ 'serveexp_editorial_' + idx + '_' + x for x in tmpnames ] # 使用给定的idx产生对当前记录特定的names，如'workexp1_title'
        # 接下来产生第一行（标签行），使用公用红色星号字符串（如果该记录为required）
        tmp1stRow = [ '<td><label for="' + nomen + '">' + lab + ( str_required if flag_required else '' ) + '</label></td>' for nomen,lab in zip(tmpnames,tmplabels) ]
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # 然后生成第二行
        tmp2ndRow = []
        # 2.0 title，使用公用字符串列表 li_editortitle 和方法newSelect
        tmp2ndRow.append( '<td>' + 
            newSelect(li_editortitle, id = 'q_' + tmpnames[0], name=tmpnames[0], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 2.1 journal，就是普通的input text
        tmp2ndRow.append(
            '<td>' + '<input type="text" name ="' + tmpnames[1] + '" placeholder="type the journal name" style="width:80%;"' + 
            ( ' required ' if flag_required else '' ) + '/></td>'
        )
        # 3.2 since year, 使用公用方法newYearInput(since,until)
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[2], name=tmpnames[2], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.3 until year, 同since year
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[3], name=tmpnames[3], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.4 until now?，现在还在干嘛，使用checkbox，如果当前记录required，则默认checked
        tmp2ndRow.append(
            '<td>' + '<input type="checkbox" id="q_workexp"' + idx + '_untilnow"' + ' name="' + tmpnames[4] + '" ' + 
            ( ' checked required ' if flag_required else ' ' ) + '/></td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow





# --------------- serving 经历：院士
class ServeExp_academician(ExpRecord):
    """
    academician 模板类，使用CSS class auto_country，默认封装在一个table里，生成两行（一行标签，一行input）
    """
    def new(self, idx:str, flag_required : bool = False ):
        """
        生成一个给定序号index的 academician experience 记录，其中index指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项

        """
        # 首先构建第一行的标签们
        tmplabels = [ 'Country', 'Academy Type', 'Since' ]
        # 以及对应的问题names（数据字段名，keys）
        tmpnames = [ 'country', 'academytype', 'sinceyear' ]
        tmpnames = [ 'serveexp_academician_' + idx + '_' + x for x in tmpnames ] # 使用给定的idx产生对当前记录特定的names，如'workexp1_title'
        # 接下来产生第一行（标签行），使用公用红色星号字符串（如果该记录为required）
        tmp1stRow = [ '<td><label for="' + nomen + '">' + lab + ( str_required if flag_required else '' ) + '</label></td>' for nomen,lab in zip(tmpnames,tmplabels) ]
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # 然后生成第二行
        tmp2ndRow = []
        # 2.0 country，使用公用字符串列表 li_editortitle 和方法newSelect
        tmp2ndRow.append( 
            '<td>' + '<input class="auto_country" name ="' + tmpnames[0] + '" placeholder="type to search" style="width:80%;"' + 
            ( ' required ' if flag_required else '' ) + '/></td>'
        )
        # 2.1 academytype, 使用 li_academytype
        tmp2ndRow.append( '<td>' + 
            newSelect(li_academytype, id = 'q_' + tmpnames[1], name=tmpnames[1], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 3.2 since year, 使用公用方法newYearInput(since,until)
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[2], name=tmpnames[2], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow








# --------------- serving 经历：NBER
class ServeExp_nber(ExpRecord):
    """
    nber 模板类，默认封装在一个table里，生成两行（一行标签，一行input）
    """
    def new(self, idx:str, flag_required : bool = False ):
        """
        生成一个给定序号index的 nber experience 记录，其中index指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项

        """
        # 首先构建第一行的标签们
        tmplabels = [ 'Title', 'Since', 'Until', 'Until Now?' ]
        # 以及对应的问题names（数据字段名，keys）
        tmpnames = [ 'title', 'sinceyear', 'untilyear', 'untilnow' ]
        tmpnames = [ 'serveexp_nber_' + idx + '_' + x for x in tmpnames ] # 使用给定的idx产生对当前记录特定的names，如'workexp1_title'
        # 接下来产生第一行（标签行），使用公用红色星号字符串（如果该记录为required）
        tmp1stRow = [ '<td><label for="' + nomen + '">' + lab + ( str_required if flag_required else '' ) + '</label></td>' for nomen,lab in zip(tmpnames,tmplabels) ]
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # 然后生成第二行
        tmp2ndRow = []
        # 2.0 title，使用公用字符串列表 li_nbertitle 和方法newSelect
        tmp2ndRow.append( '<td>' + 
            newSelect(li_nbertitle, id = 'q_' + tmpnames[0], name=tmpnames[0], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 3.2 since year, 使用公用方法newYearInput(since,until)
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[1], name=tmpnames[1], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.3 until year, 同since year
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[2], name=tmpnames[2], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.4 until now?，现在还在干嘛，使用checkbox，如果当前记录required，则默认checked
        tmp2ndRow.append(
            '<td>' + '<input type="checkbox" id="q_workexp"' + idx + '_untilnow"' + ' name="' + tmpnames[3] + '" ' + 
            ( ' checked required ' if flag_required else ' ' ) + '/></td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow








# --------------- serving 经历：NGO
class ServeExp_NGO(ExpRecord):
    """
    NGO serving exp 模板类。默认封装在一个table里，生成两行（一行标签，一行input）
    """
    def new(self, idx:str, flag_required : bool = False ):
        """
        生成一个给定序号index的 NGO experience记录，其中index指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项

        """
        # 首先构建第一行的标签们
        tmplabels = [ 'Title', 'Organization', 'If other, please type its full name', 'Since', 'Until', 'Until Now?' ]
        # 以及对应的问题names（数据字段名，keys）
        tmpnames = [ 'title', 'organization', 'fullname', 'sinceyear', 'untilyear', 'untilnow' ]
        tmpnames = [ 'serveexp_ngo_' + idx + '_' + x for x in tmpnames ] # 使用给定的idx产生对当前记录特定的names，如'workexp1_title'
        # 接下来产生第一行（标签行），使用公用红色星号字符串（如果该记录为required）
        tmp1stRow = [ '<td><label for="' + nomen + '">' + lab + ( str_required if flag_required else '' ) + '</label></td>' for nomen,lab in zip(tmpnames,tmplabels) ]
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # 然后生成第二行
        tmp2ndRow = []
        # 2.0 title，使用公用字符串列表 li_servengotitle 和方法 newSelect
        tmp2ndRow.append( '<td>' + 
            newSelect(li_servengotitle, id = 'q_' + tmpnames[0], name=tmpnames[0], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 2.1 organization，使用公用字符串列表 li_ngoname 和方法 newSelect
        tmp2ndRow.append(  '<td>' + 
            newSelect(li_ngoname, id = 'q_' + tmpnames[1], name=tmpnames[1], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 3.2 fullname, 普通的键入
        tmp2ndRow.append( 
            '<td>' + '<input type="text" name ="' + tmpnames[1] + '" placeholder="please type" style="width:80%;"' + 
            ( ' required ' if flag_required else '' ) + '/></td>'
        )
        # 3.3 since year, 使用公用方法newYearInput(since,until)
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[3], name=tmpnames[3], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.4 until year, 同since year
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[4], name=tmpnames[4], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.5 until now?，现在还在干嘛，使用checkbox，如果当前记录required，则默认checked
        tmp2ndRow.append(
            '<td>' + '<input type="checkbox" id="q_workexp"' + idx + '_untilnow"' + ' name="' + tmpnames[5] + '" ' + 
            ( ' checked required ' if flag_required else ' ' ) + '/></td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow






# --------------- serving 经历：政府
class ServeExp_gov(ExpRecord):
    """
    government 模板类，使用CSS class auto_country，默认封装在一个table里，生成两行（一行标签，一行input）
    """
    def new(self, idx:str, flag_required : bool = False ):
        """
        生成一个给定序号index的 government experience 记录，其中index指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项

        """
        # 首先构建第一行的标签们
        tmplabels = [ 'Country', 'Department', 'Title', 'Since', 'Until', 'Until Now?' ]
        # 以及对应的问题names（数据字段名，keys）
        tmpnames = [ 'country', 'department', 'title', 'sinceyear', 'untilyear', 'untilnow' ]
        tmpnames = [ 'serveexp_academician_' + idx + '_' + x for x in tmpnames ] # 使用给定的idx产生对当前记录特定的names，如'workexp1_title'
        # 接下来产生第一行（标签行），使用公用红色星号字符串（如果该记录为required）
        tmp1stRow = [ '<td><label for="' + nomen + '">' + lab + ( str_required if flag_required else '' ) + '</label></td>' for nomen,lab in zip(tmpnames,tmplabels) ]
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # 然后生成第二行
        tmp2ndRow = []
        # 2.0 country，使用公用字符串列表 li_editortitle 和方法newSelect
        tmp2ndRow.append( 
            '<td>' + '<input class="auto_country" name ="' + tmpnames[0] + '" placeholder="type to search" style="width:80%;"' + 
            ( ' required ' if flag_required else '' ) + '/></td>'
        )
        # 2.1 department, 使用 li_govdeparttype
        tmp2ndRow.append( '<td>' + 
            newSelect(li_govdeparttype, id = 'q_' + tmpnames[1], name=tmpnames[1], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 2.2 title, 使用 li_govtitle
        tmp2ndRow.append( '<td>' + 
            newSelect(li_govtitle, id = 'q_' + tmpnames[2], name=tmpnames[2], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 3.3 since year, 使用公用方法newYearInput(since,until)
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[3], name=tmpnames[3], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.4 until year, 同since year
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[4], name=tmpnames[4], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.5 until now?，现在还在干嘛，使用checkbox，如果当前记录required，则默认checked
        tmp2ndRow.append(
            '<td>' + '<input type="checkbox" id="q_workexp"' + idx + '_untilnow"' + ' name="' + tmpnames[5] + '" ' + 
            ( ' checked required ' if flag_required else ' ' ) + '/></td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow









# --------------- serving 经历：企业
class ServeExp_firm(ExpRecord):
    """
    firm 模板类，使用CSS class auto_country，默认封装在一个table里，生成两行（一行标签，一行input）
    """
    def new(self, idx:str, flag_required : bool = False ):
        """
        生成一个给定序号index的 firm experience 记录，其中index指的是标记id时候的类似于"workexp01_title"中的01，用于区分不同的记录.
        1. idx : int
        2. flag_required : bool, 该记录是否为必填项

        """
        # 首先构建第一行的标签们
        tmplabels = [ 'Country', 'Firm Name', 'Firm Type', 'Title', 'Since', 'Until', 'Until Now?' ]
        # 以及对应的问题names（数据字段名，keys）
        tmpnames = [ 'country', 'firmname', 'firmtype', 'title', 'sinceyear', 'untilyear', 'untilnow' ]
        tmpnames = [ 'serveexp_academician_' + idx + '_' + x for x in tmpnames ] # 使用给定的idx产生对当前记录特定的names，如'workexp1_title'
        # 接下来产生第一行（标签行），使用公用红色星号字符串（如果该记录为required）
        tmp1stRow = [ '<td><label for="' + nomen + '">' + lab + ( str_required if flag_required else '' ) + '</label></td>' for nomen,lab in zip(tmpnames,tmplabels) ]
        tmp1stRow = '<tr>' + ''.join(tmp1stRow) + '</tr>' # add <tr> to become a row string
        # 然后生成第二行
        tmp2ndRow = []
        # 2.0 country，使用公用字符串列表 li_editortitle 和方法newSelect
        tmp2ndRow.append( 
            '<td>' + '<input class="auto_country" name ="' + tmpnames[0] + '" placeholder="type to search" style="width:80%;"' + 
            ( ' required ' if flag_required else '' ) + '/></td>'
        )
        # 2.1 firm name，普通输入
        tmp2ndRow.append( 
            '<td>' + '<input type="text" name ="' + tmpnames[1] + '" placeholder="please type" style="width:80%;"' + 
            ( ' required ' if flag_required else '' ) + '/></td>'
        )
        # 2.2 department, 使用 li_firmtype
        tmp2ndRow.append( '<td>' + 
            newSelect(li_firmtype, id = 'q_' + tmpnames[2], name=tmpnames[2], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 2.2 title, 使用 li_firmtitle
        tmp2ndRow.append( '<td>' + 
            newSelect(li_firmtitle, id = 'q_' + tmpnames[3], name=tmpnames[3], 
            style='', flag_required = flag_required, placeholder='please select' ) + '</td>'
        )
        # 3.3 since year, 使用公用方法newYearInput(since,until)
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[4], name=tmpnames[4], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.4 until year, 同since year
        tmp2ndRow.append(
            '<td>' + newYearType(1920,2019, id= 'q_'+tmpnames[5], name=tmpnames[5], style='width:50%;', flag_required=flag_required ) + '</td>'
        )
        # 3.5 until now?，现在还在干嘛，使用checkbox，如果当前记录required，则默认checked
        tmp2ndRow.append(
            '<td>' + '<input type="checkbox" id="q_workexp"' + idx + '_untilnow"' + ' name="' + tmpnames[6] + '" ' + 
            ( ' checked required ' if flag_required else ' ' ) + '/></td>'
        )
        # 拼接第二行然后生成整个字符串
        tmp2ndRow = '<tr>' + ''.join(tmp2ndRow) + '</tr>'
        # final return
        return tmp1stRow + tmp2ndRow














