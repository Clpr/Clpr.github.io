# PART V: FULL-TIME: ACADEMIA
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("V. FULL-TIME: ACADEMIA 全职学术类经历"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "全职学术类经历指该教师全职在某大学或其他机构担任教授等常规职位的工作经历。",
    "请按照时间逆序填写，第一条记录（Record 1）应当为该教师在 Current Institution 的正在进行的工作。",
    "若该教师的此类经历多于10个，请在仍按时间逆序的前提下，优先填写不是 visiting（访问）的经历，以及优先填写高级职称的经历（如：教授经历优先于副教授经历）",
]))



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
RcdNum = 10  # number of records
tmpmat = predefvars.empty_tablematrix(3 * RcdNum + 1,6)
    # now, lets fill it (3 records)
    # ----------------------
    for idx in 1:RcdNum
        tmpmat[(idx*3-2):(idx*3),:] = templates.AcademiaFullTimeRecord( idx, required = ( idx == 1 ? true : false ) )
    end # idx
    # ---------------------- more records than asked?
    tmpmat[3 * RcdNum + 1,1:2] = templates.AskMoreRecord( "fulltime_academia_morerecord" , required = true )



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_fulltime_academia", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
