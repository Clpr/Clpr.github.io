p_navigator = tag_div(style="position:fixed;width:15%;margin-left:0%;border-style:solid;")


add!(p_navigator,tag_h3("Navigator"))
add!(p_navigator,quicktag_ol([
    tag_p(	"I. 基本信息",	onclick="document.querySelector('#tab_basicinfo').scrollIntoView();"),
    tag_p(	"II. 研究领域",	onclick="document.querySelector('#tab_researchfield').scrollIntoView();"),
    tag_p(	"III. 教育背景",	onclick="document.querySelector('#tab_education').scrollIntoView();"),
    tag_p(	"IV. 全职博士后",	onclick="document.querySelector('#tab_fulltime_postdoc').scrollIntoView();"),
    tag_p(	"V. 全职学术类经历",	onclick="document.querySelector('#tab_fulltime_academia').scrollIntoView();"),
    tag_p(	"VI. 全职业界工作",	onclick="document.querySelector('#tab_fulltime_industrial').scrollIntoView();"),
    tag_p(	"VII. 全职政府工作",	onclick="document.querySelector('#tab_fulltime_government').scrollIntoView();"),
    tag_p(	"VIII. 全职非政府组织经历",	onclick="document.querySelector('#tab_fulltime_ngo').scrollIntoView();"),
    tag_p(	"IX. 诺贝尔奖",	onclick="document.querySelector('#tab_nobel').scrollIntoView();"),
    tag_p(	"X. 官方院士荣誉",	onclick="document.querySelector('#tab_academician').scrollIntoView();"),
    tag_p(	"XI: 常见学术社团与非官方院士荣誉",	onclick="document.querySelector('#tab_societyandfellow').scrollIntoView();"),
    tag_p(	"XII. 其他研究资金来源",	onclick="document.querySelector('#tab_otherfunding').scrollIntoView();"),
    tag_p(	"XIII. 兼职学术期刊类经历",	onclick="document.querySelector('#tab_serve_editorial').scrollIntoView();"),
    tag_p(	"XIV. 兼职政府职务",	onclick="document.querySelector('#tab_serve_government').scrollIntoView();"),
    tag_p(	"XV. 兼职非政府组织经历",	onclick="document.querySelector('#tab_serve_ngo').scrollIntoView();"),
    tag_p(	"XVI. 兼职业界工作",	onclick="document.querySelector('#tab_serve_industrial').scrollIntoView();"),
    tag_p(	"XVII: 教课信息",	onclick="document.querySelector('#tab_teaching_courses').scrollIntoView();"),
    tag_p(	"XVIII: 学术休假",	onclick="document.querySelector('#tab_sabbatical').scrollIntoView();"),
]))






# add to body
add!(p_body,p_navigator)
#
