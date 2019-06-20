# dependency lib
module src
    import predefvars



# -------------- CONSTANTS
const CONSTSTR = Dict{String,String}(
    "redstar" => """ <font color="red">*</font> """,
)
# -------------- small methods
add_quotes(x::String) = "\"" * x * "\""
# -------------- make options



# -------------- TEMPLATE: EDUCATION RECORD 教育经历模板
function record_edu( univ_name::String, question_id::String ; class::String = ".auto_alluniv", required::Bool = false )
    return """
    <tr>
        <td>$(univ_name)$(required ? CONSTSTR["redstar"] : nothing)</td>
        <td>Major$(required ? CONSTSTR["redstar"] : nothing)</td>
        <td>Graduate year$(required ? CONSTSTR["redstar"] : nothing)</td>
    </tr>
    <tr>
        <td><input type="text" name=$(add_quotes(question_id * "_")) class=$(add_quotes(class)) placeholder="type to search..." $(required ? "required" : nothing)></td>
        <td></td>
        <td><input type="number" name=></td>
    </tr>
    """::String
end # record_edu









end # src