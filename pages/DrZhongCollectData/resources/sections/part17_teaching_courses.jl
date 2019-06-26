# PART XVII: TEACHING COURSES
# ---------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("XVII: TEACHING COURSES 教课信息"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "本节统计该教师迄今为止教授过的不同层次（本科、研究生）课程的数量。",
]))



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
# RcdNum = 5  # number of records
tmpmat = predefvars.empty_tablematrix(2,4)
    # now, lets fill it
    # ----------------------
    # 1. undergraduate courses
    tmpmat[1,1] = BlankHtmlTag("How many <b>undergraduate</b> courses did he/she teach?" * HtmlConstructor.CONS.RedAsterisk)
    tmpmat[1,2] = tag_input(name="teach_undergraduate_coursenumber",type="number",min="0",
        placeholder="please type a non-negative integer", required = true)
    # 2. graduate courses
    tmpmat[2,1] = BlankHtmlTag("How many <b>graduate</b> courses did he/she teach?" * HtmlConstructor.CONS.RedAsterisk)
    tmpmat[2,2] = tag_input(name="teach_graduate_coursenumber",type="number",min="0",
        placeholder="please type a non-negative integer", required = true)



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_teaching_courses", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form


















#
