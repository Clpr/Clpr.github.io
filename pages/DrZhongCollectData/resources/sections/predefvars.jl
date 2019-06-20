module predefvars


# ----------------- quick method to initialized a given-size Any matrix
empty_tablematrix( nrow::Int, ncol::Int ; placeholder::Any = "" ) = begin
    local tmpmat = Any[]
    for x in 1:nrow, y in 1:ncol
        push!(tmpmat, placeholder)
    end

    return reshape( tmpmat, (nrow,ncol) )::Matrix{Any}
end # empty_tablematrix








# ----------------- SEX CANDIDATES
Sex = [ "Male", "Female", "Unknown" ]


# ----------------- RACE CANDIDATES
Races = [
    "Unknown",
    "White", "Black or African American",
    "Asian", "American Indian or Alaska Native",
    "Hispanic or Latino", "Native Hawaiian or Other Pacific Islander",
    "Half-blood", "Other",
]

# ----------------- RESEARCH FIELDS
Fields = [
    "Unknown (#)",
    "Other (Z)",
    "Agricultural economics (Q)", "Business economics (M)", "Computational economics (C)", "Decision theory (D)",
    "Demographic economics (J)", "Development economics (O)", "Econometrics (C)", "Economic geography (Q)",
    "Economic history (N)", "Economic model (C)", "Economic planning (P)", "Economic policy (E)",
    "Economic sociology (Y)", "Economic statistics (C)", "Economic theory (A)", "Education economics (I)",
    "Environmental economics (Q)", "Experimental economics (Z)", "Financial economics (G)", "Game theory (D)",
    "Health economics (I)", "Industrial engineering (L)", "Industrial organization (L)", "Input-output model (E)",
    "International economics (F)", "Knowledge economics (O)", "Labor economics (J)", "Law and economics (K)",
    "Macroeconomics (E)", "Mathematical economics (C)", "Mathematical finance (G)", "Mechanism design (D)",
    "Microeconomics (D)", "Monetary economics (E)", "Natural resource (Q)", "Political economy (A)",
    "Public choice (H)", "Public economics (H)", "Regional economics (R)", "Service economics (R)",
    "Socioeconomics (Y)", "Transportation (R)", "Urban economics (R)", "Welfare economics (I)",
]


# -------------------------- MAJOR (DEPARTMENT)
Majors = [
    "Unknown",
    "D of Economics", "D of Finance", "D of Applied Econ", "D of Agri Econ", "D of Stats", "Other Depart(s)",
]


# ----------------------- ACADEMIC TITLES
AcademicTitles = [
    "Assistant Professor", "Associate Professor", "Professor",
    "Assistant Teaching Professor", "Assistant Research Professor",
    "Visiting Assistant Professor", "Professor of Practice", "Adjunct Professor",
]

# ----------------------- ACADEMIC DEPARTMENT
AcademicDept = [
    "Unknown",
    "Economics", "Applied Economics", "Finance", "Statistics", "Biostatistics", "Mathematics", "Physics",
    "Other natural sciences", "Other social sciences", "Arts, literature or languages", "Engineering",
    "Other",
]

# ----------------------- INDUSTRIAL TITLES
IndustrialTitles = [
    "Unknown",
    "Founder", "CEO", "Chairman", "Director on board", "Department director",
    "Economist/Analyst", "Advisor/Consultant", "Administration",
    "Other"
]

# ---------------------- INDUSTRIAL INSTITUTION TYPE
IndustrialInstitutionTypes = [
    "Unknown",
    "Bank", "Hedge Fund", "Investment Fund", "Private Equity Fund",
    "Consulting", "Investment Bank",
    "Tech (e.g. AI)", "Manufacturing", "Agricultural",
    "Other",
]

# ---------------------- GOVERNMENT TITLE
GovernmentTitles = [
    "Unknown",
    "Senior Research Fellow", "Junior Research Fellow", "Associate Research Fellow", "Researcher",
    "President", "Vice President", "Director", "Advisor/Consultant",
    "Other research titles","Other administrative titles",
]


# ------------------------- GOVERNMENT DEPARTMENT
GovernmentDept = [
    "Unknown",
    "State House or equivalent",
    "Ministry/Depart of Treasury/Finance",
    "Security/Exchange authority",
    "Fed/Central banks",
    "Local government",
    "Other",
]


# ------------------------ NGO TITLES
NGOTitles = [
    "Unknown",
    "Senior Research Fellow", "Junior Research Fellow", "Associate Research Fellow", "Researcher",
    "President", "Vice President", "Director", "Advisor/Consultant",
    "Other research titles","Other administrative titles",
]

# ------------------------ NGO TYPES
NGOTypes = [
    "Unknown",
    "United Nations", "World Bank", "IMF", "WTO", "OECD",
    "Other NGO",
]



# ------------------------ SOCIETY TITLES/POSITIONS
SocietyPositions = [
    "Unknown",
    "Research Assistant (NBER)", "Research Associate (NBER)", "Faculty Research Fellow (NBER)",
    "Fellow (ES)", "Membership (ES)",
    "President", "Vice President", "Executive Vice-president", "Department Director",
    "Other research titles","Other administrative titles",
]


# ------------------------ FUNDING TYPES
FundingTypes = [
    "Unknown",
    "Fellowship", "Program/Project", "Award",
    "Other",
]


# ------------------------ FUNDING GRANT BY
FundingGrantBy = [
    "Unknown",
    "NSF of US", "NSFC of China", "NSF of UK", "NSF of European countries", "NSF of other countries",
    "Academy Funding of US", "Academy Funding of China",
    "Academy Funding of UK", "Academy Funding of European countries", "Academy Funding of other countries",
    "General fellowship", "General award", "Private funding",
    "Other",
]



# ------------------------ EDITORIAL TITLES
EditorialTitles = [
    "Unknown",
    "Editor", "Assistant editor", "Associate editor", "Cheif/President editor", "Co-editor", "Editor on board",
    "Other",
]





















end # predefvars
