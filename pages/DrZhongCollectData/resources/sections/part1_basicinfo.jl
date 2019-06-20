# PART I: BASIC INFORMATION
# -----------------------------------------------
# 0. first, prepare an empty div to include this section
tmpdiv = quicktag_paired("div")

# 1. header <h2>
add!(tmpdiv, tag_h2("I. BASIC INFORMATION"))
add!(tmpdiv, tag_h3("NOTE:"))
# 2. notes <ol>
add!(tmpdiv, quicktag_ol(String[
    "First name 亦称为 given name; last name 亦称为 surname",
    "若无法判断出生国家（Birth country），请使用该教师本科毕业院校所在国家填写。",
    "sex 指的是该教师的生物学性别。若无法判断，请选择Unknown。",
    "若找不到该教师的出生年份，请使用其本科毕业年份减去22作为出生年份估计。",
]))


# 3. then, we begin to make the table
# an empty table matrix (be Any to locate & replace elements)
tmpmat = predefvars.empty_tablematrix(3,6)
    # now, lets fill it
    # a. [1,1:2] first name
        tmp_QuestionName = "first_name"
        tmpmat[1,1] = tag_label( "First name" * HtmlConstructor.CONS.RedAsterisk , tmp_QuestionName )
        tmpmat[1,2] = tag_input( id = "FacultyFirstName", name = tmp_QuestionName, type = "text", placeholder = "e.g. James", required = true )
    # b. [1,3:4] middle name
        tmp_QuestionName = "middle_name"
        tmpmat[1,3] = tag_label( "Middle name", tmp_QuestionName )
        tmpmat[1,4] = tag_input( name = tmp_QuestionName, type = "text", placeholder = "e.g. Von" )
    # c. [1,5:6] last name
        tmp_QuestionName = "last_name"
        tmpmat[1,5] = tag_label( "Last name"  * HtmlConstructor.CONS.RedAsterisk , tmp_QuestionName )
        tmpmat[1,6] = tag_input( id = "FacultyLastName", name = tmp_QuestionName, type = "text", placeholder = "e.g. Bond" )
    # d. [2,1:2] current institution
        tmp_QuestionName = "current_institution"
        tmpmat[2,1] = tag_label( "Current institution"  * HtmlConstructor.CONS.RedAsterisk , tmp_QuestionName )
        tmpmat[2,2] = tag_input( id = "FacultyCurrentUniversity", name = tmp_QuestionName, class = "auto_USuniv", type = "text", placeholder = "type to search", required = true )
    # f. [2,3:4] race
        tmp_QuestionName = "race"
        tmpmat[2,3] = tag_label( "Race"  * HtmlConstructor.CONS.RedAsterisk , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.Races ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = true, disabled = true )) # 加一个空选项(如果问题必填)
        tmpmat[2,4] = quicktag_select( tmp_select, name = tmp_QuestionName, required = true )
    # g. [2,5:6] sex
        tmp_QuestionName = "sex"
        tmpmat[2,5] = tag_label( "Sex"  * HtmlConstructor.CONS.RedAsterisk , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.Sex ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = true, disabled = true )) # 加一个空选项(如果问题必填)
        tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = true )
    # h. [3,1:2] birth year
        tmp_QuestionName = "birth_year"
        tmpmat[3,1] = tag_label( "Birth year"  * HtmlConstructor.CONS.RedAsterisk , tmp_QuestionName )
        tmpmat[3,2] = templates.InputYear( 1920, 2000, name = tmp_QuestionName, width = "50%", required = true )
    # i. [3,4:5] birth country
        tmp_QuestionName = "birth_country"
        tmpmat[3,3] = tag_label( "Birth country"  * HtmlConstructor.CONS.RedAsterisk , tmp_QuestionName )
        tmpmat[3,4] = tag_input( name = tmp_QuestionName, class = "auto_country", type = "text", placeholder = "type to search", required = true )


# then, make the table tag
tmptab = quicktag_table(tmpmat, id = "tab_basicinfo", width = "100%", border = "0", cellspacing = "120%",
    style = "border-collapse:separate; border-spacing:0px 10px;" )

# finally, add the tmpdiv to the main form
add!(tmpdiv, tmptab)  # form << table
    add!(p_mainform, tmpdiv)  # div << form
#
