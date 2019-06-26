# PART XI: SOCIETY & COMMON FELLOWSHIP
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("XI: SOCIETY & COMMON FELLOWSHIP 常见学术社团与非官方院士荣誉"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "NBER是美国国家经济研究局（National Bureau of Economic Research），是私人机构。",
    "Econometric Society (ES) 是国际计量经济学会。",
    "在 current/last position 问题中我们区分了NBER和ES特有的职位，请注意。",
]))



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
# RcdNum = 2  # number of records
tmpmat = predefvars.empty_tablematrix(4 * 2 + 1,4)
    # now, lets fill it (10 records)
    # ----------------------
    tmpmat[1:4,:] = templates.CommonSocietyAndFellowship( "NBER", required = true )
    tmpmat[5:8,:] = templates.CommonSocietyAndFellowship( "Econometric Society", required = true )



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_societyandfellow", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
