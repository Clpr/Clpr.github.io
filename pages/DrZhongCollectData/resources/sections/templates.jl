module templates
    using HtmlConstructor
    import predefvars

# ------------------- template: more records?
AskMoreRecord( QuestionName::String ; required::Bool = false ) = begin
    local tmpmat = predefvars.empty_tablematrix(1,2)
    tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    # ----- now, fill it
    tmp_QuestionName = QuestionName
    tmpmat[1,1] = tag_label( "More records?"  * tmpstr , tmp_QuestionName )
        tmp_select = [ tag_option(x, value = x) for (x,y) in zip(["Yes","No"],[false,true]) ]
        insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
    tmpmat[1,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # AskMoreRecord


# -------------------- template: input year
InputYear( minyear::Int, maxyear::Int ; name::String = "default", width::String = "50%", required::Bool = false ) = begin
    local res = tag_input( type = "number", name = name,
        min = string(minyear), max = string(maxyear),
        placeholder = string(minyear) * " ~ " * string(maxyear), required = required,
        style = "width:" * width )
    return res
end # InputYear




# ------------------------ template: education record
EducationRecord( QuestionNamePrefix::String, InstitutionLabel::String ; required::Bool = false, width::String = "70%" ) = begin
    local tmpmat = predefvars.empty_tablematrix(1,6)  # 1 * 6 Vector{Any} prepared
    tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    # -----
    # a.1) [1,1:2] institution (required)
        tmp_QuestionName = QuestionNamePrefix * "_institution"
        tmpmat[1,1] = tag_label( InstitutionLabel  * tmpstr , tmp_QuestionName )
        tmpmat[1,2] = tag_input( name = tmp_QuestionName, class = "auto_alluniv", type = "text", placeholder = "type to search", required = required )
    # a.2) [1,3:4] major (required)
        tmp_QuestionName = QuestionNamePrefix * "_major"
        tmpmat[1,3] = tag_label( "Major"  * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.Majors ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[1,4] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # a.3) [1,5:6] graduate year (required)
        tmp_QuestionName = QuestionNamePrefix * "_gradyear"
        tmpmat[1,5] = tag_label( "Graduate year"  * tmpstr , tmp_QuestionName )
        tmpmat[1,6] = templates.InputYear( 1920, 2020, name = tmp_QuestionName, width = width, required = required )

    return tmpmat::Matrix{Any}
end


# ---------------------------- template: post-doctoral researcher
PostDocRecord( Idx::Int ; required::Bool = false ) = begin
    local tmpmat = predefvars.empty_tablematrix(1,8)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"
    local tmpprefix = "fulltime_academia_"
    # --------------- now, let`s fill it
    # a. institution
        tmp_QuestionName = tmpprefix * string(Idx) * "_institution"
        tmpmat[1,1] = tag_label( "Institution " * string(Idx) * tmpstr , tmp_QuestionName )
        tmpmat[1,2] = tag_input( name = tmp_QuestionName, class = "auto_alluniv", type = "text", placeholder = "type to search", required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[1,3] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[1,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[1,5] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[1,6] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[1,7] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x, selected = y) for (x,y) in zip(["Yes","No"],[false,true]) ]
        tmpmat[1,8] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # --------------------
    return tmpmat::Matrix{Any}
end # PostDocRecords


# ----------------------- template: full-time, academia
AcademiaFullTimeRecord( Idx::Int ; required::Bool = true ) = begin
    local tmpmat = predefvars.empty_tablematrix(3,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "fulltime_academia_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # a) title
        tmp_QuestionName = tmpprefix * string(Idx) * "_title"
        tmpmat[2,1] = tag_label( "Title " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.AcademicTitles ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b) institution
        tmp_QuestionName = tmpprefix * string(Idx) * "_institution"
        tmpmat[2,3] = tag_label( "Institution "* tmpstr , tmp_QuestionName )
        tmpmat[2,4] = tag_input( name = tmp_QuestionName, class = "auto_alluniv", type = "text", placeholder = "type to search", required = required )
    # 3) department
        tmp_QuestionName = tmpprefix * string(Idx) * "_department"
        tmpmat[2,5] = tag_label( "Department " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.AcademicDept ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[3,1] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[3,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[3,3] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[3,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[3,5] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x, selected = y) for (x,y) in zip(["Yes","No"],[false,true]) ]
        tmpmat[3,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # AcademiaFullTimeRecord








# ----------------------- template: full-time, industrial
IndustrialFullTimeRecord( Idx::Int ; required::Bool = true ) = begin
    local tmpmat = predefvars.empty_tablematrix(3,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "fulltime_industrial_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # a) title
        tmp_QuestionName = tmpprefix * string(Idx) * "_title"
        tmpmat[2,1] = tag_label( "Title " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.IndustrialTitles ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b) institution
        tmp_QuestionName = tmpprefix * string(Idx) * "_institution"
        tmpmat[2,3] = tag_label( "Institution "* tmpstr , tmp_QuestionName )
        tmpmat[2,4] = tag_input( name = tmp_QuestionName, class = nothing, type = "text", placeholder = "please type", required = required )
    # 3) institution type
        tmp_QuestionName = tmpprefix * string(Idx) * "_institutiontype"
        tmpmat[2,5] = tag_label( "Institution type " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.IndustrialInstitutionTypes ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[3,1] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[3,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[3,3] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[3,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[3,5] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x, selected = y) for (x,y) in zip(["Yes","No"],[false,true]) ]
        tmpmat[3,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # IndustrialFullTimeRecord









# ----------------------- template: full-time, government
GovernmentFullTimeRecord( Idx::Int ; required::Bool = true ) = begin
    local tmpmat = predefvars.empty_tablematrix(3,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "fulltime_government_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # a) title
        tmp_QuestionName = tmpprefix * string(Idx) * "_title"
        tmpmat[2,1] = tag_label( "Title " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.GovernmentTitles ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b) country
        tmp_QuestionName = tmpprefix * string(Idx) * "_country"
        tmpmat[2,3] = tag_label( "Country "* tmpstr , tmp_QuestionName )
        tmpmat[2,4] = tag_input( name = tmp_QuestionName, class = "auto_country", type = "text", placeholder = "type to search", required = required )
    # 3) governmental department
        tmp_QuestionName = tmpprefix * string(Idx) * "_department"
        tmpmat[2,5] = tag_label( "Department " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.GovernmentDept ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[3,1] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[3,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[3,3] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[3,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[3,5] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x, selected = y) for (x,y) in zip(["Yes","No"],[false,true]) ]
        tmpmat[3,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # AcademiaFullTimeRecord










# ----------------------- template: full-time, ngo research
NGOFullTimeRecord( Idx::Int ; required::Bool = true ) = begin
    local tmpmat = predefvars.empty_tablematrix(3,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "fulltime_ngo_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # a) title
        tmp_QuestionName = tmpprefix * string(Idx) * "_title"
        tmpmat[2,1] = tag_label( "Title " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.NGOTitles ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b) institution
        tmp_QuestionName = tmpprefix * string(Idx) * "_institution"
        tmpmat[2,3] = tag_label( "Institution "* tmpstr , tmp_QuestionName )
        tmpmat[2,4] = tag_input( name = tmp_QuestionName, class = nothing, type = "text", placeholder = "please type", required = required )
    # 3) institution type
        tmp_QuestionName = tmpprefix * string(Idx) * "_institutiontype"
        tmpmat[2,5] = tag_label( "Institution type " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.NGOTypes ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[3,1] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[3,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[3,3] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[3,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[3,5] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for (x,y) in zip(["Yes","No"],[false,true]) ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[3,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # AcademiaFullTimeRecord






# ----------------------- template: honor, academician
AcademicianRecord( Idx::Int ; required::Bool = false ) = begin
    local tmpmat = predefvars.empty_tablematrix(1,4)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "academician_"
    # ------------------
    # a. country
        tmp_QuestionName = tmpprefix * string(Idx) * "_country"
        tmpmat[1,1] = tag_label( "Country " * string(Idx) * tmpstr, tmp_QuestionName )
        tmpmat[1,2] = tag_input( name = tmp_QuestionName, class = "auto_country", type = "text", placeholder = "type to search", required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[1,3] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[1,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )

    return tmpmat::Matrix{Any}
end # AcademicianRecord



# ---------------------- template: common society & fellowship
CommonSocietyAndFellowship( SocietyName::String ; required::Bool = false ) = begin
    local tmpmat = predefvars.empty_tablematrix(4,4)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "societyandfellow_" * SocietyName
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record - " * SocietyName * tmpstr , style = "font-size:13pt;" )
    # 1) ever served?
        tmp_QuestionName = tmpprefix * "_everserved"
        tmpmat[2,1] = tag_label("Ever served or is serving " * SocietyName * "?" * tmpstr, tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for (x,y) in zip(["Yes","No"],[false,true]) ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # 2) position now?
        tmp_QuestionName = tmpprefix * "_nowposition"
        tmpmat[3,1] = tag_label("If true, what current/last position?" * tmpstr, tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.SocietyPositions ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[3,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # 3) from which year?
        tmp_QuestionName = tmpprefix * "_sinceyear"
        tmpmat[4,1] = tag_label( "From which year did he/she begin to serve? " * tmpstr , tmp_QuestionName )
        tmpmat[4,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    return tmpmat::Matrix{Any}
end # CommonSocietyAndFellowship



# -------------------------- template: other fellowship & funding
OtherFunding( Idx::Int ; required::Bool = false ) = begin
    local tmpmat = predefvars.empty_tablematrix(2,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "otherfunding_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # 1) funding type
        tmp_QuestionName = tmpprefix * "_fundtype"
        tmpmat[2,1] = tag_label( "Type " * tmpstr, tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.FundingTypes ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # 2) grant by
        tmp_QuestionName = tmpprefix * "_grantby"
        tmpmat[2,3] = tag_label( "Grant by " * tmpstr, tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.FundingGrantBy ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,4] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # 3) grant year
        tmp_QuestionName = tmpprefix * "_grantyear"
        tmpmat[2,5] = tag_label( "Grant year " * tmpstr, tmp_QuestionName )
        tmpmat[2,6] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )

    return tmpmat::Matrix{Any}
end # OtherFunding




# --------------------------- template: editorial serve
EditorialServe( Idx::Int ; required::Bool = false ) = begin
    local tmpmat = predefvars.empty_tablematrix(3,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "serve_editorial_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # a) title
        tmp_QuestionName = tmpprefix * string(Idx) * "_title"
        tmpmat[2,1] = tag_label( "Title " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.EditorialTitles ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b) journal
        tmp_QuestionName = tmpprefix * string(Idx) * "_journal"
        tmpmat[2,3] = tag_label( "Journal "* tmpstr , tmp_QuestionName )
        tmpmat[2,4] = tag_input( name = tmp_QuestionName, class = nothing, type = "text", placeholder = "please type", required = required )
    # # 3) governmental department
    #     tmp_QuestionName = tmpprefix * string(Idx) * "_institutiontype"
    #     tmpmat[2,5] = tag_label( "Institution type " * tmpstr , tmp_QuestionName )
    #         tmp_select = [ tag_option(x, value = x) for x in predefvars.NGOTypes ]
    #         insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
    #     tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[3,1] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[3,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[3,3] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[3,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[3,5] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for (x,y) in zip(["Yes","No"],[false,true]) ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[3,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # EditorialServe




# ----------------------- template: full-time, government
GovernmentPartTimeRecord( Idx::Int ; required::Bool = true ) = begin
    local tmpmat = predefvars.empty_tablematrix(3,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "serve_government_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # a) title
        tmp_QuestionName = tmpprefix * string(Idx) * "_title"
        tmpmat[2,1] = tag_label( "Title " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.GovernmentTitles ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b) country
        tmp_QuestionName = tmpprefix * string(Idx) * "_country"
        tmpmat[2,3] = tag_label( "Country "* tmpstr , tmp_QuestionName )
        tmpmat[2,4] = tag_input( name = tmp_QuestionName, class = "auto_country", type = "text", placeholder = "type to search", required = required )
    # 3) governmental department
        tmp_QuestionName = tmpprefix * string(Idx) * "_department"
        tmpmat[2,5] = tag_label( "Department " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.GovernmentDept ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[3,1] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[3,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[3,3] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[3,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[3,5] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x, selected = y) for (x,y) in zip(["Yes","No"],[false,true]) ]
        tmpmat[3,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # GovernmentPartTimeRecord




# ----------------------- template: full-time, ngo research
NGOPartTimeRecord( Idx::Int ; required::Bool = true ) = begin
    local tmpmat = predefvars.empty_tablematrix(3,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "serve_ngo_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # a) title
        tmp_QuestionName = tmpprefix * string(Idx) * "_title"
        tmpmat[2,1] = tag_label( "Title " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.NGOTitles ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b) institution
        tmp_QuestionName = tmpprefix * string(Idx) * "_institution"
        tmpmat[2,3] = tag_label( "Institution "* tmpstr , tmp_QuestionName )
        tmpmat[2,4] = tag_input( name = tmp_QuestionName, class = nothing, type = "text", placeholder = "please type", required = required )
    # 3) institution type
        tmp_QuestionName = tmpprefix * string(Idx) * "_institutiontype"
        tmpmat[2,5] = tag_label( "Institution type " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.NGOTypes ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[3,1] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[3,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[3,3] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[3,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[3,5] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for (x,y) in zip(["Yes","No"],[false,true]) ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[3,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # NGOPartTimeRecord




# ----------------------- template: full-time, industrial
IndustrialPartTimeRecord( Idx::Int ; required::Bool = true ) = begin
    local tmpmat = predefvars.empty_tablematrix(3,6)
    local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
    local tmpwidth = "70%"  # for year input
    local tmpprefix = "serve_industrial_"
    # --------------- now, let`s fill it
    # 0) mark
        tmpmat[1,1] = tag_b( "Record " * string(Idx) * tmpstr , style = "font-size:13pt;" )
    # a) title
        tmp_QuestionName = tmpprefix * string(Idx) * "_title"
        tmpmat[2,1] = tag_label( "Title " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.IndustrialTitles ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,2] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b) institution
        tmp_QuestionName = tmpprefix * string(Idx) * "_institution"
        tmpmat[2,3] = tag_label( "Institution "* tmpstr , tmp_QuestionName )
        tmpmat[2,4] = tag_input( name = tmp_QuestionName, class = nothing, type = "text", placeholder = "please type", required = required )
    # 3) institution type
        tmp_QuestionName = tmpprefix * string(Idx) * "_institutiontype"
        tmpmat[2,5] = tag_label( "Institution type " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x) for x in predefvars.IndustrialInstitutionTypes ]
            insert!(tmp_select, 1, tag_option("# please select #", value = "#", selected = required, disabled = required )) # 加一个空选项(如果问题必填)
        tmpmat[2,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    # b. since year
        tmp_QuestionName = tmpprefix * string(Idx) * "_sinceyear"
        tmpmat[3,1] = tag_label( "Since " * tmpstr , tmp_QuestionName )
        tmpmat[3,2] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. until year
        tmp_QuestionName = tmpprefix * string(Idx) * "_untilyear"
        tmpmat[3,3] = tag_label( "Until " * tmpstr , tmp_QuestionName )
        tmpmat[3,4] = InputYear( 1920, 2019, name = tmp_QuestionName, width = tmpwidth, required = required )
    # b. still ?
        tmp_QuestionName = tmpprefix * string(Idx) * "_still"
        tmpmat[3,5] = tag_label( "Still? " * tmpstr , tmp_QuestionName )
            tmp_select = [ tag_option(x, value = x, selected = y) for (x,y) in zip(["Yes","No"],[false,true]) ]
        tmpmat[3,6] = quicktag_select( tmp_select, name = tmp_QuestionName, required = required )
    return tmpmat::Matrix{Any}
end # IndustrialPartTimeRecord




# -------------------------- COURSE RECORD
# CourseRecord( CourseName::String ; required::Bool = false ) = begin
#     local tmpmat = predefvars.empty_tablematrix(1,6)
#     local tmpstr = required ? HtmlConstructor.CONS.RedAsterisk : ""  # used to mark the red star
#     local tmpwidth = "70%"  # for year input
#     local tmpprefix = "teach_" * lowercase(CourseName) * "_"
#     # --------------- now, let`s fill it
#     # 0) Course name
#         tmpmat[1,1] = tag_b( CourseName * string(Idx) * tmpstr )
#     # 1) how many times did he/she taught?
#         tmpmat[1,2] = tag_input( name = tmpprefix * "times", type = "number", min = "0", max = "" )
#
#
#     return tmpmat::Matrix
# end # CourseRecord


























end # templates
