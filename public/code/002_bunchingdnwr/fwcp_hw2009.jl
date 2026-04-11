module EmpiricalDownwardWageRigidityEstimators 
# abbreviation: edre
# ==============================================================================
import Statistics: quantile

import KernelDensity as kd
import QuadGK as qk


export fwcp
export HoldenWulfsberg2009


# ==============================================================================
# Generic helpers
# ==============================================================================
function validate_vec!(x::AbstractVector)::Nothing
    if length(x) < 1
        throw(ArgumentError("Input vector must have at least one element"))
    end
    if any(isnan, x)
        throw(ArgumentError("Input vector must not contain NaN values"))
    end
    if any(isinf, x)
        throw(ArgumentError("Input vector must not contain Inf values"))
    end
    return nothing
end
# ------------------------------------------------------------------------------
function validate_qt!(x::Real)::Nothing
    if isnan(x)
        throw(ArgumentError("Input quantile must not be NaN"))
    end
    if isinf(x)
        throw(ArgumentError("Input quantile must not be Inf"))
    end
    if !(0 <= x <= 1)
        throw(ArgumentError("Input quantile must be in [0,1]"))
    end
    return nothing
end
# ------------------------------------------------------------------------------
function validate_qtrange!(x::NTuple{2,Real})::Nothing
    validate_qt(x[1])
    validate_qt(x[2])
    if x[1] > x[2]
        throw(ArgumentError("Input quantile range must have first element <= second element"))
    end
    return nothing
end
# ------------------------------------------------------------------------------





# ==============================================================================
# Symmetry-based estimator: Holden and Wulfsberg (2009, JME)
# ==============================================================================
function hw09_rescale!(G01::Vector{Float64}, loc::Float64, dispersion::Float64)
    G01 .*= dispersion
    G01 .+= loc
    return nothing
end
# ------------------------------------------------------------------------------
function hw09_rescale_G01(
    G01::Vector{Float64},
    datObs::AbstractVector{<:Real};
    topCut::Real = 0.25,
    normQt::NTuple{2,Real} = (0.35, 0.75)
)::Vector{Float64}
    qtObs = quantile(datObs, normQt)
    midObs = quantile(datObs, 0.5)
    GObs = similar(G01)
    hw09_rescale!(GObs, midObs, qtObs[2] - qtObs[1])
    return GObs
end
# ------------------------------------------------------------------------------
mutable struct HoldenWulfsberg2009
    datNotional::Vector{Float64}
    topCut::Float64
    normQt::NTuple{2,Float64}

    function HoldenWulfsberg2009(
        refDat::AbstractVector{<:Real} ;
        topCut::Real = 0.25,
        normQt::NTuple{2,Real} = (0.35, 0.75)
    )
        validate_vec!(refDat)
        validate_qt!(topCut)
        validate_qtrange!(normQt)

        datTop = refDat[refDat .>= quantile(refDat, 1 - topCut)]
        
        datMid = minimum(datTop)
        G = vcat(datTop, 2 * datMid .- datTop)
        datNotional = (G .- datMid) ./ (quantile(G,normQt[2]) - quantile(G,normQt[1]))

        new(datNotional, topCut, normQt)
    end
end # HoldenWulfsberg2009
# ------------------------------------------------------------------------------
function fwcp(
    hw    ::HoldenWulfsberg2009, 
    datObs::AbstractVector{<:Real} ;
    
    method::
)


















































# ==============================================================================
end # module EmpiricalDownwardWageRigidityEstimators