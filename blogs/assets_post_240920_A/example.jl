import Plots as plt
import Interpolations as itp
import Statistics as stat
asg = include("/Users/tianhaozhao/Library/CloudStorage/Dropbox/AdaptiveSG/src/AdaptiveSG.jl")

# ------------------------------------------------------------------------------
function f2fit(X::AbstractVector)::Float64
    return -1.0 / (0.1 + sum(abs.(X)))
end
# ------------------------------------------------------------------------------
# EXAMPLE: 1D case
let
    RTOL = 1E-2
    G = asg.AdaptiveSparseGrid{1}(20, rtol = RTOL, atol = RTOL, use_rtol = true)
    asg.train!(
        G,
        f2fit,
    )

    Xtest    = LinRange(0.0,1.0,100)
    allNodes = asg.vectorize_x(G)


    # compare with regular linear interpolation
    tmp = 1:51
    fpli = itp.linear_interpolation(
        tmp,
        [f2fit([(x-1)/tmp[end-1],]) for x in tmp],
        extrapolation_bc = itp.Line()
    )


    Figs = plt.Plot[]

    # fig 01: interpolant vs. original
    _fig = plt.plot(
        Xtest, [f2fit([x]) for x in Xtest],
        label = "True function",
        color = :black,
        linestyle = :dash,
        linewidth = 2,
        legend = :bottomright,
        xlabel = "x",
        ylabel = "f(x)",
        title = "#nodes = $(length(allNodes))",
    )
    plt.plot!(_fig,
        Xtest, 
        [asg.evaluate(G, [x,]) for x in Xtest],
        label = "ASG interpolant",
        color = :red,
        linewidth = 2,
        linestyle = :solid,
    )
    plt.scatter!(_fig,
        allNodes[:,1],
        asg.vectorize_nodal(G),
        label = "Supporting nodes",
        color = :blue,
        marker = :circle,
        markersize = 3,
    )
    push!(Figs, _fig)


    # fig 02: relative error
    _fig = plt.plot(
        Xtest, 
        [abs(f2fit([x]) - asg.evaluate(G, [x,])) / abs(f2fit([x])) * 100 for x in Xtest],
        # [abs(f2fit([x]) - asg.evaluate(G, [x,])) * 100 for x in Xtest],
        color = :red,
        linewidth = 2,
        linestyle = :solid,
        xlabel = "x",
        ylabel = "Relative error (%)",
        legend = :best,
        label = "relative error",
        title = "Interpolation error",
    )
    plt.hline!(_fig,
        [RTOL * 100,],
        color = :blue,
        label = "tolerance",
        linestyle = :dash,
    )
    push!(Figs, _fig)


    # fig 03: regular linear interpolation
    _fig = plt.plot(
        Xtest, [f2fit([x]) for x in Xtest],
        label = "True function",
        color = :black,
        linestyle = :dash,
        linewidth = 2,
        legend = :bottomright,
        xlabel = "x",
        ylabel = "f(x)",
        title = "#nodes = $(length(tmp))",
    )
    plt.plot!(_fig,
        Xtest, 
        x01 -> fpli( x01 * tmp[end-1] + 1 ),
        label = "Piecewise Linear interpolant",
        color = :red,
        linewidth = 2,
        linestyle = :solid,
    )
    plt.scatter!(_fig,
        (tmp .- 1) ./ tmp[end-1],
        x01 -> fpli( x01 * tmp[end-1] + 1 ),
        label = "Supporting nodes",
        color = :blue,
        marker = :circle,
        markersize = 3,
    )
    push!(Figs, _fig)

    # fig 04: relative error
    _fig = plt.plot(
        Xtest, 
        [abs(f2fit([x]) - fpli( x * tmp[end-1] + 1 )) / abs(f2fit([x])) * 100 for x in Xtest],
        # [abs(f2fit([x]) - fpli( x * tmp[end-1] + 1 )) * 100 for x in Xtest],
        color = :red,
        linewidth = 2,
        linestyle = :solid,
        xlabel = "x",
        ylabel = "Relative error (%)",
        legend = :best,
        label = "relative error",
        title = "Interpolation error",
    )
    plt.hline!(_fig,
        [RTOL * 100,],
        color = :blue,
        label = "tolerance",
        linestyle = :dash,
    )
    push!(Figs, _fig)



    fig = plt.plot(Figs..., layout = (2,2), size = 400 .* (2,2))

    plt.savefig(fig, "example_1D.svg")
end # 1D case





# ------------------------------------------------------------------------------
# EXAMPLE: 2D case
let
    RTOL = 1E-2
    G = asg.AdaptiveSparseGrid{2}(20, rtol = RTOL, atol = RTOL, use_rtol = true)
    asg.train!(
        G,
        f2fit,
    )

    Xtest    = LinRange(0.0,1.0,100)
    allNodes = asg.vectorize_x(G)


    # compare with regular linear interpolation
    tmpX   = 1:51
    tmpX01 = (tmpX .- 1) ./ tmpX[end-1]
    tmpF   = [
        f2fit([
            (x-1)/tmpX[end-1], 
            (y-1)/tmpX[end-1]
        ]) 
        for x in tmpX, y in tmpX
    ]
    fpli = itp.linear_interpolation(
        (tmpX, tmpX), tmpF,
        extrapolation_bc = itp.Line()
    )
    affine(x01) = x01 * tmpX[end-1] + 1
    
    tmpAllX01 = [(x,y) for x in tmpX01, y in tmpX01] |> vec |> stack |> permutedims

    Figs = plt.Plot[]



    # fig 01: interpolant vs. original
    _fig = plt.surface(
        Xtest, Xtest,
        (x,y) -> asg.evaluate(G, [x,y]),
        label = "ASG interpolant",
        color = :red,
        alpha = 0.6,
        colorbar = false,
        camera = (-30,30),
        title = "ASG",
    )
    plt.scatter!(_fig,
        allNodes[:,1], allNodes[:,2],
        asg.vectorize_nodal(G),
        label = "Supporting nodes",
        color = :blue,
        marker = :circle,
        markersize = 3,
    )
    push!(Figs, _fig)

    
    # fig 04: regular linear interpolation
    _fig = plt.surface(
        Xtest, Xtest,
        (x,y) -> fpli(affine(x), affine(y)),
        label = "Piecewise Linear interpolant",
        color = :red,
        alpha = 0.6,
        colorbar = false,
        camera = (-30,30),
        title = "Piecewise Linear",
    )
    plt.scatter!(_fig,
        tmpAllX01[:,1], tmpAllX01[:,2],
        tmpF[:],
        label = "Supporting nodes",
        color = :blue,
        marker = :circle,
        markersize = 3,
    )
    push!(Figs, _fig)






    # fig 02: error distribution
    _fig = plt.surface(
        Xtest, Xtest,
        (x,y) -> abs(f2fit([x,y]) - asg.evaluate(G, [x,y])) / abs(f2fit([x,y])) * 100,
        label = "relative error",
        alpha = 0.6,
        colorbar = false,
        camera = (-30,30),
        xlabel = "x1",
        ylabel = "x2",
        title = "ASG: Relative error (%)",
    )
    plt.surface!(
        _fig,
        Xtest, Xtest,
        (x,y) -> RTOL * 100,
        label = "tolerance",
        alpha = 0.6,
        colorbar = false,
    )
    push!(Figs, _fig)
    


    # fig 05: error distribution
    _fig = plt.surface(
        Xtest, Xtest,
        (x,y) -> abs(f2fit([x,y]) - fpli(affine(x), affine(y))) / abs(f2fit([x,y])) * 100,
        label = "relative error",
        alpha = 0.6,
        colorbar = false,
        camera = (-30,30),
        xlabel = "x1",
        ylabel = "x2",
        title = "Piecewise linear: Relative error (%)",
    )
    plt.surface!(
        _fig,
        Xtest, Xtest,
        (x,y) -> RTOL * 100,
        label = "tolerance",
        alpha = 0.6,
        colorbar = false,
    )
    push!(Figs, _fig)





    # fig 03: node distribution
    _fig = plt.scatter(
        allNodes[:,1], allNodes[:,2],
        label = "Supporting nodes",
        color = :blue,
        marker = :circle,
        markersize = 3,
        xlabel = "x1",
        ylabel = "x2",
        title = "ASG: #nodes = $(length(allNodes))",
    )
    push!(Figs, _fig)


    # fig 06: node distribution
    _fig = plt.scatter(
        tmpAllX01[:,1], tmpAllX01[:,2],
        label = "Supporting nodes",
        color = :blue,
        marker = :circle,
        markersize = 3,
        xlabel = "x1",
        ylabel = "x2",
        title = "Piecewise linear: #nodes = $(length(tmpX)^2)",
    )
    push!(Figs, _fig)



    plt.plot(Figs..., layout = (3,2), size = 400 .* (2,3))

    plt.savefig("example_2D.png")
end # 2D case








# ------------------------------------------------------------------------------
# EXAMPLE: 3D case
let
    RTOL = 1E-2
    G = asg.AdaptiveSparseGrid{3}(22, rtol = RTOL, atol = RTOL, use_rtol = true)
    asg.train!(
        G,
        f2fit,
    )

    Xtest    = LinRange(0.0,1.0,100)
    allNodes = asg.vectorize_x(G)

    # compare with regular linear interpolation
    tmpX   = 1:50
    tmpX01 = (tmpX .- 1) ./ tmpX[end-1]
    tmpF   = [
        f2fit([
            (x-1)/tmpX[end-1], 
            (y-1)/tmpX[end-1],
            (z-1)/tmpX[end-1],
        ]) 
        for x in tmpX, y in tmpX, z in tmpX
    ]
    fpli = itp.linear_interpolation(
        (tmpX, tmpX, tmpX), tmpF,
        extrapolation_bc = itp.Line()
    )
    affine(x01) = x01 * tmpX[end-1] + 1
    
    tmpAllX01 = [
        (x,y,z) 
        for x in tmpX01, y in tmpX01, z in tmpX01
    ] |> vec |> stack |> permutedims

    Figs = plt.Plot[]


    # figure: ASG node spatial distribution
    _fig = plt.scatter(
        allNodes[:,1], allNodes[:,2], allNodes[:,3],
        title = "ASG node, #nodes = $(length(allNodes))",
        xlabel = "x1",
        ylabel = "x2",
        zlabel = "x3",
        color = :blue,
        marker = :circle,
        markersize = 2,
        camera = (-30,30),
    )
    push!(Figs, _fig)

    # figure: error distribution of ASG & linear interpolation
    errASG = [
        abs(f2fit([x,y,z]) - asg.evaluate(G, [x,y,z])) / abs(f2fit([x,y,z])) * 100
        # abs(f2fit([x,y,z]) - asg.evaluate(G, [x,y,z])) 
        for x in Xtest, y in Xtest, z in Xtest
    ] |> vec
    errPLI = [
        abs(f2fit([x,y,z]) - fpli(affine(x), affine(y), affine(z))) / abs(f2fit([x,y,z])) * 100
        # abs(f2fit([x,y,z]) - fpli(affine(x), affine(y), affine(z))) 
        for x in Xtest, y in Xtest, z in Xtest
    ] |> vec

    _fig = plt.histogram(
        errASG,
        bins = 30,
        title = "Relative error (%)",
        label = "ASG, #nodes = $(length(allNodes))",
        xlabel = "",
        ylabel = "Density",
        alpha = 0.6,
        color = :red,
        normalize = true,
        margin = 5plt.mm,
    )
    plt.histogram!(_fig,
        errPLI,
        bins = 30,
        label = "Linear interpolation, #nodes = $(length(tmpX)^3)",
        alpha = 0.6,
        color = :blue,
        normalize = true,
    )
    plt.vline!(_fig, [RTOL * 100,], color = :black, linestyle = :dash, label = "tolerance") 
    push!(Figs, _fig)

    # figure: tail distribution of the error
    Qts = LinRange(0.95,1.0,20)
    _fig = plt.plot(
        Qts,
        stat.quantile(errASG, Qts),
        label = "ASG",
        color = :red,
        linestyle = :solid,
        linewidth = 2,
        xlabel = "Quantile",
        ylabel = "Relative error (%)",
        title = "Tail distribution or errors",
        margin = 5plt.mm,
    )
    plt.plot!(_fig,
        Qts,
        stat.quantile(errPLI, Qts),
        label = "Linear interpolation",
        color = :blue,
        linestyle = :solid,
        linewidth = 2,
    )
    plt.hline!(_fig, [RTOL * 100,], color = :black, linestyle = :dash, label = "tolerance")
    push!(Figs, _fig)


    fig = plt.plot(Figs..., layout = (1,3), size = (3 * 500,1 * 500))
    plt.savefig(fig, "example_3D.svg")
end # 3D case


