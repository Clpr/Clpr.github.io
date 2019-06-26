# PART II: RESEARCH FIELDS
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("II. RESEARCH FIELDS 研究领域"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "研究领域通常可在该教师的院系主页或索引页找到。若没有，请在Google Scholar查找该教师的个人简历。",
    "若该教师披露的研究领域与列表选项不完全匹配，请选择最相近的选项，或联系指导教师。",
    "推荐按照披露的顺序依次填写。若领域多于3个，则对于研究领域1（必填项）请填写最能代表该教师研究的领域。"
]))


# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
tmpmat = predefvars.empty_tablematrix(3,2)
    # now, lets fill it
    # a. [1,1:2] field 1 (required)
        tmp_QuestionName = "researchfield_1"
        tmpmat[1,1] = tag_label( "Field 1" * HtmlConstructor.CONS.RedAsterisk, tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.Fields ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = true, disabled = true )) # 加一个空选项(如果问题必填)
        tmpmat[1,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = true )
    # b. [2,1:2] field 2 (not required)
    for idx in 2:3
        tmp_QuestionName = "researchfield_" * string(idx)
        tmpmat[idx,1] = tag_label( "Field " * string(idx) , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.Fields ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = true, disabled = false ))
        tmpmat[idx,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = false )
    end # idx



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_researchfield", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form

#
