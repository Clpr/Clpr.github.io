# 本文件中都是一些预先定义好的常量，名单等


# ---------------
str_required = ' <font color=red>*</font> ' # 公用变量，用于标记required字段
# ---------------
# 共用变量，用于生成种族列表
li_race = [
    "Unknown", 
    "White", "Black or African American", 
    "Asian", "American Indian or Alaska Native", 
    "Hispanic or Latino", "Native Hawaiian or Other Pacific Islander", 
    "Half-blood", "Other",    
]
# 共用变量，用于生成研究领域中的领域列表
li_field = [
    "Unknown (#)", 
    "Other (Z)", 
    "Agricultural economics (Q)", "Business economics (M)", "Computational economics (C)", "Decision theory (D)", 
    "Demographic economics (J)", "Development economics (O)", "Econometrics (C)", "Economic geography (Q)", 
    "Economic history (N)", "Economic model (C)", "Economic planning (P)", "Economic policy (E)", 
    "Economic sociology (Y)", "Economic statistics (C)", "Economic theory (A)", "Education economics (I)", 
    "Environmental economics (Q)", "Experimental economics (Z)", "Financial economics (G)", "Game theory (D)", 
    "Health economics (I)", "Industrial engineering (L)", "Industrial organization (L)", "Input-output model (E)", 
    "International economics (F)", "Knowledge economics (O)", "Labor economics (J)", "Law and economics (K)", 
    "Macroeconomics (E)", "Mathematical economics (C)", "Mathematical finance (G)", "Mechanism design (D)", 
    "Microeconomics (D)", "Monetary economics (E)", "Natural resource (Q)", "Political economy (A)", 
    "Public choice (H)", "Public economics (H)", "Regional economics (R)", "Service economics (R)", 
    "Socioeconomics (Y)", "Transportation (R)", "Urban economics (R)", "Welfare economics (I)",
]
# 公用变量，用于生成教学经历中的下拉菜单<select>
li_worktitle_teach = [
    'Unknown',  # 必须项，用于处理others
    'Chair Professor', 'Professor', 'Associate Professor', 'Assistant Professor', 'Adjunct Professor',
    'Senior Lecturer', 'Lecturer',
    'Visiting Professor', 'In Memorium',
    'Other',
]
# 共用变量，用于生成专职非教学经历中的下拉菜单
li_worktitle_nonteach = [
    'Unknown',
    'Economist/Fellow', 'Chief Economist/Fellow',
    'Consultant/Advisory', 'Visiting Scholar', 
    'President/Vice', 'Director on Board', 'Founder', 'Chief Officer(s)',
    'Department Director',
    'Other',
]
# 公用变量，用于生成全职非教学经历中的institution type下拉菜单
li_workinstituiontype_nonteach = [
    'Unknown',
    'Government', 'Non-gov Org (NGO)', 'Commercial',
    'Other',
]
# 公用变量，用于生成全职非教学经历中的institution下拉菜单
li_workinstituion_nonteach = [
    'Unknown',
    'GOV: State House/D of Treasury', 'GOV: Security/Exchange Admin', 'GOV: Central Bank/Fed', 'GOV: Other Gov',
    'NGO: United Nations', 'NGO: World Bank', 'NGO: IMF', 'NGO: WTO', 'NGO: OECD', 'NGO: Other',
    'COM: Financial Company', 'COM: Non-financial Company',
    'Other',
]
# 共用变量，用于生成department类型的下拉菜单
li_departtype = [
    'Unknown',
    'D of Economics', 'D of Finance', 'D of Applied Econ', 'D of Agri Econ', 'D of Stats', 'Other Depart(s)',
]
# 共用变量，用于生成教育经历的学位类型
li_degreemajor = [
    'Unknown',
    'Economics', 'Applied Economics', 'Finance', 'Statistics', 'Biostatistics', 'Mathematics', 'Physics',
    'Other natural sciences', 'Other social sciences', 'Arts, literature or languages', 'Engineering',
    'Other',
]
# 共用变量，用于生成NGO名单
li_ngoname = [
    'Unknown',
    'UN & suborgans', 'IMF', 'WB', 'Fed & suborgans', 'PBC & suborgans', 'NSF & suborgans',
    'EU', 'OECD', 'WTO', 'Other',
]
# 共用变量，用于生成academy类型名单
li_academytype = [
    'Unknwon',
    'Science', 'Art', 'Art & Science', 'Social Science', 'Engineering',
    'Other',
]
# 共用变量，用于生成NBER title
li_nbertitle = [
    'Unknown',
    'Research assistant (RAssi)', 'Research associate (RAsso)', 'Faculty research fellow (FRF)',
    'Other',
]
# 共用变量，用于生成editorial头衔
li_editortitle = [
    'Unknown',
    'Editor', 'Assitant editor', 'Associate editor', 'Cheif/President editor', 'Co-editor', 'Editor on board',
    'Reviewer/Referee', 'Other',
]
# 共用变量，用于生成government department类型
li_govdeparttype = [
    'Unknown',
    'State House or equivalent',
    'Ministry/Depart of Treasury/Finance',
    'Security/Exchange authority',
    'Fed/Central banks',
    'Local government',
    'Other',
]
# 共用变量，用于生成government service的title
li_govtitle = [
    'Unknown',
    'President/Vice president',
    'Director/Officer', 
    'full-time Consultant/Advisor',
    'full-time Economist/Cheif Economist',
    'Other',
]
# 共用变量，用于生成firm类型
li_firmtype = [
    'Unknown',
    'Bank', 'Hedge Fund', 'Investment Fund', 'Private Equity Fund'
    'Consulting', 'Investment Bank',
    'Tech (e.g. AI)', 'Manufacturing', 'Agricultural',
    'Other',
]
# 共用变量，用于生成firm里担任职务的title
li_firmtitle = [
    'Unknwon',
    'Founder', 'Partner', 'CEO/COO', 'Chairman', 'Founder + CEO/Chairman',
    'CFO', 'Other Cheif(s)', 'Director/Independent Director on Board',
    'Economist/Consultant',
    'Other',
]
# 公用变量，用于生成 ngo serving 里面的title下拉菜单
li_servengotitle = [
    'Unknown',
    'Economist/Fellow', 'Chief Economist/Fellow',
    'Consultant/Advisory', 'Visiting Scholar', 
    'President/Vice', 'Director on Board', 'Founder', 'Chief Officer(s)',
    'Department Director', 'Committee Member',
    'Other',
]





















