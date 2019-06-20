# tags used in <form></form>



# ----------------------- form block <form>
"""
    tag_form( content::String ; id::String = "", class::String = "", style::String = "" )

creates a <form>content</form> tag string.
please organize your contents before packaging them in a form block.
"""
function tag_form( content::String ; id::String = "", class::String = "", style::String = "" )
    return PairedHtmlTag( "form", id, class, style, String[], Dict(), content )
end # tag_form




# -------------------- typical tags generating functions
# input: 文本类型（用于一般输入）
"""
    tag_input_text( name::String ; id::String = "id_" * name, class::String = "", style::String = "", placeholder::String = "please type", flag_required::Bool = false, flag_readonly::Bool = false, flag_disabled::Bool = false )
"""
function tag_input_text( name::String ;
    id::String = "id_" * name, class::String = "", style::String = "",
    placeholder::String = "please type",
    flag_required::Bool = false, flag_readonly::Bool = false, flag_disabled::Bool = false )
    # prepare single attributes
    local singleattrs = [
        ( flag_required ? "required" : "" ),
        ( flag_readonly ? "readonly" : "" ),
        ( flag_disabled ? "disabled" : "" ),
    ]
    # prepare paired attributes
    local pairedattrs = Dict(
        "placeholder" => add_doublequotations(placeholder),
        "type" => add_doublequotations("text"),
    )
    # new a SingleHtmlTag
    return SingleHtmlTag("input", id, class, style, singleattrs, pairedattrs)
end # tag_input_text

# -------------
# input: 数字类型（用于年份等）
"""
    tag_input_number( name::String ; id::String = "id_" * name, class::String = "", style::String = "", num_range::Union{Vector{T},Tuple{T,T}} where T <: Real = (1920,2019), placeholder::String = "please type", flag_required::Bool = false, flag_readonly::Bool = false, flag_disabled::Bool = false )
"""
function tag_input_number( name::String ;
    id::String = "id_" * name, class::String = "", style::String = "",
    num_range::Union{Vector{T},Tuple{T,T}} where T <: Real = (1920,2019),
    placeholder::String = "type a number in $(num_range[1]) ~ $(num_range[2])",
    flag_required::Bool = false, flag_readonly::Bool = false, flag_disabled::Bool = false )
    # validation: num_range
    if isa(num_range,Vector); @assert( length(num_range) == 2, "num_range is allowed to have 2 elements" ); end;
    # prepare single attributes
    local singleattrs = [
        ( flag_required ? "required" : "" ),
        ( flag_readonly ? "readonly" : "" ),
        ( flag_disabled ? "disabled" : "" ),
    ]
    # prepare paired attributes
    local pairedattrs = Dict(
        "min" => string(num_range[1]),
        "max" => string(num_range[1]),
        "placeholder" => add_doublequotations(placeholder),
        "type" => add_doublequotations("number"),
    )
    # new a SingleHtmlTag string
    return SingleHtmlTag("input", id, class, style, singleattrs, pairedattrs)
end # tag_input_text

# -------------
# input: 单选题目(radio) NOTE: 返回的是一个<input /> string列表
"""
    tag_input_radio( name::String, options::Dict{T,String} where T <: Any ; label_id::String = "id_labelfor_" * name, label_class::String = "", label_style::String = "", id::String = "id_" * name, class::String = "", style::String = "", whichlabel_checked::Union{String,Nothing} = nothing )

1. :options should be a Dict whose keys are the contents displayed as label, and the values are the "value" attribute recorded in <input value="">
2. returns a **LIST** of PairedHtmlTag
"""
function tag_input_radio( name::String,
    options::Dict{T,String} where T <: Any ; # label text => radio (input) value
    label_id::String = "id_labelfor_" * name, label_class::String = "", label_style::String = "", # attributes of out-layer <label></label> tag
    id::String = "id_" * name, class::String = "", style::String = "", # attributes of inner <input /> tag
    whichlabel_checked::Union{String,Nothing} = nothing )  # which one (label text) (1st, 2nd ...) option should be checked by default
    # -------------
    # a tag list
    local res = PairedHtmlTag[]
    # make tags
    for labelstr in keys(options)
        local tmpSingleAttr4input::Vector{String} = whichlabel_checked == labelstr ? String["checked",] : String[]
        local in_radiotag = new_tag(SingleHtmlTag( "input",
            id, class, style, tmpSingleAttr4input,
            Dict(
                "type" => add_doublequotations("radio"),
                "value" => add_doublequotations(options[labelstr]),
            )
        ))
        local out_labtag = PairedHtmlTag( "label",
            label_id, label_class, label_style, [], Dict(),
            labelstr * in_radiotag )
        push!(res, out_labtag)
    end # labelstr
    return res::Vector{PairedHtmlTag}
end


# -------------
# input: 复选框(checkbox)
"""
    tag_input_checkbox( name::String, options::Dict{T,String} where T <: Any ; label_id::String = "id_labelfor_" * name, label_class::String = "", label_style::String = "", id::String = "id_" * name, class::String = "", style::String = "", whichlabel_checked::Union{String,Nothing,Vector{String}} = nothing )
"""
function tag_input_checkbox( name::String,
    options::Dict{T,String} where T <: Any ; # label text => radio (input) value
    label_id::String = "id_labelfor_" * name, label_class::String = "", label_style::String = "", # attributes of out-layer <label></label> tag
    id::String = "id_" * name, class::String = "", style::String = "", # attributes of inner <input /> tag
    whichlabel_checked::Union{String,Nothing,Vector{String}} = nothing )  # which (label text) (1st, 2nd ...) option(s) should be checked by default
    # -------------
    # a tag list
    local res = PairedHtmlTag[]
    # make tags
    for labelstr in keys(options)
        local tmpSingleAttr4input::Vector{String} = String[]
        if isa(whichlabel_checked, String)
            if whichlabel_checked == labelstr; push!(tmpSingleAttr4input, "checked"); end;
        elseif isa(whichlabel_checked, Vector)
            if labelstr in whichlabel_checked; push!(tmpSingleAttr4input, "checked"); end;
        end
        local in_radiotag = new_tag(SingleHtmlTag( "input",
            id, class, style, tmpSingleAttr4input,
            Dict(
                "type" => add_doublequotations("checkbox"),
                "value" => add_doublequotations(options[labelstr]),
            )
        ))
        local out_labtag = PairedHtmlTag( "label",
            label_id, label_class, label_style, [], Dict(),
            labelstr * in_radiotag )
        push!(res, out_labtag)
    end # labelstr
    return res::Vector{PairedHtmlTag}
end # tag_input_checkbox







# -------------
# select: 下拉框





# -------------
# datalist: 下拉框(用于<input>的list=属性，list=后面跟datalist的id)，即可复用的select














#
