# 使用代码拼合各个html文件生成总的调查表页面，以解决大量选项选择题的问题
import codecs # UTF8 I/O
import json  # json encoding
import src  # sources

# 0. create a list 
htmlstr = []

# =======================================================================


# 1. create a head string (not closed, because we will insert many long scripts from files)
with codecs.open("asset/part01_head.html","r",encoding="utf8") as fp:
    htmlstr.append( fp.read() )




# manually end the head section
htmlstr.append("</head>")

# =======================================================================

# 2. page title and notes
with codecs.open("asset/part02_beforeform.html","r",encoding="utf8") as fp:
    htmlstr.append( fp.read() )

# 3. (manually) add the beginning of form label
# NOTE: use enctype to upload data in a json file
htmlstr.append( ' <form action="#" onsubmit="return onSubmit(this)" id="mainform" enctype="application/json" > ' )





# ======================================================================= BASIC
# 4. Basic information: names, current university
with codecs.open("asset/part03_basicinfo1.html","r",encoding="utf8") as fp:
    htmlstr.append( fp.read() )

# 5. Basic information: sex, race, year of birth, birth country
with codecs.open("asset/part04_basicinfo2.html","r",encoding="utf8") as fp:
    htmlstr.append( fp.read() )





# ======================================================================= FIELD
# 6. Research Field(s)
with codecs.open("asset/part05_researchfield.html","r",encoding="utf8") as fp:
    htmlstr.append( fp.read() )










# # ======================================================================= EDUCATION
# # 7.1 表头
# tmpstr = [
#     '<hr />',
#     '<h2>Education</h2>',
#     '<p><i>Note: </i> please type in part of a university\'s name to locate it; please use the English name when searching a Chinese university</p>',
#     '<table name="tab_education" width="100%">',
# ]
# tmprecord = src.EduExp() # 实例化一个教育经历
# # 7.2 添加教育记录
# tmpstr.append( tmprecord.new( str(1), flag_required = True,  degreetype = 'PhD 1' ) ) # phd 1 (required)
# tmpstr.append( tmprecord.new( str(2), flag_required = False, degreetype = 'PhD 2' ) ) # phd 2
# tmpstr.append( tmprecord.new( str(3), flag_required = False, degreetype = 'Master 1' ) ) # master 1
# tmpstr.append( tmprecord.new( str(4), flag_required = False, degreetype = 'Master 2' ) ) # master 2
# tmpstr.append( tmprecord.new( str(5), flag_required = True,  degreetype = 'Bachelor 1' ) ) # bachelor 1 (required)
# tmpstr.append( tmprecord.new( str(6), flag_required = False, degreetype = 'Bachelor 2' ) ) # bachelor 2
# # 7.3 close the table
# tmpstr.append( '</table>' )
# # 7.4 add to htmlstr
# htmlstr.append(''.join(tmpstr))











# # ======================================================================= WORKING
# # full-time 工作经历，分为 teaching 和 non-teaching 两个部分

# # 9.1 添加表头
# tmpstr = [
#     '<hr />',
#     '<h2>Working Experiences (full-time)</h2>',
#     '<p>1. working experiences means <b>full-time</b> jobs.</p>',
#     '<p>   工作经历指（学术或非学术）<b>全职</b>工作</p>',
#     '<p>2. please use the most recent working experience as the 1st record.</p>',
#     '<p>   请使用该教师当前所在机构对应的工作经历作为第一条记录，并按时间顺序逆序填写</p>',
#     '<p>3. if there are more than 10 experiences, please check the last check-box.</p>',
#     '<p>   若该教师工作经历多于当前提供槽位，请勾选最后的“More than xx records?”</p>',
#     '<p>4. please primarily input those <b>non-visiting</b> experiences.</p>',
#     '<p>   请优先填写非访问类（如访问学者）经历</p>',
#     '<p>5. For the 1st record, if "Until Now" checked, please fill 2019 in "Until".</p>',
#     '<p>   对于第1条记录，当勾选"Until Now"时，由于"Until"一栏为必填，故请填写2019</p>',    
#     '<table id="tab_workexp" width="100%">',
# ]
# # 9.2 添加 teaching working experience 标题
# tmpstr.append( '<tr><td><h3>Experience: Teaching</h3></td></tr>' )
# # 9.3 添加 teaching 类型的 working experience
# tmprecord = src.WorkExp_teaching() # 实例化一个工作记录模板
# for idx in range(10):
#     tmpstr.append(
#         # 第一条记录 required，其余可选
#         tmprecord.new( str(idx+1), flag_required = ( True if idx == 0 else False ) )
#     )
# # 9.4 添加 more records? 单选题
# tmpstr.append(
#     src.newMoreRecordRadio( 10, name = 'workexp_teach_morerecords' )
# )
# # 9.5 添加 non-teaching working experience 标题
# tmpstr.append( '<tr><td><h3>Experience: Non-teaching</h3></td></tr>' )
# # 9.6 添加 non-teaching 类型的 working experience
# tmprecord = src.WorkExp_nonteach()
# for idx in range(5):
#     tmpstr.append(
#         # 第一条记录 required，其余可选
#         tmprecord.new( str(idx+1), flag_required = ( True if idx == -1 else False ) )
#     )
# # 9.7 添加 more records? 单选题
# tmpstr.append(
#     src.newMoreRecordRadio( 5, name = 'workexp_nonteach_morerecords' )
# )
# # 9.8 close the table
# tmpstr.append( '</table>' )
# # 9.9 拼接并接续到 htmlstr 列表
# htmlstr.append( ''.join(tmpstr) )








# # ======================================================================= SERVE: NOBEL LAUREATE
# # SERVING: 诺奖
# tmpstr = [
#     '<hr />',
#     '<h2>Serving Experiences (part-time)</h2>',
#     '<p>1. Serving experiences mean the positions in government, non-government organizations (NGO), journal publisher, membership etc.</p>',
#     '<h3>Nobel Laureate</h3>',
#     '<table id="tab_serve_nobel" width="100%">',
#     '<tr>',
#     '<td>1. Is this faculty member a Nobel Laureate? </td>', '</tr><tr>',
#     '<td>',
#     '<label for="isa_nobellaureate">Yes</label><input type="radio" name="isa_nobellaureate" value="Yes"  />',
#     '<label for="isa_nobellaureate">No</label><input type="radio" name="isa_nobellaureate" value="No" checked  />',
#     '</td>',
#     '</tr>',
#     '<tr>',
#     '<td>2. If he/she is, the year of his/her <b>first</b> time to win a Nobel Prize?</td>', '</tr><tr>',
#     '<td><input name="nobelyear" type="number" min=1920 max=2019 style="width:60%;" placeholder="1920-2019"  /></td>',
#     '</tr>',
#     '</table>',
# ]
# # 拼接并接续到 htmlstr 列表
# htmlstr.append( ''.join(tmpstr) )


# # ======================================================================= SERVE: ACADEMICIAN
# # SERVING: 院士
# tmpstr = [
#     '<h3>Academician</h3>',
#     '<table id="tab_serve_academician" width="100%">',
# ]
# # 添加院士记录
# tmprecord = src.ServeExp_academician()
# for idx in range(5):
#     tmpstr.append(
#         tmprecord.new( str(idx+1), flag_required = False )
#     )
# # 添加 more records? 单选题
# tmpstr.append(
#     src.newMoreRecordRadio( 5, name = 'serveexp_academician_morerecords' )
# )
# # close the table
# tmpstr.append( '</table>' )
# # 拼接并接续到 htmlstr 列表
# htmlstr.append( ''.join(tmpstr) )









# # ======================================================================= SERVE: NBER
# # SERVING: NBER
# tmpstr = [
#     '<h3>NBER</h3>',
#     '<table id="tab_serve_nber0" width="100%">',
#     '<tr>',
#     '<td>Does this faculty member has a fellowship at NBER <b>now</b>? &nbsp&nbsp',
#     '<label for="nber_now">Yes</label><input type="radio" name="nber_now" value="Yes"  /> &nbsp',
#     '<label for="nber_now">No</label><input type="radio" name="nber_now" value="No" checked  /> &nbsp',
#     '</td>',
#     '</tr>',
#     '</table>',
#     '<table id="tab_serve_nber1" width="100%">',    
# ]
# # 添加NBER经历
# tmprecord = src.ServeExp_nber()
# for idx in range(5):
#     tmpstr.append(
#         tmprecord.new( str(idx+1), flag_required = False )
#     )
# # 添加 more records? 单选题
# tmpstr.append(
#     src.newMoreRecordRadio( 5, name = 'serveexp_nber_morerecords' )
# )
# # close the table
# tmpstr.append( '</table>' )
# # 拼接并接续到 htmlstr 列表
# htmlstr.append( ''.join(tmpstr) )




# # ======================================================================= SERVE: EDITORIAL
# # SERVING: 编辑类工作
# tmpstr = [
#     '<h3>Editorial</h3>',
#     '<table id="tab_serve_editorial" width="100%">',
# ]
# # 添加 editorial 记录
# tmprecord = src.ServeExp_editorial()
# for idx in range(10):
#     tmpstr.append(
#         tmprecord.new( str(idx+1), flag_required = False )
#     )
# # 添加 more records? 单选题
# tmpstr.append(
#     src.newMoreRecordRadio( 10, name = 'serveexp_editorial_morerecords' )
# )
# # close the table
# tmpstr.append( '</table>' )
# # 拼接并接续到 htmlstr 列表
# htmlstr.append( ''.join(tmpstr) )









# # ======================================================================= SERVE: NGO
# # SERVING: 非政府组织
# tmpstr = [
#     '<h3>Non-government Organizations (NGO)</h3>',
#     '<p>1. e.g. UN, IMF, WB, OECD, EU, where the research department(s) of EU is considered an NGO.</p>',
#     '<p>2. NGO does not include commercial organizations.</p>',
#     '<p>3. The research departments (rd) of central banks are considered as NGO in this form. Please indicate the country name in the second text box if "Researc Department of other countries\' central bank" selected.</p>',
#     '<table id="tab_serve_ngo" width="100%">',
# ]
# # 填充记录
# tmprecord = src.ServeExp_NGO()
# for idx in range(5):
#     tmpstr.append(
#         tmprecord.new( str(idx+1), flag_required = False )
#     )
# # 添加 more records? 单选题
# tmpstr.append(
#     src.newMoreRecordRadio( 5, name = 'serveexp_ngo_morerecords' )
# )
# # close the table
# tmpstr.append( '</table>' )
# # 拼接并接续到 htmlstr 列表
# htmlstr.append( ''.join(tmpstr) )






# # ======================================================================= SERVE: GOV
# # SERVING: 政府
# tmpstr = [
#     '<h3>Government</h3>',
#     '<p>1. e.g. officials of a country\'s government, advisors employed by a government. </p>',
#     '<p>2. an example is Lawrence Summers. He was once a senior U.S. Treasury Department official throughout President.</p>',
#     '<table id="tab_serve_gov" width="100%">',
# ]
# # 添加记录
# tmprecord = src.ServeExp_gov()
# for idx in range(5):
#     tmpstr.append(
#         tmprecord.new( str(idx+1), flag_required = False )
#     )
# # 添加 more records? 单选题
# tmpstr.append(
#     src.newMoreRecordRadio( 5, name = 'serveexp_gov_morerecords' )
# )
# # close the table
# tmpstr.append( '</table>' )
# # 拼接并接续到 htmlstr 列表
# htmlstr.append( ''.join(tmpstr) )




# # ======================================================================= SERVE: 企业
# # SERVING: 企业
# tmpstr = [
#     '<h3>Commercial</h3>',
#     '<p>e.g. company, hedge fund, investment bank</p>',
#     '<table id="tab_serve_firm" width="100%">',
# ]
# # 添加记录
# tmprecord = src.ServeExp_firm()
# for idx in range(5):
#     tmpstr.append(
#         tmprecord.new( str(idx+1), flag_required = False )
#     )
# # 添加 more records? 单选题
# tmpstr.append(
#     src.newMoreRecordRadio( 5, name = 'serveexp_firm_morerecords' )
# )
# # close the table
# tmpstr.append( '</table>' )
# # 拼接并接续到 htmlstr 列表
# htmlstr.append( ''.join(tmpstr) )






# ======================================================================= FINAL SIGNATURE
# 13. Signature
with codecs.open("asset/beforesubmit.html","r",encoding="utf8") as fp:
    htmlstr.append( fp.read() )








# =======================================================================

# *. add a hline and a white space block
htmlstr.append( '<hr/><div style= "height:50px" ></div>' )


# *. (manually) add the end of form label
# NOTE: this </div> is for the outer-layer large <div> which scales the form
htmlstr.append( ' <input type="submit" id="downloadasjson" value="Submit" style="width:25%;height:50px;" />  </form></div> ' ) 




# =======================================================================
# add a div for information
with codecs.open("asset/part12_References.html","r",encoding="utf8") as fp:
    htmlstr.append( fp.read() )


# *. (manually) add the end of the document
htmlstr.append( " </body></html> " )

# =======================================================================

# finally, paste all strings and output to file
final_htmlstr = " ".join(htmlstr)
with codecs.open("NewProfile.html","w",encoding="utf8") as fp:
    fp.write(final_htmlstr)




