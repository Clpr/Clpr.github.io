# PART XVI. SERVE: INDUSTRIAL
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
RcdNum = 5  # number of records
tmpmat = predefvars.empty_tablematrix(3,3)
    # now, lets fill it (10 records)
    # ----------------------
    # a. please sign, info
    tmpmat[1,2] = tag_h4("Please signature and submit (case insensitive) " * HtmlConstructor.CONS.RedAsterisk )
    tmpmat[2,2] = tag_input(name = "signature", type = "text",
        placeholder = "e.g. James Zhang", style = "width:70%", required = true  )
    # ----------------------
    # b. submit
    tmpmat[3,2] = tag_input( type = "submit", value = "Submit", style="width:25%;height:50px;", id = "downloadasjson" )






# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_serve_industrial", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
