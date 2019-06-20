# general methods defined



## DECORATING METHODS
# -------------- string-decorating methods
add_tagstr_left(tagname::String) = "<" * tagname * ">"
add_tagstr_right(tagname::String) = "</" * tagname * ">"
add_tagstr_single(tagname::String) = "<" * tagname * "/>"
add_tagstr_paired( tagname::String, content::String ) = add_tagstr_left(tagname) * content * add_tagstr_right(tagname)
"""
    add_doublequotations( s::String )

add explicit double quotations to the given string,
e.g. add_doublequotations("fuck") --> "\"fuck\""
"""
add_doublequotations( s::String ) = begin; if s[1] == '"' == s[end]; return s::String; else; return ( "\"" * s * "\"" )::String; end; end # add_doublequotations









## QUICK TAG GENERATORS
# --------------- quick tag generators (synonyms of reloaded constructors)
"""
    quicktag_blank(content::Any)

creates a `BlankHtmlTag` according to given `content`;
the `content` will be converted to `String`.
If it cannot be stringlized, an error will be thrown
"""
quicktag_blank(content::Any) = BlankHtmlTag(string(content))
"""
    quicktag_single(tagname::String)

creates a `SingleHtmlTag` instance without any attribute.
a synonym of `SingleHtmlTag(::String)`.
"""
quicktag_single(tagname::String) = SingleHtmlTag(tagname)
"""
    quicktag_paired(tagname::String)

creates a `PairedHtmlTag` instance without any attribute.
a synonym of `PairedHtmlTag(::String)`.
"""
quicktag_paired(tagname::String) = PairedHtmlTag(tagname)














## TAG STRINGLIZATION
# -------------- general method: create tag string from a tag type instance
"""
    make_tag( d::SingleHtmlTag )

build a tag from `SingleHtmlTag` to a `String`, returns a `String`.
"""
function make_tag( d::SingleHtmlTag )
    local res::Vector = String[ "<" * d.tag, ]
    # add id, class, inline CSS style
    isa(d.id, Nothing) ? nothing : push!(res, "id=" * add_doublequotations(d.id) )
    isa(d.class, Nothing) ? nothing : push!(res, "class=" * add_doublequotations(d.class) )
    isa(d.style, Nothing) ? nothing : push!(res, "style=" * add_doublequotations(d.style) )
    # add paired attributes
    append!(res, [ key * "=" * add_doublequotations(value) for (key,value) in d.pairedAttributes ])
    # add single attributes
    append!(res, d.singleAttributes)
    # close the tag
    push!(res, "/>")
    # join the tag as a string, each part is separated by a space
    return join(res, " ")::String
end # make_tag
# ----------------------------------------------
"""
    make_tag( d::BlankHtmlTag )

build a tag from `BlankHtmlTag` to a `String`, returns a `String`.
"""
make_tag( d::BlankHtmlTag ) = return (d.content)::String
# ----------------------------------------------
"""
    make_tag( d::PairedHtmlTag )

build a tag from `PairedHtmlTag` to a `String`, returns a `String`.
"""
function make_tag( d::PairedHtmlTag )
    local res::Vector = String[ "<" * d.tag, ]
    # add id, class, inline CSS style
    isa(d.id, Nothing) ? nothing : push!(res, "id=" * add_doublequotations(d.id) )
    isa(d.class, Nothing) ? nothing : push!(res, "class=" * add_doublequotations(d.class) )
    isa(d.style, Nothing) ? nothing : push!(res, "style=" * add_doublequotations(d.style) )
    # add paired attributes
    append!(res, [ key * "=" * add_doublequotations(value) for (key,value) in d.pairedAttributes ])
    # add single attributes
    append!(res, d.singleAttributes)
    # close the tag
    push!(res, ">")
    # add contents between paired tags & the right tag
    if length(d.content) == 0
        # if there is no content, just skip it
        nothing
    elseif (length(d.content) == 1)
        # if there is only one element, str-lize it
        push!(res, make_tag(d.content[1]))
    else
        # if there is more than one element in the tag`s content, loop and/or recursive stringlize all elements
        for tmptag in d.content
            if isa(tmptag, BlankHtmlTag)
                push!(res, tmptag.content)
            elseif isa(tmptag, SingleHtmlTag)
                push!(res, make_tag(tmptag))
            else
                push!(res, make_tag(tmptag)) # NOTE: recursive calling
            end
        end
    end
    # add </tag>
    push!(res, add_tagstr_right(d.tag) )
    # join the tag as a string, each part is separated by a space
    return join(res, " ")::String
end # make_tag













## TAG OPERATIONS: add sub tag elements to PairedHtmlTag instance
# ------------------------------ add element to a paired tag`s content
"""
    add!( suptag::PairedHtmlTag, subtag::AbstractHtmlTag )

add a new sub-tag member to a given paired tag instance.
"""
function add!( suptag::PairedHtmlTag, subtag::AbstractHtmlTag )
    push!(suptag.content, subtag)
end # add
# ------------------------------ reload add! to add String
"""
    add!( suptag::PairedHtmlTag, subtag::String )

add a new sub-tag member (in the form of string) to a given paired tag instance.
"""
function add!( suptag::PairedHtmlTag, subtag::String )
    push!(suptag.content, BlankHtmlTag(subtag) )
end # add
# ------------------------------ reload add! to allow vector input
"""
    add!( suptag::PairedHtmlTag, v_subtag::Vector )

add a list of new sub-tag members to a given paired tag instance.
if there are non-stringlizable elements, an error will be thrown by `Base.string()`
"""
function add!( suptag::PairedHtmlTag, v_subtag::Vector )
    for x in v_subtag
        if isa(x, AbstractHtmlPage)
            add!(suptag, x );
        elseif isa(x, String)
            add!(suptag, x)
        else
            add!(suptag, string(x))
        end # if
    end # loop x
end # add



## TAG OPERATIONS: drop (pop) sub tag elements from PairedHtmlTag instance
# ------------------------------ pop! reload for tag types
"""
    pop!( d::PairedHtmlTag, k::Int )

deletes the item with key (index) `k` in the `content` attribute of a `PairedHtmlTag`,
and returns the value associated with `k`.
"""
pop!( d::PairedHtmlTag, k::Int ) = pop!(d.content, k)::AbstractHtmlTag






## SPECIAL TAG: commenting
# ------------------------------
"""
    comment(cmttxt::String)

comment tag, returns a `BlankHtmlTag` with content: "<!-- cmttxt -->"
"""
function comment(cmttxt::String)
    return BlankHtmlTag( "<!-- " * cmttxt * " -->" )
end # comment




#
