# PART XII: OTHER FUNDING
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("XII: OTHER FUNDING/SUPPORT/FELLOWSHIP/AWARD"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "其他学术资金来源。",
    "NSF是国家科学基金，指某国<b>官方</b>设立的科学资助机构。此处代指所有具有政府背景的科学资助基金。",
    "Academy funding指各国科学院/社科院等提供的科学资助基金。",
]))



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
RcdNum = 10  # number of records
tmpmat = predefvars.empty_tablematrix(2 * RcdNum + 1,6)
    # now, lets fill it (10 records)
    # ----------------------
    for idx in 1:RcdNum
        tmpmat[(idx*2-1):(idx*2),:] = templates.OtherFunding( idx, required = false )
    end # idx
    # ---------------------- more records than asked?
    tmpmat[size(tmpmat,1),1:2] = templates.AskMoreRecord( "otherfunding_morerecord" , required = true )



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_otherfunding", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
