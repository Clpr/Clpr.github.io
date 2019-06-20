    push!(LOAD_PATH,pwd())
    using HtmlConstructor


# ------------------- 初始化一个页面实例
page = HtmlPage(filename = "NewProfile.html")

# ------------------- 填充头部
# tmp_head = 