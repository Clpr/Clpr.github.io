# included by src.jl
# core types used in html constructing



# ------------------- type tree
abstract type AbstractHtmlType <: Any end
abstract type AbstractHtmlTag <: AbstractHtmlType end
abstract type AbstractHtmlPage <: AbstractHtmlType end


# ------------------- public constants
const CONS = (
    RedAsterisk = "<font color=red>*</font>", # red asterisk for required terms
    AllTags = String[ "a", "abbr", "acronym", "address", "applet",
            "area", "article", "aside", "audio", "b", "base", "basefont", "bdi",
            "bdo", "big", "blockquote", "body", "br", "button", "canvas", "caption",
            "center", "cite", "code", "col", "colgroup", "command", "datalist", "dd",
            "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt", "em", "embed",
            "fieldset", "figcaption", "figure", "font", "footer", "form", "frame",
            "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hr", "html", "i",
            "iframe", "img", "input", "ins", "kbd", "keygen", "label", "legend",
            "li", "link", "main", "map", "mark", "menu", "menuitem", "meta", "meter",
            "nav", "noframes", "noscript", "object", "ol", "optgroup", "option",
            "output", "p", "param", "pre", "progress", "q", "rp", "rt", "ruby",
            "s", "samp", "script", "section", "select", "small", "source", "span",
            "strike", "strong", "style", "sub", "summary", "sup", "table", "tbody",
            "td", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track",
            "tt", "u", "ul", "var", "video", "wbr", ],  # all tags allowed
)




# ------------------- synonym def
StrOrTag = Union{String,AbstractHtmlTag}
StrOrNo = Union{String,Nothing}
HtmlTagVector = Vector{T} where T <: AbstractHtmlTag
# ------------------- contentizable
Contentizable = Union{String,AbstractHtmlTag}







# ------------------- 成对标签 paired tag: <tag>content</tag>
"""
    PairedHtmlTag <: AbstractHtmlTag

core type (mutable) for paired html tags, e.g. <font></font>;
with attributes:
1. tag::String  # tag name, e.g. table, head
2. id::StrOrNo  # tag id
3. class::StrOrNo  # tag class applied
4. style::StrOrNo  # CSS style
5. singleAttributes::Vector{String}  # single attribute, e.g. required
6. pairedAttributes::Dict{String,String}  # paired attributes, e.g. min=2000, width=\"100\"
7. content::HtmlTagVector  # content between <tag> and </tag>

The constructor of this type is designed that only 1-4 attributes are allowed to be initialized
when newing an instance. 5, 6 and 7 need to be added/modified separately.
I believe this helps your code be more readale.
"""
mutable struct PairedHtmlTag <: AbstractHtmlTag
    tag::String  # tag name, e.g. table, head
    # ------------- basic attributes (required)
    id::StrOrNo  # tag id
    class::StrOrNo  # tag class applied
    style::StrOrNo  # CSS style
    # ------------- other single attributes (tag-specific)
    singleAttributes::Vector{String}  # e.g. required
    # ------------- other "=" attributes
    pairedAttributes::Dict{String,String}  # e.g. min=2000, width=\"100\"
    # ------------- contents/texts between two paired tags
    content::HtmlTagVector
    # -------------
    """
        PairedHtmlTag(tag::String, id::StrOrNo, class::StrOrNo, style::StrOrNo)

    constructor of type `PairedHtmlTag`. `StrOrNo = Union{String,Nothing}`
    """
    function PairedHtmlTag(tag::String, id::StrOrNo, class::StrOrNo, style::StrOrNo)
        @assert( tag in CONS.AllTags, "unknown tag" )
        local singleAttributes::Vector{String} = String[]
        local pairedAttributes::Dict{String,String} = Dict{String,String}()
        local content::HtmlTagVector = AbstractHtmlTag[]
        new(tag,id,class,style,singleAttributes,pairedAttributes,content)
    end
end
"""
    PairedHtmlTag(tag::String)

reloaded constructor which creates a `PairedHtmlTag` instance without any attribute.
"""
PairedHtmlTag(tag::String) = PairedHtmlTag(tag,nothing,nothing,nothing)



# ------------------- 单个标签 Single tag: <tag />
"""
    SingleHtmlTag <: AbstractHtmlTag

core type (mutable) for single html tags which do not have contents, e.g. <br /> (XHTML style);
with attributes:
1. tag::String  # tag name, e.g. table, head
2. id::StrOrNo  # tag id
3. class::StrOrNo  # tag class applied
4. style::StrOrNo  # CSS style
5. singleAttributes::Vector{String}  # single attribute, e.g. required
6. pairedAttributes::Dict{String,String}  # paired attributes, e.g. min=2000, width=\"100\"

The constructor of this type is designed that only 1-4 attributes are allowed to be initialized
when newing an instance. 5, 6 and 7 need to be added/modified separately.
I believe this helps your code be more readale.
"""
mutable struct SingleHtmlTag <: AbstractHtmlTag
    tag::String  # tag name, e.g. table, head
    id::StrOrNo  # tag id
    class::StrOrNo  # tag class applied
    style::StrOrNo  # CSS style
    singleAttributes::Vector{String}  # single attribute, e.g. required
    pairedAttributes::Dict{String,String}  # paired attributes, e.g. min=2000, width=\"100\"
    # -------------
    """
        SingleHtmlTag(tag::String, id::StrOrNo, class::StrOrNo, style::StrOrNo)

    constructor of type `SingleHtmlTag`. `StrOrNo = Union{String,Nothing}`
    """
    function SingleHtmlTag(tag::String, id::StrOrNo, class::StrOrNo, style::StrOrNo)
        @assert( tag in CONS.AllTags, "unknown tag" )
        singleAttributes::Vector{String} = String[]
        pairedAttributes::Dict{String,String} = Dict{String,String}()
        new(tag,id,class,style,singleAttributes,pairedAttributes)
    end
end
"""
    SingleHtmlTag(tag::String)

reloaded constructor which creates a `SingleHtmlTag` instance without any attribute.
"""
SingleHtmlTag(tag::String) = SingleHtmlTag(tag,nothing,nothing,nothing)



# -------------------- 空白tag：blank tag, (a placeolder for pure string contents)
"""
    BlankHtmlTag <: AbstractHtmlTag

a nominal tag type for pure-text html components.
It has only one attribute: content::String
"""
struct BlankHtmlTag <: AbstractHtmlTag
    content::String
end



# -------------------- HTML page (.html file)
"""
    HtmlPage <: AbstractHtmlPage

type to define an HTML page file. including attributes:
1. filename::String # file name when saved
2. pagetitle::String # page title displayed on browser's status bar
3. lang::String # language, "en-us" by default
4. charset::String # <meta charset = "utf-8" /> by default
5. head::Vector{AbstractHtmlTag} # a list of the elements in the <head> part
6. body::Vector{AbstractHtmlTag} # a list of the elements in the <body> part, ordered
"""
mutable struct HtmlPage <: Any
    filename::String # file name when saved
    pagetitle::String # page title displayed on browser's status bar
    lang::String # language, "en-us" by default
    charset::String # <meta charset = "utf-8" /> by default
    head::Vector{AbstractHtmlTag} # a list of the elements in the <head> part
    body::Vector{AbstractHtmlTag} # a list of the elements in the <body> part, ordered
    # ---------------------------
    """
        HtmlPage( ; filename::String = "index.html", pagetitle::String = "main", lang::String = "en-us", charset::String = "utf-8" )

    constructor of type `HtmlPage`;
    receives no location argument but several keyword arguments;
    """
    function HtmlPage( ; filename::String = "index.html",
        pagetitle::String = "main", lang::String = "en-us",
        charset::String = "utf-8" )
        new(filename,pagetitle,lang,charset,AbstractHtmlTag[],AbstractHtmlTag[])
    end
end
















#
