with source as (
    select * from {{ref('cashboost_dataset') }} -- curly braces are dbt specific syntax, telling dbt to handle the table
    -- ref tells dbt to look up the table, ensured dbt understands the dependency between models
),
renamed as (

    select
    -- identifiers
    farmer_id,
    "group" as treatment_group, -- wrapping in double quotes so duck db does not mistake it for GROUP by syntax
    treatment, 

    -- demographics
    region,
    farm_size,
    enrollment_cohort,
    age,
    female as is_female,
    household_size,

    -- baseline outcomes
    baseline_income_usd,
    baseline_food_security_score,
    baseline_farm_output_kg,

    -- endline outcomes
    endline_income_usd,
    endline_food_security_score,
    endline_farm_output_kg,

    -- derived
    income_change_usd,
    sessions_attended

from source
),

final as (

    select 
        *,
        case 
            when income_change_usd > 0 then 'Increased'
            when income_change_usd < 0 then 'Decreased'
            else 'No Change'
        end as income_direction

    from renamed
)

select * from final