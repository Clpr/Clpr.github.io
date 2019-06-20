# PART IV: POST DOCTORAL
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("IV. FULL-TIME: POST-DOCTORAL RESEARCHER"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "博士后（post-doctoral）。",
]))



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
RcdNum = 3  # number of records
tmpmat = predefvars.empty_tablematrix(1 * RcdNum + 1,8)
    # now, lets fill it (3 records)
    # ----------------------
    for idx in 1:RcdNum
        tmpmat[idx,:] = templates.PostDocRecord( idx, required = false )
    end # idx
    # ---------------------- more records than asked?
    tmpmat[size(tmpmat,1),1:2] = templates.AskMoreRecord( "fulltime_postdoc_morerecord" , required = true )



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_fulltime_postdoc", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
