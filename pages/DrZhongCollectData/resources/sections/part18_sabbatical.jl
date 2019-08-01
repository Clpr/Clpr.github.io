# PART XVIII. SABBATICAL
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("XVIII. SABBATICAL 学术休假"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "学术休假指处于一份全职学术工作中的教师暂时离开大学或研究机构，休假、去其他学校做Visiting Professor或前往业界任职，然后返回原本大学继续工作的经历。",
]))



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
RcdNum = 5  # number of records
tmpmat = predefvars.empty_tablematrix(3 * RcdNum + 1,6)
    # now, lets fill it (5 records)
    # ----------------------
    for idx in 1:RcdNum
        tmpmat[(idx*3-2):(idx*3),:] = templates.SabbaticalRecord( idx, required = false )
    end # idx
    # ---------------------- more records than asked?
    tmpmat[size(tmpmat,1),1:2] = templates.AskMoreRecord( "sabbatical_morerecord" , required = true )






# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_sabbatical", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
