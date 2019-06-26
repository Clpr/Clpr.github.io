# PART XIV. SERVE: GOVERNMENT (RESEARCH/ADMINISTRATION)
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("XIV. SERVE: GOVERNMENT (RESEARCH/ADMINISTRATION) 兼职政府职务（研究或行政）"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "兼职政府职务指该教师在全职工作外还在某国政府担任兼职的学术（如顾问）或行政工作的经历。",
    "请按时间逆序填写，其余要求同前。在时间逆序的前提下，请优先填写高级职位经历。",
]))

# NOTE: 和全职的几乎完全一样

# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
RcdNum = 3  # number of records
tmpmat = predefvars.empty_tablematrix(3 * RcdNum + 1,6)
    # now, lets fill it (10 records)
    # ----------------------
    for idx in 1:RcdNum
        tmpmat[(idx*3-2):(idx*3),:] = templates.GovernmentPartTimeRecord( idx, required = false )
    end # idx
    # ---------------------- more records than asked?
    tmpmat[size(tmpmat,1),1:2] = templates.AskMoreRecord( "serve_government_morerecord" , required = true )



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_serve_government", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
