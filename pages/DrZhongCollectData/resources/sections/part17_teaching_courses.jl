# PART XVII: TEACHING COURSES
# ---------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("XVII: TEACHING COURSES 教课信息"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "本节统计该教师迄今为止教授过的不同层次的课程，若至少教授过一次，请勾选复选框。",
]))



# 3. then, we begin to make the table, providing a list of courses
tmpmat = templates.CourseRecord( predefvars.Courses )



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_teaching_courses", width = "100%",
    border = "1", cellspacing = "120%" )
    # style = "border-collapse:collapse; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form


















#
