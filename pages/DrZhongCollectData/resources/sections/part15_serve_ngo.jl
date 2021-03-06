# PART XV. SERVE: NGO RESEARCH
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("XV. SERVE: NGO RESEARCH 兼职非政府组织经历"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "兼职非政府组织经历指该教师全职工作外，兼职于非政府组织（如UN、美联储Fed等）的经历。",
    "请按照时间逆序填写，其余要求同前。在时间逆序前提下，请优先填写高级职位。",
]))



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
RcdNum = 5  # number of records
tmpmat = predefvars.empty_tablematrix(3 * RcdNum + 1,6)
    # now, lets fill it (10 records)
    # ----------------------
    for idx in 1:RcdNum
        tmpmat[(idx*3-2):(idx*3),:] = templates.NGOPartTimeRecord( idx, required = false )
    end # idx
    # ---------------------- more records than asked?
    tmpmat[size(tmpmat,1),1:2] = templates.AskMoreRecord( "serve_ngo_morerecord" , required = true )



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_serve_ngo", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
