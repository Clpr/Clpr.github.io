# PART III: EDUCATION
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("III. EDUCATION"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "若该教师拥有多个同水平学位（如双博士），请优先填写经济、金融类有关学位。",
]))



# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
tmpmat = predefvars.empty_tablematrix(6,6)
    # now, lets fill it
    # ----------------------
    # a. PhD degrees
    tmpmat[1,:] = templates.EducationRecord( "phd_1", "PhD 1 institution", required = true, width = "70%" )
    tmpmat[2,:] = templates.EducationRecord( "phd_2", "PhD 2 institution", required = false, width = "70%" )
    # ----------------------
    # c. Master degrees
    tmpmat[3,:] = templates.EducationRecord( "master_1", "Master 1 institution", required = false, width = "70%" )
    tmpmat[4,:] = templates.EducationRecord( "master_2", "Master 2 institution", required = false, width = "70%" )
    # --------------------
    # d. Bachelor degree
    tmpmat[5,:] = templates.EducationRecord( "bachelor_1", "Bachelor 1 institution", required = true, width = "70%" )
    tmpmat[6,:] = templates.EducationRecord( "bachelor_2", "Bachelor 2 institution", required = false, width = "70%" )






# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_education", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
