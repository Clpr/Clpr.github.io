# tag generators for js scripts





# ----------------------- JS <script> block
"""
    tag_script( script::String ; type::String = add_doublequotations("text/javascript") )
"""
function tag_script( script::String ; type::String = "text/javascript" )
    local tmptype::String = ( type[1] == '\"' ? type : add_doublequotations(type)  )
    return PairedHtmlTag( "script", nothing, nothing, nothing,
        singleAttributes = String[],
        pairedAttributes = Dict{String,String}("type" => tmptype),
        content = [BlankHtmlTag(script),] )
end # tag_script




# ------------------------ JS script string
"""
    JS_str(script)

define a <script>js code input</script> string,
which returns a string.
e.g. JS\"\"\" var a = 2; \"\"\" --> " <script> var a = 2; </script> "
"""
macro JS_str(script)
    return quote
        tag_script( "\n" * string($script) * "\n" )
    end
end # JS_str




#
