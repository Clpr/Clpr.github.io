# PART VIIII: HONOR: ACADEMICIAN
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("IX. HONOR: NOBEL LAUREATE 诺贝尔奖"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "该节调查该教师是否为诺贝尔经济学奖获得者。",
]))

# 3. then, begin to fill the table
tmpmat = predefvars.empty_tablematrix(2,2)
    # a. is this faculty member a Nobel Laureate? (required)
        tmp_QuestionName = "nobel_flag_owner"
        tmpmat[1,1] = tag_label( "Is this faculty member a Nobel Laureate?" * HtmlConstructor.CONS.RedAsterisk, tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for (x,y) in zip(["Yes","No"],[false,true]) ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = true, disabled = true )) # 加一个空选项(如果问题必填)
        tmpmat[1,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = true )
    # b. which year?
        tmp_QuestionName = "nobel_grantyear"
        tmpmat[2,1] = tag_label( "If true, which year was he/she granted?", tmp_QuestionName )
        tmpmat[2,2] = templates.InputYear( 1920, 2019, name = tmp_QuestionName, width = "70%", required = false )

# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_nobel", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form




# ==============================
# ==============================
# ==============================
# ==============================





# PART X: HONOR: ACADEMICIAN
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("X. HONOR: ACADEMICIAN 官方院士荣誉"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "官方院士指各国官方科学院（如中科院、社科院、美国科学院等）颁发的院士头衔荣誉，不同于学术社团的院士（fellow）。",
    "若该教师同时为同一国家多个科学院的院士，则按照两个国家处理，请分别填写两条记录。另外，请优先填写大国的院士荣誉。",
    "英国及其他拥有类似于“<b>皇家</b>XX学会”的，按照官方院士处理。",
]))


# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
RcdNum = 5  # number of records
tmpmat = predefvars.empty_tablematrix(2 + 1 * RcdNum + 1,4)
    # now, lets fill it (10 records)
    # ----------------------
    # a. is this faculty member an academician? (required)
        tmp_QuestionName = "academician_flag"
        tmpmat[1,1] = tag_label( "Is this faculty member an academician of any country?" * HtmlConstructor.CONS.RedAsterisk, tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for (x,y) in zip(["Yes","No"],[false,true]) ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = true, disabled = true )) # 加一个空选项(如果问题必填)
        tmpmat[1,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = true )
    # b. information
        tmpmat[2,1] = quicktag_paired("p", content = "If true, please list all these countries:")
    # ---------------------- records
    for idx in 1:RcdNum
        tmpmat[2+idx,:] = templates.AcademicianRecord( idx, required = false )
    end # idx
    # ---------------------- more records than asked?
    tmpmat[size(tmpmat,1),1:2] = templates.AskMoreRecord( "academician_morerecord" , required = true )



# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_academician", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
