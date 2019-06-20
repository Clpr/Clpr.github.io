# tags used in <head></head> part

# --------------------- <meta />s
"""
    tag_meta( charset::Union{String,Nothing} = "utf-8", lang::Union{String,Nothing} = "en-us", name::Union{String,Nothing} = "", scheme::Union{String,Nothing} = "", content::Union{String,Nothing} = "", http_equiv::Union{String,Nothing} = "")
"""
function tag_meta( ; charset::Union{String,Nothing} = "utf-8", lang::Union{String,Nothing} = "en-us",
    name::Union{String,Nothing} = nothing, scheme::Union{String,Nothing} = nothing, content::Union{String,Nothing} = nothing, http_equiv::Union{String,Nothing} = nothing)
    local tmppairedattrs = Dict{String,String}()
    isa(charset, Nothing) ? nothing : tmppairedattrs["charset"] = charset
    isa(lang, Nothing) ? nothing : tmppairedattrs["lang"] = lang
    isa(name, Nothing) ? nothing : tmppairedattrs["name"] = name
    isa(scheme, Nothing) ? nothing : tmppairedattrs["scheme"] = scheme
    isa(content, Nothing) ? nothing : tmppairedattrs["content"] = content
    isa(http_equiv, Nothing) ? nothing : tmppairedattrs["http-equiv"] = http_equiv
    return SingleHtmlTag( "meta",nothing,nothing,nothing,singleAttributes = String[], pairedAttributes = tmppairedattrs )
end # tag_meta





# ----------------------- linking external sources (dropped those attributes which are not supported by HTML5)
"""
    tag_link( rel::String, type::String, href::String ; hreflang::Union{String, Nothing} = nothing, media::Union{String, Nothing} = nothing )

creates a <link /> tag which is used in <head></head> part of the html document.
all attributed not supported by HTML5 are removed.
returns a SingleHtmlTag.

1. :rel is limited to be one of [ \"alternate\", \"author\", \"help\", \"icon\", \"licence\", \"next\", \"pingback\", \"prefetch\", \"prev\", \"search\", \"sidebar\", \"stylesheet\", \"tag\" ]
"""
function tag_link( rel::String, type::String, href::String ;
    hreflang::Union{String, Nothing} = nothing, media::Union{String, Nothing} = nothing )
    # prepare attributes
    local tmppairedattrs = Dict{String,String}(
        "rel" => add_doublequotations(rel),
        "type" => add_doublequotations(type),
        "href" => add_doublequotations(href),
    )
    isa(hreflang, Nothing) ? nothing : tmppairedattrs["hreflang"] = add_doublequotations(hreflang)
    isa(media   , Nothing) ? nothing : tmppairedattrs["media"] = add_doublequotations(media)
    return SingleHtmlTag( "link", nothing, nothing, nothing, singleAttributes = String[], pairedAttributes = tmppairedattrs )
end # tag_link







#
