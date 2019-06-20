# tag generators: general tags
# NOTE: StrOrTag = Union{String, AbstractHtmlTag}


# ------------------ Hyperlink/Address <a>
"""
    tag_a( href::StrOrNo, text::StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing, hreflang::StrOrNo = nothing, rel::StrOrNo = nothing, target::StrOrNo = nothing, download::StrOrNo = nothing, media::StrOrNo = nothing, type::StrOrNo = nothing )

generating paired <a>text</a> tag string, returns a `PairedHtmlTag`.
attributes not supported by HTML5 are dropped.
`download`, `media`, `type` are HTML5 features.

usage:
```julia
In> juliahlink = tag_a("www.google.com","Hi Google!")
In> println(make_tag(juliahlink)::String)
Out> <a href = "www.google.com">Hi Google!</a>
```
"""
function tag_a( href::StrOrNo, text::StrOrTag ;
    id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing,
    hreflang::StrOrNo = nothing, rel::StrOrNo = nothing, target::StrOrNo = nothing,
    download::StrOrNo = nothing, media::StrOrNo = nothing, type::StrOrNo = nothing )
    # --------
    # preprare paired attributes
    local pairedattrs = Dict{String,String}()
    # add attributes
        isa(href,Nothing) ? nothing : pairedattrs["href"] = add_doublequotations(href)
        isa(hreflang,Nothing) ? nothing : pairedattrs["hreflang"] = add_doublequotations(hreflang)
        isa(rel,Nothing) ? nothing : pairedattrs["rel"] = add_doublequotations(rel)
        isa(target,Nothing) ? nothing : pairedattrs["target"] = add_doublequotations(target)
        isa(download,Nothing) ? nothing : pairedattrs["download"] = add_doublequotations(download)
        isa(media,Nothing) ? nothing : pairedattrs["media"] = add_doublequotations(media)
        isa(type,Nothing) ? nothing : pairedattrs["type"] = add_doublequotations(type)
    # make a PairedHtmlTag
    local res = PairedHtmlTag("a", id, class, style)
    res.pairedAttributes = pairedattrs
    add!(res, text)
    return res::PairedHtmlTag
end # tag_a


# ----------------------- Abbreviation <abbr>
"""
    tag_abbr(title::StrOrNo, text::StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing )

creates an <abbr> tag, returns a `PairedHtmlTag` instance.

usage:
```julia
In[1] > tmp = tag_abbr("World Bank","WB"); println(typeof(tmp))
OUt[1] > PairedHtmlTag
In[2] > println(make_tag(tmp))
OUt[2] > <abbr title="World Bank">WB</abbr>
```
"""
function tag_abbr(title::StrOrNo, text::StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing )
    local pairedattrs = Dict{String,String}()
    # add attributes
    isa(title, String) ? pairedattrs["title"] = add_doublequotations(title) : nothing
    # make a PairedHtmlTag
    local res = PairedHtmlTag("abbr", id, class, style)
    res.pairedAttributes = pairedattrs
    add!(res, text)
    return res::PairedHtmlTag
end # tag_abbr



# ----------------------- Bold font <b>
"""
    tag_b(text::StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing )

creates <b>text</b> tag, returns a `PairedHtmlTag` instance.

usage:
```julia
In[1] > tmp = tag_b("sample text"); print(typeof(tmp))
Out[1] > PairedHtmlTag
In[2] > tmp2 = tag_b(tmp::PairedHtmlTag); println(make_tag(tmp2))
Out[2] > <b ><b > sample text </b> </b>
```
"""
tag_b(text::StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing) = begin
    local res = PairedHtmlTag("b",id,class,style); add!(res, text)
    return res::PairedHtmlTag
end # tag_b



# ---------------------- Default URL <base>
"""
    tag_base(href::String, target::StrOrNo)

creates <base href= /> tag, returns a `SingleHtmlTag` instance;
<base/> must be inside <head></head>;
`href` is required by <base> tag, but `target` is optional;
`target` can be one of: "_blank", "_parent", "_self", "_top", or a specific frame name;
if no `target` attribute needed, pls use `nothing`;

usage:
```
In[1] > tmp = tag_base("www.google.com",nothing); println(make_tag(tmp))
Out[1] > <base href="www.google.com">
In[2] > tmp = tag_base("www.google.com","_blank"); println(make_tag(tmp))
Out[2] > <base href="www.google.com" target="_blank">
```
"""
function tag_base(href::String, target::StrOrNo)
    local pairedattrs = Dict{String,String}( "href" => add_doublequotations(href) )
    isa(target, String) ? pairedattrs["target"] = add_doublequotations(target) : nothing
    local res = SingleHtmlTag("base",nothing,nothing,nothing)
    res.pairedAttributes = pairedattrs
    return res::SingleHtmlTag
end # tag_base



# ---------------------- Text Direction <bdo>
"""
    tag_bdo(content::String, dir::Str)

creates <bdo dir= ></bdo> tag, returns a `PairedHtmlTag` instance;
`dir` means direction, it should be "rtl" (right-to-left) or "ltr" (left-to-right);

usage:
```
In[1] > tmp = tag_bdo("www.google.com","rtl"); println(make_tag(tmp))
Out[1] > <bdo dir="rtl">www.google.com</bdo>
```
"""
function tag_bdo(content::String, dir::String)
    @assert( dir in ["rtl", "ltr"] , "dir should be rtl or ltr" )
    local pairedattrs = Dict{String,String}( "dir" => add_doublequotations(dir) )
    local res = PairedHtmlTag("bdo")
    res.pairedAttributes = pairedattrs
    add!(res, content)
    return res::PairedHtmlTag
end # tag_bdo



# ----------------------- Bigger font <big> (nest-able)
"""
    tag_big(text::StrOrTag)

bigger font size;
creates <big>text</big> tag, returns a `PairedHtmlTag` instance;
this tag, actually, can be nested; but not recommended.

usage:
```julia
In[1] > tmp = tag_big("sample text"); print(typeof(tmp))
Out[1] > PairedHtmlTag
In[2] > tmp2 = tag_big(tmp::PairedHtmlTag); println(make_tag(tmp2))
Out[2] > <big ><big > sample text </big> </big>
```
"""
tag_big(text::StrOrTag) = begin
    local res = PairedHtmlTag("big"); add!(res, text)
    return res::PairedHtmlTag
end # tag_big




# ----------------------- Block quotation <blockquote>
"""
    tag_blockquote(text::StrOrTag, cite::StrOrNo ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing )

Block quotation;
creates an <blockquote> tag, returns a `PairedHtmlTag` instance.
`cite` is the source of this quotation block.
please note: by default, `tag_blockquote` is not strict-XHTML.

usage:
```julia
In[1] > tmp = tag_blockquote("World Bank","www.google.com"); println(typeof(tmp))
OUt[1] > PairedHtmlTag
In[2] > println(make_tag(tmp))
OUt[2] > <abbr cite="www.google.com">World Bank</abbr>
```
"""
function tag_blockquote(text::StrOrTag, cite::StrOrNo ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing )
    local pairedattrs = Dict{String,String}()
    # add attributes
    isa(cite, String) ? pairedattrs["cite"] = add_doublequotations(cite) : nothing
    # make a PairedHtmlTag
    local res = PairedHtmlTag("blockquote", id, class, style)
    res.pairedAttributes = pairedattrs
    add!(res, text)
    return res::PairedHtmlTag
end # tag_blockquote


# -------------------------------------- New line <br/>
"""
    tag_br()

new line; returns a `SingleHtmlTag` instance;
"""
tag_br() = SingleHtmlTag("br")






# ----------------------- Button <button></button>
"""



"""
function tag_button(text::String, value::String)
    nothing



end # tag_button






































# ----------------------- horizental line & new line
tag_hr() = quickEmptySingleTag("hr")
tag_br() = quickEmptySingleTag("br")
# ----------------------- sup & sub
tag_sup(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("sup",content)
tag_sub(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("sub",content)
# ----------------------- bold font, italic, underline, del
tag_b(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("b",content)
tag_i(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("i",content)
tag_u(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("u",content)
tag_del(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("del",content)
# ----------------------- header <h1> - <h6>
tag_h1(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("h1",content)
tag_h2(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("h2",content)
tag_h3(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("h3",content)
tag_h4(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("h4",content)
tag_h5(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("h5",content)
tag_h6(content::Union{StrOrTag,Vector}) = quickEmptyPairedTag("h6",content)






# ----------------------- font block <font>
"""
    tag_font( content::StrOrTag ; color::Union{String,Nothing} = nothing, face::Union{String,Nothing} = nothing, size::Union{String,Nothing} = nothing )

add a paired font tag to your content; returns a PairedHtmlTag instance;
not recommended since HTML 4.x;
StrOrTag = Union{String, AbstractHtmlTag}.
"""
function tag_font( content::StrOrTag ; color::StrOrNo = nothing, face::StrOrNo = nothing, size::StrOrNo = nothing )
    local tmppairedattrs = Dict{String,String}()
    isa(color, Nothing) ? nothing : tmppairedattrs["color"] = add_doublequotations(color)
    isa(face , Nothing) ? nothing : tmppairedattrs["face"] = add_doublequotations(face)
    isa(size , Nothing) ? nothing : tmppairedattrs["size"] = add_doublequotations(size)
    return PairedHtmlTag( "font", nothing, nothing, nothing,
        pairedAttributes = tmppairedattrs,
        content = AbstractHtmlTag[StrOrTag2Tag(content),] )
end # tag_font


# ----------------------- division block <div>
"""
    tag_div( content::StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing )

creates a <div>content</div> tag PairedHtmlTag.
please organize your contents before packaging them in a div block.
"""
function tag_div( content::StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing )
    return PairedHtmlTag( "div", id, class, style,
        content = AbstractHtmlTag[StrOrTag2Tag(content),] )
end # tag_div




# ----------------------- Hyperlink <a>


# ----------------------- numerate list <ol>
"""
    tag_ol( items::Vector{T} where T <: StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing, type::String = "1", start::Int = 1, flag_reversed::Bool = false )

1. :type can be one of [ "A", "a", "1", "I", "i" ]
2. :items is a list of listing items
3. :start should be an integer to indicate where to start counting
4. return a PairedHtmlTag
"""
function tag_ol( items::Vector{T} where T <: StrOrTag ;
    id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing,
    type::String = "1", start::Int = 1, flag_reversed::Bool = false )
    # prepare list items
    local content::Vector = [ quickEmptyPairedTag("li", x) for x in items ]
    # new a tag instance
    return PairedHtmlTag(
        "ol", id, class, style,
            singleAttributes = String[( flag_reversed ? "reversed" : "" ),],
            pairedAttributes = Dict(
                "type" => add_doublequotations(type),
                "start" => add_doublequotations(string(start)),
            ),
            content = content
    )
end # tag_ol


# ----------------------- non-order list <ul>
"""
    tag_ul( items::Vector{T} where T <: StrOrTag ; id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing, type::StrOrNo = nothing )

1. :type can be one of [ "default" "disc", "square", "circle" ]
2. :items is a list of listing items
4. return a PairedHtmlTag
"""
function tag_ul( items::Vector{T} where T <: StrOrTag ;
    id::StrOrNo = nothing, class::StrOrNo = nothing, style::StrOrNo = nothing,
    type::StrOrNo = nothing )
    # prepare list items
    local content::Vector = [ quickEmptyPairedTag("li", x) for x in items ]
    # new a tag instance
    local tmppairedattrs::Dict = isa(type, Nothing) ? Dict{String,String}() : Dict{String,String}( "type" => add_doublequotations(type), )
    return PairedHtmlTag( "ul", id, class, style,
        pairedAttributes = tmppairedattrs, content = content )
end # tag_ol

















#
