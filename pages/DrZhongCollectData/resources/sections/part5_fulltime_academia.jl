# PART V: FULL-TIME: ACADEMIA
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("V. FULL-TIME: ACADEMIA"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "全职教学类工作。",
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
