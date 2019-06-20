# source of page constructor
module HtmlConstructor

    # types & low-level constructors
    export SingleHtmlTag, PairedHtmlTag, BlankHtmlTag, HtmlPage

    # basic generic methods
    export make_tag, make_page, add!, pop!
    export add_doublequotations, add_tagstr_left, add_tagstr_right, add_tagstr_single, add_tagstr_paired
    # quick tag generators
    export quicktag_blank, quicktag_single, quicktag_paired
    # comment (<!-- comment text -->)
    export comment


    # 1) tag generators: general
    # a ~ c
    export tag_a, tag_abbr, tag_b, tag_base, tag_bdo, tag_big, tag_blockquote, tag_body, tag_br, tag_button, tag_caption, tag_cite, tag_code
    # d ~ h
    export tag_del, tag_div, tag_em, tag_frame, tag_frameset, tag_h1, tag_h2, tag_h3, tag_h4, tag_h5, tag_h6, tag_head, tag_hr, tag_html
    # i ~ p
    export tag_i, tag_iframe, tag_ins, tag_kbd, tag_link, tag_meta, tag_noframes, tag_noscript, tag_object, tag_p, tag_param, tag_pre
    # q ~ v
    export tag_q, tag_samp, tag_small, tag_span, tag_strong, tag_sub, tag_sup, tag_title, tag_tt, tag_var

    # 2) tag generators: table
    export tag_col, tag_colgroup, tag_table, tag_tbody, tag_td, tag_tfoot, tag_th, tag_thead, tag_tr
    # 3) tag generators: form
    export tag_fieldset, tag_form, tag_input, tag_label, tag_legend, tag_optgroup, tag_option, tag_select, tag_textarea
    # 4) tag generators: media
    export tag_area, tag_figcaption, tag_figure, tag_img, tag_map
    # 5) tag generators: listing
    export tag_dd, tag_dfn, tag_dt, tag_dl, tag_li, tag_menu, tag_menuitem, tag_ol, tag_ul
    # 6) tag generators: deprecated
    # NOTE: not supported by HTML5 or not recommended (by W3C) to use
    export tag_acronym, tag_applet, tag_basefont, tag_center, tag_dir, tag_font, tag_s, tag_strike, tag_u
    # 7) tag generators: new features (HTML5)
    export tag_address, tag_article, tag_aside, tag_audio, tag_bdi
    export tag_canvas, tag_command, tag_datalist, tag_details, tag_dialog
    export tag_embed, tag_footer, tag_header, tag_keygen, tag_main, tag_mark, tag_meter
    export tag_nav, tag_output, tag_progress, tag_rp, tag_rt, tag_ruby
    export tag_section, tag_source, tag_summary, tag_time, tag_track
    export tag_video, tag_wbr

    # 8) tag generators: special (CSS, JS)
    export link_script, JS_str  # javascripts string
    export link_style, CS_str  # CSS style string & methods







# -------------- type definition
include("asset/CoreType.jl")

# -------------- general methods
include("asset/GeneMethods.jl")

# -------------- general tag generators
include("asset/TagGen_general.jl")















#
# # -------------- common tag generators
# include("asset/TagGenerators_common.jl")
#
# # -------------- tag generators used in forms
# include("asset/TagGenerators_form.jl")
#
# # -------------- tag generators for javascripts
# # NOTE: including some often-used realizations
# include("asset/TagGenerators_js.jl")
#
#
#
# # -------------- CSS style constructors
# include("asset/CssStyles.jl")
#
#
#
#
# # -------------- tools to construct a page (work flow)
# include("asset/PageConstructor.jl")
#
#
# # -------------- tags used in <head> part
# include("asset/TagGenerators_head.jl")


















end  # module src
#
